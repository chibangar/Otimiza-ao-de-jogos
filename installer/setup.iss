; Midnight Optimizer — instalador Windows (Inno Setup 6)
#define AppVersion "1.9.2"

[Setup]
AppName=Midnight Optimizer
AppVersion={#AppVersion}
AppPublisher=Midnight Optimizer
DefaultDirName={autopf}\Midnight Optimizer
DefaultGroupName=Midnight Optimizer
OutputDir=..\installer
OutputBaseFilename=MidnightOptimizer-Setup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\MidnightOptimizer.exe
SetupIconFile=..\assets\icon.ico
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho no ambiente de trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Files]
Source: "..\dist\MidnightOptimizer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\oauth_config.example.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\Midnight Optimizer"; Filename: "{app}\MidnightOptimizer.exe"
Name: "{group}\Desinstalar Midnight Optimizer"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Midnight Optimizer"; Filename: "{app}\MidnightOptimizer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MidnightOptimizer.exe"; Description: "Abrir o Midnight Optimizer"; Flags: nowait postinstall skipifsilent

[Code]
var
  CableZip: String;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResCode: Integer;
  DestDir, Cmd: String;
begin
  if CurStep = ssInstall then
  begin
    CableZip := ExpandConstant('{tmp}\VBCABLE_Driver_Pack45.zip');
    Cmd := '$ProgressPreference="SilentlyContinue"; Invoke-WebRequest -Uri "https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack45.zip" -OutFile "' + CableZip + '"';
    if (not Exec('powershell.exe', '-NoProfile -ExecutionPolicy Bypass -Command ' + Cmd, '', SW_HIDE, ewWaitUntilTerminated, ResCode)) or (ResCode <> 0) or (not FileExists(CableZip)) then
    begin
      MsgBox('Sem internet: o micro virtual (VB-CABLE) nao foi instalado. Corre o Setup outra vez com net para o teres.', mbInformation, MB_OK);
      CableZip := '';
    end;
  end;
  if (CurStep = ssPostInstall) and (CableZip <> '') then
  begin
    DestDir := ExpandConstant('{tmp}\vbcable');
    Cmd := 'Expand-Archive -LiteralPath "' + CableZip + '" -DestinationPath "' + DestDir + '" -Force';
    Exec('powershell.exe', '-NoProfile -ExecutionPolicy Bypass -Command ' + Cmd, '', SW_HIDE, ewWaitUntilTerminated, ResCode);
    Exec(DestDir + '\VBCABLE_Setup_x64.exe', '-i -h', '', SW_HIDE, ewWaitUntilTerminated, ResCode);
    MsgBox('Micro virtual instalado! A app rebatiza-o para "Midnight Mic" sozinha. Reinicia o PC e no CS2/Discord escolhe "Midnight Mic" como microfone.', mbInformation, MB_OK);
  end;
end;
