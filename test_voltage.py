#!/usr/bin/env python3
"""
Voltage Output Test - 0-3.3V met verschillende patronen
"""
import time
from dac_controller import DACController

print("=" * 60)
print(" Voltage Output Test (0-3.3V)")
print("=" * 60)
print()

try:
    dac = DACController()
    
    # Test 1: Constante spanningen
    print("Test 1: Constante spanningen")
    test_voltages = [0, 0.5, 1.0, 1.65, 2.5, 3.3]
    for v in test_voltages:
        print(f"  Instellen: {v}V")
        dac.set_voltage_output(v)
        print(f"  -> Meet de spanning aan de opamp uitgang!")
        time.sleep(3)
    
    # Test 2: Langzame sweep van 0 naar 3.3V
    print("\nTest 2: Sweep van 0V naar 3.3V (10 seconden)")
    print("  -> Bekijk de spanning langzaam oplopen")
    start_time = time.time()
    duration = 10.0
    while (time.time() - start_time) < duration:
        elapsed = time.time() - start_time
        voltage = (elapsed / duration) * 3.3
        dac.set_voltage_output(voltage)
        print(f"\r  Huidige spanning: {voltage:.2f}V", end="", flush=True)
        time.sleep(0.1)
    print()
    
    # Test 3: Sweep terug naar 0V
    print("\nTest 3: Sweep van 3.3V naar 0V (10 seconden)")
    start_time = time.time()
    while (time.time() - start_time) < duration:
        elapsed = time.time() - start_time
        voltage = 3.3 - (elapsed / duration) * 3.3
        dac.set_voltage_output(voltage)
        print(f"\r  Huidige spanning: {voltage:.2f}V", end="", flush=True)
        time.sleep(0.1)
    print()
    
    # Reset naar 0V
    print("\nReset naar 0V...")
    dac.set_voltage_output(0)
    
    print("\n✓ Voltage test voltooid!")
    print("\nVerifieer dat je:")
    print("  - Verschillende spanningen gemeten hebt")
    print("  - De sweep van 0-3.3V zag")
    print("  - De opamp output correct schakelt")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
