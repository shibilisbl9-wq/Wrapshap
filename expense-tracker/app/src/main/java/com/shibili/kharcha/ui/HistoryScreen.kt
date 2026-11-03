package com.shibili.kharcha.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shibili.kharcha.data.AppState
import com.shibili.kharcha.data.Categories
import com.shibili.kharcha.data.Money
import com.shibili.kharcha.data.TxType
import com.shibili.kharcha.data.Txn
import com.shibili.kharcha.data.toLocalDate

@Composable
fun HistoryScreen(state: AppState, onEdit: (Txn) -> Unit, onDelete: (Txn) -> Unit) {
    var filter by rememberSaveable { mutableIntStateOf(0) }
    var query by rememberSaveable { mutableStateOf("") }
    val top = WindowInsets.statusBars.asPaddingValues().calculateTopPadding()

    val filtered = remember(state.txns, filter, query) {
        val q = query.trim().lowercase()
        state.txns.filter { t ->
            val typeOk = when (filter) {
                1 -> t.type == TxType.EXPENSE
                2 -> t.type == TxType.INCOME
                else -> true
            }
            typeOk && (q.isEmpty() ||
                t.note.lowercase().contains(q) ||
                Categories.byId(t.categoryId).name.lowercase().contains(q))
        }
    }
    val groups = remember(filtered) { filtered.groupBy { it.time.toLocalDate() }.toList() }

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 20.dp, end = 20.dp, top = top + 14.dp, bottom = 150.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item(key = "title") {
            Text("History", style = MaterialTheme.typography.headlineLarge, color = K.Text)
        }
        item(key = "search") { SearchField(query) { query = it } }
        item(key = "filter") {
            SegmentedPill(
                listOf("All", "Spent", "Income"),
                selected = filter,
                onSelect = { filter = it },
                brushes = listOf(K.violetPink, K.coralOrange, K.mintCyan),
            )
        }
        if (groups.isEmpty()) {
            item(key = "empty") {
                if (state.txns.isEmpty()) EmptyState("No history yet", "Your entries will show up here", "📜")
                else EmptyState("No matches", "Try a different search or filter", "🔍")
            }
        }
        groups.forEach { (day, list) ->
            item(key = "h$day") {
                val net = list.sumOf { if (it.type == TxType.INCOME) it.amount else -it.amount }
                Row(
                    Modifier.fillMaxWidth().padding(top = 10.dp, start = 4.dp, end = 4.dp).animateItem(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(dayTitle(list.first().time), color = K.Text, fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    Spacer(Modifier.weight(1f))
                    Text(
                        Money.format(net, state.currency, signed = true),
                        color = if (net >= 0) K.Mint else K.Muted,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 13.sp,
                    )
                }
            }
            items(list, key = { it.id }) { t ->
                Box(Modifier.animateItem()) {
                    AppearIn(0) {
                        SwipeTxnRow(t, state.currency, { onEdit(t) }, { onDelete(t) }, withDay = false)
                    }
                }
            }
        }
    }
}

@Composable
private fun SearchField(value: String, onChange: (String) -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .height(50.dp)
            .clip(RoundedCornerShape(18.dp))
            .background(K.Card)
            .padding(horizontal = 16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("🔎", fontSize = 16.sp)
        Spacer(Modifier.width(10.dp))
        Box(Modifier.weight(1f)) {
            if (value.isEmpty()) Text("Search notes or categories", color = K.Muted, fontSize = 15.sp)
            BasicTextField(
                value = value,
                onValueChange = onChange,
                singleLine = true,
                textStyle = TextStyle(color = K.Text, fontSize = 15.sp),
                cursorBrush = SolidColor(K.Violet),
                modifier = Modifier.fillMaxWidth(),
            )
        }
        if (value.isNotEmpty()) {
            Text(
                "✕",
                color = K.Muted,
                fontSize = 16.sp,
                modifier = Modifier.bouncyClick { onChange("") }.padding(6.dp),
            )
        }
    }
}
