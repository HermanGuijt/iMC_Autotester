#!/usr/bin/env python3
"""
Dual Processor Reed Contact Simulator
Simuleert 2 processoren met pull-ups aan reed contact
"""
import time
from dac_controller import DACController
from relay_controller import RelayController

print("=" * 70)
print(" Dual Processor Reed Contact Simulator")
print("=" * 70)
print()
print("Hardware Setup:")
print("  1. BeagleBone Relay (P9_12) → IoT Input Pin → simuleert reed contact")
print("  2. BeagleBone DAC VOUTA → [10kΩ weerstand] → IoT Input Pin")
print("     └─ simuleert zwakke pull-up van processor 2")
print("  3. BeagleBone GND → IoT GND (gemeenschappelijk)")
print()
print("  ** Plaats 10kΩ weerstand op proto cape tussen VOUTA en IoT input **")
print()

try:
    # Initialiseer hardware
    dac = DACController()
    relay = RelayController("P9_12")
    
    print("=" * 70)
    print("Test Scenario's")
    print("=" * 70)
    
    # Scenario 1: Normale situatie (3.3V pull-up)
    print("\n1. NORMALE situatie - Processor 2 met goede pull-up (3.3V)")
    print("   DAC = 3.3V, Reed OPEN")
    dac.set_voltage_output(3.3)
    relay.set_state(False)  # Reed OPEN
    print("   → Meet spanning aan IoT input (verwacht: ~3.3V)")
    time.sleep(5)
    
    print("\n   Reed CLOSED (puls)")
    relay.set_state(True)  # Reed CLOSED
    print("   → Meet spanning aan IoT input (verwacht: ~0V)")
    time.sleep(3)
    relay.set_state(False)
    
    # Scenario 2: Zwakke pull-up (2.8V inzak)
    print("\n\n2. PROBLEEM situatie - Processor 2 met zwakke pull-up (2.8V)")
    print("   DAC = 2.8V, Reed OPEN")
    dac.set_voltage_output(2.8)
    relay.set_state(False)
    print("   → Meet spanning aan IoT input (verwacht: ~2.8-3.0V)")
    time.sleep(5)
    
    print("\n   Reed CLOSED (puls)")
    relay.set_state(True)
    print("   → Meet spanning aan IoT input (verwacht: ~0V)")
    time.sleep(3)
    relay.set_state(False)
    
    # Scenario 3: Zeer zwakke pull-up (2.5V)
    print("\n\n3. ERNSTIG probleem - Processor 2 met zeer zwakke pull-up (2.5V)")
    print("   DAC = 2.5V, Reed OPEN")
    dac.set_voltage_output(2.5)
    relay.set_state(False)
    print("   → Meet spanning aan IoT input (verwacht: ~2.5-2.8V)")
    time.sleep(5)
    
    # Scenario 4: Dynamisch testen met pulsen
    print("\n\n4. DYNAMISCH test - Reed pulsen met zwakke pull-up")
    print("   DAC = 2.8V, Reed schakelt 1 Hz (10 pulsen)")
    dac.set_voltage_output(2.8)
    relay.start_switching(1.0)  # 1 Hz
    
    for i in range(10):
        print(f"   Puls {i+1}/10")
        time.sleep(1)
    
    relay.stop()
    
    # Interactieve modus
    print("\n\n5. INTERACTIEVE modus - Stel zelf in")
    print("=" * 70)
    
    while True:
        print("\nHuidige instellingen:")
        status = relay.get_state()
        print(f"  DAC spanning: {dac.get_voltage_output():.2f}V")
        print(f"  Relay: {'CLOSED (0V)' if status['state'] else 'OPEN'}")
        print(f"  Switching: {status['frequency']}Hz" if status['switching'] else "")
        
        print("\nOpties:")
        print("  1. Verander DAC spanning (processor 2 pull-up)")
        print("  2. Reed OPEN")
        print("  3. Reed CLOSED")
        print("  4. Reed pulsen (frequency)")
        print("  5. Stop pulsen")
        print("  6. Afsluiten")
        
        choice = input("\nKeuze: ").strip()
        
        if choice == "1":
            v = float(input("DAC spanning (0-3.3V): "))
            dac.set_voltage_output(v)
            print(f"✓ DAC ingesteld op {v}V")
        elif choice == "2":
            relay.stop()
            relay.set_state(False)
            print("✓ Reed OPEN")
        elif choice == "3":
            relay.stop()
            relay.set_state(True)
            print("✓ Reed CLOSED")
        elif choice == "4":
            freq = float(input("Frequentie (Hz): "))
            relay.start_switching(freq)
            print(f"✓ Reed pulst op {freq}Hz")
        elif choice == "5":
            relay.stop()
            print("✓ Pulsen gestopt")
        elif choice == "6":
            break
    
    # Cleanup
    print("\n\nReset naar veilige staat...")
    relay.stop()
    dac.set_voltage_output(3.3)
    
    print("✓ Simulatie voltooid!")
    
except KeyboardInterrupt:
    print("\n\nOnderbroken door gebruiker")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        relay.stop()
        relay.cleanup()
    except:
        pass

print("\n" + "=" * 70)
print("DIAGNOSE TIPS:")
print("  - Als IoT device niet werkt met 2.8V → te lage threshold")
print("  - Als pulsen missen → pull-up te zwak of timing probleem")
print("  - Vergelijk gedrag met 3.3V vs 2.8V vs 2.5V")
print("=" * 70)
