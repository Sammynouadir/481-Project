@echo off
set "SCRIPT_DIR=%~dp0"
copy /Y "FireTruckSim\PumpBrainHost\PumpBrain\bin\Debug\net7.0\PumpBrain.dll" "%SCRIPT_DIR%PumpBrain.dll"
start python controlpanel.py
start python FireTruckSim\FoamController\foam_controller.py
start python FireTruckSim\Gauges\gaugesUDP.py
start cmd /c "npm start --prefix FireTruckSim\Governor"
start cmd /c "npm start --prefix FireTruckSim\PTO\PTO"
pushd FireTruckSim
pushd ValveControllers
call runValves.bat
start "" "%SCRIPT_DIR%ScreenSetter.exe"
