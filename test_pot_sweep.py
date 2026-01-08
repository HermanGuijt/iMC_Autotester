#!/usr/bin/env python3
"""
MCP4131 Digital Potentiometer Test Programma
Interactieve test tool voor weerstands sweeps en handmatige controle
"""

import time
import sys
from mcp4131_driver import MCP4131


def slow_sweep(pot):
    """Langzame sweep van 0Ω naar 10kΩ"""
    print("\n=== Langzame Sweep (0Ω → 10kΩ) ===")
    print("Duur: ~25 seconden")
    print()
    
    for i in range(129):  # 0-128
        pot.set_wiper(i)
        resistance = (i / 128) * pot.resistance
        percentage = (i / 128) * 100
        print(f"\rWiper: {i:3d}/128 → {resistance:6.0f}Ω ({percentage:5.1f}%)", end='', flush=True)
        time.sleep(0.2)
    
    print("\n✓ Sweep voltooid\n")
    time.sleep(1)


def fast_sweep(pot):
    """Snelle sweep van 0Ω naar 10kΩ en terug"""
    print("\n=== Snelle Sweep (0Ω ⇄ 10kΩ) ===")
    print("10 cycli, ~10 seconden")
    print()
    
    for cycle in range(10):
        # Omhoog
        for i in range(0, 129, 8):
            pot.set_wiper(i)
            resistance = (i / 128) * pot.resistance
            print(f"\rCyclus {cycle+1}/10: {resistance:6.0f}Ω ↑", end='', flush=True)
            time.sleep(0.05)
        
        # Omlaag
        for i in range(128, -1, -8):
            pot.set_wiper(i)
            resistance = (i / 128) * pot.resistance
            print(f"\rCyclus {cycle+1}/10: {resistance:6.0f}Ω ↓", end='', flush=True)
            time.sleep(0.05)
    
    print("\n✓ Sweep voltooid\n")
    time.sleep(1)


def step_test(pot):
    """Test discrete weerstandswaarden"""
    print("\n=== Stappen Test (0%, 25%, 50%, 75%, 100%) ===")
    print("Elke stap 3 seconden")
    print()
    
    percentages = [0, 25, 50, 75, 100]
    
    for pct in percentages:
        wiper = int((pct / 100) * 128)
        pot.set_wiper(wiper)
        resistance = (wiper / 128) * pot.resistance
        
        print(f"{pct:3d}% → Wiper: {wiper:3d}, R: {resistance:6.0f}Ω")
        time.sleep(3)
    
    print("✓ Test voltooid\n")
    time.sleep(1)


def custom_resistance(pot):
    """Handmatig weerstand instellen"""
    print("\n=== Handmatige Weerstand ===")
    print(f"Bereik: 0 - {pot.resistance}Ω")
    
    while True:
        try:
            resistance_str = input("\nGeef weerstand in Ω (of 'q' om terug): ")
            
            if resistance_str.lower() == 'q':
                break
            
            resistance = float(resistance_str)
            
            if not 0 <= resistance <= pot.resistance:
                print(f"❌ Waarde moet tussen 0 en {pot.resistance}Ω zijn")
                continue
            
            wiper = int((resistance / pot.resistance) * 128)
            pot.set_wiper(wiper)
            actual_r = (wiper / 128) * pot.resistance
            percentage = (wiper / 128) * 100
            
            print(f"✓ Ingesteld: {actual_r:.0f}Ω (wiper: {wiper}, {percentage:.1f}%)")
            
        except ValueError:
            print("❌ Ongeldige invoer")
        except KeyboardInterrupt:
            print("\n")
            break


def custom_percentage(pot):
    """Handmatig percentage instellen"""
    print("\n=== Handmatig Percentage ===")
    print("Bereik: 0 - 100%")
    
    while True:
        try:
            pct_str = input("\nGeef percentage (of 'q' om terug): ")
            
            if pct_str.lower() == 'q':
                break
            
            pct = float(pct_str)
            
            if not 0 <= pct <= 100:
                print("❌ Percentage moet tussen 0 en 100 zijn")
                continue
            
            wiper = int((pct / 100) * 128)
            pot.set_wiper(wiper)
            actual_pct = (wiper / 128) * 100
            resistance = (wiper / 128) * pot.resistance
            
            print(f"✓ Ingesteld: {actual_pct:.1f}% (wiper: {wiper}, {resistance:.0f}Ω)")
            
        except ValueError:
            print("❌ Ongeldige invoer")
        except KeyboardInterrupt:
            print("\n")
            break


def increment_decrement_test(pot):
    """Test increment/decrement functionaliteit"""
    print("\n=== Increment/Decrement Test ===")
    print("20 stappen omhoog, dan 20 stappen omlaag")
    print()
    
    # Start in midden
    pot.set_wiper(64)
    print("Start positie: 50% (5kΩ)")
    time.sleep(1)
    
    print("\nIncrement (20 stappen):")
    for i in range(20):
        pot.increment()
        print(f"  Stap {i+1}/20 omhoog", end='\r', flush=True)
        time.sleep(0.2)
    
    print("\n\nDecrement (20 stappen):")
    for i in range(20):
        pot.decrement()
        print(f"  Stap {i+1}/20 omlaag", end='\r', flush=True)
        time.sleep(0.2)
    
    print("\n✓ Test voltooid\n")
    time.sleep(1)


def show_menu():
    """Toon hoofdmenu"""
    print("\n" + "="*60)
    print("MCP4131 Digital Potentiometer Test Menu")
    print("="*60)
    print("1. Langzame sweep (0 → 10kΩ)")
    print("2. Snelle sweep (0 ⇄ 10kΩ, 10x)")
    print("3. Stappen test (0%, 25%, 50%, 75%, 100%)")
    print("4. Handmatig weerstand instellen")
    print("5. Handmatig percentage instellen")
    print("6. Increment/Decrement test")
    print("7. Reset naar 50%")
    print("q. Afsluiten")
    print("="*60)


def main():
    print("MCP4131 Digital Potentiometer Test")
    print("Zorg dat dac_startup.sh is uitgevoerd!")
    print()
    
    try:
        # Initialiseer potentiometer
        pot = MCP4131(spi_bus=0, spi_device=0, cs_pin="P9_24")
        print()
        
        # Start op 50%
        pot.set_wiper(64)
        print("Startpositie: 50% (5kΩ)")
        
        # Hoofdloop
        while True:
            show_menu()
            
            try:
                choice = input("\nKeuze: ").strip().lower()
                
                if choice == 'q':
                    break
                elif choice == '1':
                    slow_sweep(pot)
                elif choice == '2':
                    fast_sweep(pot)
                elif choice == '3':
                    step_test(pot)
                elif choice == '4':
                    custom_resistance(pot)
                elif choice == '5':
                    custom_percentage(pot)
                elif choice == '6':
                    increment_decrement_test(pot)
                elif choice == '7':
                    pot.set_wiper(64)
                    print("✓ Reset naar 50% (5kΩ)")
                    time.sleep(1)
                else:
                    print("❌ Ongeldige keuze")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n\nTerug naar menu...")
                time.sleep(0.5)
        
        print("\nProgramma wordt afgesloten...")
        
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Cleanup
        pot.cleanup()
        print("✓ Cleanup voltooid")


if __name__ == "__main__":
    main()
