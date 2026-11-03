# Kharcha: expense & income tracker (Android)

A dark, colourful money tracker with springy animations, a daily streak, a monthly
budget, stats, and a home-screen widget. Default currency is AED; you can switch it
in the **You** tab (AED, PKR, INR, SAR, USD, EUR, GBP).

## Features

- **Home**: this month's balance, which counts up when it changes, plus income/spent,
  a budget ring with "≈ X/day left", quick-add buttons, and recent entries. Swipe an
  entry left to delete it (you can undo); tap it to edit.
- **Add sheet**: Expense/Income toggle, a big custom number keypad (long-press ⌫ to
  clear), emoji category chips, a note, and a date. Saving a new entry fires confetti.
- **History**: every entry grouped by day, with search and All/Spent/Income filters.
- **Stats**: a month switcher, an animated donut chart by category (tap a row to
  highlight it), the share each category takes, a 6-month income-vs-spent bar chart,
  and fun facts (daily average, biggest spend, heaviest day, no-spend days).
- **You**: current/best streak, a 7-day streak strip, currency picker, budget, and
  erase-all.
- **Widget (4×2)**: this month's balance, income, spent, and streak, with
  **➖ Expense** / **➕ Income** buttons that open the add sheet directly.

All data stays on the phone, in a single JSON file in the app's private storage. There's
no account, no network access, and no cloud backup. Uninstalling the app deletes your data.

## Getting the APK

The GitHub Actions workflow `.github/workflows/kharcha-apk.yml` builds the release APK
on every push that touches `expense-tracker/` and attaches it to a GitHub Release named
**Kharcha (build N)**. Download `Kharcha-1.0-buildN.apk` on the phone and open it.
Android will ask you to allow installs from your browser or file manager.

Requires Android 8.0 (API 26) or newer.

### Signing (important for updates)

Android only installs an update over an existing app when both are signed with the same
key. Add these **repository secrets** (Settings → Secrets and variables → Actions) so
that every build uses your key:

| Secret | Value |
| --- | --- |
| `KHARCHA_KEYSTORE_BASE64` | `base64 -w0 kharcha-release.jks` |
| `KHARCHA_STORE_PASSWORD` | keystore password |
| `KHARCHA_KEY_ALIAS` | key alias |
| `KHARCHA_KEY_PASSWORD` | key password |

Without these secrets the workflow signs with a throwaway debug key. The app works, but
the next build won't install over it: you'd have to uninstall first, which deletes your
data.

## Building locally

Requires JDK 17 and the Android SDK (platform 35):

```bash
cd expense-tracker
./gradlew assembleRelease   # app/build/outputs/apk/release/app-release.apk
```

Tech: Kotlin 2.0, Jetpack Compose (Material 3), Glance for the widget, AGP 8.7.
