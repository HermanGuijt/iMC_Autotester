#!/usr/bin/env python3
"""
Relay Controller voor BeagleBone Black
GPIO control voor relay met instelbare schakelfrequentie (1-60Hz)
"""

import time
import threading

try:
    import Adafruit_BBIO.GPIO as GPIO
except ImportError:
    print("Waarschuwing: Adafruit_BBIO niet gevonden. Test modus...")
    GPIO = None


class RelayController:
    """Controller voor relay met frequentie instelbaar schakelen"""
    
    def __init__(self, gpio_pin="P9_12"):
        """
        Initialiseer relay controller
        
        Args:
            gpio_pin: BeagleBone GPIO pin (default P9_12)
        """
        self.gpio_pin = gpio_pin
        self.is_switching = False
        self.switch_thread = None
        self.current_frequency = 0
        self.state = False
        
        try:
            if GPIO:
                # Configureer GPIO pin als output
                GPIO.setup(self.gpio_pin, GPIO.OUT)
                GPIO.output(self.gpio_pin, GPIO.LOW)
                print(f"✓ Relay geïnitialiseerd op pin {self.gpio_pin}")
            else:
                print("⚠ Test modus: GPIO niet geïnitialiseerd")
                
        except Exception as e:
            print(f"✗ Fout bij initialiseren relay: {e}")
    
    def set_state(self, state):
        """
        Zet relay aan of uit (constant)
        
        Args:
            state: True = AAN, False = UIT
        """
        self.stop()  # Stop eventueel lopend schakelen
        self.state = state
        
        if GPIO:
            try:
                GPIO.output(self.gpio_pin, GPIO.HIGH if state else GPIO.LOW)
            except Exception as e:
                print(f"✗ Fout bij zetten relay state: {e}")
        else:
            print(f"[TEST] Relay zou {'AAN' if state else 'UIT'} gezet worden")
    
    def start_switching(self, frequency):
        """
        Start het schakelen van de relay met opgegeven frequentie
        
        Args:
            frequency: Schakelfrequentie in Hz (0.01-60)
                      Bijv: 0.5 Hz = 1 puls per 2 seconden
                            0.1 Hz = 1 puls per 10 seconden
        """
        # Valideer frequentie
        if frequency < 0.01 or frequency > 60:
            print(f"✗ Frequentie moet tussen 0.01 en 60 Hz zijn (gegeven: {frequency})")
            return False
        
        # Stop eventueel lopend schakelen
        self.stop()
        
        self.current_frequency = frequency
        self.is_switching = True
        
        # Start schakel thread
        self.switch_thread = threading.Thread(target=self._switch_loop, 
                                              args=(frequency,), 
                                              daemon=True)
        self.switch_thread.start()
        
        print(f"✓ Relay schakelt op {frequency}Hz")
        return True
    
    def _switch_loop(self, frequency):
        """
        Thread functie voor het schakelen van de relay
        
        Args:
            frequency: Schakelfrequentie in Hz
        """
        # Bereken half-periode (tijd voor AAN of UIT)
        half_period = 1.0 / (2.0 * frequency)
        
        try:
            while self.is_switching:
                # Zet relay AAN
                self.state = True
                if GPIO:
                    GPIO.output(self.gpio_pin, GPIO.HIGH)
                
                # Wacht halve periode
                time.sleep(half_period)
                
                if not self.is_switching:
                    break
                
                # Zet relay UIT
                self.state = False
                if GPIO:
                    GPIO.output(self.gpio_pin, GPIO.LOW)
                
                # Wacht halve periode
                time.sleep(half_period)
                
        except Exception as e:
            print(f"✗ Fout in schakel loop: {e}")
            self.is_switching = False
    
    def stop(self):
        """Stop het schakelen en zet relay UIT"""
        if self.is_switching:
            self.is_switching = False
            
            # Wacht tot thread klaar is
            if self.switch_thread and self.switch_thread.is_alive():
                self.switch_thread.join(timeout=1.0)
            
            self.current_frequency = 0
        
        # Zet relay uit
        self.state = False
        if GPIO:
            try:
                GPIO.output(self.gpio_pin, GPIO.LOW)
            except Exception as e:
                print(f"✗ Fout bij stoppen relay: {e}")
        else:
            print("[TEST] Relay zou UIT gezet worden")
    
    def get_state(self):
        """
        Krijg huidige relay status
        
        Returns:
            dict met 'state', 'switching', en 'frequency'
        """
        return {
            'state': self.state,
            'switching': self.is_switching,
            'frequency': self.current_frequency
        }
    
    def pulse(self, duration=0.1):
        """
        Geef een enkele puls
        
        Args:
            duration: Puls duur in seconden
        """
        if self.is_switching:
            print("✗ Kan geen puls geven tijdens schakelen")
            return
        
        try:
            if GPIO:
                GPIO.output(self.gpio_pin, GPIO.HIGH)
                time.sleep(duration)
                GPIO.output(self.gpio_pin, GPIO.LOW)
            else:
                print(f"[TEST] Relay puls van {duration}s zou gegeven worden")
                
        except Exception as e:
            print(f"✗ Fout bij relay puls: {e}")
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        self.stop()
        if GPIO:
            try:
                GPIO.cleanup(self.gpio_pin)
                print("✓ Relay GPIO cleanup voltooid")
            except Exception as e:
                print(f"✗ Fout bij cleanup: {e}")


# Test functie
if __name__ == "__main__":
    print("Relay Controller Test")
    print("=" * 50)
    
    relay = RelayController("P9_12")
    
    try:
        # Test constant AAN/UIT
        print("\nTest 1: Relay constant AAN/UIT")
        print("  Relay AAN...")
        relay.set_state(True)
        time.sleep(2)
        
        print("  Relay UIT...")
        relay.set_state(False)
        time.sleep(2)
        
        # Test enkele puls
        print("\nTest 2: Enkele puls (0.5s)")
        relay.pulse(0.5)
        time.sleep(1)
        
        # Test lage frequentie
        print("\nTest 3: Schakelen op 1 Hz (5 seconden)")
        relay.start_switching(1)
        time.sleep(5)
        relay.stop()
        print("  Gestopt")
        time.sleep(1)
        
        # Test medium frequentie
        print("\nTest 4: Schakelen op 5 Hz (5 seconden)")
        relay.start_switching(5)
        time.sleep(5)
        relay.stop()
        print("  Gestopt")
        time.sleep(1)
        
        # Test hoge frequentie
        print("\nTest 5: Schakelen op 30 Hz (5 seconden)")
        relay.start_switching(30)
        time.sleep(5)
        relay.stop()
        print("  Gestopt")
        
        # Test status
        print("\nTest 6: Status opvragen")
        status = relay.get_state()
        print(f"  State: {status['state']}")
        print(f"  Switching: {status['switching']}")
        print(f"  Frequency: {status['frequency']} Hz")
        
        print("\n✓ Alle tests voltooid")
        
    except KeyboardInterrupt:
        print("\n\nTest onderbroken")
    finally:
        relay.cleanup()
