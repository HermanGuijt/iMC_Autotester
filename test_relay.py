#!/usr/bin/env python3
"""
Relay Test Script - 20Hz voor 60 seconden
"""
import time
from relay_controller import RelayController

print("=" * 60)
print(" Relay Test - 20Hz voor 60 seconden")
print("=" * 60)
print()

try:
    # Initialiseer relay
    relay = RelayController("P9_12")
    
    print("Start relay op 20Hz...")
    relay.start_switching(20)
    
    # Wacht 60 seconden met voortgang indicator
    for i in range(60):
        print(f"\rTijd verstreken: {i+1}/60 seconden", end="", flush=True)
        time.sleep(1)
    
    print("\n\nStop relay...")
    relay.stop()
    
    print("✓ Test voltooid!")
    
except KeyboardInterrupt:
    print("\n\nTest onderbroken door gebruiker")
    relay.stop()
except Exception as e:
    print(f"\n✗ Fout: {e}")
    
finally:
    try:
        relay.cleanup()
    except:
        pass
