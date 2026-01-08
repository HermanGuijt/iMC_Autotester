#!/bin/bash
# DAC/Potmeter Startup - activeer SPI en fix GPIO
# Run dit VOOR je DAC/MCP4131 applicatie

echo "Activeer SPI voor DAC en digitale potmeter..."

# 1. SPI power on
echo 'on' | sudo tee /sys/class/spi_master/spi0/device/power/control > /dev/null

# 2. Maak P9_20 vrij voor DAC CS (GPIO 12)
sudo sh -c 'echo 12 > /sys/class/gpio/unexport' 2>/dev/null

# 3. Maak P9_24 vrij voor MCP4131 CS (GPIO 15)
sudo sh -c 'echo 15 > /sys/class/gpio/unexport' 2>/dev/null

# 4. Configureer pins
sudo config-pin P9_20 gpio    # DAC CS (manual control)
sudo config-pin P9_12 gpio    # DAC LDAC
sudo config-pin P9_24 gpio    # MCP4131 CS (manual control - spi_cs not available!)

echo "✓ SPI ready voor DAC en MCP4131"
