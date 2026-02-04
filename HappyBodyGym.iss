; Script generado para Inno Setup Compiler para el sistema de control de asistencia Gym
; Ajusta los paths y nombres según tu entorno y necesidades

[Setup]
AppName=HappyBodyGym
AppVersion=1.1
DefaultDirName={pf}\HappyBodyGym
DefaultGroupName=HappyBodyGym
OutputDir=Output
OutputBaseFilename=HappyBodyGym_Setup_v1.1
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
; Ejecutable principal generado por PyInstaller
Source: "dist\HappyBodyGym.exe"; DestDir: "{app}"; Flags: ignoreversion
; Base de datos Access
Source: "Database.accdb"; DestDir: "{app}"; Flags: ignoreversion
; Icono de la app
Source: "asent\gym.ico"; DestDir: "{app}"; Flags: ignoreversion
; Archivo de versión (opcional)
Source: "file_version_info.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\HappyBodyGym"; Filename: "{app}\HappyBodyGym.exe"; IconFilename: "{app}\gym.ico"
Name: "{commondesktop}\HappyBodyGym"; Filename: "{app}\HappyBodyGym.exe"; IconFilename: "{app}\gym.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear un icono en el escritorio"; GroupDescription: "Iconos adicionales:"

[Run]
Filename: "{app}\HappyBodyGym.exe"; Description: "Iniciar HappyBodyGym"; Flags: nowait postinstall skipifsilent
