package com.shibili.kharcha.ui

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.SwipeToDismissBox
import androidx.compose.material3.SwipeToDismissBoxValue
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberSwipeToDismissBoxState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shibili.kharcha.data.Categories
import com.shibili.kharcha.data.Money
import com.shibili.kharcha.data.TxType
import com.shibili.kharcha.data.Txn
import com.shibili.kharcha.data.toLocalDate
import kotlinx.coroutines.delay
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import kotlin.math.roundToLong
import kotlin.random.Random

// ---------------------------------------------------------------------------
// Interaction helpers
// ---------------------------------------------------------------------------

/** Squishy press: shrinks while pressed and springs back with a wobble. */
@OptIn(ExperimentalFoundationApi::class)
fun Modifier.bouncyClick(
    pressedScale: Float = 0.9f,
    haptic: Boolean = true,
    onLongClick: (() -> Unit)? = null,
    onClick: () -> Unit,
): Modifier = composed {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (pressed) pressedScale else 1f,
        animationSpec = spring(dampingRatio = 0.35f, stiffness = Spring.StiffnessMedium),
        label = "bouncy",
    )
    val hf = LocalHapticFeedback.current
    this
        .graphicsLayer {
            scaleX = scale
            scaleY = scale
        }
        .combinedClickable(
            interactionSource = interaction,
            indication = null,
            onLongClick = onLongClick,
            onClick = {
                if (haptic) hf.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                onClick()
            },
        )
}

/** Fades + springs content in once, staggered by [index]. */
@Composable
fun AppearIn(index: Int = 0, content: @Composable () -> Unit) {
    val anim = remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        delay(index.coerceAtMost(8) * 45L)
        anim.animateTo(1f, spring(dampingRatio = 0.62f, stiffness = Spring.StiffnessLow))
    }
    Box(
        Modifier.graphicsLayer {
            val v = anim.value
            alpha = v.coerceIn(0f, 1f)
            translationY = (1f - v) * 70f
            scaleX = 0.92f + 0.08f * v
            scaleY = 0.92f + 0.08f * v
        }
    ) { content() }
}

// ---------------------------------------------------------------------------
// Money text that counts up / down
// ---------------------------------------------------------------------------

@Composable
fun AnimatedMoney(
    minor: Long,
    currency: String,
    style: TextStyle,
    color: Color,
    modifier: Modifier = Modifier,
    signed: Boolean = false,
    durationMs: Int = 900,
) {
    val progress = remember { Animatable(0f) }
    var from by remember { mutableLongStateOf(0L) }
    var to by remember { mutableLongStateOf(minor) }
    LaunchedEffect(minor) {
        if (minor != to || progress.value == 0f) {
            from += ((to - from) * progress.value).roundToLong()
            to = minor
            progress.snapTo(0f)
            progress.animateTo(1f, tween(durationMs, easing = FastOutSlowInEasing))
        }
    }
    val shown = from + ((to - from) * progress.value).roundToLong()
    Text(
        Money.format(shown, currency, signed),
        style = style,
        color = color,
        maxLines = 1,
        overflow = TextOverflow.Ellipsis,
        modifier = modifier,
    )
}

// ---------------------------------------------------------------------------
// Confetti
// ---------------------------------------------------------------------------

private class Particle(
    val vx: Float,
    val vy: Float,
    val w: Float,
    val h: Float,
    val color: Color,
    val rot: Float,
    val spin: Float,
)

private val confettiColors = listOf(K.Violet, K.Pink, K.Orange, K.Mint, K.Amber, K.Cyan, Color.White)

/** Increment [trigger] to fire a burst from the bottom of the screen. */
@Composable
fun ConfettiBurst(trigger: Int, big: Boolean = false) {
    if (trigger == 0) return
    key(trigger) {
        val count = if (big) 140 else 80
        val particles = remember {
            List(count) {
                Particle(
                    vx = Random.nextFloat() * 1.2f - 0.6f,
                    vy = -(Random.nextFloat() * 0.9f + 0.9f),
                    w = Random.nextFloat() * 10f + 8f,
                    h = Random.nextFloat() * 8f + 6f,
                    color = confettiColors.random(),
                    rot = Random.nextFloat() * 360f,
                    spin = Random.nextFloat() * 720f - 360f,
                )
            }
        }
        val t = remember { Animatable(0f) }
        LaunchedEffect(Unit) { t.animateTo(1f, tween(2300, easing = LinearEasing)) }
        Canvas(Modifier.fillMaxSize()) {
            val p = t.value
            if (p >= 1f) return@Canvas
            val time = p * 2.3f
            val g = 1.25f
            particles.forEach { pt ->
                val x = size.width * (0.5f + pt.vx * time * 0.6f)
                val y = size.height * (0.92f + pt.vy * time + 0.5f * g * time * time)
                val a = (1f - p).coerceIn(0f, 1f)
                rotate(pt.rot + pt.spin * time, pivot = Offset(x, y)) {
                    drawRect(
                        color = pt.color.copy(alpha = a),
                        topLeft = Offset(x - pt.w / 2, y - pt.h / 2),
                        size = Size(pt.w, pt.h),
                    )
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Segmented pill with a sliding, springy indicator
// ---------------------------------------------------------------------------

@Composable
fun SegmentedPill(
    options: List<String>,
    selected: Int,
    onSelect: (Int) -> Unit,
    modifier: Modifier = Modifier,
    brushes: List<Brush> = List(options.size) { K.violetPink },
) {
    BoxWithConstraints(
        modifier
            .fillMaxWidth()
            .height(48.dp)
            .clip(RoundedCornerShape(24.dp))
            .background(K.Card)
            .padding(4.dp)
    ) {
        val segW = maxWidth / options.size
        val x by animateDpAsState(
            targetValue = segW * selected,
            animationSpec = spring(dampingRatio = 0.6f, stiffness = Spring.StiffnessMediumLow),
            label = "pill",
        )
        Box(
            Modifier
                .offset(x = x)
                .width(segW)
                .fillMaxHeight()
                .clip(RoundedCornerShape(20.dp))
                .background(brushes[selected])
        )
        Row(Modifier.fillMaxSize()) {
            options.forEachIndexed { i, label ->
                val isSel = i == selected
                val c by animateFloatAsState(if (isSel) 1f else 0f, label = "segText")
                Box(
                    Modifier
                        .weight(1f)
                        .fillMaxHeight()
                        .bouncyClick(0.94f) { onSelect(i) },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        label,
                        color = lerpColor(K.Muted, Color.White, c),
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp,
                    )
                }
            }
        }
    }
}

fun lerpColor(a: Color, b: Color, t: Float): Color = Color(
    red = a.red + (b.red - a.red) * t,
    green = a.green + (b.green - a.green) * t,
    blue = a.blue + (b.blue - a.blue) * t,
    alpha = a.alpha + (b.alpha - a.alpha) * t,
)

// ---------------------------------------------------------------------------
// Little bits
// ---------------------------------------------------------------------------

@Composable
fun Flame(active: Boolean, size: Int = 20) {
    val inf = rememberInfiniteTransition(label = "flame")
    val s by inf.animateFloat(
        0.92f, 1.12f,
        infiniteRepeatable(tween(520, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "flameScale",
    )
    val r by inf.animateFloat(
        -7f, 7f,
        infiniteRepeatable(tween(760, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "flameRot",
    )
    Text(
        "🔥",
        fontSize = size.sp,
        modifier = Modifier.graphicsLayer {
            if (active) {
                scaleX = s
                scaleY = s
                rotationZ = r
            } else {
                alpha = 0.45f
            }
        },
    )
}

@Composable
fun FloatingEmoji(emoji: String, size: Int = 56) {
    val inf = rememberInfiniteTransition(label = "float")
    val y by inf.animateFloat(
        -10f, 10f,
        infiniteRepeatable(tween(1400, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "floatY",
    )
    val r by inf.animateFloat(
        -8f, 8f,
        infiniteRepeatable(tween(2100, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "floatR",
    )
    Text(emoji, fontSize = size.sp, modifier = Modifier.graphicsLayer { translationY = y; rotationZ = r })
}

@Composable
fun KCard(
    modifier: Modifier = Modifier,
    padding: Dp = 18.dp,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(26.dp))
            .background(K.Card)
            .padding(padding),
        content = content,
    )
}

@Composable
fun SectionTitle(title: String, action: String? = null, onAction: () -> Unit = {}) {
    Row(Modifier.fillMaxWidth().padding(top = 4.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(title, style = androidx.compose.material3.MaterialTheme.typography.titleLarge, color = K.Text)
        Spacer(Modifier.weight(1f))
        if (action != null) {
            Text(
                action,
                color = K.Violet,
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp,
                modifier = Modifier
                    .clip(RoundedCornerShape(12.dp))
                    .bouncyClick { onAction() }
                    .padding(horizontal = 8.dp, vertical = 4.dp),
            )
        }
    }
}

@Composable
fun EmptyState(title: String, subtitle: String, emoji: String = "🪙") {
    Column(
        Modifier.fillMaxWidth().padding(vertical = 36.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        FloatingEmoji(emoji)
        Spacer(Modifier.height(14.dp))
        Text(title, color = K.Text, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        Spacer(Modifier.height(4.dp))
        Text(subtitle, color = K.Muted, fontSize = 14.sp)
    }
}

// ---------------------------------------------------------------------------
// Transaction row (+ swipe to delete)
// ---------------------------------------------------------------------------

private val timeFmt = DateTimeFormatter.ofPattern("h:mm a")
private val dayFmt = DateTimeFormatter.ofPattern("d MMM")

fun Txn.timeLabel(withDay: Boolean): String {
    val zdt = Instant.ofEpochMilli(time).atZone(ZoneId.systemDefault())
    return if (withDay) zdt.format(dayFmt) + " · " + zdt.format(timeFmt) else zdt.format(timeFmt)
}

@Composable
fun TxnRow(t: Txn, currency: String, onClick: () -> Unit, withDay: Boolean = true) {
    val cat = Categories.byId(t.categoryId)
    val income = t.type == TxType.INCOME
    Row(
        Modifier
            .fillMaxWidth()
            .bouncyClick(0.96f) { onClick() }
            .clip(RoundedCornerShape(22.dp))
            .background(K.Card)
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier
                .size(46.dp)
                .clip(RoundedCornerShape(15.dp))
                .background(cat.color.copy(alpha = 0.2f)),
            contentAlignment = Alignment.Center,
        ) { Text(cat.emoji, fontSize = 22.sp) }
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(
                t.note.ifBlank { cat.name },
                color = K.Text,
                fontWeight = FontWeight.SemiBold,
                fontSize = 15.sp,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                cat.name + " · " + t.timeLabel(withDay),
                color = K.Muted,
                fontSize = 12.sp,
                maxLines = 1,
            )
        }
        Spacer(Modifier.width(8.dp))
        Text(
            (if (income) "+" else "−") + Money.format(t.amount, currency),
            color = if (income) K.Mint else K.Text,
            fontWeight = FontWeight.Bold,
            fontSize = 15.sp,
        )
    }
}

@Composable
fun SwipeTxnRow(
    t: Txn,
    currency: String,
    onClick: () -> Unit,
    onDelete: () -> Unit,
    withDay: Boolean = true,
) {
    val state = rememberSwipeToDismissBoxState(
        confirmValueChange = {
            if (it == SwipeToDismissBoxValue.EndToStart) {
                onDelete(); true
            } else false
        },
    )
    SwipeToDismissBox(
        state = state,
        enableDismissFromStartToEnd = false,
        backgroundContent = {
            val p = state.progress
            val scale by animateFloatAsState(
                if (state.targetValue == SwipeToDismissBoxValue.EndToStart) 1.3f else 0.9f,
                spring(dampingRatio = 0.4f),
                label = "bin",
            )
            Box(
                Modifier
                    .fillMaxSize()
                    .clip(RoundedCornerShape(22.dp))
                    .background(K.Coral.copy(alpha = 0.25f + 0.5f * p.coerceIn(0f, 1f)))
                    .padding(end = 22.dp),
                contentAlignment = Alignment.CenterEnd,
            ) {
                Text("🗑️", fontSize = 22.sp, modifier = Modifier.graphicsLayer { scaleX = scale; scaleY = scale })
            }
        },
    ) {
        TxnRow(t, currency, onClick, withDay)
    }
}

// ---------------------------------------------------------------------------
// Charts
// ---------------------------------------------------------------------------

@Composable
fun BudgetRing(fraction: Float, modifier: Modifier = Modifier, stroke: Dp = 10.dp) {
    val anim = remember { Animatable(0f) }
    LaunchedEffect(fraction) {
        anim.animateTo(fraction, spring(dampingRatio = 0.55f, stiffness = Spring.StiffnessVeryLow))
    }
    val over = fraction >= 0.9f
    val brush = if (over) Brush.sweepGradient(listOf(K.Orange, K.Coral, K.Orange))
    else Brush.sweepGradient(listOf(K.Mint, K.Cyan, K.Violet, K.Mint))
    Box(modifier, contentAlignment = Alignment.Center) {
        Canvas(Modifier.fillMaxSize()) {
            val s = stroke.toPx()
            val tl = Offset(s / 2, s / 2)
            val sz = Size(size.width - s, size.height - s)
            drawArc(Color.White.copy(alpha = 0.08f), 0f, 360f, false, tl, sz, style = Stroke(s))
            val sweep = 360f * anim.value.coerceIn(0f, 1f)
            if (sweep > 0.5f) {
                rotate(-90f) {
                    drawArc(brush, 0f, sweep, false, tl, sz, style = Stroke(s, cap = StrokeCap.Round))
                }
            }
        }
        Text(
            "${(anim.value * 100).toInt().coerceAtLeast(0)}%",
            color = if (over) K.Coral else K.Text,
            fontWeight = FontWeight.ExtraBold,
            fontSize = 17.sp,
        )
    }
}

data class Slice(val color: Color, val value: Long)

@Composable
fun DonutChart(
    slices: List<Slice>,
    selected: Int,
    modifier: Modifier = Modifier,
    center: @Composable () -> Unit,
) {
    val total = slices.sumOf { it.value }.coerceAtLeast(1)
    val anim = remember(slices) { Animatable(0f) }
    LaunchedEffect(slices) { anim.animateTo(1f, tween(1100, easing = FastOutSlowInEasing)) }
    val pop by animateFloatAsState(1f, label = "pop")
    Box(modifier, contentAlignment = Alignment.Center) {
        Canvas(Modifier.fillMaxSize()) {
            val base = 24.dp.toPx()
            val maxStroke = base * 1.35f
            val tl = Offset(maxStroke / 2, maxStroke / 2)
            val sz = Size(size.width - maxStroke, size.height - maxStroke)
            drawArc(Color.White.copy(alpha = 0.06f), 0f, 360f, false, tl, sz, style = Stroke(base))
            val drawn = 360f * anim.value
            val gap = if (slices.size > 1) 2.5f else 0f
            var start = 0f
            slices.forEachIndexed { i, sl ->
                val sweep = 360f * sl.value / total
                val visible = (drawn - start).coerceIn(0f, sweep)
                if (visible > gap) {
                    val w = if (i == selected) base * 1.35f * pop else base
                    drawArc(
                        sl.color,
                        startAngle = -90f + start + gap / 2,
                        sweepAngle = visible - gap,
                        useCenter = false,
                        topLeft = tl,
                        size = sz,
                        style = Stroke(w),
                    )
                }
                start += sweep
            }
        }
        center()
    }
}

@Composable
fun GrowBar(fraction: Float, brush: Brush, delayMs: Long, maxHeight: Dp, width: Dp = 12.dp) {
    val anim = remember { Animatable(0f) }
    LaunchedEffect(fraction) {
        delay(delayMs)
        anim.animateTo(fraction, spring(dampingRatio = 0.5f, stiffness = Spring.StiffnessLow))
    }
    val h = (maxHeight * anim.value.coerceIn(0f, 1.08f)).coerceAtLeast(3.dp)
    Box(
        Modifier
            .width(width)
            .height(h)
            .clip(RoundedCornerShape(topStart = 6.dp, topEnd = 6.dp, bottomStart = 3.dp, bottomEnd = 3.dp))
            .background(brush)
    )
}

// ---------------------------------------------------------------------------
// Budget dialog
// ---------------------------------------------------------------------------

@Composable
fun BudgetDialog(current: Long, currency: String, onDismiss: () -> Unit, onSave: (Long) -> Unit) {
    var text by remember { mutableStateOf(if (current > 0) Money.toInput(current) else "") }
    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = K.Surface,
        shape = RoundedCornerShape(28.dp),
        title = { Text("🎯 Monthly budget", fontWeight = FontWeight.ExtraBold) },
        text = {
            Column {
                Text(
                    "How much do you want to spend at most each month? We'll warn you as you get close.",
                    color = K.Muted,
                    fontSize = 14.sp,
                )
                Spacer(Modifier.height(14.dp))
                OutlinedTextField(
                    value = text,
                    onValueChange = { v ->
                        val clean = v.filter { it.isDigit() || it == '.' }
                        if (clean.count { it == '.' } <= 1 && clean.length <= 12) text = clean
                    },
                    singleLine = true,
                    prefix = { Text(Money.symbol(currency) + " ", color = K.Muted) },
                    placeholder = { Text("3000") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    shape = RoundedCornerShape(16.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = K.Violet,
                        unfocusedBorderColor = K.Stroke,
                        cursorColor = K.Violet,
                    ),
                )
            }
        },
        confirmButton = {
            TextButton(onClick = { onSave(Money.parseInput(text)) }) {
                Text("Save", color = K.Violet, fontWeight = FontWeight.Bold)
            }
        },
        dismissButton = {
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                if (current > 0) {
                    TextButton(onClick = { onSave(0) }) { Text("Remove", color = K.Coral) }
                }
                TextButton(onClick = onDismiss) { Text("Cancel", color = K.Muted) }
            }
        },
    )
}

/** Day label used in History headers. */
fun dayTitle(epochMs: Long): String {
    val d = epochMs.toLocalDate()
    val today = java.time.LocalDate.now()
    return when (d) {
        today -> "Today"
        today.minusDays(1) -> "Yesterday"
        else -> d.format(DateTimeFormatter.ofPattern("EEE, d MMM"))
    }
}

@Composable
fun Dot(color: Color, size: Dp = 8.dp) {
    Box(Modifier.size(size).clip(CircleShape).background(color))
}
