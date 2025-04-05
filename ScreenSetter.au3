Local $DashboardTitle = "Pump Panel Dashboard"
Local $ControlPanelTitle = "Pump Control Panel"
Local $PTOTitle = "PTO Viewer"
Local $GovernorTitle = "Governor"
Local $TankFillTitle = "Valve Control tank fill position"
Local $TankToPumpTitle = "Valve Control tank to pump position"
Local $IntakeTitle = "Valve Control intake position"
Local $FoamControllerTitle = "Foam Controller"
Local $Discharge1Title = "Valve Control discharge 1 position"
Local $Discharge2Title = "Valve Control discharge 2 position"
Local $Discharge3Title = "Valve Control discharge 3 position"

Global $firstWindowFound = False

Func MoveWindow($title, $x, $y, $width, $height)
    Local $handle
    If Not $firstWindowFound Then
        $handle = WinWait($title, "", 30)
        If Not WinExists($title) Then Return
        $firstWindowFound = True
    Else
        $handle = WinGetHandle($title)
        If @error Or $handle = "" Then Return
    EndIf

    ; Restore if minimized
    If WinGetState($handle) <> "" Then
        Local $state = WinGetState($handle)
        If BitAND($state, 16) Then ; 16 = minimized
            WinSetState($handle, "", @SW_RESTORE)
        EndIf
    EndIf

    ; Move and bring to front
    WinMove($handle, "", $x, $y, $width, $height)
    WinActivate($handle)
EndFunc

MoveWindow($DashboardTitle,       0,    0,    1104, 311)
MoveWindow($PTOTitle,             1089, 0,    438,  312)
MoveWindow($ControlPanelTitle,    1510, 0,    416,  1050)
MoveWindow($Discharge1Title,      0,    303,  400,  190)
MoveWindow($Discharge2Title,      0,    485,  400,  190)
MoveWindow($Discharge3Title,      0,    667,  400,  190)
MoveWindow($IntakeTitle,          0,    849,  400,  197)
MoveWindow($FoamControllerTitle,  385,  303,  400,  372)
MoveWindow($TankToPumpTitle,      385,  667,  400,  190)
MoveWindow($TankFillTitle,        385,  849,  400,  197)
MoveWindow($GovernorTitle,        770,  303,  755,  745)
