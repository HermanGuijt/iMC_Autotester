#!/usr/bin/env python3
"""
ADS1115 ADC Controller
16-bit 4-channel I2C ADC voor BeagleBone Black
"""

import time
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
except ImportError:
    print("Waarschuwing: Adafruit ADS1x15 library niet gevonden. Test modus...")
    board = None
    ADS = None
    AnalogIn = None


class ADCController:
    """Controller voor ADS1115 16-bit ADC"""
    
    # ADS1115 configuratie
    GAIN = 1  # Gain 1 = +/- 4.096V range
    
    def __init__(self, i2c_bus=2, address=0x48):
        """
        Initialiseer ADS1115 ADC
        
        Args:
            i2c_bus: I2C bus nummer (default 2 voor P9_19/P9_20)
            address: I2C adres van ADS1115 (default 0x48)
        """
        self.i2c_bus = i2c_bus
        self.address = address
        self.adc = None
        self.channels = {}
        
        try:
            if board and ADS:
                # Initialiseer I2C (P9_19 = SCL, P9_20 = SDA)
                i2c = busio.I2C(board.SCL_1, board.SDA_1)
                self.adc = ADS.ADS1115(i2c, address=address, gain=self.GAIN)
                
                # Configureer alle 4 single-ended kanalen
                self.channels[0] = AnalogIn(self.adc, ADS.P0)
                self.channels[1] = AnalogIn(self.adc, ADS.P1)
                self.channels[2] = AnalogIn(self.adc, ADS.P2)
                self.channels[3] = AnalogIn(self.adc, ADS.P3)
                
                print(f"✓ ADS1115 ADC geïnitialiseerd op adres 0x{address:02X}")
            else:
                print("⚠ Test modus: ADC niet geïnitialiseerd")
                
        except Exception as e:
            print(f"✗ Fout bij initialiseren ADC: {e}")
            self.adc = None
    
    def read_channel(self, channel):
        """
        Lees één ADC kanaal
        
        Args:
            channel: Kanaal nummer (0-3)
            
        Returns:
            Spanning in Volt
        """
        if not self.adc:
            # Test modus - return dummy waarde
            return 1.23 + (channel * 0.1)
        
        try:
            if channel in self.channels:
                voltage = self.channels[channel].voltage
                return voltage
            else:
                print(f"✗ Ongeldig kanaal: {channel}")
                return 0.0
                
        except Exception as e:
            print(f"✗ Fout bij lezen kanaal {channel}: {e}")
            return 0.0
    
    def read_channel_raw(self, channel):
        """
        Lees ruwe ADC waarde
        
        Args:
            channel: Kanaal nummer (0-3)
            
        Returns:
            Ruwe ADC waarde (16-bit signed)
        """
        if not self.adc:
            return 1000 + (channel * 100)
        
        try:
            if channel in self.channels:
                raw_value = self.channels[channel].value
                return raw_value
            else:
                print(f"✗ Ongeldig kanaal: {channel}")
                return 0
                
        except Exception as e:
            print(f"✗ Fout bij lezen kanaal {channel}: {e}")
            return 0
    
    def read_all_channels(self):
        """
        Lees alle 4 kanalen
        
        Returns:
            List met 4 voltage waarden [CH0, CH1, CH2, CH3]
        """
        values = []
        for channel in range(4):
            values.append(self.read_channel(channel))
        return values
    
    def read_all_channels_raw(self):
        """
        Lees alle 4 kanalen (ruwe waarden)
        
        Returns:
            List met 4 ruwe ADC waarden
        """
        values = []
        for channel in range(4):
            values.append(self.read_channel_raw(channel))
        return values
    
    def read_differential(self, pos_channel, neg_channel):
        """
        Lees differentieel tussen twee kanalen
        
        Args:
            pos_channel: Positieve kanaal (0-3)
            neg_channel: Negatieve kanaal (0-3)
            
        Returns:
            Verschil spanning in Volt
        """
        if not self.adc:
            return 0.5
        
        try:
            from adafruit_ads1x15.analog_in import AnalogIn
            
            # Map kanaal nummers naar ADS pins
            pin_map = [ADS.P0, ADS.P1, ADS.P2, ADS.P3]
            
            if pos_channel < 4 and neg_channel < 4:
                diff_channel = AnalogIn(self.adc, 
                                       pin_map[pos_channel], 
                                       pin_map[neg_channel])
                return diff_channel.voltage
            else:
                print(f"✗ Ongeldige kanalen: {pos_channel}, {neg_channel}")
                return 0.0
                
        except Exception as e:
            print(f"✗ Fout bij differentieel lezen: {e}")
            return 0.0
    
    def continuous_read(self, channel, duration=10, sample_rate=128):
        """
        Lees een kanaal continu voor een bepaalde tijd
        
        Args:
            channel: Kanaal nummer (0-3)
            duration: Leestijd in seconden
            sample_rate: Samples per seconde (max 860 voor ADS1115)
            
        Returns:
            List met voltage samples
        """
        if not self.adc:
            print("[TEST] Continuous read zou uitgevoerd worden")
            return [1.0] * int(duration * sample_rate)
        
        samples = []
        interval = 1.0 / sample_rate
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < duration:
                voltage = self.read_channel(channel)
                samples.append(voltage)
                time.sleep(interval)
                
            return samples
            
        except KeyboardInterrupt:
            print("\nContinuous read onderbroken")
            return samples
        except Exception as e:
            print(f"✗ Fout bij continuous read: {e}")
            return samples
    
    def monitor_channels(self, update_interval=0.5, callback=None):
        """
        Monitor alle kanalen en roep callback functie aan bij elke update
        
        Args:
            update_interval: Update interval in seconden
            callback: Functie die aangeroepen wordt met channel data
                     callback(channel_values: list) -> bool (True = continue, False = stop)
        """
        try:
            while True:
                values = self.read_all_channels()
                
                if callback:
                    if not callback(values):
                        break
                else:
                    # Default: print naar console
                    print(f"\rCH0:{values[0]:6.3f}V  CH1:{values[1]:6.3f}V  "
                          f"CH2:{values[2]:6.3f}V  CH3:{values[3]:6.3f}V", end="")
                
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring gestopt")
        except Exception as e:
            print(f"\n✗ Fout bij monitoring: {e}")


# Test functie
if __name__ == "__main__":
    print("ADS1115 ADC Controller Test")
    print("=" * 50)
    
    adc = ADCController()
    
    print("\nLees alle kanalen (5 samples)...")
    for i in range(5):
        values = adc.read_all_channels()
        print(f"Sample {i+1}: CH0={values[0]:.3f}V  CH1={values[1]:.3f}V  "
              f"CH2={values[2]:.3f}V  CH3={values[3]:.3f}V")
        time.sleep(0.5)
    
    print("\nLees individuele kanalen...")
    for ch in range(4):
        voltage = adc.read_channel(ch)
        raw = adc.read_channel_raw(ch)
        print(f"  CH{ch}: {voltage:.4f}V (raw: {raw})")
    
    print("\nTest differentiële meting (CH0-CH1)...")
    diff = adc.read_differential(0, 1)
    print(f"  Verschil: {diff:.4f}V")
    
    print("\n✓ Test voltooid")
    print("\nDruk CTRL+C om continuous monitoring te starten/stoppen")
    
    try:
        input("Druk Enter voor continuous monitoring...")
        print("\nContinuous monitoring (CTRL+C om te stoppen):")
        adc.monitor_channels(update_interval=0.2)
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring gestopt")
