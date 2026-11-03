package com.shibili.kharcha.ui

import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shibili.kharcha.data.AppState
import com.shibili.kharcha.data.Money
import com.shibili.kharcha.data.Stats
import com.shibili.kharcha.data.Store
import java.time.LocalDate
import java.time.format.TextStyle
import java.util.Locale

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun SettingsScreen(state: AppState) {
    val top = WindowInsets.statusBars.asPaddingValues().calculateTopPadding()
    val today = LocalDate.now()
    val streak = remember(state.txns) { Stats.streak(state.txns, today) }
    var showBudget by rememberSaveable { mutableStateOf(false) }
    var confirmWipe by rememberSaveable { mutableStateOf(false) }

    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(start = 20.dp, end = 20.dp, top = top + 14.dp, bottom = 150.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Text("You", style = MaterialTheme.typography.headlineLarge, color = K.Text)

        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            BigStat("🔥", "$streak", "Day streak", Modifier.weight(1f), K.Amber)
            BigStat("🏆", "${maxOf(state.bestStreak, streak)}", "Best streak", Modifier.weight(1f), K.Violet)
            BigStat("🧾", "${state.txns.size}", "Entries", Modifier.weight(1f), K.Cyan)
        }

        KCard {
            Text("Your week", color = K.Text, fontWeight = FontWeight.Bold, fontSize = 16.sp)
            Text(
                if (Stats.loggedOn(state.txns, today)) "Logged today — streak is safe ✅"
                else "Log something today to keep the flame alive 🔥",
                color = K.Muted,
                fontSize = 13.sp,
            )
            Spacer(Modifier.height(14.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                (6 downTo 0).forEachIndexed { i, back ->
                    val d = today.minusDays(back.toLong())
                    val on = Stats.loggedOn(state.txns, d)
                    DayBubble(d.dayOfWeek.getDisplayName(TextStyle.NARROW, Locale.getDefault()), on, d == today, i)
                }
            }
        }

        KCard {
            Text("Currency", color = K.Text, fontWeight = FontWeight.Bold, fontSize = 16.sp)
            Spacer(Modifier.height(12.dp))
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Money.currencies.forEach { c ->
                    val sel = c == state.currency
                    val s by animateFloatAsState(
                        if (sel) 1.08f else 1f,
                        spring(dampingRatio = 0.4f, stiffness = Spring.StiffnessMedium),
                        label = "cur",
                    )
                    Box(
                        Modifier
                            .graphicsLayer { scaleX = s; scaleY = s }
                            .bouncyClick { Store.setCurrency(c) }
                            .clip(RoundedCornerShape(14.dp))
                            .background(if (sel) K.violetPink else Brush.linearGradient(listOf(K.CardHi, K.CardHi)))
                            .padding(horizontal = 14.dp, vertical = 9.dp),
                    ) {
                        Text(
                            "${Money.symbol(c).let { if (it == c) "" else "$it " }}$c",
                            color = if (sel) Color.White else K.Muted,
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp,
                        )
                    }
                }
            }
        }

        SettingRow(
            "🎯",
            "Monthly budget",
            if (state.budget > 0) Money.format(state.budget, state.currency) else "Not set",
        ) { showBudget = true }

        SettingRow("🧹", "Erase all data", "Deletes every entry on this phone", danger = true) { confirmWipe = true }

        Text(
            "Kharcha v1.0 · Your data stays on this phone 💜",
            color = K.Muted,
            fontSize = 12.sp,
            modifier = Modifier.align(Alignment.CenterHorizontally).padding(top = 8.dp),
        )
    }

    if (showBudget) {
        BudgetDialog(state.budget, state.currency, { showBudget = false }) {
            Store.setBudget(it); showBudget = false
        }
    }
    if (confirmWipe) {
        AlertDialog(
            onDismissRequest = { confirmWipe = false },
            containerColor = K.Surface,
            shape = RoundedCornerShape(28.dp),
            title = { Text("Erase everything? 😱", fontWeight = FontWeight.ExtraBold) },
            text = { Text("All ${state.txns.size} entries will be deleted. This can't be undone.", color = K.Muted) },
            confirmButton = {
                TextButton(onClick = { Store.clearAll(); confirmWipe = false }) {
                    Text("Erase", color = K.Coral, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { confirmWipe = false }) { Text("Keep my data", color = K.Muted) }
            },
        )
    }
}

@Composable
private fun BigStat(emoji: String, value: String, label: String, modifier: Modifier, glow: Color) {
    Column(
        modifier
            .clip(RoundedCornerShape(22.dp))
            .background(Brush.verticalGradient(listOf(glow.copy(alpha = 0.22f), K.Card)))
            .padding(vertical = 16.dp, horizontal = 10.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        if (emoji == "🔥") Flame(active = value != "0", size = 26) else FloatingEmoji(emoji, 26)
        Spacer(Modifier.height(6.dp))
        Text(value, color = K.Text, fontWeight = FontWeight.ExtraBold, fontSize = 22.sp)
        Text(label, color = K.Muted, fontSize = 12.sp)
    }
}

@Composable
private fun DayBubble(letter: String, on: Boolean, isToday: Boolean, index: Int) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        AppearIn(index) {
            Box(
                Modifier
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(if (on) K.coralOrange else Brush.linearGradient(listOf(K.CardHi, K.CardHi)))
                    .then(
                        if (isToday) Modifier.border(2.dp, K.Amber, CircleShape) else Modifier
                    ),
                contentAlignment = Alignment.Center,
            ) {
                Text(if (on) "🔥" else "", fontSize = 16.sp)
            }
        }
        Spacer(Modifier.height(6.dp))
        Text(letter, color = if (isToday) K.Amber else K.Muted, fontSize = 12.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun SettingRow(emoji: String, title: String, subtitle: String, danger: Boolean = false, onClick: () -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .bouncyClick(0.97f) { onClick() }
            .clip(RoundedCornerShape(22.dp))
            .background(K.Card)
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier.size(42.dp).clip(RoundedCornerShape(14.dp)).background(K.CardHi),
            contentAlignment = Alignment.Center,
        ) { Text(emoji, fontSize = 20.sp) }
        Spacer(Modifier.width(14.dp))
        Column(Modifier.weight(1f)) {
            Text(title, color = if (danger) K.Coral else K.Text, fontWeight = FontWeight.Bold, fontSize = 15.sp)
            Text(subtitle, color = K.Muted, fontSize = 13.sp)
        }
        Text("›", color = K.Muted, fontSize = 26.sp)
    }
}
