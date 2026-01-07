#!/usr/bin/env python3
"""
Current Output Test - 4-20mA simulatie
"""
import time
from dac_controller import DACController

print("=" * 60)
print(" Current Output Test (4-20mA)")
print("=" * 60)
print()

try:
    dac = DACController()
    
    # Test 1: Constante stromen
    print("Test 1: Constante stromen")
    test_currents = [4, 8, 12, 16, 20]
    for i in test_currents:
        print(f"  Instellen: {i}mA")
        dac.set_current_output(i)
        print(f"  -> Meet de stroom aan de IRLZ44N output!")
        time.sleep(3)
    
    # Test 2: Langzame sweep van 4 naar 20mA
    print("\nTest 2: Sweep van 4mA naar 20mA (10 seconden)")
    print("  -> Bekijk de stroom langzaam oplopen")
    start_time = time.time()
    duration = 10.0
    while (time.time() - start_time) < duration:
        elapsed = time.time() - start_time
        current = 4 + (elapsed / duration) * 16  # 4-20mA = 16mA range
        dac.set_current_output(current)
        print(f"\r  Huidige stroom: {current:.2f}mA", end="", flush=True)
        time.sleep(0.1)
    print()
    
    # Test 3: Sweep terug naar 4mA
    print("\nTest 3: Sweep van 20mA naar 4mA (10 seconden)")
    start_time = time.time()
    while (time.time() - start_time) < duration:
        elapsed = time.time() - start_time
        current = 20 - (elapsed / duration) * 16
        dac.set_current_output(current)
        print(f"\r  Huidige stroom: {current:.2f}mA", end="", flush=True)
        time.sleep(0.1)
    print()
    
    # Reset naar 4mA (minimum)
    print("\nReset naar 4mA (minimum)...")
    dac.set_current_output(4)
    
    print("\n✓ Current test voltooid!")
    print("\nVerifieer dat je:")
    print("  - Verschillende stromen gemeten hebt (4-20mA)")
    print("  - De sweep van 4-20mA zag")
    print("  - De MOSFET/opamp schakeling correct werkt")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
