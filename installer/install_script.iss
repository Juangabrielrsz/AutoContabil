[Setup]
AppName=AutoContabil
AppVersion=1.0
DefaultDirName={pf}\AutoContabil
DefaultGroupName=AutoContabil
UninstallDisplayIcon={app}\AutoContabil.exe
OutputDir=.
OutputBaseFilename=AutoContabilInstaller
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\dist\AutoContabil.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "app\database.db"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "C:\Users\juang\OneDrive\Área de Trabalho\automacao_contabil\app\tabs\modelos\holerite_modelo_em_branco.pdf"; DestDir: "{app}\app\tabs\modelos"; Flags: ignoreversion
Source: "vcredist_x64.exe"; DestDir: "{tmp}"; Flags: ignoreversion

[Icons]
Name: "{group}\AutoContabil"; Filename: "{app}\AutoContabil.exe"
Name: "{commondesktop}\AutoContabil"; Filename: "{app}\AutoContabil.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Opções adicionais"

[Run]
Filename: "{app}\AutoContabil.exe"; Description: "Executar AutoContabil"; Flags: nowait postinstall skipifsilent
Filename: "{tmp}\vcredist_x64.exe"; Parameters: "/quiet /norestart"; Flags: waituntilterminated

