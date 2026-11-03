package com.shibili.kharcha.data

import java.time.Instant
import java.time.LocalDate
import java.time.YearMonth
import java.time.ZoneId

data class Totals(val income: Long = 0, val expense: Long = 0) {
    val balance: Long get() = income - expense
}

fun Long.toLocalDate(): LocalDate =
    Instant.ofEpochMilli(this).atZone(ZoneId.systemDefault()).toLocalDate()

object Stats {
    fun inMonth(txns: List<Txn>, ym: YearMonth): List<Txn> =
        txns.filter { YearMonth.from(it.time.toLocalDate()) == ym }

    fun totals(txns: List<Txn>): Totals {
        var inc = 0L
        var exp = 0L
        for (t in txns) if (t.type == TxType.INCOME) inc += t.amount else exp += t.amount
        return Totals(inc, exp)
    }

    /**
     * Consecutive days (ending today, or yesterday if nothing logged yet today)
     * with at least one entry of any kind.
     */
    fun streak(txns: List<Txn>, today: LocalDate = LocalDate.now()): Int {
        if (txns.isEmpty()) return 0
        val days = txns.mapTo(HashSet()) { it.time.toLocalDate() }
        var d = if (today in days) today else today.minusDays(1)
        var count = 0
        while (d in days) {
            count++
            d = d.minusDays(1)
        }
        return count
    }

    fun loggedOn(txns: List<Txn>, date: LocalDate): Boolean =
        txns.any { it.time.toLocalDate() == date }

    fun breakdown(txns: List<Txn>, type: TxType): List<Pair<Category, Long>> =
        txns.filter { it.type == type }
            .groupBy { it.categoryId }
            .map { (id, list) -> Categories.byId(id) to list.sumOf { it.amount } }
            .sortedByDescending { it.second }

    fun lastMonths(txns: List<Txn>, end: YearMonth, n: Int = 6): List<Pair<YearMonth, Totals>> {
        val byMonth = txns.groupBy { YearMonth.from(it.time.toLocalDate()) }
        return (n - 1 downTo 0).map { back ->
            val ym = end.minusMonths(back.toLong())
            ym to totals(byMonth[ym].orEmpty())
        }
    }
}
