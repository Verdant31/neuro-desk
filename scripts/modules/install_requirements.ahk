#Requires AutoHotkey v2.0

RunInstallModule() {
    psCommand := "
    (
    Set-ExecutionPolicy remotesigned -Scope Process -Force;
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;
    Install-Module -Name DisplayConfig -Force -AllowClobber -Scope CurrentUser
    )"

    Run('*RunAs powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "' psCommand '"')
}

RunInstallModule()