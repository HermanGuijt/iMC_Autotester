#!/bin/bash
# Installatie script voor BeagleBone Black MCP4822 DAC
# Gebruik: ./install.sh (geen sudo nodig)

echo "=========================================="
echo " BeagleBone MCP4822 DAC Installatie"
echo "=========================================="
echo ""

echo "1. Python dependencies installeren..."
pip3 install -r requirements.txt --user

echo ""
echo "2. SPI configuratie controleren..."
if [ -e "/dev/spidev0.0" ]; then
    echo "✓ SPI0 device gevonden"
else
    echo "⚠ SPI0 device niet gevonden"
    echo "  SPI controller moet mogelijk geactiveerd worden"
fi

echo ""
echo "3. Bestandspermissies instellen..."
chmod +x dac_startup.sh
chmod +x test_dac_sweep.py

echo ""
echo "=========================================="
echo " ✓ Installatie voltooid!"
echo "=========================================="
echo ""
echo "BELANGRIJK: Voer na elke boot uit:"
echo "  sudo ./dac_startup.sh"
echo ""
echo "Start de applicatie met:"
echo "  python3 test_dac_sweep.py"
echo ""
