[Setup]
; Basic application information
AppName=Whisper Transcriber
AppVersion=1.0.0
AppPublisher=Whisper Transcriber Team
AppPublisherURL=https://github.com/ammarlakis/whisper-ui
AppSupportURL=https://github.com/ammarlakis/whisper-ui/issues
AppUpdatesURL=https://github.com/ammarlakis/whisper-ui/releases
DefaultDirName={autopf}\Whisper Transcriber
DefaultGroupName=Whisper Transcriber
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.md
OutputDir=installer_output
OutputBaseFilename=WhisperTranscriber-1.0.0-Setup
#ifexist "icon.ico"
SetupIconFile=icon.ico
#endif
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Version information
VersionInfoVersion=1.0.0.0
VersionInfoCompany=Whisper Transcriber Team
VersionInfoDescription=Whisper Transcriber Setup
VersionInfoCopyright=Copyright (C) 2024 Whisper Transcriber Team
VersionInfoProductName=Whisper Transcriber
VersionInfoProductVersion=1.0.0

; Uninstall information
UninstallDisplayName=Whisper Transcriber
UninstallDisplayIcon={app}\WhisperTranscriber.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\WhisperTranscriber\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Whisper Transcriber"; Filename: "{app}\WhisperTranscriber.exe"
Name: "{group}\{cm:ProgramOnTheWeb,Whisper Transcriber}"; Filename: "https://github.com/your-repo/whisper-transcriber"
Name: "{group}\{cm:UninstallProgram,Whisper Transcriber}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Whisper Transcriber"; Filename: "{app}\WhisperTranscriber.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Whisper Transcriber"; Filename: "{app}\WhisperTranscriber.exe"; Tasks: quicklaunchicon

[Registry]
; Application registry entries
Root: HKLM; Subkey: "Software\Whisper Transcriber"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Whisper Transcriber"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"; Flags: uninsdeletekey

; File associations removed

[Run]
Filename: "{app}\WhisperTranscriber.exe"; Description: "{cm:LaunchProgram,Whisper Transcriber}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  
  // Check Windows version (Windows 10 or later recommended)
  if Version.Major < 10 then
  begin
    if MsgBox('Whisper Transcriber is designed for Windows 10 or later. ' +
              'You are running an older version of Windows. ' +
              'The application may not work correctly. ' +
              'Do you want to continue with the installation?',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;
  
  Result := True;
end;

procedure InitializeWizard();
begin
  WizardForm.LicenseAcceptedRadio.Checked := True;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  // Check for running instances
  if CheckForMutexes('WhisperTranscriberMutex') then
  begin
    Result := 'Whisper Transcriber is currently running. Please close it before continuing.';
    Exit;
  end;
  
  Result := '';
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Refresh shell icons to show file associations
    RefreshEnvironment;
  end;
end;
