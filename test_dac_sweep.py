#!/usr/bin/env python3
"""
Test script voor MCP4822 DAC
Verschillende test modi voor verificatie met oscilloscoop

BELANGRIJK: Gebruik Python 3!
Uitvoeren: python3 test_dac_sweep.py
"""

import time
import sys

# Check Python versie
if sys.version_info[0] < 3:
    print("ERROR: Dit script vereist Python 3!")
    print("Gebruik: python3 test_dac_sweep.py")
    sys.exit(1)

from mcp4922_driver import MCP4822


def slow_sweep_test(dac, channel='A', max_v=3.3):
    """
    Langzame sweep van 0V naar max spanning voor oscilloscoop verificatie
    """
    print("\n" + "=" * 60)
    print("SLOW SWEEP TEST")
    print("=" * 60)
    print(f"Kanaal {channel} wordt langzaam gesweept van 0V naar {max_v}V")
    print("Monitor met oscilloscoop op VOUT{}\n".format(channel))
    
    input("Druk op Enter om te starten...")
    
    # Langzame sweep: 10 seconden totaal, 200 stappen
    dac.voltage_sweep(channel, 0, max_v, steps=200, delay=0.05)
    
    print(f"\nSweep voltooid. Output op {max_v}V")
    print("Druk op Enter om door te gaan...")
    input()


def fast_sweep_test(dac, channel='A', max_v=3.3, cycles=3):
    """
    Snelle herhaalde sweeps voor dynamische test
    """
    print("\n" + "=" * 60)
    print("FAST SWEEP TEST")
    print("=" * 60)
    print(f"Kanaal {channel}: {cycles} snelle sweeps van 0V naar {max_v}V")
    print("Monitor met oscilloscoop op VOUT{}\n".format(channel))
    
    input("Druk op Enter om te starten...")
    
    for cycle in range(cycles):
        print(f"\nCycle {cycle + 1}/{cycles}")
        dac.voltage_sweep(channel, 0, max_v, steps=100, delay=0.01)
        time.sleep(0.5)
    
    print("\nFast sweep test voltooid")
    print("Druk op Enter om door te gaan...")
    input()


def step_test(dac, channel='A', max_v=3.3):
    """
    Test met discrete spanningsstappen
    """
    print("\n" + "=" * 60)
    print("STEP VOLTAGE TEST")
    print("=" * 60)
    print(f"Kanaal {channel}: Discrete spanningsstappen")
    print("Monitor met oscilloscoop op VOUT{}\n".format(channel))
    
    # Test voltages: 0%, 25%, 50%, 75%, 100% van max
    test_voltages = [
        (0.00 * max_v, "  0%"),
        (0.25 * max_v, " 25%"),
        (0.50 * max_v, " 50%"),
        (0.75 * max_v, " 75%"),
        (1.00 * max_v, "100%"),
    ]
    
    input("Druk op Enter om te starten...")
    
    for voltage, label in test_voltages:
        dac_val = dac.set_voltage(channel, voltage)
        print(f"{label} → {voltage:.3f}V (DAC: {dac_val}/4095)")
        time.sleep(2)
    
    print("\nStep test voltooid")
    print("Druk op Enter om door te gaan...")
    input()


def manual_voltage_test(dac, channel='A', max_v=3.3):
    """
    Handmatige spanning instelling
    """
    print("\n" + "=" * 60)
    print("MANUAL VOLTAGE CONTROL")
    print("=" * 60)
    print(f"Kanaal {channel}: Handmatige spanning controle")
    print(f"Bereik: 0V - {max_v}V")
    print("Type 'q' om te stoppen\n")
    
    while True:
        try:
            user_input = input("Gewenste spanning (V): ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                break
            
            voltage = float(user_input)
            
            if voltage < 0 or voltage > max_v:
                print(f"⚠️  Spanning buiten bereik! (0V - {max_v}V)")
                continue
            
            dac_val = dac.set_voltage(channel, voltage)
            # Bepaal gain voor berekening
            gain = 2 if voltage > 2.048 else 1
            actual_v = (dac_val / 4095) * (2.048 * gain)
            print(f"✓ Ingesteld: {actual_v:.4f}V (DAC: {dac_val}/4095, gain={gain})\n")
            
        except ValueError:
            print("⚠️  Ongeldige invoer. Voer een getal in.\n")
        except KeyboardInterrupt:
            break
    
    print("\nHandmatige controle beëindigd")


def main():
    """
    Hoofdmenu voor DAC test
    """
    print("=" * 60)
    print("MCP4822 DAC TEST PROGRAMMA")
    print("=" * 60)
    print("BeagleBone Black - iMC Autotester V2")
    print("=" * 60)
    
    # MCP4822 met interne 2.048V referentie
    # Met gain=2 kan output tot 4.096V (we gebruiken 3.3V als praktisch max)
    print("\nMCP4822 gebruikt interne 2.048V referentie")
    print("Gain=2 wordt automatisch gebruikt voor spanningen > 2.048V")
    
    max_voltage = 3.3  # Praktisch maximum voor testen
    print(f"Max spanning: {max_voltage}V")
    
    # Initialiseer DAC met hardware Vref (altijd 2.048V)
    try:
        dac = MCP4822(vref=2.048)
        
        # Reset naar 0V
        print("\nReset DAC outputs naar 0V...")
        dac.set_voltage('A', 0)
        dac.set_voltage('B', 0)
        time.sleep(0.5)
        
        # Hoofd test loop
        while True:
            print("\n" + "=" * 60)
            print("TEST MENU")
            print("=" * 60)
            print("1. Langzame Sweep (0V → VCC) - voor scope verificatie")
            print("2. Snelle Sweep (meerdere cycles) - dynamische test")
            print("3. Stap Test (0%, 25%, 50%, 75%, 100%)")
            print("4. Handmatige Spanning Controle")
            print("5. Reset naar 0V")
            print("q. Afsluiten")
            
            choice = input("\nKeuze: ").strip().lower()
            
            if choice == '1':
                slow_sweep_test(dac, 'A', max_voltage)
            elif choice == '2':
                fast_sweep_test(dac, 'A', max_voltage)
            elif choice == '3':
                step_test(dac, 'A', max_voltage)
            elif choice == '4':
                manual_voltage_test(dac, 'A', max_voltage)
            elif choice == '5':
                print("\nReset naar 0V...")
                dac.set_voltage('A', 0)
                dac.set_voltage('B', 0)
                print("✓ Beide kanalen op 0V")
                time.sleep(1)
            elif choice == 'q':
                break
            else:
                print("⚠️  Ongeldige keuze")
        
    except KeyboardInterrupt:
        print("\n\nProgramma gestopt door gebruiker")
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up...")
        dac.cleanup()
        print("Programma beëindigd")


if __name__ == "__main__":
    main()
