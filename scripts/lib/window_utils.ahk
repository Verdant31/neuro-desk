#Requires AutoHotkey v2.0

; Extract the executable name from a full path
; Removes .exe extension if present
ExtractExeName(path) {
    parts := StrSplit(path, "\")
    fileName := parts[parts.Length]
    if (SubStr(fileName, -4) = ".exe") {
        fileName := SubStr(fileName, 1, StrLen(fileName) - 4)
    }
    return fileName
}

; Find a window by app name in the window list
; Returns the hwnd if found, 0 if not found
FindWindowByName(appName) {
    cleanAppName := ExtractExeName(appName)

    windows := WinGetList()
    loop windows.Length {
        hwnd := windows[A_Index]
        windowTitleLower := StrLower(WinGetTitle("ahk_id " . hwnd))
        if (InStr(windowTitleLower, StrLower(cleanAppName))) {
            return hwnd
        }
    }
    return 0
}
