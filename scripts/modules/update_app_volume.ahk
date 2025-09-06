#Requires AutoHotkey v2.0
#Include "../lib/arg_parser.ahk"
#Include "../lib/window_utils.ahk"
#Include "../lib/Stdout.ahk"

SoundVolumeViewPath := "../assets/SoundVolumeView.exe"
TempCSV := "../temp_sound_items.csv"

Clamp(valor, minimo, maximo) {
    return (valor < minimo) ? minimo : (valor > maximo) ? maximo : valor
}

try {
    paramConfig := Map(
        "required", ["action"],
        "optional", ["value", "app"],
        "validation", Map(
            "action", Map("valid_values", ["aumentar", "diminuir"], "type", "string"),
            "value", Map("type", "number", "min", 0, "max", 100)
        )
    )
    args := ParseArgs(paramConfig)

    action := GetParam(args, "action", "")
    action_value := GetParam(args, "value", 0)
    app := GetParam(args, "app", "")

    alteracao := (action = "aumentar") ? action_value : -action_value

    if (app = "") {
        system_is_muted := SoundGetMute()

        if (action_value == 0) {
            SoundSetMute(1)
            Stdout("System muted successfully.")
            ExitApp 0
        } else if (action = "aumentar" AND system_is_muted) {
            SoundSetMute(0)
        }

        volumeAtual := SoundGetVolume()
        novoVolume := volumeAtual + alteracao
        novoVolume := Clamp(novoVolume, 0, 100)
        SoundSetVolume(novoVolume)
        Stdout("System volume changed successfully.")
        ExitApp(0)
    } else {
        app := ExtractExeName(app)

        RunWait(Format('"{1}" /scomma "{2}"', SoundVolumeViewPath, TempCSV), , "Hide")
        if !FileExist(TempCSV) {
            Stdout("Error generating audio applications list.")
            ExitApp(1)
        }

        csvContent := FileRead(TempCSV)
        lines := StrSplit(csvContent, "`n", "`r")
        found := false
        bestMatchLine := ""
        for idx, line in lines {
            if InStr(line, ".exe") {
                if InStr(StrLower(line), StrLower(app)) {
                    bestMatchLine := line
                    found := true
                    break
                }
            }
        }

        cmdId := VerifyParams()[1]
        fields := VerifyParams()[2]

        isMuted := false
        if (fields.Length >= 9) {
            isMuted := (Trim(fields[9]) = "Yes")
        }

        if (action_value == 0) {
            comando := Format('"{1}" /Mute "{2}"', SoundVolumeViewPath, cmdId)
        } else {
            if (alteracao > 0 && isMuted) {
                unmuteCmd := Format('"{1}" /Unmute "{2}"', SoundVolumeViewPath, cmdId)
                RunWait(unmuteCmd, , "Hide")
            }
            comando := Format('"{1}" /ChangeVolume "{2}" {3}', SoundVolumeViewPath, cmdId, alteracao)
        }
        RunWait(comando, , "Hide")

        FileDelete TempCSV
        Stdout("Application volume change successful.")
        ExitApp 0
    }
} catch Error as e {
    Stdout(e.Message)
    ExitApp(1)
}

VerifyParams() {
    if (!found) {
        Stdout("Application not found. Check the name/exe. Examples:\n" . csvContent)
        ExitApp(1)
    }
    fields := StrSplit(bestMatchLine, ",")
    if fields.Length < 19 {
        Stdout("Could not extract application identifier.")
        ExitApp(1)
    }
    cmdId := fields[19]
    if (cmdId = "") {
        Stdout("Could not extract application identifier.")
        ExitApp(1)
    }
    return [cmdId, fields]
}
