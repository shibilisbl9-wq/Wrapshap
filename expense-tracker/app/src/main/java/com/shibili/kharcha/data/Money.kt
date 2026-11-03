package com.shibili.kharcha.data

import java.util.Locale
import kotlin.math.abs

object Money {
    val currencies = listOf("AED", "PKR", "INR", "SAR", "USD", "EUR", "GBP")

    fun symbol(code: String): String = when (code) {
        "PKR" -> "Rs"
        "INR" -> "₹"
        "USD" -> "$"
        "EUR" -> "€"
        "GBP" -> "£"
        else -> code
    }

    private fun joinSymbol(code: String, num: String): String {
        val s = symbol(code)
        return if (s.length > 1 && s.all { it.isLetter() }) "$s $num" else "$s$num"
    }

    private fun grouped(whole: Long): String = String.format(Locale.US, "%,d", whole)

    /** "AED 1,250" or "AED 12.50". Decimals are shown only when non-zero. */
    fun format(minor: Long, code: String, signed: Boolean = false): String {
        val a = abs(minor)
        val whole = a / 100
        val frac = a % 100
        val num = if (frac == 0L) grouped(whole) else grouped(whole) + "." + frac.toString().padStart(2, '0')
        val sign = when {
            minor < 0 -> "−"
            signed && minor > 0 -> "+"
            else -> ""
        }
        return sign + joinSymbol(code, num)
    }

    /** Short form for tight spaces: 950, 12.4K, 1.2M. */
    fun compact(minor: Long, code: String): String {
        val a = abs(minor) / 100.0
        val num = when {
            a >= 1_000_000 -> trim(a / 1_000_000) + "M"
            a >= 10_000 -> trim(a / 1_000) + "K"
            else -> grouped(a.toLong())
        }
        return (if (minor < 0) "−" else "") + joinSymbol(code, num)
    }

    private fun trim(v: Double): String {
        val s = String.format(Locale.US, "%.1f", v)
        return if (s.endsWith(".0")) s.dropLast(2) else s
    }

    /** Parses keypad input like "12.5" into minor units (1250). */
    fun parseInput(s: String): Long {
        if (s.isBlank()) return 0
        val parts = s.split('.')
        val whole = parts[0].ifEmpty { "0" }.toLongOrNull() ?: 0
        val fracStr = parts.getOrNull(1).orEmpty().padEnd(2, '0').take(2)
        val frac = fracStr.toLongOrNull() ?: 0
        return whole * 100 + frac
    }

    /** Minor units back to keypad text: 1250 -> "12.5", 1200 -> "12". */
    fun toInput(minor: Long): String {
        val whole = minor / 100
        val frac = minor % 100
        if (frac == 0L) return whole.toString()
        val f = frac.toString().padStart(2, '0').trimEnd('0')
        return "$whole.$f"
    }

    /** Groups the integer part of keypad text for display: "12345.5" -> "12,345.5". */
    fun prettyInput(s: String): String {
        if (s.isEmpty()) return "0"
        val dot = s.indexOf('.')
        val intPart = if (dot >= 0) s.substring(0, dot) else s
        val rest = if (dot >= 0) s.substring(dot) else ""
        val g = intPart.toLongOrNull()?.let { grouped(it) } ?: intPart
        return g + rest
    }
}
