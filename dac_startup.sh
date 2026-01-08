#!/bin/bash
# DAC Startup - activeer SPI en fix GPIO
# Run dit VOOR je DAC applicatie

echo "Activeer SPI voor DAC..."

# 1. SPI power on
echo 'on' | sudo tee /sys/class/spi_master/spi0/device/power/control > /dev/null

# 2. Maak P9_20 vrij voor GPIO CS
sudo sh -c 'echo 12 > /sys/class/gpio/unexport' 2>/dev/null

# 3. Configureer pins
sudo config-pin P9_20 gpio
sudo config-pin P9_12 gpio

echo "✓ SPI ready voor DAC"
