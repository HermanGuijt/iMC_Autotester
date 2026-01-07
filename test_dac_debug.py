#!/usr/bin/env python3
"""
DAC Debug - Test VOUTA en VOUTB apart
"""
import time
from dac_controller import DACController

print("=" * 60)
print(" DAC Debug - VOUTA en VOUTB Test")
print("=" * 60)
print()

try:
    dac = DACController()
    
    print("Hardware configuratie:")
    print("  VOUTA (Channel A) -> OPA197 pin 3 (+)")
    print("  VOUTB (Channel B) -> OPA197 pin 2 (-)")
    print()
    
    # Test 1: Alleen Channel A variëren, B op 0
    print("Test 1: Channel A variëren (0-3.3V), Channel B = 0V")
    for v in [0, 1.0, 2.0, 3.0]:
        print(f"  VOUTA = {v}V, VOUTB = 0V")
        dac.set_raw_channel('A', dac._voltage_to_dac(v))
        dac.set_raw_channel('B', 0)
        print(f"  -> Meet spanning aan opamp uitgang")
        time.sleep(3)
    
    # Test 2: Beide kanalen op zelfde spanning
    print("\nTest 2: Beide kanalen op zelfde spanning")
    for v in [0, 1.65, 3.3]:
        print(f"  VOUTA = {v}V, VOUTB = {v}V")
        dac.set_raw_channel('A', dac._voltage_to_dac(v))
        dac.set_raw_channel('B', dac._voltage_to_dac(v))
        print(f"  -> Meet spanning aan opamp uitgang")
        time.sleep(3)
    
    # Test 3: Alleen Channel B variëren, A op 0
    print("\nTest 3: Channel B variëren (0-3.3V), Channel A = 0V")
    for v in [0, 1.0, 2.0, 3.0]:
        print(f"  VOUTA = 0V, VOUTB = {v}V")
        dac.set_raw_channel('A', 0)
        dac.set_raw_channel('B', dac._voltage_to_dac(v))
        print(f"  -> Meet spanning aan opamp uitgang")
        time.sleep(3)
    
    # Reset
    print("\nReset beide kanalen naar 0V...")
    dac.set_raw_channel('A', 0)
    dac.set_raw_channel('B', 0)
    
    print("\n✓ Debug test voltooid!")
    print("\nVertel me:")
    print("  - Verandert de output als je VOUTA varieert?")
    print("  - Verandert de output als je VOUTB varieert?")
    print("  - Wat meet je in elk scenario?")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
