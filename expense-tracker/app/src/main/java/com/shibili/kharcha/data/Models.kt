package com.shibili.kharcha.data

import androidx.compose.ui.graphics.Color

enum class TxType { EXPENSE, INCOME }

/** A single entry. [amount] is stored in minor units (1/100 of the currency). */
data class Txn(
    val id: Long,
    val type: TxType,
    val amount: Long,
    val categoryId: String,
    val note: String,
    val time: Long,
)

data class Category(
    val id: String,
    val name: String,
    val emoji: String,
    val color: Color,
    val type: TxType,
)

data class AppState(
    /** Always sorted newest first. */
    val txns: List<Txn> = emptyList(),
    val currency: String = "AED",
    /** Monthly budget in minor units, 0 = not set. */
    val budget: Long = 0L,
    val bestStreak: Int = 0,
)

object Categories {
    private fun e(id: String, name: String, emoji: String, c: Long) =
        Category(id, name, emoji, Color(c), TxType.EXPENSE)

    private fun i(id: String, name: String, emoji: String, c: Long) =
        Category(id, name, emoji, Color(c), TxType.INCOME)

    val expense = listOf(
        e("food", "Food", "🍔", 0xFFFF8A4C),
        e("groceries", "Groceries", "🛒", 0xFF34D399),
        e("transport", "Transport", "🚕", 0xFFFBBF24),
        e("shopping", "Shopping", "🛍️", 0xFFEC4899),
        e("bills", "Bills", "💡", 0xFF60A5FA),
        e("rent", "Rent", "🏠", 0xFFA78BFA),
        e("fun", "Fun", "🎮", 0xFFF472B6),
        e("coffee", "Coffee", "☕", 0xFFD4A373),
        e("health", "Health", "💊", 0xFF2DD4BF),
        e("travel", "Travel", "✈️", 0xFF38BDF8),
        e("education", "Learning", "📚", 0xFF818CF8),
        e("gifts", "Gifts", "🎁", 0xFFFB7185),
        e("family", "Family", "👨‍👩‍👧", 0xFFF59E0B),
        e("other_e", "Other", "✨", 0xFF94A3B8),
    )

    val income = listOf(
        i("salary", "Salary", "💼", 0xFF34D399),
        i("freelance", "Freelance", "💻", 0xFF22D3EE),
        i("business", "Business", "📈", 0xFFA3E635),
        i("gift_in", "Gift", "🎁", 0xFFF472B6),
        i("invest", "Investment", "💰", 0xFFFBBF24),
        i("refund", "Refund", "🔁", 0xFF60A5FA),
        i("other_i", "Other", "✨", 0xFF94A3B8),
    )

    private val all = (expense + income).associateBy { it.id }

    fun byId(id: String): Category = all[id] ?: expense.last()

    fun forType(t: TxType): List<Category> = if (t == TxType.EXPENSE) expense else income
}
