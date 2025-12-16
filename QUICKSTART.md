# Quick Start Guide - BeagleBone Black Controller

## Snelle Installatie via SSH

### 1. Bestanden uploaden naar BeagleBone

Vanaf je Windows computer (in de map met de Python bestanden):

```powershell
# Vervang <IP> met het IP-adres van je BeagleBone
$BB_IP = "192.168.7.2"  # Of je BeagleBone IP

# Upload alle bestanden
scp *.py *.txt *.sh *.md debian@${BB_IP}:~/beaglebone_controller/
```

### 2. Inloggen op BeagleBone

```powershell
ssh debian@192.168.7.2
# Default wachtwoord: temppwd
```

### 3. Installeren en starten

```bash
cd ~/beaglebone_controller
chmod +x install.sh
sudo ./install.sh

# Start de applicatie
sudo python3 beaglebone_controller.py
```

## Snelle Test Volgorde

### Test 1: I2C Devices Controleren
```bash
i2cdetect -y -r 2
# Verwacht: 0x48 (ADC) en 0x60 (DAC)
```

### Test 2: Individuele Modules
```bash
# Test DAC (MCP4728)
sudo python3 dac_controller.py

# Test ADC (ADS1115)  
sudo python3 adc_controller.py

# Test Relay
sudo python3 relay_controller.py
```

### Test 3: Volledige Applicatie
```bash
sudo python3 beaglebone_controller.py
```

## Gebruik Scenario's

### Scenario 1: Constant 12V Spanningstest
```
Menu: 1 (Spanningsbron)
Keuze: 1 (Constant)
Spanning: 2.2
→ Output blijft op 2.2V
```

### Scenario 2: 4-20mA Loop Simulatie
```
Menu: 2 (Stroombron)
Keuze: 2 (Sinus golf)
Min stroom: 4
Max stroom: 20
Frequentie: 0.1
→ Langzame sinus tussen 4-20mA
```

### Scenario 3: Relay PWM Simulatie
```
Menu: 3 (Relay)
Keuze: 1 (Start met frequentie)
Frequentie: 25
→ 25Hz schakelfrequentie (40ms periode)
```

### Scenario 4: Monitoring
```
Menu: 4 (ADC waarden)
→ Real-time weergave van alle ingangen
→ CTRL+C om te stoppen
```

## Handige Commando's

### BeagleBone Info
```bash
# Kernel versie
uname -a

# Temperatuur
cat /sys/class/thermal/thermal_zone0/temp

# GPIO status
cat /sys/kernel/debug/gpio
```

### I2C Debug
```bash
# Scan alle I2C buses
i2cdetect -l

# Dump register van device
i2cdump -y 2 0x60  # DAC
i2cdump -y 2 0x48  # ADC
```

### Process Management
```bash
# Start in background
sudo python3 beaglebone_controller.py &

# Stop process
sudo killall python3

# Check running processes
ps aux | grep python
```

## Troubleshooting Quick Fixes

### "No module named 'board'"
```bash
pip3 install --upgrade adafruit-blinka
```

### "Permission denied" GPIO
```bash
sudo chown root:gpio /dev/gpiochip*
sudo chmod g+rw /dev/gpiochip*
```

### I2C niet gevonden
```bash
# Check device tree
ls /sys/bus/i2c/devices/

# Force reload I2C
sudo modprobe i2c-dev
sudo modprobe i2c-bcm2708
```

### Python dependencies missen
```bash
pip3 install -r requirements.txt --user
```

## Safety Reminders

⚠️ **Voor gebruik**:
- Controleer spanning limieten (max 3.3V)
- Controleer stroom limieten (4-20mA)
- Test relay schakelfrequentie limiet (max 60Hz)

🛑 **Emergency stop**: 
- CTRL+C in terminal
- Menu optie 6 (Alles stoppen)
- Power cycle BeagleBone

## Windows Upload Script

Maak een `upload.ps1` bestand op je Windows PC:

```powershell
# upload.ps1
$BB_IP = "192.168.7.2"  # Pas aan naar jouw IP

Write-Host "Uploading naar BeagleBone..." -ForegroundColor Green
scp *.py debian@${BB_IP}:~/beaglebone_controller/

Write-Host "Done! SSH verbinden..." -ForegroundColor Green
ssh debian@${BB_IP}
```

Gebruik:
```powershell
.\upload.ps1
```

---

**Happy Testing!** 🎛️
