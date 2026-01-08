#!/usr/bin/env python3
"""
MCP4131 Digital Potentiometer Driver voor BeagleBone Black
7-bit resolutie (129 stappen: 0-128)
10kΩ weerstand
SPI interface

Hardware:
- BeagleBone Black P9 header
- MCP4131-103/P (10kΩ)
- SPI Mode 0 (CPOL=0, CPHA=0)
"""

import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.SPI as SPI


class MCP4131:
    """
    MCP4131 Digital Potentiometer driver
    
    Args:
        spi_bus: SPI bus nummer (0 of 1)
        spi_device: SPI device nummer (0 of 1)
        cs_pin: Chip Select pin (bijv. "P9_24")
    """
    
    def __init__(self, spi_bus=0, spi_device=0, cs_pin="P9_24"):
        """
        Initialiseer MCP4131 digitale potmeter
        
        Args:
            spi_bus: SPI bus (0 of 1)
            spi_device: SPI device (0 of 1)
            cs_pin: GPIO pin voor Chip Select
        """
        self.cs_pin = cs_pin
        self.max_value = 128  # 7-bit resolutie (0-128)
        self.resistance = 10000  # 10kΩ
        
        # Setup GPIO CS pin
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.output(self.cs_pin, GPIO.HIGH)  # CS inactive
        
        # Setup SPI
        self.spi = SPI.SPI(spi_bus, spi_device)
        self.spi.mode = 0  # Mode 0 (CPOL=0, CPHA=0)
        self.spi.msh = 1000000  # 1 MHz (max 10 MHz)
        self.spi.bpw = 8  # 8 bits per word
        
        print(f"MCP4131 geïnitialiseerd op SPI{spi_bus}.{spi_device}")
        print(f"CS: {cs_pin}, Resistance: {self.resistance}Ω, Steps: 0-{self.max_value}")
    
    def _send_command(self, cmd_byte, data_byte):
        """
        Verstuur 16-bit commando naar MCP4131
        
        Args:
            cmd_byte: Command byte (bits 15-8)
            data_byte: Data byte (bits 7-0)
        """
        # CS low
        GPIO.output(self.cs_pin, GPIO.LOW)
        time.sleep(0.000001)  # 1µs delay
        
        # Verstuur 2 bytes
        self.spi.writebytes([cmd_byte, data_byte])
        
        # CS high
        time.sleep(0.000001)
        GPIO.output(self.cs_pin, GPIO.HIGH)
    
    def set_wiper(self, value):
        """
        Stel wiper positie in (0-128)
        
        Args:
            value: Wiper positie (0-128)
                  0 = minimale weerstand (wiper naar B)
                  128 = maximale weerstand (wiper naar A)
        
        Returns:
            Actuele ingestelde waarde
        """
        # Valideer waarde
        if value < 0:
            value = 0
        elif value > self.max_value:
            value = self.max_value
        
        # MCP4131 commando format (16-bit):
        # Bits 15-12: 0000 (Address = wiper 0)
        # Bits 11-10: 00 (Command = write)
        # Bits 9-8: D8-D7 (upper data bits, always 0 for values 0-128)
        # Bits 7-1: D6-D0 (7-bit data value, left-aligned!)
        # Bit 0: don't care
        
        # Data moet left-aligned zijn in 9-bit veld
        # Voor waarden 0-128: shift left by 1
        cmd_byte = 0x00  # Address 0, Write command
        data_byte = (value << 1) & 0xFF  # Shift left, mask to 8 bits
        
        self._send_command(cmd_byte, data_byte)
        
        return value
    
    def set_resistance(self, resistance_ohms):
        """
        Stel weerstand in (0 - 10000Ω)
        
        Args:
            resistance_ohms: Gewenste weerstand in Ohm
        
        Returns:
            Actuele weerstand in Ohm
        """
        # Bereken wiper waarde uit gewenste weerstand
        # R_total = 10kΩ, R_wiper = (value/128) * 10kΩ
        value = int((resistance_ohms / self.resistance) * self.max_value)
        
        # Stel wiper in
        actual_value = self.set_wiper(value)
        
        # Bereken actuele weerstand
        actual_resistance = (actual_value / self.max_value) * self.resistance
        
        return actual_resistance
    
    def set_percentage(self, percentage):
        """
        Stel wiper positie in als percentage (0-100%)
        
        Args:
            percentage: Percentage (0-100)
                       0% = minimale weerstand
                       100% = maximale weerstand
        
        Returns:
            Actuele percentage
        """
        # Bereken wiper waarde
        value = int((percentage / 100.0) * self.max_value)
        
        # Stel wiper in
        actual_value = self.set_wiper(value)
        
        # Bereken actueel percentage
        actual_percentage = (actual_value / self.max_value) * 100
        
        return actual_percentage
    
    def sweep(self, start=0, end=128, steps=10, delay=0.1):
        """
        Maak een sweep van start naar eind waarde
        
        Args:
            start: Start waarde (0-128)
            end: Eind waarde (0-128)
            steps: Aantal stappen
            delay: Delay tussen stappen in seconden
        """
        step_size = (end - start) / steps
        
        print(f"Sweep van {start} naar {end} in {steps} stappen")
        print(f"Step size: {step_size:.2f}, delay: {delay*1000:.1f}ms")
        
        for i in range(steps + 1):
            value = int(start + (i * step_size))
            self.set_wiper(value)
            resistance = (value / self.max_value) * self.resistance
            
            if i % max(1, steps // 10) == 0:  # Print elke 10%
                print(f"Step {i}/{steps}: value={value}, R={resistance:.0f}Ω")
            
            time.sleep(delay)
    
    def cleanup(self):
        """
        Cleanup: zet wiper op middenstand
        """
        print("\nReset wiper naar middenstand (50%)...")
        self.set_wiper(self.max_value // 2)
        print("Cleanup voltooid")


if __name__ == "__main__":
    # Test code
    print("MCP4131 Driver Test")
    print("=" * 50)
    
    try:
        # Initialiseer digitale potmeter
        pot = MCP4131(spi_bus=0, spi_device=0, cs_pin="P9_24")
        
        # Test enkele waarden
        print("\nTest enkele wiper waarden:")
        test_values = [0, 32, 64, 96, 128]
        
        for val in test_values:
            pot.set_wiper(val)
            resistance = (val / 128) * 10000
            percentage = (val / 128) * 100
            print(f"  Wiper: {val:3d} → R={resistance:5.0f}Ω ({percentage:3.0f}%)")
            time.sleep(0.5)
        
        print("\nTest percentage mode:")
        for pct in [0, 25, 50, 75, 100]:
            actual_pct = pot.set_percentage(pct)
            print(f"  {pct}% → {actual_pct:.1f}%")
            time.sleep(0.5)
        
        print("\nDruk op Ctrl+C om te stoppen")
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\n\nProgramma gestopt")
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pot.cleanup()
