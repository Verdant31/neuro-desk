#Requires AutoHotkey v2.0
#Include "../lib/arg_parser.ahk"
#Include "../lib/Stdout.ahk"

SoundVolumeViewPath := "../assets/SoundVolumeView.exe"
TempCSV := "../temp_input_devices.csv"

try {
    paramConfig := Map(
        "required", ["input_name"],
        "optional", [],
        "validation", Map(
            "input_name", Map("type", "string")
        )
    )
    args := ParseArgs(paramConfig)
    input_name := GetParam(args, "input_name", "")

    RunWait(Format('"{1}" /scomma "{2}" /ShowOnlyInputDevices 1', SoundVolumeViewPath, TempCSV), , "Hide")
    if !FileExist(TempCSV) {
        Stdout("Error generating input devices list.")
        ExitApp(1)
    }

    csvContent := FileRead(TempCSV)
    lines := StrSplit(csvContent, "`n", "`r")
    found := false
    deviceName := ""
    loop lines.Length {
        line := lines[A_Index]
        if (A_Index = 1 || line = "")
            continue
        fields := StrSplit(line, ",")
        if (fields.Length < 4)
            continue
        if (InStr(StrLower(input_name), StrLower(fields[4]))) {
            deviceName := fields[4]
            found := true
            break
        }
    }
    if (!found) {
        FileDelete(TempCSV)
        Stdout("Input device not found: " . input_name)
        ExitApp(1)
    }

    RunWait(Format('"{1}" /SetDefault "{2}" 1', SoundVolumeViewPath, deviceName), , "Hide")
    Stdout(Format('Set input device to: {1}', deviceName))
    ExitApp(0)
    FileDelete(TempCSV)
} catch Error as e {
    Stdout(e.Message)
    ExitApp(1)
}
