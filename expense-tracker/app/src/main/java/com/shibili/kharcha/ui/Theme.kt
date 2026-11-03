package com.shibili.kharcha.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

object K {
    val Bg = Color(0xFF0A0A18)
    val Surface = Color(0xFF13132A)
    val Card = Color(0xFF1B1B36)
    val CardHi = Color(0xFF25254A)
    val Stroke = Color(0x1FFFFFFF)
    val Text = Color(0xFFF4F4FF)
    val Muted = Color(0xFF9696BE)
    val Violet = Color(0xFF8B5CF6)
    val Pink = Color(0xFFEC4899)
    val Orange = Color(0xFFFF8A4C)
    val Mint = Color(0xFF34D399)
    val Coral = Color(0xFFFB7185)
    val Amber = Color(0xFFFBBF24)
    val Cyan = Color(0xFF22D3EE)

    val hero = Brush.linearGradient(listOf(Violet, Pink, Orange))
    val violetPink = Brush.linearGradient(listOf(Violet, Pink))
    val mintCyan = Brush.linearGradient(listOf(Mint, Cyan))
    val coralOrange = Brush.linearGradient(listOf(Coral, Orange))
}

private val scheme = darkColorScheme(
    primary = K.Violet,
    onPrimary = Color.White,
    secondary = K.Pink,
    onSecondary = Color.White,
    tertiary = K.Mint,
    background = K.Bg,
    onBackground = K.Text,
    surface = K.Surface,
    onSurface = K.Text,
    surfaceVariant = K.Card,
    onSurfaceVariant = K.Muted,
    surfaceContainerHigh = K.Card,
    surfaceContainerHighest = K.CardHi,
    error = K.Coral,
    outline = K.Muted,
)

private val type = Typography(
    headlineLarge = TextStyle(fontSize = 30.sp, fontWeight = FontWeight.ExtraBold, letterSpacing = (-0.5).sp),
    headlineMedium = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.ExtraBold),
    titleLarge = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
    titleMedium = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
    bodyLarge = TextStyle(fontSize = 16.sp),
    bodyMedium = TextStyle(fontSize = 14.sp),
    labelLarge = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
    labelMedium = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium),
)

@Composable
fun KharchaTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = scheme, typography = type, content = content)
}
