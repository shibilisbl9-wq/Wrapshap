package com.shibili.kharcha.widget

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.glance.GlanceId
import androidx.glance.GlanceModifier
import androidx.glance.ImageProvider
import androidx.glance.action.Action
import androidx.glance.action.clickable
import androidx.glance.appwidget.GlanceAppWidget
import androidx.glance.appwidget.GlanceAppWidgetReceiver
import androidx.glance.appwidget.action.actionStartActivity
import androidx.glance.appwidget.cornerRadius
import androidx.glance.appwidget.provideContent
import androidx.glance.background
import androidx.glance.layout.Alignment
import androidx.glance.layout.Box
import androidx.glance.layout.Column
import androidx.glance.layout.Row
import androidx.glance.layout.Spacer
import androidx.glance.layout.fillMaxSize
import androidx.glance.layout.fillMaxWidth
import androidx.glance.layout.height
import androidx.glance.layout.padding
import androidx.glance.layout.width
import androidx.glance.text.FontWeight
import androidx.glance.text.Text
import androidx.glance.text.TextStyle
import androidx.glance.unit.ColorProvider
import com.shibili.kharcha.MainActivity
import com.shibili.kharcha.R
import com.shibili.kharcha.data.AppState
import com.shibili.kharcha.data.Money
import com.shibili.kharcha.data.Stats
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.LocalDate
import java.time.YearMonth
import java.time.format.TextStyle as JTextStyle
import java.util.Locale

class BalanceWidget : GlanceAppWidget() {

    override suspend fun provideGlance(context: Context, id: GlanceId) {
        withContext(Dispatchers.IO) { com.shibili.kharcha.data.Store.init(context) }
        provideContent {
            val state by com.shibili.kharcha.data.Store.state.collectAsState()
            WidgetBody(context, state)
        }
    }
}

class BalanceWidgetReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget: GlanceAppWidget = BalanceWidget()
}

private val White = Color.White
private val Soft = Color(0xD9FFFFFF)
private val Mint = Color(0xFFB9FBDD)
private val Peach = Color(0xFFFFE1D6)
private val Amber = Color(0xFFFFE08A)

private fun addIntent(context: Context, kind: String): Action =
    actionStartActivity(
        Intent(context, MainActivity::class.java)
            .setAction(Intent.ACTION_VIEW)
            .setData(Uri.parse("kharcha://add/$kind"))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP)
    )

@Composable
private fun WidgetBody(context: Context, state: AppState) {
    val today = LocalDate.now()
    val ym = YearMonth.from(today)
    val totals = Stats.totals(Stats.inMonth(state.txns, ym))
    val streak = Stats.streak(state.txns, today)
    val loggedToday = Stats.loggedOn(state.txns, today)
    val monthName = ym.month.getDisplayName(JTextStyle.SHORT, Locale.getDefault())
    val cur = state.currency

    Column(
        modifier = GlanceModifier
            .fillMaxSize()
            .background(ImageProvider(R.drawable.widget_bg))
            .cornerRadius(24.dp)
            .padding(horizontal = 16.dp, vertical = 12.dp)
            .clickable(actionStartActivity<MainActivity>()),
    ) {
        Row(modifier = GlanceModifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text(
                "Kharcha · $monthName",
                style = TextStyle(color = ColorProvider(Soft), fontSize = 12.sp, fontWeight = FontWeight.Medium),
            )
            Spacer(GlanceModifier.defaultWeight())
            Text(
                if (streak > 0) "🔥 $streak" else "🔥 0",
                style = TextStyle(
                    color = ColorProvider(if (loggedToday) Amber else Soft),
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                ),
            )
        }
        Text(
            Money.format(totals.balance, cur),
            maxLines = 1,
            style = TextStyle(color = ColorProvider(White), fontSize = 26.sp, fontWeight = FontWeight.Bold),
        )
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                "↑ " + Money.compact(totals.income, cur),
                style = TextStyle(color = ColorProvider(Mint), fontSize = 12.sp, fontWeight = FontWeight.Medium),
            )
            Spacer(GlanceModifier.width(12.dp))
            Text(
                "↓ " + Money.compact(totals.expense, cur),
                style = TextStyle(color = ColorProvider(Peach), fontSize = 12.sp, fontWeight = FontWeight.Medium),
            )
        }
        Spacer(GlanceModifier.defaultWeight())
        Row(modifier = GlanceModifier.fillMaxWidth()) {
            WidgetButton("➖ Expense", addIntent(context, "expense"), GlanceModifier.defaultWeight())
            Spacer(GlanceModifier.width(8.dp))
            WidgetButton("➕ Income", addIntent(context, "income"), GlanceModifier.defaultWeight())
        }
    }
}

@Composable
private fun WidgetButton(label: String, action: Action, modifier: GlanceModifier) {
    Box(
        modifier = modifier
            .height(38.dp)
            .background(ImageProvider(R.drawable.widget_btn))
            .cornerRadius(14.dp)
            .clickable(action),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            label,
            style = TextStyle(color = ColorProvider(White), fontSize = 13.sp, fontWeight = FontWeight.Bold),
        )
    }
}
