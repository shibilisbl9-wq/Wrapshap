package com.shibili.kharcha.ui

import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.animation.expandHorizontally
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkHorizontally
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.slideOutVertically
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.Snackbar
import androidx.compose.material3.SnackbarDuration
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.SnackbarResult
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.shibili.kharcha.data.Categories
import com.shibili.kharcha.data.Money
import com.shibili.kharcha.data.Store
import com.shibili.kharcha.data.TxType
import com.shibili.kharcha.data.Txn
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

@Composable
fun KharchaApp(addRequests: StateFlow<TxType?>, consumeAdd: () -> Unit) {
    val state by Store.state.collectAsStateWithLifecycle()
    var tab by rememberSaveable { mutableIntStateOf(0) }
    var editor by remember { mutableStateOf<EditorRequest?>(null) }
    var lastEditor by remember { mutableStateOf<EditorRequest?>(null) }
    var confetti by remember { mutableIntStateOf(0) }
    var bigConfetti by remember { mutableStateOf(false) }
    val snackbar = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    val pending by addRequests.collectAsStateWithLifecycle()
    LaunchedEffect(pending) {
        pending?.let {
            editor = EditorRequest(it)
            consumeAdd()
        }
    }

    fun toast(msg: String) {
        scope.launch {
            snackbar.currentSnackbarData?.dismiss()
            snackbar.showSnackbar(msg, duration = SnackbarDuration.Short)
        }
    }

    val delete: (Txn) -> Unit = { t ->
        Store.delete(t.id)
        scope.launch {
            snackbar.currentSnackbarData?.dismiss()
            val cat = Categories.byId(t.categoryId)
            val r = snackbar.showSnackbar(
                "${cat.emoji} Deleted ${Money.format(t.amount, state.currency)}",
                actionLabel = "Undo",
                duration = SnackbarDuration.Short,
            )
            if (r == SnackbarResult.ActionPerformed) Store.upsert(t)
        }
    }
    val openAdd: (TxType) -> Unit = { editor = EditorRequest(it) }
    val openEdit: (Txn) -> Unit = { editor = EditorRequest(it.type, it) }

    BackHandler(enabled = editor != null) { editor = null }
    BackHandler(enabled = editor == null && tab != 0) { tab = 0 }

    Box(Modifier.fillMaxSize().background(K.Bg)) {
        AnimatedContent(
            targetState = tab,
            transitionSpec = {
                val dir = if (targetState > initialState) 1 else -1
                (slideInHorizontally(spring(dampingRatio = 0.85f, stiffness = Spring.StiffnessMediumLow)) { it * dir / 5 } +
                    fadeIn(tween(220))) togetherWith
                    (slideOutHorizontally(tween(200)) { -it * dir / 5 } + fadeOut(tween(160)))
            },
            label = "tabs",
        ) { t ->
            when (t) {
                0 -> HomeScreen(state, openAdd, openEdit, delete, onSeeAll = { tab = 1 })
                1 -> HistoryScreen(state, openEdit, delete)
                2 -> StatsScreen(state)
                else -> SettingsScreen(state)
            }
        }

        BottomBar(
            tab = tab,
            onTab = { tab = it },
            onAdd = { openAdd(TxType.EXPENSE) },
            modifier = Modifier.align(Alignment.BottomCenter),
        )

        ConfettiBurst(confetti, bigConfetti)

        SnackbarHost(
            snackbar,
            Modifier
                .align(Alignment.BottomCenter)
                .navigationBarsPadding()
                .padding(bottom = 96.dp, start = 12.dp, end = 12.dp),
        ) { data ->
            Snackbar(
                data,
                shape = RoundedCornerShape(18.dp),
                containerColor = K.CardHi,
                contentColor = K.Text,
                actionColor = K.Violet,
            )
        }

        // Editor overlay. Keep the last request around so the exit animation has content.
        SideEffect { if (editor != null) lastEditor = editor }
        val shown = editor ?: lastEditor
        AnimatedVisibility(
            visible = editor != null,
            enter = slideInVertically(spring(dampingRatio = 0.78f, stiffness = Spring.StiffnessMediumLow)) { it } + fadeIn(tween(150)),
            exit = slideOutVertically(tween(260)) { it } + fadeOut(tween(260)),
        ) {
            if (shown != null) {
                key(shown.nonce) {
                    EditorSheet(
                        req = shown,
                        currency = state.currency,
                        onClose = { editor = null },
                        onDelete = { t -> editor = null; delete(t) },
                        onSaved = { r ->
                            editor = null
                            val streakUp = r.streakAfter > r.streakBefore
                            if (r.isNew) {
                                bigConfetti = streakUp
                                confetti++
                            }
                            val msg = when {
                                r.type == TxType.EXPENSE && r.budgetPctBefore < 100 && r.budgetPctAfter >= 100 ->
                                    "😬 You've gone over this month's budget"
                                r.type == TxType.EXPENSE && r.budgetPctBefore < 80 && r.budgetPctAfter >= 80 ->
                                    "⚠️ Heads up: ${r.budgetPctAfter}% of your budget used"
                                streakUp && r.streakAfter >= 2 -> "🔥 ${r.streakAfter}-day streak! Keep it going"
                                streakUp -> "🎉 Streak started! Come back tomorrow"
                                !r.isNew -> "✏️ Entry updated"
                                r.type == TxType.INCOME -> "💸 Cha-ching! Income added"
                                else -> "✅ Expense saved"
                            }
                            toast(msg)
                        },
                    )
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Floating bottom bar with a big bouncy FAB in the middle
// ---------------------------------------------------------------------------

private data class TabSpec(val label: String, val icon: ImageVector?)

private val tabs = listOf(
    TabSpec("Home", Icons.Filled.Home),
    TabSpec("History", Icons.Filled.DateRange),
    TabSpec("Stats", null),
    TabSpec("You", Icons.Filled.Person),
)

@Composable
private fun BottomBar(tab: Int, onTab: (Int) -> Unit, onAdd: () -> Unit, modifier: Modifier) {
    Box(
        modifier
            .fillMaxWidth()
            .navigationBarsPadding()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        contentAlignment = Alignment.Center,
    ) {
        Row(
            Modifier
                .fillMaxWidth()
                .height(68.dp)
                .shadow(24.dp, RoundedCornerShape(34.dp), ambientColor = K.Violet, spotColor = K.Violet)
                .clip(RoundedCornerShape(34.dp))
                .background(K.Surface)
                .border(1.dp, K.Stroke, RoundedCornerShape(34.dp))
                .padding(horizontal = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            TabItem(tabs[0], tab == 0, Modifier.weight(1f)) { onTab(0) }
            TabItem(tabs[1], tab == 1, Modifier.weight(1f)) { onTab(1) }
            Spacer(Modifier.width(72.dp))
            TabItem(tabs[2], tab == 2, Modifier.weight(1f)) { onTab(2) }
            TabItem(tabs[3], tab == 3, Modifier.weight(1f)) { onTab(3) }
        }
        AddFab(onAdd, Modifier.align(Alignment.Center))
    }
}

@Composable
private fun TabItem(spec: TabSpec, selected: Boolean, modifier: Modifier, onClick: () -> Unit) {
    val lift by animateFloatAsState(
        if (selected) 1f else 0f,
        spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessMediumLow),
        label = "lift",
    )
    val tint = lerpColor(K.Muted, Color.White, lift.coerceIn(0f, 1f))
    Box(modifier.height(56.dp), contentAlignment = Alignment.Center) {
        Box(
            Modifier
                .bouncyClick(0.8f) { onClick() }
                .clip(RoundedCornerShape(20.dp))
                .background(K.Violet.copy(alpha = 0.22f * lift.coerceIn(0f, 1f)))
                .padding(horizontal = 10.dp, vertical = 8.dp),
            contentAlignment = Alignment.Center,
        ) {
            Box(
                Modifier.graphicsLayer {
                    translationY = -3f * lift
                    scaleX = 1f + 0.12f * lift
                    scaleY = 1f + 0.12f * lift
                },
                contentAlignment = Alignment.Center,
            ) {
                if (spec.icon != null) {
                    Icon(spec.icon, contentDescription = spec.label, tint = tint, modifier = Modifier.size(24.dp))
                } else {
                    StatsIcon(tint)
                }
            }
        }
        AnimatedVisibility(
            visible = selected,
            enter = fadeIn() + expandHorizontally(),
            exit = fadeOut() + shrinkHorizontally(),
            modifier = Modifier.align(Alignment.BottomCenter),
        ) {
            Box(Modifier.size(width = 16.dp, height = 3.dp).clip(RoundedCornerShape(2.dp)).background(K.Pink))
        }
    }
}

@Composable
private fun StatsIcon(tint: Color) {
    Canvas(Modifier.size(24.dp)) {
        val w = size.width
        val h = size.height
        val bw = w * 0.2f
        val r = CornerRadius(bw / 2, bw / 2)
        drawRoundRect(tint, Offset(w * 0.12f, h * 0.45f), Size(bw, h * 0.43f), r)
        drawRoundRect(tint, Offset(w * 0.40f, h * 0.15f), Size(bw, h * 0.73f), r)
        drawRoundRect(tint, Offset(w * 0.68f, h * 0.32f), Size(bw, h * 0.56f), r)
    }
}

@Composable
private fun AddFab(onAdd: () -> Unit, modifier: Modifier) {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    var spins by remember { mutableIntStateOf(0) }
    val scale by animateFloatAsState(
        if (pressed) 0.82f else 1f,
        spring(dampingRatio = 0.3f, stiffness = Spring.StiffnessMedium),
        label = "fabScale",
    )
    val rot by animateFloatAsState(
        spins * 90f,
        spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessLow),
        label = "fabRot",
    )
    val hf = LocalHapticFeedback.current
    Box(
        modifier
            .size(64.dp)
            .graphicsLayer { scaleX = scale; scaleY = scale }
            .shadow(18.dp, CircleShape, ambientColor = K.Pink, spotColor = K.Pink)
            .clip(CircleShape)
            .background(K.hero)
            .clickable(interactionSource = interaction, indication = null) {
                hf.performHapticFeedback(HapticFeedbackType.LongPress)
                spins++
                onAdd()
            },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            "+",
            color = Color.White,
            fontSize = 36.sp,
            fontWeight = FontWeight.Light,
            modifier = Modifier.graphicsLayer { rotationZ = rot },
        )
    }
}
