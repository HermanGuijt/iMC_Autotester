# BeagleBone Black MCP4822 DAC Controller

Python driver en test applicatie voor het besturen van een MCP4822 12-bit dual DAC via SPI.

## Hardware Specificaties

### MCP4822 DAC
- **Type**: 12-bit dual channel DAC
- **Interface**: SPI (max 20 MHz)
- **Vref**: 2.048V interne referentie
- **Output bereik**: 
  - Gain=1: 0 - 2.048V
  - Gain=2: 0 - 4.096V (auto-select in driver)
- **Praktisch gebruikt**: 0 - 3.3V

## Pin Configuratie BeagleBone Black

### SPI Pins (P9 header)
- **P9_17**: SPI0_CS (hardware CS - niet gebruikt)
- **P9_18**: SPI0_MOSI (SDI naar DAC)
- **P9_21**: SPI0_MISO (niet gebruikt voor DAC)
- **P9_22**: SPI0_SCLK (SCK naar DAC)

### GPIO Pins
- **P9_20**: Chip Select (CS) - software controlled
- **P9_12**: LDAC (Latch DAC) - triggers output update

## Software Architectuur

```
mcp4822_driver.py           # MCP4822 DAC driver class
├── SPI communicatie (1 MHz)
├── Auto gain selection
└── Voltage sweep functies

test_dac_sweep.py           # Test programma met menu
├── Slow sweep (oscilloscoop verificatie)
├── Fast sweep (dynamische test)  
├── Step test (0%, 25%, 50%, 75%, 100%)
└── Manual voltage control

dac_startup.sh              # Hardware initialisatie script
├── Activate SPI controller (runtime PM)
└── Free GPIO 12 (unexport voor P9_20)
```

## Installatie op BeagleBone Black

### 1. Voorbereiding
```bash
# Update systeem
sudo apt-get update
sudo apt-get upgrade

# Installeer Python en pip
sudo apt-get install python3 python3-pip
```

### 2. Python Dependencies Installeren
```bash
# Upload requirements.txt naar BeagleBone
# Via SCP vanaf je computer:
# scp requirements.txt debian@<beaglebone-ip>:~/

# Op BeagleBone:
pip3 install -r requirements.txt
```

### 3. Hardware Initialisatie (BELANGRIJK!)
**De SPI controller en GPIO moeten bij elke boot worden geïnitialiseerd:**

```bash
# Maak dac_startup.sh executable
chmod +x dac_startup.sh

# Voer uit (vereist sudo):
sudo ./dac_startup.sh
```

Dit script doet:
1. Activeer SPI0 controller (runtime power management)
2. Free GPIO 12 voor gebruik als P9_20 CS pin
3. Configureer pin modes voor SPI

**Let op**: Dit moet na elke reboot opnieuw worden uitgevoerd!

### 4. Applicatie Uploaden
Upload alle bestanden naar de BeagleBone:
```bash
# Vanaf je computer via SCP:
scp mcp4822_driver.py test_dac_sweep.py dac_startup.sh requirements.txt debian@<beaglebone-ip>:~/autotester/
```

### 5. Hardware Testen
```bash
# Controleer SPI device
ls -la /dev/spidev*
# Moet /dev/spidev0.0 tonen

# Start test programma
python3 test_dac_sweep.py
```

## Gebruik

### 1. Hardware Initialisatie (na elke boot)
```bash
sudo ./dac_startup.sh
```

### 2. Test Programma Starten
```bash
python3 test_dac_sweep.py
```

### 3. Menu Navigatie

```
============================================================
TEST MENU
============================================================
1. Langzame Sweep (0V → VCC) - voor scope verificatie
2. Snelle Sweep (meerdere cycles) - dynamische test
3. Stap Test (0%, 25%, 50%, 75%, 100%)
4. Handmatige Spanning Controle
5. Reset naar 0V
q. Afsluiten
```

#### Optie 1: Langzame Sweep
- Sweep van 0V → 3.3V in 200 stappen
- 50ms delay per stap (10 seconden totaal)
- Ideaal voor oscilloscoop verificatie

#### Optie 2: Snelle Sweep
- 3 herhaalde sweeps
- 100 stappen per sweep
- 10ms delay per stap
- Voor dynamische test

#### Optie 3: Stap Test
- Vaste percentages: 0%, 25%, 50%, 75%, 100%
- 2 seconden per stap
- Verificatie van discrete spanningen

#### Optie 4: Handmatige Controle
```
Gewenste spanning (V): 2.5
✓ Ingesteld: 2.5000V (DAC: 2499/4095, gain=2)
```
Type 'q' om te stoppen

### 4. Direct Python API Gebruik

```python
from mcp4822_driver import MCP4822

# Initialiseer DAC (hardware Vref = 2.048V)
dac = MCP4822(vref=2.048)

# Stel spanning in (gain wordt automatisch gekozen)
dac.set_voltage('A', 1.5)    # Kanaal A op 1.5V (gain=1)
dac.set_voltage('B', 3.0)    # Kanaal B op 3.0V (gain=2 auto)

# Voltage sweep
dac.voltage_sweep('A', start_v=0, end_v=3.3, steps=100, delay=0.01)

# Cleanup
dac.cleanup()
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

## Technische Details

### Auto Gain Selection
De driver selecteert automatisch de juiste gain:
- **Gain=1** voor spanningen ≤ 2.048V (bereik 0-2.048V)
- **Gain=2** voor spanningen > 2.048V (bereik 0-4.096V)

### SPI Configuratie
- **Mode**: 0 (CPOL=0, CPHA=0)
- **Clock**: 1 MHz
- **Bits per word**: 8
- **Chip Select**: Software controlled (actief LOW)

### DAC Command Word Format
```
Bit 15: A/B Select (0=A, 1=B)
Bit 14: BUF (1=buffered Vref)
Bit 13: GA (0=2x gain, 1=1x gain)
Bit 12: SHDN (1=active output, 0=shutdown)
Bit 11-0: 12-bit DAC value (0-4095)
```

## Troubleshooting

### SPI Device niet gevonden
```bash
# Controleer SPI device:
ls -l /dev/spidev0.0

# Voer startup script uit:
sudo ./dac_startup.sh
```

### GPIO Permission Denied
Gebruik `sudo` voor het startup script:
```bash
sudo ./dac_startup.sh
```

### Geen output op DAC
1. Controleer of startup script is uitgevoerd (na elke boot!)
2. Controleer SPI clock op oscilloscoop (P9_22)
3. Controleer CS signaal op P9_20
4. Verifieer LDAC pulses op P9_12

### Import Errors
Controleer of Adafruit_BBIO geïnstalleerd is:
```bash
pip3 list | grep -i adafruit
# Moet tonen: Adafruit-BBIO

# Herinstalleer indien nodig:
pip3 install --upgrade -r requirements.txt
```

### Hardware Checklist
- ✓ MCP4822 voeding (2.7V - 5.5V, typisch 3.3V)
- ✓ Vref pin aangesloten (of interne 2.048V gebruikt)
- ✓ LDAC pin naar P9_12 (of naar GND voor auto-update)
- ✓ CS pin naar P9_20
- ✓ SDI (MOSI) naar P9_18
- ✓ SCK naar P9_22
- ✓ Alle ground pins verbonden

### BeagleBone Specifieke Issues

**SPI Controller Suspended** (meest voorkomende probleem):
```bash
# Activeer SPI controller:
sudo sh -c 'echo "on" > /sys/class/spi_master/spi0/device/power/control'

# Of gebruik het startup script:
sudo ./dac_startup.sh
```

**P9_20 GPIO Conflict**:
```bash
# Free GPIO 12:
sudo sh -c 'echo 12 > /sys/class/gpio/unexport'
```

## Bekende Beperkingen

- BeagleBone SPI0 controller gaat standaard in suspended mode → gebruik dac_startup.sh
- Na reboot moet dac_startup.sh opnieuw worden uitgevoerd
- Maximum praktische output: 3.3V (theoretisch 4.096V mogelijk)

## Licentie

Deze code is ontwikkeld voor gebruik met BeagleBone Black en MCP4822 DAC.

---

**Veel succes met je DAC project!** 🚀
