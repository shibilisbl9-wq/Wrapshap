package com.shibili.kharcha

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.shibili.kharcha.data.Store
import com.shibili.kharcha.data.TxType
import com.shibili.kharcha.ui.KharchaApp
import com.shibili.kharcha.ui.KharchaTheme
import kotlinx.coroutines.flow.MutableStateFlow

class MainActivity : ComponentActivity() {

    /** Set when the widget's quick-add buttons open the app. */
    private val addRequest = MutableStateFlow<TxType?>(null)

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.dark(Color.TRANSPARENT),
            navigationBarStyle = SystemBarStyle.dark(Color.TRANSPARENT),
        )
        super.onCreate(savedInstanceState)
        Store.init(this)
        if (savedInstanceState == null) handleIntent(intent)
        setContent {
            KharchaTheme {
                KharchaApp(addRequest) { addRequest.value = null }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        val data = intent?.data ?: return
        if (data.scheme != "kharcha" || data.host != "add") return
        addRequest.value = when (data.lastPathSegment) {
            "income" -> TxType.INCOME
            else -> TxType.EXPENSE
        }
    }
}
