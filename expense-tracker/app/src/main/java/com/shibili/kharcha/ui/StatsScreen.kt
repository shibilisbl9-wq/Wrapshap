package com.shibili.kharcha.ui

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shibili.kharcha.data.AppState
import com.shibili.kharcha.data.Money
import com.shibili.kharcha.data.Stats
import com.shibili.kharcha.data.TxType
import com.shibili.kharcha.data.toLocalDate
import java.time.LocalDate
import java.time.YearMonth
import java.time.format.TextStyle
import java.util.Locale

private fun YearMonth.index() = year * 12 + (monthValue - 1)
private fun ymOf(index: Int): YearMonth = YearMonth.of(index / 12, index % 12 + 1)

@Composable
fun StatsScreen(state: AppState) {
    val now = YearMonth.now()
    var ymIndex by rememberSaveable { mutableIntStateOf(now.index()) }
    var kind by rememberSaveable { mutableIntStateOf(0) }
    val ym = ymOf(ymIndex)
    val top = WindowInsets.statusBars.asPaddingValues().calculateTopPadding()

    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(start = 20.dp, end = 20.dp, top = top + 14.dp, bottom = 150.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Text("Stats", style = MaterialTheme.typography.headlineLarge, color = K.Text)

        MonthSwitcher(
            ym = ym,
            canNext = ymIndex < now.index(),
            onPrev = { ymIndex-- },
            onNext = { if (ymIndex < now.index()) ymIndex++ },
        )

        AnimatedContent(
            targetState = ymIndex,
            transitionSpec = {
                val dir = if (targetState > initialState) 1 else -1
                (slideInHorizontally(spring(dampingRatio = 0.8f, stiffness = Spring.StiffnessMediumLow)) { it * dir } + fadeIn()) togetherWith
                    (slideOutHorizontally { -it * dir } + fadeOut())
            },
            label = "month",
        ) { idx ->
            MonthBody(state, ymOf(idx), kind, onKind = { kind = it })
        }

        KCard {
            Text("Last 6 months", color = K.Text, fontWeight = FontWeight.Bold, fontSize = 16.sp)
            Spacer(Modifier.height(4.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Dot(K.Mint); Spacer(Modifier.width(6.dp))
                Text("Income", color = K.Muted, fontSize = 12.sp)
                Spacer(Modifier.width(14.dp))
                Dot(K.Coral); Spacer(Modifier.width(6.dp))
                Text("Spent", color = K.Muted, fontSize = 12.sp)
            }
            Spacer(Modifier.height(14.dp))
            val months = remember(state.txns, ymIndex) { Stats.lastMonths(state.txns, ym, 6) }
            val max = months.maxOf { maxOf(it.second.income, it.second.expense) }.coerceAtLeast(1)
            Row(
                Modifier.fillMaxWidth().height(150.dp),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.Bottom,
            ) {
                months.forEachIndexed { i, (m, t) ->
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Row(
                            Modifier.height(124.dp),
                            verticalAlignment = Alignment.Bottom,
                            horizontalArrangement = Arrangement.spacedBy(4.dp),
                        ) {
                            key2(ymIndex, i) {
                                GrowBar(t.income.toFloat() / max, K.mintCyan, i * 70L, 112.dp)
                                GrowBar(t.expense.toFloat() / max, K.coralOrange, i * 70L + 35, 112.dp)
                            }
                        }
                        Spacer(Modifier.height(6.dp))
                        Text(
                            m.month.getDisplayName(TextStyle.SHORT, Locale.getDefault()),
                            color = if (m == ym) K.Text else K.Muted,
                            fontSize = 11.sp,
                            fontWeight = if (m == ym) FontWeight.Bold else FontWeight.Normal,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun key2(a: Any, b: Any, content: @Composable () -> Unit) {
    androidx.compose.runtime.key(a, b) { content() }
}

@Composable
private fun MonthSwitcher(ym: YearMonth, canNext: Boolean, onPrev: () -> Unit, onNext: () -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(20.dp))
            .background(K.Card)
            .padding(6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        ArrowBtn("‹", true, onPrev)
        Text(
            ym.month.getDisplayName(TextStyle.FULL, Locale.getDefault()) + " " + ym.year,
            color = K.Text,
            fontWeight = FontWeight.Bold,
            fontSize = 16.sp,
            textAlign = TextAlign.Center,
            modifier = Modifier.weight(1f),
        )
        ArrowBtn("›", canNext, onNext)
    }
}

@Composable
private fun ArrowBtn(label: String, enabled: Boolean, onClick: () -> Unit) {
    Box(
        Modifier
            .size(40.dp)
            .bouncyClick(0.8f) { if (enabled) onClick() }
            .clip(CircleShape)
            .background(if (enabled) K.CardHi else Color.Transparent),
        contentAlignment = Alignment.Center,
    ) {
        Text(label, color = if (enabled) K.Text else K.Muted.copy(alpha = 0.3f), fontSize = 24.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun MonthBody(state: AppState, ym: YearMonth, kind: Int, onKind: (Int) -> Unit) {
    val cur = state.currency
    val monthTx = remember(state.txns, ym) { Stats.inMonth(state.txns, ym) }
    val totals = remember(monthTx) { Stats.totals(monthTx) }
    val type = if (kind == 0) TxType.EXPENSE else TxType.INCOME
    val parts = remember(monthTx, type) { Stats.breakdown(monthTx, type) }
    val total = parts.sumOf { it.second }
    var selected by remember(parts) { mutableIntStateOf(0) }

    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            StatChip("Income", Money.compact(totals.income, cur), K.Mint, Modifier.weight(1f))
            StatChip("Spent", Money.compact(totals.expense, cur), K.Coral, Modifier.weight(1f))
            val saved = if (totals.income > 0) ((totals.balance * 100) / totals.income).toInt() else 0
            StatChip("Saved", if (totals.income > 0) "$saved%" else "—", K.Amber, Modifier.weight(1f))
        }

        SegmentedPill(
            listOf("Spending", "Income"),
            selected = kind,
            onSelect = onKind,
            brushes = listOf(K.coralOrange, K.mintCyan),
        )

        KCard {
            if (parts.isEmpty()) {
                EmptyState(
                    if (type == TxType.EXPENSE) "No spending logged" else "No income logged",
                    "Add entries and watch this fill up",
                    "📊",
                )
            } else {
                val sel = selected.coerceIn(0, parts.lastIndex)
                DonutChart(
                    slices = parts.map { Slice(it.first.color, it.second) },
                    selected = sel,
                    modifier = Modifier.size(220.dp).align(Alignment.CenterHorizontally),
                ) {
                    AnimatedContent(targetState = sel, label = "center") { s ->
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(parts[s].first.emoji, fontSize = 28.sp)
                            Text(parts[s].first.name, color = K.Muted, fontSize = 12.sp)
                            Text(
                                Money.compact(parts[s].second, cur),
                                color = K.Text,
                                fontWeight = FontWeight.ExtraBold,
                                fontSize = 18.sp,
                            )
                        }
                    }
                }
                Spacer(Modifier.height(16.dp))
                parts.forEachIndexed { i, (cat, amt) ->
                    val frac = amt.toFloat() / total.coerceAtLeast(1)
                    val isSel = i == sel
                    val bg by animateFloatAsState(if (isSel) 1f else 0f, label = "legendBg")
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .bouncyClick(0.97f) { selected = i }
                            .clip(RoundedCornerShape(16.dp))
                            .background(K.CardHi.copy(alpha = bg))
                            .padding(horizontal = 10.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(cat.emoji, fontSize = 20.sp)
                        Spacer(Modifier.width(10.dp))
                        Column(Modifier.weight(1f)) {
                            Row {
                                Text(cat.name, color = K.Text, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                                Spacer(Modifier.weight(1f))
                                Text(Money.format(amt, cur), color = K.Text, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                            }
                            Spacer(Modifier.height(6.dp))
                            ProgressLine(frac, cat.color)
                        }
                        Spacer(Modifier.width(10.dp))
                        Text(
                            "${(frac * 100).toInt()}%",
                            color = K.Muted,
                            fontSize = 12.sp,
                            modifier = Modifier.width(34.dp),
                            textAlign = TextAlign.End,
                        )
                    }
                }
            }
        }

        FunFacts(monthTx, ym, cur)
    }
}

@Composable
private fun ProgressLine(fraction: Float, color: Color) {
    val anim = remember { androidx.compose.animation.core.Animatable(0f) }
    LaunchedEffect(fraction) {
        anim.animateTo(fraction, spring(dampingRatio = 0.7f, stiffness = Spring.StiffnessLow))
    }
    Box(
        Modifier
            .fillMaxWidth()
            .height(6.dp)
            .clip(RoundedCornerShape(3.dp))
            .background(Color.White.copy(alpha = 0.07f))
    ) {
        Box(
            Modifier
                .fillMaxWidth(anim.value.coerceIn(0.01f, 1f))
                .fillMaxHeight()
                .clip(RoundedCornerShape(3.dp))
                .background(color)
        )
    }
}

@Composable
private fun StatChip(label: String, value: String, color: Color, modifier: Modifier) {
    Column(
        modifier
            .clip(RoundedCornerShape(20.dp))
            .background(K.Card)
            .padding(horizontal = 12.dp, vertical = 12.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Dot(color)
            Spacer(Modifier.width(6.dp))
            Text(label, color = K.Muted, fontSize = 12.sp)
        }
        Spacer(Modifier.height(4.dp))
        Text(value, color = K.Text, fontWeight = FontWeight.ExtraBold, fontSize = 16.sp, maxLines = 1)
    }
}

@Composable
private fun FunFacts(monthTx: List<com.shibili.kharcha.data.Txn>, ym: YearMonth, cur: String) {
    val expenses = monthTx.filter { it.type == TxType.EXPENSE }
    if (expenses.isEmpty()) return
    val today = LocalDate.now()
    val daysCounted = if (ym == YearMonth.from(today)) today.dayOfMonth else ym.lengthOfMonth()
    val avg = expenses.sumOf { it.amount } / daysCounted.coerceAtLeast(1)
    val biggest = expenses.maxBy { it.amount }
    val topDay = expenses.groupBy { it.time.toLocalDate() }.maxBy { (_, l) -> l.sumOf { it.amount } }
    val noSpendDays = (1..daysCounted).count { d ->
        val date = ym.atDay(d)
        expenses.none { it.time.toLocalDate() == date }
    }

    KCard {
        Text("Fun facts", color = K.Text, fontWeight = FontWeight.Bold, fontSize = 16.sp)
        Spacer(Modifier.height(10.dp))
        Fact("📅", "Daily average", Money.format(avg, cur))
        Fact(
            "💥",
            "Biggest spend",
            Money.format(biggest.amount, cur) + " · " + com.shibili.kharcha.data.Categories.byId(biggest.categoryId).name,
        )
        Fact(
            "🌋",
            "Heaviest day",
            topDay.key.dayOfMonth.toString() + " " +
                topDay.key.month.getDisplayName(TextStyle.SHORT, Locale.getDefault()) +
                " · " + Money.format(topDay.value.sumOf { it.amount }, cur),
        )
        Fact("😇", "No-spend days", "$noSpendDays")
    }
}

@Composable
private fun Fact(emoji: String, label: String, value: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(
            Modifier.size(38.dp).clip(RoundedCornerShape(12.dp)).background(K.CardHi),
            contentAlignment = Alignment.Center,
        ) { Text(emoji, fontSize = 18.sp, modifier = Modifier.graphicsLayer { }) }
        Spacer(Modifier.width(12.dp))
        Text(label, color = K.Muted, fontSize = 14.sp, modifier = Modifier.weight(1f))
        Text(value, color = K.Text, fontWeight = FontWeight.Bold, fontSize = 14.sp)
    }
}
