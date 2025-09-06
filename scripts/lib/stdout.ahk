#Requires AutoHotkey v2.0

Stdout(message) {
    try {
        oFile := FileOpen("*", "w")
        oFile.Write(message)
        oFile.Close()
    } catch {
        MsgBox message
    }
}
