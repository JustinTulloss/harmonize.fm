; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{D263B192-EF2C-43E9-BD75-BB529F8345E6}
AppName=Harmonize.fm
AppVerName=Harmonize Alpha
AppPublisher=Harmonize, Inc.
AppPublisherURL=http://harmonize.fm
AppSupportURL=http://harmonize.fm
AppUpdatesURL=http://harmonize.fm
DefaultDirName={pf}\Harmonize
DisableDirPage=yes
DefaultGroupName=Harmonize
OutputBaseFilename=Harmonizer Setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: english; MessagesFile: compiler:Default.isl

[Tasks]
Name: desktopicon; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: unchecked

[Files]
Source: C:\Documents and Settings\Brian\rubicon-local\uploader\dist\Harmonize.exe; DestDir: {app}; Flags: ignoreversion
Source: C:\Documents and Settings\Brian\rubicon-local\uploader\dist\*; DestDir: {app}; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files
Source: C:\Program Files\ISTool\isxdl.dll; DestDir: {app}

[Icons]
Name: {group}\Harmonizer; Filename: {app}\Harmonize.exe; WorkingDir: {app}; IconFilename: "{app}\harmonize_icon.ico"
Name: {commondesktop}\Harmonizer; Filename: {app}\Harmonize.exe; Tasks: desktopicon; WorkingDir: {app}; IconFilename: "{app}\harmonize_icon.ico"

[Run]
Filename: {app}\Harmonize.exe; Description: {cm:LaunchProgram,Harmonize}; Flags: nowait postinstall skipifsilent

[Code]
var
  dotnetRedistPath: string;
  downloadNeeded: boolean;
  dotNetNeeded: boolean;
  memoDependenciesNeeded: string;

procedure isxdl_AddFile(URL, Filename: PChar);
external 'isxdl_AddFile@files:isxdl.dll stdcall';
function isxdl_DownloadFiles(hWnd: Integer): Integer;
external 'isxdl_DownloadFiles@files:isxdl.dll stdcall';
function isxdl_SetOption(Option, Value: PChar): Integer;
external 'isxdl_SetOption@files:isxdl.dll stdcall';


const
  dotnetRedistURL = 'http://download.microsoft.com/download/5/6/7/567758a3-759e-473e-bf8f-52154438565a/dotnetfx.exe';
  // local system for testing...
  // dotnetRedistURL = 'http://192.168.1.1/dotnetfx.exe';

function InitializeSetup(): Boolean;

begin
  Result := true;
  dotNetNeeded := false;


  // Check for required netfx installation
  //if (not GetUserDefaultLangID() = 'English') then begin

        //msgbox('Language Is Not English');

  //end;

  if (not RegKeyExists(HKLM, 'Software\Microsoft\.NETFramework\policy\v2.0')) then begin
    dotNetNeeded := true;
    if (not IsAdminLoggedOn()) then begin
      MsgBox('Image Gallery Designer 0.9 needs the Microsoft .NET Framework 2.0 to be installed by an Administrator', mbInformation, MB_OK);
      Result := false;
    end else begin
      memoDependenciesNeeded := memoDependenciesNeeded + '      .NET Framework 2.0' #13;
      dotnetRedistPath := ExpandConstant('{src}\dotnetfx.exe');
      if not FileExists(dotnetRedistPath) then begin
        dotnetRedistPath := ExpandConstant('{tmp}\dotnetfx.exe');
        if not FileExists(dotnetRedistPath) then begin
          isxdl_AddFile(dotnetRedistURL, dotnetRedistPath);
          downloadNeeded := true;
        end;
      end;
      SetIniString('install', 'dotnetRedist', dotnetRedistPath, ExpandConstant('{tmp}\dep.ini'));
    end;
  end;

end;

function NextButtonClick(CurPage: Integer): Boolean;
var
  hWnd: Integer;
  ResultCode: Integer;

begin
  Result := true;

  if CurPage = wpReady then begin

    hWnd := StrToInt(ExpandConstant('{wizardhwnd}'));

    // don't try to init isxdl if it's not needed because it will error on < ie 3
    if downloadNeeded then begin

      isxdl_SetOption('label', 'Downloading Microsoft .NET Framework 2.0');
      isxdl_SetOption('description', 'Harmonizer needs to install the Microsoft .NET Framework 2.0. Please wait while Setup is downloading extra files to your computer.');
      if isxdl_DownloadFiles(hWnd) = 0 then Result := false;
    end;
    if (Result = true) and (dotNetNeeded = true) then begin
      if Exec(ExpandConstant(dotnetRedistPath), '', '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then begin
        // handle success if necessary; ResultCode contains the exit code
        if not (ResultCode = 0) then begin
          Result := false;
        end;
      end else begin
        // handle failure if necessary; ResultCode contains the error code
        Result := false;
      end;
    end;
  end;
end;

function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo, MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
var
  s: string;

begin
  if memoDependenciesNeeded <> '' then s := s + 'Dependencies that will be automatically downloaded And installed:' + NewLine + memoDependenciesNeeded + NewLine;
  s := s + MemoDirInfo + NewLine + NewLine;

  Result := s
end;
