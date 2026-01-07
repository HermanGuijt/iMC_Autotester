#!/usr/bin/env python3
"""
GPIO Debug Script - Test P9_12 direct
"""
import time

try:
    import Adafruit_BBIO.GPIO as GPIO
    print("✓ Adafruit_BBIO.GPIO geïmporteerd")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)

PIN = "P9_12"

try:
    print(f"\n1. Setup pin {PIN} als OUTPUT...")
    GPIO.setup(PIN, GPIO.OUT)
    print(f"   ✓ Pin {PIN} geconfigureerd")
    
    print(f"\n2. Test pin HIGH/LOW (5 cycli, 1Hz)...")
    for i in range(5):
        print(f"   Cyclus {i+1}: HIGH", end="", flush=True)
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(0.5)
        
        print(" -> LOW", flush=True)
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(0.5)
    
    print(f"\n3. Test snelle schakel (20Hz voor 3 seconden)...")
    start = time.time()
    count = 0
    while time.time() - start < 3:
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(0.025)
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(0.025)
        count += 1
    print(f"   Aantal schakelingen: {count}")
    
    print("\n4. Cleanup...")
    GPIO.cleanup(PIN)
    
    print("\n✓ Test voltooid zonder errors!")
    print("\nAls het relay NIET schakelde, check:")
    print("  - Is het relay aangesloten op P9_12?")
    print("  - Heeft het relay externe voeding?")
    print("  - Is de relay trigger actief-hoog of actief-laag?")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    try:
        GPIO.cleanup(PIN)
    except:
        pass
