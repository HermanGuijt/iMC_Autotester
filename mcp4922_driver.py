#!/usr/bin/env python3
"""
MCP4822 DAC Driver voor BeagleBone Black
12-bit Dual Channel DAC met SPI interface

Hardware connecties:
- CS:   P9_20 (GPIO_12) - Software CS (moet unexport worden!)
- SCK:  P9_22 (SPI0_SCLK)
- SDI:  P9_18 (SPI0_D1)
- LDAC: P9_12 (GPIO_60)

BELANGRIJK: Gebruik Python 3!
"""

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.SPI as SPI
import time
import subprocess


class MCP4822:
    # Command bits
    CHANNEL_A = 0x0000
    CHANNEL_B = 0x8000
    GAIN_1X = 0x2000
    GAIN_2X = 0x0000
    SHUTDOWN = 0x0000
    ACTIVE = 0x1000
    
    def __init__(self, spi_bus=0, spi_device=0, cs_pin="P9_20", ldac_pin="P9_12", vref=2.048):
        """
        Initialiseer MCP4822 DAC
        
        Args:
            spi_bus: SPI bus nummer (0 of 1)
            spi_device: SPI device nummer (0 of 1)
            cs_pin: Chip Select pin (standaard "P9_20")
            ldac_pin: LDAC pin voor latching output (bijv. "P9_12")
            vref: Referentie spanning in Volt (2.048V voor MCP4822)
        """
        self.vref = vref
        self.cs_pin = cs_pin
        self.ldac_pin = ldac_pin
        self.max_value = 4095  # 12-bit resolutie
        
        # Configureer pin modes EERST
        print("Configureer SPI pins...")
        self._setup_pin_modes(spi_bus)
        
        # Setup GPIO pins
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.ldac_pin, GPIO.OUT)
        
        # CS high (inactive)
        GPIO.output(self.cs_pin, GPIO.HIGH)
        # LDAC high (no auto-update)
        GPIO.output(self.ldac_pin, GPIO.HIGH)
        
        # Setup SPI
        self.spi = SPI.SPI(spi_bus, spi_device)
        self.spi.mode = 0  # Mode 0 (CPOL=0, CPHA=0)
        self.spi.msh = 1000000  # 1 MHz clock
        self.spi.bpw = 8  # 8 bits per word
        
        print(f"MCP4822 geïnitialiseerd op SPI{spi_bus}.{spi_device}")
        print(f"CS: {cs_pin}, LDAC: {ldac_pin}, Vref: {vref}V")
    
    def _setup_pin_modes(self, spi_bus):
        """Configureer pin modes voor SPI"""
        try:
            # Bepaal welke pins voor deze SPI bus
            if spi_bus == 0:
                pins = {
                    'P9_17': 'spi_cs',    # SPI0_CS0
                    'P9_18': 'spi',       # SPI0_D1 (MOSI)
                    'P9_21': 'spi',       # SPI0_D0 (MISO)
                    'P9_22': 'spi_sclk',  # SPI0_SCLK
                }
            elif spi_bus == 1:
                pins = {
                    'P9_28': 'spi_cs',    # SPI1_CS0
                    'P9_29': 'spi',       # SPI1_D1
                    'P9_30': 'spi',       # SPI1_D0
                    'P9_31': 'spi_sclk',  # SPI1_SCLK
                }
            else:
                print(f"  Waarschuwing: Onbekende SPI bus {spi_bus}")
                return
            
            # Configureer elke pin
            for pin, mode in pins.items():
                try:
                    result = subprocess.run(
                        ['config-pin', pin, mode],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        print(f"  ✓ {pin} → {mode}")
                    else:
                        print(f"  ! {pin} configuratie failed: {result.stderr.strip()}")
                except FileNotFoundError:
                    print("  ! config-pin niet gevonden - handmatig configureren!")
                    break
                except Exception as e:
                    print(f"  ! Fout bij {pin}: {e}")
            
            # Wacht even voor pin stabilisatie
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  Waarschuwing: Pin configuratie failed: {e}")
            print("  SPI pins moeten mogelijk handmatig geconfigureerd worden")
    
    def write_dac(self, channel, value, gain=1):
        """
        Schrijf waarde naar DAC kanaal
        
        Args:
            channel: 'A' of 'B'
            value: 12-bit waarde (0-4095)
            gain: Gain setting (1 of 2)
        """
        # Valideer input
        if value < 0:
            value = 0
        elif value > self.max_value:
            value = self.max_value
        
        value = int(value)
        
        # Bouw command word
        command = self.ACTIVE  # DAC actief
        
        # Channel select
        if channel.upper() == 'B':
            command |= self.CHANNEL_B
        else:
            command |= self.CHANNEL_A
        
        # Gain select (1x of 2x)
        if gain == 1:
            command |= self.GAIN_1X
        else:
            command |= self.GAIN_2X
        
        # Data (12-bit)
        command |= (value & 0x0FFF)
        
        # Splits in 2 bytes (MSB first)
        byte1 = (command >> 8) & 0xFF
        byte2 = command & 0xFF
        
        # CS low
        GPIO.output(self.cs_pin, GPIO.LOW)
        time.sleep(0.000001)  # 1µs delay
        
        # Verstuur data via SPI
        self.spi.writebytes([byte1, byte2])
        
        # CS high
        time.sleep(0.000001)  # 1µs delay
        GPIO.output(self.cs_pin, GPIO.HIGH)
        
        # LDAC pulse om output te updaten
        time.sleep(0.000001)
        GPIO.output(self.ldac_pin, GPIO.LOW)
        time.sleep(0.000001)  # 1µs pulse
        GPIO.output(self.ldac_pin, GPIO.HIGH)
    
    def set_voltage(self, channel, voltage, gain=None):
        """
        Stel spanning in op DAC kanaal
        
        Args:
            channel: 'A' of 'B'
            voltage: Gewenste spanning in Volt
            gain: Gain setting (1 of 2), None = auto-select
        """
        # Auto-select gain als niet gespecificeerd
        if gain is None:
            gain = 2 if voltage > self.vref else 1
        
        # Bereken max output spanning
        max_voltage = self.vref * gain
        
        # Valideer voltage
        if voltage < 0:
            voltage = 0
        elif voltage > max_voltage:
            voltage = max_voltage
        
        # Bereken DAC waarde
        dac_value = int((voltage / max_voltage) * self.max_value)
        
        # Schrijf naar DAC
        self.write_dac(channel, dac_value, gain)
        
        return dac_value
    
    def voltage_sweep(self, channel, start_v, end_v, steps=100, delay=0.01, gain=None):
        """
        Maak een sweep van start naar eind spanning
        
        Args:
            channel: 'A' of 'B'
            start_v: Start spanning in Volt
            end_v: Eind spanning in Volt
            steps: Aantal stappen
            delay: Delay tussen stappen in seconden
            gain: Gain setting (1 of 2), None = auto-select
        """
        # Auto-select gain voor het bereik
        if gain is None:
            gain = 2 if end_v > self.vref else 1
        
        max_voltage = self.vref * gain
        step_size = (end_v - start_v) / steps
        
        print(f"Sweep van {start_v}V naar {end_v}V in {steps} stappen (gain={gain}, max={max_voltage}V)")
        print(f"Step size: {step_size*1000:.2f}mV, delay: {delay*1000:.1f}ms")
        
        for i in range(steps + 1):
            voltage = start_v + (i * step_size)
            dac_value = self.set_voltage(channel, voltage, gain)
            
            if i % 10 == 0:  # Print elke 10 stappen
                print(f"Step {i}/{steps}: {voltage:.3f}V (DAC value: {dac_value})")
            
            time.sleep(delay)
    
    def cleanup(self):
        """
        Cleanup GPIO resources
        """
        # Zet outputs op 0V
        self.set_voltage('A', 0)
        self.set_voltage('B', 0)
        
        # Cleanup SPI
        self.spi.close()
        
        # Cleanup GPIO
        GPIO.cleanup()
        
        print("MCP4822 cleanup voltooid")


if __name__ == "__main__":
    # Test code
    print("MCP4822 Driver Test")
    print("=" * 50)
    
    try:
        # Initialiseer DAC met 2.048V referentie (MCP4822)
        dac = MCP4822(vref=2.048)
        
        # Test enkele spanningen
        print("\nTest enkele spanningen op kanaal A:")
        test_voltages = [0.0, 0.5, 1.0, 1.5, 2.0, 2.048]
        
        for v in test_voltages:
            dac_val = dac.set_voltage('A', v)
            print(f"  {v}V → DAC value: {dac_val}")
            time.sleep(0.5)
        
        print("\nDruk op Ctrl+C om te stoppen")
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\n\nTest gestopt door gebruiker")
    except Exception as e:
        print(f"\nFout: {e}")
    finally:
        dac.cleanup()
        print("Programma beëindigd")
