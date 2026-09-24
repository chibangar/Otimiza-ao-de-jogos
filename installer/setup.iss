#define APP_VERSION "3.1.0"
#define APP_NAME "Midnight Optimizer 3.1.0"
#define AUTHOR "chibangar"

[Setup]
AppName={#APP_NAME}
AppVersion={#APP_VERSION}
AppPublisher={#AUTHOR}
AppPublisherEmail=contact@midnightoptimizer.com
DefaultDirName={autopf}\Midnight Optimizer
DefaultGroupName=Midnight Optimizer
WizardStyle=modern
OutputBaseFilename=Midnight_Optimizer_3.1.0_Setup
Compression=lzma2
SolidCompression=yes
DisableDirPage=yes
DisableProgramsPage=yes
DisableReadyPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Files]
Source: "dist\MidnightOptimizer.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\Midnight Optimizer"; Filename: "{app}\MidnightOptimizer.exe"
Name: "{commonprograms}\Midnight Optimizer"; Filename: "{app}\MidnightOptimizer.exe"

[Run]
Filename: "{app}\MidnightOptimizer.exe"; Description: "Iniciar Midnight Optimizer"; Flags: nowait postinstall skipifsilent
