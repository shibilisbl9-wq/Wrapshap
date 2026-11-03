package com.shibili.kharcha.data

import android.content.Context
import android.util.Log
import androidx.glance.appwidget.updateAll
import com.shibili.kharcha.widget.BalanceWidget
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.time.LocalDate
import java.time.YearMonth

/**
 * Tiny JSON-file backed store. All data lives on the device in
 * files/kharcha.json – nothing leaves the phone.
 */
object Store {
    private const val FILE = "kharcha.json"
    private const val TAG = "KharchaStore"

    private val _state = MutableStateFlow(AppState())
    val state: StateFlow<AppState> = _state.asStateFlow()

    private lateinit var appContext: Context
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val writeLock = Mutex()

    @Volatile
    private var loaded = false

    @Synchronized
    fun init(context: Context) {
        if (loaded) return
        appContext = context.applicationContext
        _state.value = read(appContext)
        loaded = true
    }

    data class SaveResult(
        val isNew: Boolean,
        val type: TxType,
        val streakBefore: Int,
        val streakAfter: Int,
        val budgetPctBefore: Int,
        val budgetPctAfter: Int,
    )

    fun upsert(txn: Txn): SaveResult {
        val before = _state.value
        val isNew = before.txns.none { it.id == txn.id }
        mutate { s ->
            val list = (s.txns.filterNot { it.id == txn.id } + txn).sortedByDescending { it.time }
            val streak = Stats.streak(list)
            s.copy(txns = list, bestStreak = maxOf(s.bestStreak, streak))
        }
        val after = _state.value
        return SaveResult(
            isNew = isNew,
            type = txn.type,
            streakBefore = Stats.streak(before.txns),
            streakAfter = Stats.streak(after.txns),
            budgetPctBefore = budgetPct(before),
            budgetPctAfter = budgetPct(after),
        )
    }

    fun delete(id: Long) = mutate { s -> s.copy(txns = s.txns.filterNot { it.id == id }) }

    fun setCurrency(code: String) = mutate { it.copy(currency = code) }

    fun setBudget(minor: Long) = mutate { it.copy(budget = minor.coerceAtLeast(0)) }

    fun clearAll() = mutate { AppState(currency = it.currency) }

    fun newId(): Long = System.currentTimeMillis() * 1000 + (0..999).random()

    private fun budgetPct(s: AppState): Int {
        if (s.budget <= 0) return 0
        val spent = Stats.totals(Stats.inMonth(s.txns, YearMonth.from(LocalDate.now()))).expense
        return ((spent * 100) / s.budget).toInt()
    }

    private fun mutate(block: (AppState) -> AppState) {
        _state.update(block)
        if (!loaded) return
        scope.launch {
            writeLock.withLock { write(appContext, _state.value) }
            runCatching { BalanceWidget().updateAll(appContext) }
                .onFailure { Log.w(TAG, "widget update failed", it) }
        }
    }

    // ---------- persistence ----------

    fun read(context: Context): AppState {
        val f = File(context.filesDir, FILE)
        if (!f.exists()) return AppState()
        return try {
            val o = JSONObject(f.readText())
            val arr = o.optJSONArray("txns") ?: JSONArray()
            val list = ArrayList<Txn>(arr.length())
            for (i in 0 until arr.length()) {
                val t = arr.getJSONObject(i)
                list += Txn(
                    id = t.getLong("id"),
                    type = if (t.optString("t") == "I") TxType.INCOME else TxType.EXPENSE,
                    amount = t.getLong("a"),
                    categoryId = t.optString("c", "other_e"),
                    note = t.optString("n", ""),
                    time = t.getLong("ts"),
                )
            }
            AppState(
                txns = list.sortedByDescending { it.time },
                currency = o.optString("currency", "AED"),
                budget = o.optLong("budget", 0L),
                bestStreak = o.optInt("bestStreak", 0),
            )
        } catch (e: Exception) {
            Log.e(TAG, "Could not read data file", e)
            AppState()
        }
    }

    private fun write(context: Context, s: AppState) {
        val arr = JSONArray()
        s.txns.forEach { t ->
            arr.put(
                JSONObject()
                    .put("id", t.id)
                    .put("t", if (t.type == TxType.INCOME) "I" else "E")
                    .put("a", t.amount)
                    .put("c", t.categoryId)
                    .put("n", t.note)
                    .put("ts", t.time)
            )
        }
        val o = JSONObject()
            .put("v", 1)
            .put("currency", s.currency)
            .put("budget", s.budget)
            .put("bestStreak", s.bestStreak)
            .put("txns", arr)
        val dir = context.filesDir
        val tmp = File(dir, "$FILE.tmp")
        tmp.writeText(o.toString())
        if (!tmp.renameTo(File(dir, FILE))) {
            File(dir, FILE).writeText(o.toString())
            tmp.delete()
        }
    }
}
