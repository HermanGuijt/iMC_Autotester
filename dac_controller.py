#!/usr/bin/env python3
"""
MCP4728 DAC Controller
4-channel 12-bit I2C DAC controller voor BeagleBone Black

Hardware configuratie:
- VOUTA + VOUTB -> Eerste OPA197 -> Voltage output (0-3.3V)
- VOUTC + VOUTD -> Tweede OPA197 -> Current output via IRLZ44N (4-20mA)
"""

import time
try:
    import board
    import busio
    import adafruit_mcp4728
except ImportError:
    print("Waarschuwing: Adafruit libraries niet gevonden. Test modus...")
    board = None


class DACController:
    """Controller voor MCP4728 4-channel DAC"""
    
    # MCP4728 heeft 12-bit resolutie (0-4095)
    DAC_MAX_VALUE = 4095
    VREF = 3.3  # Reference voltage (aangepast aan BeagleBone 3.3V)
    
    # Current loop configuratie (4-20mA)
    CURRENT_MIN = 4.0   # mA
    CURRENT_MAX = 20.0  # mA
    
    def __init__(self, i2c_bus=2, address=0x60):
        """
        Initialiseer MCP4728 DAC
        
        Args:
            i2c_bus: I2C bus nummer (default 2 voor P9_19/P9_20)
            address: I2C adres van MCP4728 (default 0x60)
        """
        self.i2c_bus = i2c_bus
        self.address = address
        
        try:
            if board:
                # Initialiseer I2C direct met bus 2 (P9_19 = SCL, P9_20 = SDA)
                # BeagleBone Black I2C-2 bus (/dev/i2c-2)
                from board import SCL, SDA
                i2c = busio.I2C(SCL, SDA)
                self.dac = adafruit_mcp4728.MCP4728(i2c, address=address)
                
                # Configureer voor interne reference (2.048V met gain=2 -> 4.096V)
                # MCP4728 gebruikt internal vref van 2.048V
                # Zet alle outputs op safe startup waarden
                self.dac.channel_a.value = 0  # Voltage output low
                self.dac.channel_b.value = 0
                self.dac.channel_c.value = self._current_to_dac(4.0)  # Min current
                self.dac.channel_d.value = self._current_to_dac(4.0)
                
                print(f"✓ MCP4728 DAC geïnitialiseerd op adres 0x{address:02X}")
            else:
                self.dac = None
                print("⚠ Test modus: DAC niet geïnitialiseerd")
                
        except Exception as e:
            print(f"✗ Fout bij initialiseren DAC: {e}")
            self.dac = None
    
    def _voltage_to_dac(self, voltage):
        """
        Converteer voltage (0-3.3V) naar DAC waarde (0-4095)
        
        Args:
            voltage: Gewenste voltage (0-3.3V)
            
        Returns:
            DAC waarde (0-4095)
        """
        if voltage < 0:
            voltage = 0
        elif voltage > self.VREF:
            voltage = self.VREF
        
        dac_value = int((voltage / self.VREF) * self.DAC_MAX_VALUE)
        return min(max(dac_value, 0), self.DAC_MAX_VALUE)
    
    def _current_to_dac(self, current_ma):
        """
        Converteer stroom (4-20mA) naar DAC waarde
        
        De opamp + MOSFET schakeling converteert de DAC spanning naar stroom.
        Lineaire mapping: 4mA = 0V, 20mA = 3.3V
        
        Args:
            current_ma: Gewenste stroom in mA (4-20)
            
        Returns:
            DAC waarde (0-4095)
        """
        if current_ma < self.CURRENT_MIN:
            current_ma = self.CURRENT_MIN
        elif current_ma > self.CURRENT_MAX:
            current_ma = self.CURRENT_MAX
        
        # Lineair schalen van 4-20mA naar 0-3.3V
        voltage_ratio = (current_ma - self.CURRENT_MIN) / (self.CURRENT_MAX - self.CURRENT_MIN)
        voltage = voltage_ratio * self.VREF
        
        dac_value = int((voltage / self.VREF) * self.DAC_MAX_VALUE)
        return min(max(dac_value, 0), self.DAC_MAX_VALUE)
    
    def set_voltage_output(self, voltage):
        """
        Stel spanningsuitgang in (0-3.3V)
        Gebruikt alleen Channel A voor voltage follower opamp
        Channel B wordt NIET gebruikt (opamp feedback via hardware)
        
        Args:
            voltage: Gewenste output voltage (0-3.3V)
        """
        if not self.dac:
            print(f"[TEST] Voltage zou ingesteld worden op: {voltage:.3f}V")
            return
        
        try:
            dac_value = self._voltage_to_dac(voltage)
            
            # VOUTA op + van opamp (channel A)
            # Opamp uitgang is via hardware feedback verbonden met - input
            self.dac.channel_a.value = dac_value
            
            # VOUTB NIET aansturen - laat dit open of via hardware feedback
            # self.dac.channel_b.value blijft zoals het was bij init (0)
            
        except Exception as e:
            print(f"✗ Fout bij instellen voltage: {e}")
    
    def set_current_output(self, current_ma):
        """
        Stel stroomuitgang in (4-20mA)
        Gebruikt Channel C en D voor differentiële opamp aansturing
        
        Args:
            current_ma: Gewenste output stroom in mA (4-20)
        """
        if not self.dac:
            print(f"[TEST] Stroom zou ingesteld worden op: {current_ma:.3f}mA")
            return
        
        try:
            dac_value = self._current_to_dac(current_ma)
            
            # VOUTC op + van opamp (channel C)
            self.dac.channel_c.value = dac_value
            
            # VOUTD op - van opamp (channel D)
            # Voor single-ended: zet D op 0
            self.dac.channel_d.value = 0
            
        except Exception as e:
            print(f"✗ Fout bij instellen stroom: {e}")
    
    def set_raw_channel(self, channel, value):
        """
        Stel een individueel kanaal in met ruwe DAC waarde
        
        Args:
            channel: Kanaal letter ('A', 'B', 'C', 'D')
            value: DAC waarde (0-4095)
        """
        if not self.dac:
            print(f"[TEST] Channel {channel} zou ingesteld worden op: {value}")
            return
        
        try:
            value = min(max(int(value), 0), self.DAC_MAX_VALUE)
            
            if channel.upper() == 'A':
                self.dac.channel_a.value = value
            elif channel.upper() == 'B':
                self.dac.channel_b.value = value
            elif channel.upper() == 'C':
                self.dac.channel_c.value = value
            elif channel.upper() == 'D':
                self.dac.channel_d.value = value
            else:
                print(f"✗ Ongeldig kanaal: {channel}")
                
        except Exception as e:
            print(f"✗ Fout bij instellen channel {channel}: {e}")
    
    def get_voltage_output(self):
        """
        Lees huidige voltage output waarde
        
        Returns:
            Huidige voltage in V
        """
        if not self.dac:
            return 0.0
        
        try:
            dac_value = self.dac.channel_a.value
            voltage = (dac_value / self.DAC_MAX_VALUE) * self.VREF
            return voltage
        except Exception as e:
            print(f"✗ Fout bij lezen voltage: {e}")
            return 0.0
    
    def get_current_output(self):
        """
        Lees huidige current output waarde
        
        Returns:
            Huidige stroom in mA
        """
        if not self.dac:
            return 4.0
        
        try:
            dac_value = self.dac.channel_c.value
            voltage = (dac_value / self.DAC_MAX_VALUE) * self.VREF
            voltage_ratio = voltage / self.VREF
            current_ma = self.CURRENT_MIN + voltage_ratio * (self.CURRENT_MAX - self.CURRENT_MIN)
            return current_ma
        except Exception as e:
            print(f"✗ Fout bij lezen stroom: {e}")
            return 4.0
    
    def reset_all(self):
        """Reset alle kanalen naar safe waarden"""
        if not self.dac:
            print("[TEST] DAC zou gereset worden")
            return
        
        try:
            self.set_voltage_output(0)
            self.set_current_output(4.0)
            print("✓ DAC gereset naar safe waarden")
        except Exception as e:
            print(f"✗ Fout bij reset DAC: {e}")


# Test functie
if __name__ == "__main__":
    print("MCP4728 DAC Controller Test")
    print("=" * 50)
    
    dac = DACController()
    
    print("\nTest voltage output (0-3.3V)...")
    for v in [0, 1.65, 3.3]:
        dac.set_voltage_output(v)
        print(f"  Set: {v}V, Read: {dac.get_voltage_output():.3f}V")
        time.sleep(0.5)
    
    print("\nTest current output (4-20mA)...")
    for i in [4, 12, 20]:
        dac.set_current_output(i)
        print(f"  Set: {i}mA, Read: {dac.get_current_output():.3f}mA")
        time.sleep(0.5)
    
    print("\nReset naar safe waarden...")
    dac.reset_all()
    
    print("\n✓ Test voltooid")
