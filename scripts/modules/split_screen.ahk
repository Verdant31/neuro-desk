#Requires AutoHotkey v2.0
#Include "../lib/arg_parser.ahk"
#Include "../lib/Stdout.ahk"

LaunchApp(appExe) {
    if ProcessExist(appExe)
        return false
    try {
        pid := Run(appExe)
        return pid
    } catch {
        MsgBox "Erro: não foi possível executar " appExe
        return false
    }
}

MoveWindow(appExe, left, top, width, height) {
    pid := ProcessExist(appExe)
    if !pid
        return false
    hwnd := WinExist("ahk_pid " pid)
    if hwnd
        WinMove(left, top, width, height, "ahk_id " hwnd)
    return hwnd
}

try {
    paramConfig := Map(
        "required", ["left", "right"],
        "optional", ["monitor"],
        "validation", Map(
            "monitor", Map("type", "number", "min", 1)
        )
    )

    args := ParseArgs(paramConfig)

    appExe1 := GetParam(args, "left", "")
    appExe2 := GetParam(args, "right", "")
    monitorIndex := GetParam(args, "monitor", 1)

    if !ProcessExist(appExe1)
        LaunchApp(appExe1)
    if !ProcessExist(appExe2)
        LaunchApp(appExe2)

    Sleep 500
    try {
        MonitorGetWorkArea(monitorIndex, &left, &top, &right, &bottom)
    } catch {
        MsgBox "Erro: monitor " monitorIndex " não encontrado."
        Stdout("Erro: monitor " monitorIndex " não encontrado.")
        ExitApp 1
    }
    width := right - left
    height := bottom - top
    if (width >= height) {
        sizeA := width // 2
        sizeB := width - sizeA
        MoveWindow(appExe1, left, top, sizeA, height)
        MoveWindow(appExe2, left + sizeA, top, sizeB, height)
    } else {
        sizeA := height // 2
        sizeB := height - sizeA
        MoveWindow(appExe1, left, top, width, sizeA)
        MoveWindow(appExe2, left, top + sizeA, width, sizeB)
    }
    Stdout("Windows split successfully.")
    ExitApp(0)
} catch Error as e {
    MsgBox "Error: " . e.Message
    Stdout(e.Message)
    ExitApp 1
}
