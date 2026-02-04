; Script de Inno Setup para Happy Body Gym - Control de Asistencia

[Setup]
AppName=Happy Body Gym - Control de Asistencia
AppVersion=1.0
; La siguiente línea indica el directorio de salida para el instalador.
; Asegúrate de que este directorio exista o Inno Setup lo creará.
OutputBaseFilename=HappyBodyGym_Setup
DefaultDirName={autopf}\Happy Body Gym
DefaultGroupName=Happy Body Gym
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
UninstallDisplayIcon={app}\main_app.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
; Archivo ejecutable de la aplicación (asumiendo que se ha creado con PyInstaller o similar)
; Si la aplicación se distribuye como un solo .exe, este sería el archivo principal.
; Si se distribuye como una colección de .py, necesitarías incluir el intérprete de Python
; y todos los archivos .py, lo cual es más complejo.
; Incluir todo el contenido del directorio de salida de PyInstaller (--onedir)
Source: "dist\main_app.exe"; DestDir: "{app}"; Flags: ignoreversion
; Si necesitas incluir otros archivos generados por PyInstaller en modo onefile (como DLLs si no están embebidas)
; Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Base de datos
Source: "Database.accdb"; DestDir: "{app}"; Flags: ignoreversion
; Icono de la aplicación
Source: "asent\gym.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Happy Body Gym"; Filename: "{app}\main_app.exe"; IconFilename: "{app}\gym.ico"
Name: "{autodesktop}\Happy Body Gym"; Filename: "{app}\main_app.exe"; IconFilename: "{app}\gym.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
; Ejecutar la aplicación después de la instalación
Filename: "{app}\main_app.exe"; Description: "{cm:LaunchProgram,Happy Body Gym - Control de Asistencia}"; Flags: nowait postinstall skipifsilent

[Messages]
SetupLdrNote=Este instalador requiere que el "Microsoft Access Database Engine 2010 Redistributable" (o una versión posterior) esté instalado en su sistema para funcionar correctamente. Si la aplicación no se inicia, por favor, instale este componente. Puede encontrarlo en el sitio web de Microsoft.
