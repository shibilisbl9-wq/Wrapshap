package com.shibili.kharcha.ui

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.keyframes
import androidx.compose.animation.core.spring
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyHorizontalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDefaults
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.SelectableDates
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shibili.kharcha.data.Categories
import com.shibili.kharcha.data.Category
import com.shibili.kharcha.data.Money
import com.shibili.kharcha.data.Store
import com.shibili.kharcha.data.TxType
import com.shibili.kharcha.data.Txn
import com.shibili.kharcha.data.toLocalDate
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZoneId
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

data class EditorRequest(val type: TxType, val existing: Txn? = null, val nonce: Long = System.nanoTime())

private fun applyKey(cur: String, key: String): String = when (key) {
    "⌫" -> cur.dropLast(1)
    "." -> when {
        cur.contains('.') -> cur
        cur.isEmpty() -> "0."
        else -> "$cur."
    }
    else -> {
        val dot = cur.indexOf('.')
        when {
            dot >= 0 && cur.length - dot > 2 -> cur
            dot < 0 && cur.length >= 9 -> cur
            cur == "0" -> key
            else -> cur + key
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EditorSheet(
    req: EditorRequest,
    currency: String,
    onClose: () -> Unit,
    onSaved: (Store.SaveResult) -> Unit,
    onDelete: (Txn) -> Unit,
) {
    val existing = req.existing
    var type by remember { mutableStateOf(req.type) }
    var amountText by remember { mutableStateOf(existing?.let { Money.toInput(it.amount) } ?: "") }
    var categoryId by remember { mutableStateOf(existing?.categoryId ?: Categories.forType(req.type).first().id) }
    var note by remember { mutableStateOf(existing?.note ?: "") }
    var date by remember { mutableStateOf(existing?.time?.toLocalDate() ?: LocalDate.now()) }
    var showDatePicker by remember { mutableStateOf(false) }
    val shake = remember { Animatable(0f) }
    val scope = rememberCoroutineScope()
    val haptic = LocalHapticFeedback.current

    val isExpense = type == TxType.EXPENSE
    val accentBrush = if (isExpense) K.coralOrange else K.mintCyan
    val accent = if (isExpense) K.Coral else K.Mint

    LaunchedEffect(type) {
        if (Categories.forType(type).none { it.id == categoryId }) {
            categoryId = Categories.forType(type).first().id
        }
    }

    fun save() {
        val amount = Money.parseInput(amountText)
        if (amount <= 0) {
            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
            scope.launch {
                shake.snapTo(0f)
                shake.animateTo(0f, keyframes {
                    durationMillis = 420
                    -28f at 50
                    28f at 110
                    -20f at 170
                    20f at 230
                    -10f at 290
                    10f at 350
                })
            }
            return
        }
        val zone = ZoneId.systemDefault()
        val time = if (existing != null && existing.time.toLocalDate() == date) existing.time
        else date.atTime(LocalTime.now()).atZone(zone).toInstant().toEpochMilli()
        val txn = Txn(
            id = existing?.id ?: Store.newId(),
            type = type,
            amount = amount,
            categoryId = categoryId,
            note = note.trim(),
            time = time,
        )
        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
        onSaved(Store.upsert(txn))
    }

    Column(
        Modifier
            .fillMaxSize()
            .background(K.Bg)
            .statusBarsPadding()
            .navigationBarsPadding()
            .imePadding()
    ) {
        // ---- top bar
        Row(
            Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            RoundIcon("✕") { onClose() }
            Text(
                if (existing == null) "New entry" else "Edit entry",
                color = K.Text,
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp,
                textAlign = TextAlign.Center,
                modifier = Modifier.weight(1f),
            )
            if (existing != null) RoundIcon("🗑️") { onDelete(existing) }
            else Spacer(Modifier.size(44.dp))
        }

        // ---- scrollable middle
        Column(
            Modifier
                .weight(1f)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp),
        ) {
            SegmentedPill(
                listOf("Expense", "Income"),
                selected = type.ordinal,
                onSelect = { type = TxType.entries[it] },
                brushes = listOf(K.coralOrange, K.mintCyan),
            )
            Spacer(Modifier.height(14.dp))

            AmountDisplay(amountText, currency, accent, shake.value)
            Spacer(Modifier.height(10.dp))

            Text("Category", color = K.Muted, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(8.dp))
            AnimatedContent(
                targetState = type,
                transitionSpec = {
                    val dir = if (targetState == TxType.INCOME) 1 else -1
                    (slideInHorizontally(spring(dampingRatio = 0.75f, stiffness = Spring.StiffnessMediumLow)) { it * dir } + fadeIn()) togetherWith
                        (slideOutHorizontally { -it * dir } + fadeOut())
                },
                label = "cats",
            ) { t ->
                CategoryGrid(Categories.forType(t), categoryId) {
                    haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                    categoryId = it
                }
            }
            Spacer(Modifier.height(12.dp))

            Row(verticalAlignment = Alignment.CenterVertically) {
                NoteField(note, { if (it.length <= 60) note = it }, Modifier.weight(1f))
                Spacer(Modifier.width(10.dp))
                DateChip(date) { showDatePicker = true }
            }
            Spacer(Modifier.height(12.dp))
        }

        // ---- keypad + save
        Keypad(
            onKey = { k -> amountText = applyKey(amountText, k) },
            onClear = { amountText = "" },
            modifier = Modifier.padding(horizontal = 16.dp),
        )
        Spacer(Modifier.height(10.dp))
        val cat = Categories.byId(categoryId)
        Box(
            Modifier
                .padding(horizontal = 16.dp)
                .padding(bottom = 10.dp)
                .fillMaxWidth()
                .height(58.dp)
                .bouncyClick(0.94f, haptic = false) { save() }
                .clip(RoundedCornerShape(22.dp))
                .background(accentBrush),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                when {
                    existing != null -> "Save changes ✓"
                    isExpense -> "Add expense ${cat.emoji}"
                    else -> "Add income ${cat.emoji}"
                },
                color = Color.White,
                fontWeight = FontWeight.ExtraBold,
                fontSize = 17.sp,
            )
        }
    }

    if (showDatePicker) {
        val dp = rememberDatePickerState(
            initialSelectedDateMillis = date.atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli(),
            selectableDates = object : SelectableDates {
                override fun isSelectableDate(utcTimeMillis: Long): Boolean {
                    val d = Instant.ofEpochMilli(utcTimeMillis).atZone(ZoneOffset.UTC).toLocalDate()
                    return !d.isAfter(LocalDate.now())
                }
            },
        )
        DatePickerDialog(
            onDismissRequest = { showDatePicker = false },
            confirmButton = {
                TextButton(onClick = {
                    dp.selectedDateMillis?.let {
                        date = Instant.ofEpochMilli(it).atZone(ZoneOffset.UTC).toLocalDate()
                    }
                    showDatePicker = false
                }) { Text("Pick", color = K.Violet, fontWeight = FontWeight.Bold) }
            },
            dismissButton = {
                TextButton(onClick = { showDatePicker = false }) { Text("Cancel", color = K.Muted) }
            },
            colors = DatePickerDefaults.colors(containerColor = K.Surface),
        ) {
            DatePicker(
                state = dp,
                colors = DatePickerDefaults.colors(
                    containerColor = K.Surface,
                    selectedDayContainerColor = K.Violet,
                    todayDateBorderColor = K.Pink,
                    todayContentColor = K.Pink,
                ),
            )
        }
    }
}

@Composable
private fun RoundIcon(label: String, onClick: () -> Unit) {
    Box(
        Modifier
            .size(44.dp)
            .bouncyClick(0.8f) { onClick() }
            .clip(CircleShape)
            .background(K.Card),
        contentAlignment = Alignment.Center,
    ) { Text(label, color = K.Text, fontSize = 17.sp, fontWeight = FontWeight.Bold) }
}

@Composable
private fun AmountDisplay(text: String, currency: String, accent: Color, shakeX: Float) {
    val bump = remember { Animatable(1f) }
    LaunchedEffect(text) {
        bump.snapTo(1.07f)
        bump.animateTo(1f, spring(dampingRatio = 0.35f, stiffness = Spring.StiffnessMedium))
    }
    val pretty = Money.prettyInput(text)
    val size = when {
        pretty.length > 11 -> 38.sp
        pretty.length > 8 -> 46.sp
        else -> 56.sp
    }
    Column(
        Modifier
            .fillMaxWidth()
            .graphicsLayer { translationX = shakeX },
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(Money.symbol(currency), color = accent, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.width(8.dp))
            Text(
                pretty,
                color = if (text.isEmpty()) K.Muted.copy(alpha = 0.5f) else K.Text,
                fontSize = size,
                fontWeight = FontWeight.ExtraBold,
                maxLines = 1,
                modifier = Modifier.graphicsLayer { scaleX = bump.value; scaleY = bump.value },
            )
        }
    }
}

@Composable
private fun CategoryGrid(cats: List<Category>, selectedId: String, onPick: (String) -> Unit) {
    LazyHorizontalGrid(
        rows = GridCells.Fixed(2),
        modifier = Modifier.fillMaxWidth().height(190.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
        contentPadding = PaddingValues(horizontal = 2.dp),
    ) {
        items(cats, key = { it.id }) { c ->
            CategoryChip(c, c.id == selectedId) { onPick(c.id) }
        }
    }
}

@Composable
private fun CategoryChip(c: Category, selected: Boolean, onClick: () -> Unit) {
    val s by animateFloatAsState(
        if (selected) 1.06f else 1f,
        spring(dampingRatio = 0.35f, stiffness = Spring.StiffnessMedium),
        label = "chip",
    )
    val wiggle = remember { Animatable(0f) }
    LaunchedEffect(selected) {
        if (selected) {
            wiggle.animateTo(0f, keyframes {
                durationMillis = 380
                -12f at 60
                10f at 140
                -6f at 220
                3f at 300
            })
        }
    }
    Column(
        Modifier
            .width(78.dp)
            .graphicsLayer { scaleX = s; scaleY = s }
            .bouncyClick(0.85f, haptic = false) { onClick() }
            .clip(RoundedCornerShape(22.dp))
            .background(if (selected) c.color.copy(alpha = 0.22f) else K.Card)
            .border(2.dp, if (selected) c.color else Color.Transparent, RoundedCornerShape(22.dp))
            .padding(vertical = 10.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text(c.emoji, fontSize = 26.sp, modifier = Modifier.graphicsLayer { rotationZ = wiggle.value })
        Spacer(Modifier.height(4.dp))
        Text(
            c.name,
            color = if (selected) K.Text else K.Muted,
            fontSize = 12.sp,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
            maxLines = 1,
        )
    }
}

@Composable
private fun NoteField(value: String, onChange: (String) -> Unit, modifier: Modifier) {
    Box(
        modifier
            .height(50.dp)
            .clip(RoundedCornerShape(18.dp))
            .background(K.Card)
            .padding(horizontal = 16.dp),
        contentAlignment = Alignment.CenterStart,
    ) {
        if (value.isEmpty()) Text("✏️  Add a note", color = K.Muted, fontSize = 15.sp)
        BasicTextField(
            value = value,
            onValueChange = onChange,
            singleLine = true,
            textStyle = TextStyle(color = K.Text, fontSize = 15.sp),
            cursorBrush = SolidColor(K.Violet),
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun DateChip(date: LocalDate, onClick: () -> Unit) {
    val today = LocalDate.now()
    val label = when (date) {
        today -> "Today"
        today.minusDays(1) -> "Yesterday"
        else -> date.format(DateTimeFormatter.ofPattern("d MMM"))
    }
    Row(
        Modifier
            .height(50.dp)
            .bouncyClick(0.9f) { onClick() }
            .clip(RoundedCornerShape(18.dp))
            .background(K.Card)
            .padding(horizontal = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("📅", fontSize = 15.sp)
        Spacer(Modifier.width(6.dp))
        AnimatedContent(targetState = label, transitionSpec = { scaleIn() + fadeIn() togetherWith fadeOut() }, label = "date") {
            Text(it, color = K.Text, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
        }
    }
}

@Composable
private fun Keypad(onKey: (String) -> Unit, onClear: () -> Unit, modifier: Modifier = Modifier) {
    val rows = listOf(
        listOf("1", "2", "3"),
        listOf("4", "5", "6"),
        listOf("7", "8", "9"),
        listOf(".", "0", "⌫"),
    )
    Column(modifier, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        rows.forEach { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                row.forEach { k ->
                    val isBack = k == "⌫"
                    Box(
                        Modifier
                            .weight(1f)
                            .height(54.dp)
                            .bouncyClick(
                                pressedScale = 0.82f,
                                onLongClick = if (isBack) onClear else null,
                            ) { onKey(k) }
                            .clip(RoundedCornerShape(18.dp))
                            .background(
                                if (isBack) Brush.linearGradient(listOf(K.CardHi, K.Card))
                                else Brush.linearGradient(listOf(K.Card, K.Card))
                            ),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            k,
                            color = if (isBack) K.Coral else K.Text,
                            fontSize = if (isBack) 20.sp else 24.sp,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                }
            }
        }
    }
}
