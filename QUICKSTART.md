# Quick Start Guide - BeagleBone Black MCP4822 DAC

## Snelle Installatie via SSH

### 1. Bestanden uploaden naar BeagleBone

Vanaf je Windows computer (in de map met de bestanden):

```powershell
# Vervang IP met het IP-adres van je BeagleBone
$BB_IP = "192.168.178.179"  # Of jouw BeagleBone IP

# Upload bestanden
scp mcp4922_driver.py test_dac_sweep.py dac_startup.sh requirements.txt debian@${BB_IP}:~/autotester/
```

### 2. Inloggen op BeagleBone

```powershell
ssh debian@192.168.178.179
# Default wachtwoord: temppwd
```

### 3. Installeren en initialiseren

```bash
cd ~/autotester

# Installeer Python dependencies
pip3 install -r requirements.txt

# Maak startup script executable
chmod +x dac_startup.sh

# Hardware initialiseren (VERPLICHT na elke boot!)
sudo ./dac_startup.sh
```

## Snelle Test Volgorde

### Test 1: SPI Device Controleren
```bash
ls -la /dev/spidev*
# Moet /dev/spidev0.0 tonen
```

### Test 2: DAC Test Programma
```bash
python3 test_dac_sweep.py

# Selecteer optie 1: Langzame sweep
# Monitor output op oscilloscoop
```

## Gebruik Scenario's

### Scenario 1: Oscilloscoop Verificatie
```
Menu: 1 (Langzame Sweep)
→ Sweep 0V → 3.3V in 10 seconden
→ Controleer lineaire stijging op scope
```

### Scenario 2: Vaste Spanning Instellen
```
Menu: 4 (Handmatige Controle)
Spanning: 2.5
→ Output blijft op 2.5V
→ Type 'q' om te stoppen
```

### Scenario 3: Stap Test
```
Menu: 3 (Stap Test)
→ Test 0%, 25%, 50%, 75%, 100% van bereik
→ Verificeer elke stap op multimeter
```

## Handige Commando's

### BeagleBone Info
```bash
# Kernel versie
uname -a

# SPI status controleren
cat /sys/class/spi_master/spi0/device/power/control
# Moet "on" tonen (niet "auto")

# Pin configuratie
cat /sys/kernel/debug/pinctrl/44e10800.pinmux/pins
```

### SPI Debug
```bash
# Controleer SPI devices
ls -la /dev/spidev*

# Check GPIO status
cat /sys/kernel/debug/gpio | grep -E "P9_20|P9_12"

# Monitor SPI transfers (vereist spidev-test tool)
spidev_test -D /dev/spidev0.0 -v
```

### Process Management
```bash
# Check Python processes
ps aux | grep python

# Kill Python processen
sudo killall python3
```

## Troubleshooting Quick Fixes

### "No such file or directory: /dev/spidev0.0"
```bash
# Run startup script!
sudo ./dac_startup.sh
```

### "Permission denied" GPIO
```bash
# Run with sudo voor startup
sudo ./dac_startup.sh
```

### SPI controller suspended
```bash
# Activeer runtime PM
sudo sh -c 'echo "on" > /sys/class/spi_master/spi0/device/power/control'
```

### P9_20 CS pin blijft HIGH
```bash
# Free GPIO 12
sudo sh -c 'echo 12 > /sys/class/gpio/unexport'
```

### Python dependencies missen
```bash
pip3 install Adafruit_BBIO --user
```

## Safety Reminders

⚠️ **Voor gebruik**:
- Controleer DAC output bereik (0-4.096V max theoretisch)
- Praktisch gebruik: 0-3.3V
- Voer dac_startup.sh uit na elke reboot

🛑 **Reset DAC**: 
```bash
# Stop programma: CTRL+C
# Of via menu: optie 5 (Reset naar 0V)
```

## Windows Upload Script

Maak een `upload.ps1` bestand op je Windows PC:

```powershell
# upload.ps1
$BB_IP = "192.168.178.179"  # Pas aan naar jouw IP

Write-Host "Uploading naar BeagleBone..." -ForegroundColor Green
scp mcp4922_driver.py test_dac_sweep.py dac_startup.sh debian@${BB_IP}:~/autotester/

Write-Host "Done! SSH verbinden..." -ForegroundColor Green
ssh debian@${BB_IP}
```

Gebruik:
```powershell
.\upload.ps1
```

## Na Reboot Checklist

**BELANGRIJK**: Na elke BeagleBone reboot moet je:

1. ✓ SSH inloggen
2. ✓ `cd ~/autotester`
3. ✓ `sudo ./dac_startup.sh` uitvoeren
4. ✓ Dan pas `python3 test_dac_sweep.py` starten

---

**Happy DAC Testing!** 📊
