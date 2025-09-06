#Requires AutoHotkey v2.0
#Include "../lib/arg_parser.ahk"
#Include "../lib/window_utils.ahk"
#Include "../lib/Stdout.ahk"

MaximizeApp(appName) {
    hwnd := FindWindowByName(appName)
    if (hwnd != 0) {
        WinMaximize "ahk_id " . hwnd
        WinActivate "ahk_id " . hwnd
        Stdout("App maximized successfully.")
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

MaximizeApp(appName)