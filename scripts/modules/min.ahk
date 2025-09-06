#Requires AutoHotkey v2.0
#Include "../lib/arg_parser.ahk"
#Include "../lib/window_utils.ahk"
#Include "../lib/Stdout.ahk"

MinimizeApp(appName) {
    hwnd := FindWindowByName(appName)
    if (hwnd != 0) {
        WinMinimize "ahk_id " . hwnd
        Stdout("App minimized successfully.")
        ExitApp(0)
    }
    ExitApp 1
}

args := ParseArgs()
appName := GetParam(args, "app", "")

if (appName = "") {
    Stdout("Error: --app parameter is required.")
    ExitApp 1
}

MinimizeApp(appName)