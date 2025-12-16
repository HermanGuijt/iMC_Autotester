#!/bin/bash
# Installatie script voor BeagleBone Black
# Gebruik: sudo ./install.sh

echo "=========================================="
echo " BeagleBone Black Controller Installatie"
echo "=========================================="
echo ""

# Check of script als root wordt uitgevoerd
if [ "$EUID" -ne 0 ]; then 
    echo "✗ Voer dit script uit als root: sudo ./install.sh"
    exit 1
fi

echo "1. Systeem updaten..."
apt-get update

echo ""
echo "2. Python dependencies installeren..."
pip3 install -r requirements.txt

echo ""
echo "3. I2C configuratie controleren..."
if [ -e "/dev/i2c-2" ]; then
    echo "✓ I2C-2 is actief"
else
    echo "✗ I2C-2 niet gevonden!"
    echo "  Activeer I2C2 in /boot/uEnv.txt en herstart"
    echo "  Voeg toe: dtb_overlay=/lib/firmware/BB-I2C2-00A0.dtbo"
fi

echo ""
echo "4. I2C devices scannen..."
i2cdetect -y -r 2

echo ""
echo "5. Bestandspermissies instellen..."
chmod +x beaglebone_controller.py
chmod +x dac_controller.py
chmod +x adc_controller.py
chmod +x relay_controller.py
chmod +x waveform_generator.py

echo ""
echo "=========================================="
echo " ✓ Installatie voltooid!"
echo "=========================================="
echo ""
echo "Start de applicatie met:"
echo "  sudo python3 beaglebone_controller.py"
echo ""
echo "Test individuele modules met:"
echo "  sudo python3 dac_controller.py"
echo "  sudo python3 adc_controller.py"
echo "  sudo python3 relay_controller.py"
echo "  python3 waveform_generator.py"
echo ""
