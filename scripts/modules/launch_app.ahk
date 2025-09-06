#Requires AutoHotkey v2+
#Include "../lib/arg_parser.ahk"
#Include "../lib/Stdout.ahk"

try {
    paramConfig := Map(
        "required", ["app"],
        "optional", []
    )

    args := ParseArgs(paramConfig)
    app := GetParam(args, "app", "")
    Run(app)
    found := false
    loop 40 {
        Sleep 100
        windows := WinGetList()
        loop windows.Length {
            hwnd := windows[A_Index]
            windowTitleLower := StrLower(WinGetTitle("ahk_id " . hwnd))
            if (InStr(windowTitleLower, StrLower(app))) {
                found := true
                break
            }
        }
        if (found) {
            break
        }
    }
    Stdout("App launched successfully.")
    ExitApp(0)
} catch Error as e {
    Stdout(e.Message)
    ExitApp 1
}
