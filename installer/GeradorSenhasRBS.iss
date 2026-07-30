#define MyAppName "Gerador de Senhas - RBS"
#define MyAppVersion "3.0.0"
#define MyAppPublisher "RBS"
#define MyAppExeName "gerador_senhas_rbs.exe"

[Setup]
AppId={{6E8FC101-4534-4677-903B-A56C869F6119}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Gerador de Senhas RBS
DefaultGroupName={#MyAppName}
OutputDir=saida
OutputBaseFilename=Instalador_Gerador_Senhas_RBS_3
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "..\build\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos adicionais:"

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent
