#Requires AutoHotkey v2.0
#Include "../lib/arg_parser.ahk"
#Include "../lib/Stdout.ahk"

try {
    paramConfig := Map(
        "required", ["app"],
        "optional", ["position", "monitor", "title"],
        "validation", Map(
            "position", Map("valid_values", ["Top", "Bottom", "Left", "Right", "Maximized"], "type", "string"),
            "monitor", Map("type", "number", "min", 1)
        )
    )

    args := ParseArgs(paramConfig)

    targetApp := GetParam(args, "app", "")
    windowPosition := GetParam(args, "position", "Maximized")
    monitorIndex := GetParam(args, "monitor", 1)
    specificWindowTitle := GetParam(args, "title", "")

    allWindows := WinGetList()
    targetWindowHwnd := 0

    loop allWindows.Length {
        currentHwnd := allWindows[A_Index]

        specificWindowTitle := StrLower(specificWindowTitle)
        currentWindowTitle := StrLower(WinGetTitle("ahk_id " . currentHwnd))
        try {
            currentProcessName := StrLower(WinGetProcessName("ahk_id " . currentHwnd))
        } catch {
            currentProcessName := ""
        }

        ; Se não foi especificado um título específico, busca pelo nome do app
        if (specificWindowTitle = "") {
            if (InStr(currentWindowTitle, StrLower(targetApp))) {
                targetWindowHwnd := currentHwnd
                break
            }
            else if (InStr(currentProcessName, StrLower(targetApp))) {
                targetWindowHwnd := currentHwnd
                break
            }
            else if (InStr(currentProcessName, StrLower(targetApp) . ".exe")) {
                targetWindowHwnd := currentHwnd
                break
            }
        } else {
            ; Se foi especificado um título, busca por ele
            if (InStr(currentWindowTitle, specificWindowTitle)) {
                targetWindowHwnd := currentHwnd
                break
            }
        }
    }

    if (targetWindowHwnd = 0) {
        Stdout("Erro: Não foi possível encontrar a janela do " . targetApp)
        ExitApp 1
    }

    MonitorGetWorkArea(monitorIndex, &left, &top, &right, &bottom)

    WinActivate(targetWindowHwnd)
    WinRestore(targetWindowHwnd)

    workAreaWidth := right - left
    workAreaHeight := bottom - top
    isLandscapeOrientation := (workAreaWidth >= workAreaHeight)

    if (isLandscapeOrientation) {
        if (windowPosition = "Maximized") {
            WinMove(left, top, workAreaWidth, workAreaHeight, "ahk_id " targetWindowHwnd)
        } else if (windowPosition = "Top") {
            WinMove(left, top, workAreaWidth, workAreaHeight / 2, "ahk_id " targetWindowHwnd)
        } else if (windowPosition = "Bottom") {
            WinMove(left, top + workAreaHeight / 2, workAreaWidth, workAreaHeight / 2, "ahk_id " targetWindowHwnd)
        } else if (windowPosition = "Left") {
            WinMove(left, top, workAreaWidth / 2, workAreaHeight, "ahk_id " targetWindowHwnd)
        } else if (windowPosition = "Right") {
            WinMove(left + workAreaWidth / 2, top, workAreaWidth / 2, workAreaHeight, "ahk_id " targetWindowHwnd)
        }
    } else {
        halfHeightA := workAreaHeight // 2
        halfHeightB := workAreaHeight - halfHeightA

        if (windowPosition = "Maximized") {
            WinMove(left, top, workAreaWidth, workAreaHeight, "ahk_id " targetWindowHwnd)
        } else if (windowPosition = "Top") {
            WinMove(left, top, workAreaWidth, halfHeightA, "ahk_id " targetWindowHwnd)
        } else if (windowPosition = "Bottom") {
            WinMove(left, top + workAreaHeight / 2, workAreaWidth, halfHeightB, "ahk_id " targetWindowHwnd)
        } else if (windowPosition = "Left") {
            WinMove(left, top, workAreaWidth / 2, workAreaHeight, "ahk_id " targetWindowHwnd)
        } else if (windowPosition = "Right") {
            WinMove(left + workAreaWidth / 2, top, workAreaWidth / 2, workAreaHeight, "ahk_id " targetWindowHwnd)
        }
    }

    Stdout("Janela movida com sucesso.")
    ExitApp(0)

} catch Error as e {
    Stdout(e.Message)
    ExitApp 1
}
