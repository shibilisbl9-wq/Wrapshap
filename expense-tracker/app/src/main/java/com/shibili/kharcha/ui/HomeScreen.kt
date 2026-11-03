package com.shibili.kharcha.ui

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shibili.kharcha.data.AppState
import com.shibili.kharcha.data.Money
import com.shibili.kharcha.data.Stats
import com.shibili.kharcha.data.Store
import com.shibili.kharcha.data.Totals
import com.shibili.kharcha.data.TxType
import com.shibili.kharcha.data.Txn
import java.time.LocalDate
import java.time.LocalTime
import java.time.YearMonth
import java.time.format.DateTimeFormatter
import java.time.format.TextStyle
import java.util.Locale

@Composable
fun HomeScreen(
    state: AppState,
    onAdd: (TxType) -> Unit,
    onEdit: (Txn) -> Unit,
    onDelete: (Txn) -> Unit,
    onSeeAll: () -> Unit,
) {
    val today = LocalDate.now()
    val month = YearMonth.from(today)
    val monthTx = remember(state.txns) { Stats.inMonth(state.txns, month) }
    val totals = remember(monthTx) { Stats.totals(monthTx) }
    val streak = remember(state.txns) { Stats.streak(state.txns, today) }
    val loggedToday = remember(state.txns) { Stats.loggedOn(state.txns, today) }
    val recent = remember(state.txns) { state.txns.take(6) }
    var showBudget by rememberSaveable { mutableStateOf(false) }
    val top = WindowInsets.statusBars.asPaddingValues().calculateTopPadding()

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 20.dp, end = 20.dp, top = top + 14.dp, bottom = 150.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item(key = "header") { AppearIn(0) { Header(streak, loggedToday) } }
        item(key = "hero") { AppearIn(1) { BalanceCard(totals, state.currency, month) } }
        item(key = "budget") {
            AppearIn(2) {
                BudgetCard(state.budget, totals.expense, state.currency, today) { showBudget = true }
            }
        }
        item(key = "quick") { AppearIn(3) { QuickAdd(onAdd) } }
        item(key = "recentTitle") {
            AppearIn(4) {
                SectionTitle("Recent", if (state.txns.size > 0) "See all" else null, onSeeAll)
            }
        }
        if (recent.isEmpty()) {
            item(key = "empty") {
                EmptyState("Nothing here yet", "Tap + to log your first entry ✨")
            }
        } else {
            itemsIndexed(recent, key = { _, t -> t.id }) { i, t ->
                Box(Modifier.animateItem()) {
                    AppearIn(5 + i) {
                        SwipeTxnRow(t, state.currency, onClick = { onEdit(t) }, onDelete = { onDelete(t) })
                    }
                }
            }
        }
    }

    if (showBudget) {
        BudgetDialog(
            current = state.budget,
            currency = state.currency,
            onDismiss = { showBudget = false },
            onSave = { Store.setBudget(it); showBudget = false },
        )
    }
}

private fun greeting(): Pair<String, String> {
    val h = LocalTime.now().hour
    return when {
        h < 5 -> "Night owl mode" to "🦉"
        h < 12 -> "Good morning" to "☀️"
        h < 17 -> "Good afternoon" to "🌤️"
        h < 21 -> "Good evening" to "🌆"
        else -> "Good night" to "🌙"
    }
}

@Composable
private fun Header(streak: Int, loggedToday: Boolean) {
    val (hello, emoji) = remember { greeting() }
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f)) {
            Text(
                LocalDate.now().format(DateTimeFormatter.ofPattern("EEEE, d MMM")),
                color = K.Muted,
                fontSize = 13.sp,
            )
            Text("$hello $emoji", style = MaterialTheme.typography.headlineMedium, color = K.Text)
        }
        Row(
            Modifier
                .clip(RoundedCornerShape(20.dp))
                .background(if (loggedToday) K.Amber.copy(alpha = 0.16f) else K.Card)
                .border(1.dp, if (loggedToday) K.Amber.copy(alpha = 0.5f) else K.Stroke, RoundedCornerShape(20.dp))
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Flame(active = loggedToday && streak > 0)
            Spacer(Modifier.width(4.dp))
            Text(
                "$streak",
                color = if (loggedToday) K.Amber else K.Muted,
                fontWeight = FontWeight.ExtraBold,
                fontSize = 17.sp,
            )
        }
    }
}

@Composable
private fun BalanceCard(totals: Totals, currency: String, month: YearMonth) {
    val inf = rememberInfiniteTransition(label = "blobs")
    val drift by inf.animateFloat(
        -1f, 1f,
        infiniteRepeatable(tween(4200, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "drift",
    )
    Box(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(30.dp))
            .background(K.hero)
    ) {
        Canvas(Modifier.matchParentSize()) {
            val d = drift * 28f
            drawCircle(
                Color.White.copy(alpha = 0.13f),
                radius = size.width * 0.34f,
                center = Offset(size.width * 0.92f + d, size.height * 0.05f - d / 2),
            )
            drawCircle(
                Color.White.copy(alpha = 0.08f),
                radius = size.width * 0.22f,
                center = Offset(size.width * 0.12f - d, size.height * 1.02f + d / 3),
            )
            drawCircle(
                Color.White.copy(alpha = 0.10f),
                radius = size.width * 0.05f,
                center = Offset(size.width * 0.62f + d * 1.5f, size.height * 0.28f),
            )
        }
        Column(Modifier.padding(22.dp)) {
            Text(
                "Balance · " + month.month.getDisplayName(TextStyle.FULL, Locale.getDefault()),
                color = Color.White.copy(alpha = 0.85f),
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
            )
            Spacer(Modifier.height(4.dp))
            AnimatedMoney(
                totals.balance,
                currency,
                style = MaterialTheme.typography.headlineLarge.copy(fontSize = 38.sp),
                color = Color.White,
            )
            Spacer(Modifier.height(18.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                MiniStat("Income", "↑", totals.income, currency, Modifier.weight(1f))
                MiniStat("Spent", "↓", totals.expense, currency, Modifier.weight(1f))
            }
        }
    }
}

@Composable
private fun MiniStat(label: String, arrow: String, value: Long, currency: String, modifier: Modifier) {
    Row(
        modifier
            .clip(RoundedCornerShape(18.dp))
            .background(Color.White.copy(alpha = 0.17f))
            .padding(10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier.size(30.dp).clip(CircleShape).background(Color.White.copy(alpha = 0.25f)),
            contentAlignment = Alignment.Center,
        ) { Text(arrow, color = Color.White, fontWeight = FontWeight.ExtraBold) }
        Spacer(Modifier.width(8.dp))
        Column {
            Text(label, color = Color.White.copy(alpha = 0.8f), fontSize = 11.sp)
            AnimatedMoney(
                value,
                currency,
                style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.ExtraBold),
                color = Color.White,
            )
        }
    }
}

@Composable
private fun BudgetCard(budget: Long, spent: Long, currency: String, today: LocalDate, onSet: () -> Unit) {
    if (budget <= 0) {
        Row(
            Modifier
                .fillMaxWidth()
                .bouncyClick(0.96f) { onSet() }
                .clip(RoundedCornerShape(24.dp))
                .background(K.Card)
                .border(1.5.dp, Brush.linearGradient(listOf(K.Violet, K.Cyan)), RoundedCornerShape(24.dp))
                .padding(18.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            FloatingEmoji("🎯", 30)
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text("Set a monthly budget", color = K.Text, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                Text("Get a heads-up before you overspend", color = K.Muted, fontSize = 13.sp)
            }
            Text("›", color = K.Violet, fontSize = 28.sp, fontWeight = FontWeight.Bold)
        }
        return
    }
    val fraction = (spent.toFloat() / budget).coerceAtLeast(0f)
    val left = budget - spent
    val daysLeft = today.lengthOfMonth() - today.dayOfMonth + 1
    val perDay = if (left > 0) left / daysLeft else 0L
    Row(
        Modifier
            .fillMaxWidth()
            .bouncyClick(0.97f) { onSet() }
            .clip(RoundedCornerShape(24.dp))
            .background(K.Card)
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        BudgetRing(fraction, Modifier.size(82.dp))
        Spacer(Modifier.width(16.dp))
        Column(Modifier.weight(1f)) {
            Text("Monthly budget", color = K.Muted, fontSize = 13.sp)
            if (left >= 0) {
                Text(
                    Money.format(left, currency) + " left",
                    color = K.Text,
                    fontWeight = FontWeight.ExtraBold,
                    fontSize = 19.sp,
                )
                Text(
                    "≈ ${Money.format(perDay, currency)}/day for $daysLeft days",
                    color = if (fraction >= 0.9f) K.Coral else K.Mint,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium,
                )
            } else {
                Text(
                    Money.format(-left, currency) + " over 😬",
                    color = K.Coral,
                    fontWeight = FontWeight.ExtraBold,
                    fontSize = 19.sp,
                )
                Text("Time to slow down a little", color = K.Muted, fontSize = 13.sp)
            }
            Text("of " + Money.format(budget, currency), color = K.Muted, fontSize = 12.sp)
        }
    }
}

@Composable
private fun QuickAdd(onAdd: (TxType) -> Unit) {
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        QuickButton("Expense", "−", K.coralOrange, Modifier.weight(1f)) { onAdd(TxType.EXPENSE) }
        QuickButton("Income", "+", K.mintCyan, Modifier.weight(1f)) { onAdd(TxType.INCOME) }
    }
}

@Composable
private fun QuickButton(label: String, sign: String, brush: Brush, modifier: Modifier, onClick: () -> Unit) {
    Row(
        modifier
            .bouncyClick(0.9f) { onClick() }
            .clip(RoundedCornerShape(22.dp))
            .background(K.Card)
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier.size(36.dp).clip(RoundedCornerShape(12.dp)).background(brush),
            contentAlignment = Alignment.Center,
        ) { Text(sign, color = Color.White, fontSize = 22.sp, fontWeight = FontWeight.ExtraBold) }
        Spacer(Modifier.width(10.dp))
        Text(label, color = K.Text, fontWeight = FontWeight.Bold, fontSize = 15.sp)
    }
}
