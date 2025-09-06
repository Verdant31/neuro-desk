#Requires AutoHotkey v2.0
#Include "../lib/arg_parser.ahk"
#Include "../lib/JSON.ahk"
#Include "../lib/Stdout.ahk"

RunChromeModule() {
    args := ParseArgs()

    profile := GetParam(args, "profile", "")
    tabs := GetParam(args, "tabs", [])

    settingsPath := A_ScriptDir . "\..\settings.json"
    if !FileExist(settingsPath) {
        Stdout("Error: settings.json not found at " settingsPath)
        ExitApp 1
    }

    try {
        settingsContent := FileRead(settingsPath)
        settings := Jxon_Load(&settingsContent)
    } catch Error as e {
        Stdout("Error loading settings.json: " e.Message)
        ExitApp 1
    }

    chromeProfiles := settings["chrome_profiles"]
    if !chromeProfiles || !(chromeProfiles is Array) || chromeProfiles.Length = 0 {
        Stdout("Error: No Chrome profiles found in settings.json")
        ExitApp 1
    }

    selectedProfile := ""
    if (profile = "") {
        selectedProfile := chromeProfiles[1]
    } else {
        for p in chromeProfiles {
            if (p['name'] = profile) {
                selectedProfile := p
                break
            }
        }

        if (!selectedProfile) {
            Stdout("Error: Profile '" profile "' not found. Available profiles:`n" GetProfileNames(chromeProfiles))
            ExitApp 1
        }
    }

    shortcutPath := selectedProfile['shortcut_path']
    if !FileExist(shortcutPath) {
        Stdout("Error: Chrome shortcut not found at " shortcutPath)
        ExitApp 1
    }

    chromeCommand := BuildChromeCommand(shortcutPath, tabs)

    try {
        Run(chromeCommand)
        Stdout("Chrome launched successfully.")
        ExitApp(0)
    } catch Error as e {
        Stdout("Error launching Chrome: " e.Message)
        ExitApp 1
    }
}

BuildChromeCommand(shortcutPath, tabs) {
    if (!tabs || !(tabs is Array) || tabs.Length = 0) {
        return shortcutPath
    }

    command := shortcutPath

    for i, tab in tabs {
        if (i = 1) {
            command .= " " . tab
        } else {
            command .= " --new-window " . tab
        }
    }

    return command
}

GetProfileNames(profiles) {
    names := ""
    for i, profile in profiles {
        if (i > 1) {
            names .= "`n"
        }
        names .= "- " . profile.name
    }
    return names
}

RunChromeModule()