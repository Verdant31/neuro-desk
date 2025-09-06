#Requires AutoHotkey v2.0
#Include "../lib/arg_parser.ahk"
#Include "../lib/Stdout.ahk"

try {
    paramConfig := Map(
        "required", ["action", "monitor"],
        "optional", [],
        "validation", Map(
            "action", Map("valid_values", ["enable", "disable"], "type", "string"),
            "monitor", Map("type", "number", "min", 1)
        )
    )

    args := ParseArgs(paramConfig)

    action := GetParam(args, "action", "")
    monitorNumber := GetParam(args, "monitor", 0)

    command := (action = "enable") ? "Enable-display " . monitorNumber : "Disable-display " . monitorNumber

    RunWait(
        'cmd.exe /c powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden ' . command
        , "", "Hide"
    )

    Stdout("Monitor control command executed successfully.")
    ExitApp(0)
} catch Error as e {
    Stdout(e.Message)
    ExitApp 1
}
