#Requires AutoHotkey v2.0
#Include "../lib/arg_parser.ahk"
#Include "../lib/Stdout.ahk"

try {
    paramConfig := Map(
        "required", ["app"],
        "optional", []
    )

    args := ParseArgs(paramConfig)

    windowName := GetParam(args, "app", "")

    if (windowName = "") {
        Stdout("Error: --app parameter is required.")
        ExitApp 1
    }

    WinClose windowName

    Stdout("App closed successfully.")
    ExitApp(0)
} catch Error as e {
    Stdout(e.Message)
    ExitApp 1
}
