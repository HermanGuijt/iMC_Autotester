#!/usr/bin/env python3
"""
Reed Contact Simulator - 60Hz
Simuleert flow meter reed contact
"""
import time
from relay_controller import RelayController

print("=" * 60)
print(" Reed Contact Simulator - 60Hz")
print("=" * 60)
print()

try:
    relay = RelayController("P9_12")
    
    # Configureer frequentie
    frequency = 60  # Hz
    duration = 60   # seconden (pas aan naar wens)
    
    print(f"Start simulatie:")
    print(f"  Frequentie: {frequency} Hz")
    print(f"  Duur: {duration} seconden")
    print(f"  Pulsen totaal: {frequency * duration}")
    print()
    print("Druk CTRL+C om te stoppen")
    print()
    
    relay.start_switching(frequency)
    
    # Timer met voortgang
    start_time = time.time()
    try:
        while True:
            elapsed = time.time() - start_time
            pulses = int(elapsed * frequency)
            
            if duration and elapsed >= duration:
                break
                
            print(f"\rTijd: {elapsed:.1f}s  Pulsen: {pulses}  ", end="", flush=True)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\nGestopt door gebruiker")
    
    print("\n\nStop relay...")
    relay.stop()
    
    total_pulses = int((time.time() - start_time) * frequency)
    print(f"✓ Simulatie voltooid - Totaal {total_pulses} pulsen")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        relay.cleanup()
    except:
        pass
