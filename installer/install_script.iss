[Setup]
AppName=CbOrganization
AppVersion=1.0
DefaultDirName={pf}\CbOrganization
DefaultGroupName=CbOrganization
UninstallDisplayIcon={app}\CbOrganization.exe
OutputDir=.
OutputBaseFilename=CbOrganizationInstaller
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\dist\CbOrganization.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "app\database.db"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "modelos\holerite_modelo_em_branco.pdf"; DestDir: "{app}\app\tabs\modelos"; Flags: ignoreversion
Source: "vcredist_x64.exe"; DestDir: "{tmp}"; Flags: ignoreversion

[Icons]
Name: "{group}\CbOrganization"; Filename: "{app}\CbOrganization.exe"
Name: "{commondesktop}\CbOrganization"; Filename: "{app}\CbOrganization.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Opções adicionais"

[Run]
Filename: "{app}\CbOrganization.exe"; Description: "Executar CbOrganization"; Flags: nowait postinstall skipifsilent
Filename: "{tmp}\vcredist_x64.exe"; Parameters: "/quiet /norestart"; Flags: waituntilterminated

