' ==============================================================================
' STARK LinkedIn Autonomous Job Applicant - Zero Terminal Launcher
' Runs Python in background windowless mode (pyw.exe) with ZERO console window.
' ==============================================================================

Dim WshShell, fso, scriptDir, pywCmd

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

' Detect available windowless Python binary
If fso.FileExists("C:\Windows\pyw.exe") Then
    pywCmd = "C:\Windows\pyw.exe app.py"
ElseIf fso.FileExists("C:\Users\" & WshShell.ExpandEnvironmentStrings("%USERNAME%") & "\AppData\Local\Programs\Python\Python314\pythonw.exe") Then
    pywCmd = """C:\Users\" & WshShell.ExpandEnvironmentStrings("%USERNAME%") & "\AppData\Local\Programs\Python\Python314\pythonw.exe"" app.py"
Else
    pywCmd = "pythonw app.py"
End If

' Launch completely hidden: 0 = SW_HIDE, False = async background execution
WshShell.Run pywCmd, 0, False
