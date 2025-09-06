; Whisper Transcriber Windows Installer
; Created with NSIS (Nullsoft Scriptable Install System)

!define APP_NAME "Whisper Transcriber"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Whisper Transcriber Team"
!define APP_URL "https://github.com/ammarlakis/whisper-ui"
!define APP_EXECUTABLE "WhisperTranscriber.exe"
!define APP_UNINSTALLER "Uninstall.exe"

; Modern UI
!include "MUI2.nsh"
!include "FileFunc.nsh"

; General settings
Name "${APP_NAME}"
OutFile "WhisperTranscriber-${APP_VERSION}-Setup.exe"
Unicode True
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallDir"
RequestExecutionLevel admin

; Version Information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "© ${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "FileVersion" "${APP_VERSION}"

; Modern UI Configuration
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXECUTABLE}"
!define MUI_FINISHPAGE_RUN_TEXT "Run ${APP_NAME}"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Core Application" SecCore
    SectionIn RO ; Read-only section
    
    SetOutPath "$INSTDIR"
    
    ; Copy application files
    File /r "dist\WhisperTranscriber\*.*"

    ; Create launcher script to set GTK env and start the app hidden
    FileOpen $0 "$INSTDIR\WhisperTranscriberLauncher.vbs" w
    FileWrite $0 "Dim shell: Set shell = CreateObject($\"WScript.Shell$\")$\r$\n"
    FileWrite $0 "Dim fso: Set fso = CreateObject($\"Scripting.FileSystemObject$\")$\r$\n"
    FileWrite $0 "Dim env: Set env = shell.Environment($\"PROCESS$\")$\r$\n"
    FileWrite $0 "env($\"GSK_RENDERER$\") = $\"gl$\"$\r$\n"
    FileWrite $0 "env($\"GTK_THEME$\") = $\"Adwaita$\"$\r$\n"
    FileWrite $0 "env($\"GTK_DATA_PREFIX$\") = $\"$INSTDIR$\"$\r$\n"
    FileWrite $0 "env($\"GTK_EXE_PREFIX$\") = $\"$INSTDIR$\"$\r$\n"
    FileWrite $0 "env($\"GSETTINGS_SCHEMA_DIR$\") = $\"$INSTDIR\share\glib-2.0\schemas$\"$\r$\n"
    FileWrite $0 "env($\"GDK_PIXBUF_MODULE_FILE$\") = $\"$INSTDIR\lib\gdk-pixbuf-2.0\2.10.0\loaders.cache$\"$\r$\n"
    FileWrite $0 "env($\"GDK_PIXBUF_MODULEDIR$\") = $\"$INSTDIR\lib\gdk-pixbuf-2.0\2.10.0\loaders$\"$\r$\n"
    FileWrite $0 "shell.CurrentDirectory = $\"$INSTDIR$\"$\r$\n"
    FileWrite $0 "Dim i, args: args = $\"$\"$\r$\n"
    FileWrite $0 "For i = 0 To WScript.Arguments.Count - 1$\r$\n"
    FileWrite $0 "  args = args & $\" $\" & Chr(34) & WScript.Arguments(i) & Chr(34)$\r$\n"
    FileWrite $0 "Next$\r$\n"
    FileWrite $0 "Dim cmd: cmd = Chr(34) & $\"$INSTDIR\WhisperTranscriber.exe$\" & Chr(34) & args$\r$\n"
    FileWrite $0 "shell.Run cmd, 0, False$\r$\n"
    FileClose $0
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\WhisperTranscriberLauncher.vbs"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\${APP_UNINSTALLER}"
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\WhisperTranscriberLauncher.vbs"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\${APP_NAME}" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${APP_VERSION}"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\${APP_UNINSTALLER}"
    
    ; Add to Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\${APP_UNINSTALLER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
    
    ; Calculate and write install size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "EstimatedSize" "$0"
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\WhisperTranscriberLauncher.vbs"
SectionEnd

Section "File Associations" SecFileAssoc
    ; Associate common audio file types
    WriteRegStr HKCR ".mp3\OpenWithProgids" "${APP_NAME}.mp3" ""
    WriteRegStr HKCR ".wav\OpenWithProgids" "${APP_NAME}.wav" ""
    WriteRegStr HKCR ".m4a\OpenWithProgids" "${APP_NAME}.m4a" ""
    WriteRegStr HKCR ".flac\OpenWithProgids" "${APP_NAME}.flac" ""
    WriteRegStr HKCR ".ogg\OpenWithProgids" "${APP_NAME}.ogg" ""
    
    WriteRegStr HKCR "${APP_NAME}.mp3" "" "MP3 Audio File"
    WriteRegStr HKCR "${APP_NAME}.mp3\DefaultIcon" "" "$INSTDIR\${APP_EXECUTABLE},0"
    WriteRegStr HKCR "${APP_NAME}.mp3\shell\open\command" "" '"$INSTDIR\WhisperTranscriberLauncher.vbs" "%1"'
    
    WriteRegStr HKCR "${APP_NAME}.wav" "" "WAV Audio File"
    WriteRegStr HKCR "${APP_NAME}.wav\DefaultIcon" "" "$INSTDIR\${APP_EXECUTABLE},0"
    WriteRegStr HKCR "${APP_NAME}.wav\shell\open\command" "" '"$INSTDIR\WhisperTranscriberLauncher.vbs" "%1"'
    
    WriteRegStr HKCR "${APP_NAME}.m4a" "" "M4A Audio File"
    WriteRegStr HKCR "${APP_NAME}.m4a\DefaultIcon" "" "$INSTDIR\${APP_EXECUTABLE},0"
    WriteRegStr HKCR "${APP_NAME}.m4a\shell\open\command" "" '"$INSTDIR\WhisperTranscriberLauncher.vbs" "%1"'
    
    WriteRegStr HKCR "${APP_NAME}.flac" "" "FLAC Audio File"
    WriteRegStr HKCR "${APP_NAME}.flac\DefaultIcon" "" "$INSTDIR\${APP_EXECUTABLE},0"
    WriteRegStr HKCR "${APP_NAME}.flac\shell\open\command" "" '"$INSTDIR\WhisperTranscriberLauncher.vbs" "%1"'
    
    WriteRegStr HKCR "${APP_NAME}.ogg" "" "OGG Audio File"
    WriteRegStr HKCR "${APP_NAME}.ogg\DefaultIcon" "" "$INSTDIR\${APP_EXECUTABLE},0"
    WriteRegStr HKCR "${APP_NAME}.ogg\shell\open\command" "" '"$INSTDIR\WhisperTranscriberLauncher.vbs" "%1"'
SectionEnd

; Section descriptions
LangString DESC_SecCore ${LANG_ENGLISH} "Core application files (required)"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Create a desktop shortcut"
LangString DESC_SecFileAssoc ${LANG_ENGLISH} "Associate audio files with ${APP_NAME}"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecFileAssoc} $(DESC_SecFileAssoc)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKLM "Software\${APP_NAME}"
    
    ; Remove file associations
    DeleteRegKey HKCR "${APP_NAME}.mp3"
    DeleteRegKey HKCR "${APP_NAME}.wav"
    DeleteRegKey HKCR "${APP_NAME}.m4a"
    DeleteRegKey HKCR "${APP_NAME}.flac"
    DeleteRegKey HKCR "${APP_NAME}.ogg"
    
    DeleteRegValue HKCR ".mp3\OpenWithProgids" "${APP_NAME}.mp3"
    DeleteRegValue HKCR ".wav\OpenWithProgids" "${APP_NAME}.wav"
    DeleteRegValue HKCR ".m4a\OpenWithProgids" "${APP_NAME}.m4a"
    DeleteRegValue HKCR ".flac\OpenWithProgids" "${APP_NAME}.flac"
    DeleteRegValue HKCR ".ogg\OpenWithProgids" "${APP_NAME}.ogg"
SectionEnd

; Functions
Function .onInit
    ; Check if already installed
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString"
    StrCmp $R0 "" done
    
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
        "${APP_NAME} is already installed. $\n$\nClick `OK` to remove the previous version or `Cancel` to cancel this upgrade." \
        IDOK uninst
    Abort
    
    uninst:
        ClearErrors
        ExecWait '$R0 _?=$INSTDIR'
        
        IfErrors no_remove_uninstaller done
        no_remove_uninstaller:
    
    done:
FunctionEnd
