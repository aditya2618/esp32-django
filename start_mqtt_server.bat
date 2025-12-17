@echo off
echo Stopping existing Mosquitto...
taskkill /F /IM mosquitto.exe >nul 2>&1

echo.
echo Opening Firewall Port 1883...
netsh advfirewall firewall add rule name="Allow MQTT" dir=in action=allow protocol=TCP localport=1883 >nul

echo.
echo Starting Mosquitto with External Access...
"C:\Program Files\mosquitto\mosquitto.exe" -c "d:\PROJECT\esp32-flasher\esp32-django\mosquitto.conf" -v

pause
