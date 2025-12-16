# BeagleBone Black DAC/ADC/Relay Controller

Complete Python applicatie voor het besturen van een custom BeagleBone Black cape met:
- **MCP4728** 4-kanaals 12-bit DAC (I2C)
- **ADS1115** 4-kanaals 16-bit ADC (I2C)
- **Relay module** (GPIO P9 pin 12)
- **OPA197** dual op-amps voor spanning en stroom output

## Hardware Configuratie

### I2C Bus (P9 pins 19 en 20)
- **P9_19**: SCL (I2C2_SCL)
- **P9_20**: SDA (I2C2_SDA)

### MCP4728 DAC Kanalen
- **Channel A + B**: Voltage output via eerste OPA197 (0-3.3V)
  - VOUTA → Pin 3 (+) van opamp
  - VOUTB → Pin 2 (-) van opamp
  
- **Channel C + D**: Current output via tweede OPA197 + IRLZ44N (4-20mA)
  - VOUTC → Pin 3 (+) van opamp
  - VOUTD → Pin 2 (-) van opamp
  - Opamp output → IRLZ44N pin 1 (Gate)

### GPIO
- **P9_12**: Relay control (1-60Hz schakelfrequentie)

### ADS1115 ADC
- **Channel 0-3**: Algemene analoge ingangen (0-4.096V range)

## Software Architectuur

```
beaglebone_controller.py     # Hoofd applicatie met menu interface
├── dac_controller.py         # MCP4728 DAC besturing
├── adc_controller.py         # ADS1115 ADC uitlezing
├── relay_controller.py       # GPIO relay besturing
└── waveform_generator.py     # Golfvorm generatie
```

## Installatie op BeagleBone Black

### 1. Voorbereiding
```bash
# Update systeem
sudo apt-get update
sudo apt-get upgrade

# Installeer Python en pip
sudo apt-get install python3 python3-pip

# Installeer I2C tools (optioneel voor debugging)
sudo apt-get install i2c-tools
```

### 2. I2C Activeren
Controleer of I2C2 actief is:
```bash
ls /dev/i2c*
# Moet /dev/i2c-2 tonen
```

Als I2C2 niet actief is, activeer in `/boot/uEnv.txt`:
```bash
sudo nano /boot/uEnv.txt
# Uncomment of voeg toe:
# dtb_overlay=/lib/firmware/BB-I2C2-00A0.dtbo
```

### 3. Python Dependencies Installeren
```bash
# Upload requirements.txt naar BeagleBone
# Via SSH/SCP vanaf je computer:
# scp requirements.txt debian@<beaglebone-ip>:~/

# Op BeagleBone:
pip3 install -r requirements.txt
```

### 4. Applicatie Uploaden
Upload alle Python bestanden naar de BeagleBone:
```bash
# Vanaf je computer via SCP:
scp beaglebone_controller.py debian@<beaglebone-ip>:~/
scp dac_controller.py debian@<beaglebone-ip>:~/
scp adc_controller.py debian@<beaglebone-ip>:~/
scp relay_controller.py debian@<beaglebone-ip>:~/
scp waveform_generator.py debian@<beaglebone-ip>:~/

# Of gebruik een directory:
scp *.py debian@<beaglebone-ip>:~/beaglebone_controller/
```

### 5. Hardware Testen
Controleer I2C devices:
```bash
# Scan I2C bus 2
i2cdetect -y -r 2

# Verwachte output:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- -- 
# 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 60: 60 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 70: -- -- -- -- -- -- -- --

# 0x48 = ADS1115 ADC
# 0x60 = MCP4728 DAC
```

## Gebruik

### 1. Applicatie Starten
```bash
cd ~/beaglebone_controller  # Of waar je bestanden staan
sudo python3 beaglebone_controller.py
```

**Opmerking**: `sudo` is nodig voor GPIO toegang.

### 2. Menu Navigatie

#### Hoofdmenu:
```
==============================================================
 BeagleBone Black - DAC/ADC/Relay Controller
==============================================================

1. Spanningsbron configureren (0-3.3V)
2. Stroombron configureren (4-20mA)
3. Relay configureren (1-60Hz)
4. ADC waarden uitlezen
5. Status weergeven
6. Alles stoppen
7. Afsluiten
```

#### 1. Spanningsbron (0-3.3V)
Kies uit verschillende curve types:
- **Constant**: Vaste spanning
- **Sinus**: Sinusgolf met instelbare min/max en frequentie
- **Driehoek**: Driehoekgolf
- **Blokgolf**: Vierkantsgolf (50% duty cycle)
- **Ramp**: Lineair oplopend van start naar eind spanning

Voorbeeld:
```
Keuze: 2 (Sinus golf)
Minimum spanning (V): 0.5
Maximum spanning (V): 3.0
Frequentie (Hz): 2
→ Genereert 2Hz sinusgolf tussen 0.5V en 3.0V
```

#### 2. Stroombron (4-20mA)
Zelfde opties als spanningsbron, maar voor stroom output:
```
Keuze: 1 (Constant)
Voer stroom in (4-20mA): 12
→ Stelt constante 12mA in
```

#### 3. Relay Configuratie
```
Keuze: 1 (Start relay met frequentie)
Frequentie (1-60Hz): 10
→ Relay schakelt 10x per seconde (10Hz)
```

#### 4. ADC Waarden
Real-time monitoring van alle 4 ADC kanalen:
```
CH0:   1.234V  CH1:   2.456V  CH2:   0.123V  CH3:   3.321V
```
Druk CTRL+C om te stoppen en terug te gaan naar het menu.

### 3. Individuele Module Tests

Test elke module afzonderlijk:

```bash
# Test DAC
sudo python3 dac_controller.py

# Test ADC
sudo python3 adc_controller.py

# Test Relay
sudo python3 relay_controller.py

# Test Waveform Generator
python3 waveform_generator.py  # Geen sudo nodig
```

## Technische Details

### DAC Output Berekening

**Spanningsuitgang (0-3.3V)**:
```python
DAC_value = (Voltage / 3.3V) × 4095
```

**Stroomuitgang (4-20mA)**:
Lineaire mapping waarbij:
- 4mA = 0V DAC output
- 20mA = 3.3V DAC output
```python
voltage_ratio = (I_mA - 4) / (20 - 4)
voltage = voltage_ratio × 3.3V
DAC_value = (voltage / 3.3V) × 4095
```

### Golfvormen

De waveform generator ondersteunt:
- **Sine**: `sin(2π × f × t)`
- **Triangle**: Lineair stijgend/dalend
- **Square**: 50% duty cycle
- **Sawtooth**: Lineair stijgend, abrupte val
- **Ramp**: Eenmalig lineair tussen twee waarden
- **Exponential**: Exponentiële benadering
- **Custom**: Vrij te definiëren punten

Update rate: **100Hz** (10ms interval)

### Thread Safety

De applicatie gebruikt threads voor:
- Voltage waveform generatie (aparte thread)
- Current waveform generatie (aparte thread)
- Relay switching (aparte thread)

Alle threads zijn daemon threads en stoppen automatisch bij afsluiten.

## Troubleshooting

### I2C Device niet gevonden
```bash
# Controleer I2C bus:
ls -l /dev/i2c-2

# Controleer device tree overlays:
sudo /opt/scripts/tools/version.sh | grep UBOOT

# Check I2C devices:
i2cdetect -y -r 2
```

### GPIO Permission Denied
Gebruik `sudo` voor GPIO toegang:
```bash
sudo python3 beaglebone_controller.py
```

Of voeg user toe aan gpio groep:
```bash
sudo usermod -a -G gpio $USER
# Log uit en weer in
```

### Import Errors
Controleer of alle dependencies geïnstalleerd zijn:
```bash
pip3 list | grep -i adafruit
pip3 list | grep -i bbio
```

Herinstalleer indien nodig:
```bash
pip3 install --upgrade -r requirements.txt
```

### Hardware Checklist
- ✓ 3.3V voeding aangesloten
- ✓ I2C pull-up weerstanden aanwezig (typisch 4.7kΩ)
- ✓ DAC ADDR pins correct geconfigureerd (standaard 0x60)
- ✓ ADC ADDR pin correct (standaard 0x48)
- ✓ Opamp voeding aangesloten
- ✓ Relay voeding en ground aangesloten

## Veiligheid

Bij het stoppen van de applicatie:
- Voltage output → 0V
- Current output → 4mA (minimum)
- Relay → UIT

Emergency stop: Druk **CTRL+C** of selecteer menu optie **6**.

## Licentie

Deze code is ontwikkeld voor gebruik met BeagleBone Black custom hardware.

## Support

Voor vragen of problemen, controleer:
1. Hardware connecties
2. I2C bus status (`i2cdetect`)
3. Python package versies
4. BeagleBone kernel versie

---

**Veel succes met je project!** 🚀
