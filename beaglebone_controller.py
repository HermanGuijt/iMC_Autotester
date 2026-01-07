#!/usr/bin/env python3
"""
BeagleBone Black Controller voor DAC, ADC en Relay
Ontworpen voor custom cape met MCP4728 DAC en ADS1115 ADC
"""

import sys
import time
import threading
from dac_controller import DACController
from adc_controller import ADCController
from relay_controller import RelayController
from waveform_generator import WaveformGenerator

class BeagleBoneController:
    def __init__(self):
        print("Initialiseren van BeagleBone controller...")
        try:
            self.dac = DACController()
            self.adc = ADCController()
            self.relay = RelayController(gpio_pin="P9_12")
            self.waveform = WaveformGenerator()
            
            # Status variabelen
            self.voltage_running = False
            self.current_running = False
            self.relay_running = False
            
            self.voltage_thread = None
            self.current_thread = None
            
            print("✓ Initialisatie succesvol")
        except Exception as e:
            print(f"✗ Fout bij initialisatie: {e}")
            sys.exit(1)
    
    def clear_screen(self):
        """Clear terminal scherm"""
        print("\033[2J\033[H", end="")
    
    def show_main_menu(self):
        """Toon het hoofdmenu"""
        self.clear_screen()
        print("=" * 60)
        print(" BeagleBone Black - DAC/ADC/Relay Controller")
        print("=" * 60)
        print()
        print("1. Spanningsbron configureren (0-3.3V)")
        print("2. Stroombron configureren (4-20mA)")
        print("3. Relay configureren (1-60Hz)")
        print("4. ADC waarden uitlezen")
        print("5. Status weergeven")
        print("6. Alles stoppen")
        print("7. Afsluiten")
        print()
        print("=" * 60)
    
    def voltage_source_menu(self):
        """Menu voor spanningsbron configuratie"""
        self.clear_screen()
        print("=" * 60)
        print(" Spanningsbron Configuratie (0-3.3V)")
        print("=" * 60)
        print()
        print("Kies een curve type:")
        print("1. Constant (vaste waarde)")
        print("2. Sinus golf")
        print("3. Driehoek golf")
        print("4. Blokgolf")
        print("5. Ramp (oplopend)")
        print("6. Stop spanningsbron")
        print("7. Terug naar hoofdmenu")
        print()
        
        choice = input("Keuze: ").strip()
        
        if choice == "1":
            voltage = float(input("Voer spanning in (0-3.3V): "))
            self.set_constant_voltage(voltage)
        elif choice == "2":
            min_v = float(input("Minimum spanning (V): "))
            max_v = float(input("Maximum spanning (V): "))
            freq = float(input("Frequentie (Hz): "))
            self.start_voltage_waveform("sine", min_v, max_v, freq)
        elif choice == "3":
            min_v = float(input("Minimum spanning (V): "))
            max_v = float(input("Maximum spanning (V): "))
            freq = float(input("Frequentie (Hz): "))
            self.start_voltage_waveform("triangle", min_v, max_v, freq)
        elif choice == "4":
            min_v = float(input("Minimum spanning (V): "))
            max_v = float(input("Maximum spanning (V): "))
            freq = float(input("Frequentie (Hz): "))
            self.start_voltage_waveform("square", min_v, max_v, freq)
        elif choice == "5":
            min_v = float(input("Start spanning (V): "))
            max_v = float(input("Eind spanning (V): "))
            duration = float(input("Duur (seconden): "))
            self.start_voltage_ramp(min_v, max_v, duration)
        elif choice == "6":
            self.stop_voltage()
        elif choice == "7":
            return
    
    def current_source_menu(self):
        """Menu voor stroombron configuratie"""
        self.clear_screen()
        print("=" * 60)
        print(" Stroombron Configuratie (4-20mA)")
        print("=" * 60)
        print()
        print("Kies een curve type:")
        print("1. Constant (vaste waarde)")
        print("2. Sinus golf")
        print("3. Driehoek golf")
        print("4. Blokgolf")
        print("5. Ramp (oplopend)")
        print("6. Stop stroombron")
        print("7. Terug naar hoofdmenu")
        print()
        
        choice = input("Keuze: ").strip()
        
        if choice == "1":
            current = float(input("Voer stroom in (4-20mA): "))
            self.set_constant_current(current)
        elif choice == "2":
            min_i = float(input("Minimum stroom (mA): "))
            max_i = float(input("Maximum stroom (mA): "))
            freq = float(input("Frequentie (Hz): "))
            self.start_current_waveform("sine", min_i, max_i, freq)
        elif choice == "3":
            min_i = float(input("Minimum stroom (mA): "))
            max_i = float(input("Maximum stroom (mA): "))
            freq = float(input("Frequentie (Hz): "))
            self.start_current_waveform("triangle", min_i, max_i, freq)
        elif choice == "4":
            min_i = float(input("Minimum stroom (mA): "))
            max_i = float(input("Maximum stroom (mA): "))
            freq = float(input("Frequentie (Hz): "))
            self.start_current_waveform("square", min_i, max_i, freq)
        elif choice == "5":
            min_i = float(input("Start stroom (mA): "))
            max_i = float(input("Eind stroom (mA): "))
            duration = float(input("Duur (seconden): "))
            self.start_current_ramp(min_i, max_i, duration)
        elif choice == "6":
            self.stop_current()
        elif choice == "7":
            return
    
    def relay_menu(self):
        """Menu voor relay configuratie"""
        self.clear_screen()
        print("=" * 60)
        print(" Relay Configuratie (0.01-60Hz)")
        print("=" * 60)
        print()
        print("1. Start relay met frequentie")
        print("2. Relay AAN (constant)")
        print("3. Relay UIT")
        print("4. Terug naar hoofdmenu")
        print()
        
        choice = input("Keuze: ").strip()
        
        if choice == "1":
            freq = float(input("Frequentie (0.01-60Hz): "))
            if 0.01 <= freq <= 60:
                self.relay.start_switching(freq)
                self.relay_running = True
                print(f"✓ Relay schakelt op {freq}Hz")
                time.sleep(2)
            else:
                print("✗ Frequentie moet tussen 0.01 en 60 Hz zijn")
                time.sleep(2)
        elif choice == "2":
            self.relay.set_state(True)
            self.relay_running = False
            print("✓ Relay is AAN")
            time.sleep(1)
        elif choice == "3":
            self.relay.stop()
            self.relay_running = False
            print("✓ Relay is UIT")
            time.sleep(1)
        elif choice == "4":
            return
    
    def set_constant_voltage(self, voltage):
        """Stel vaste spanning in"""
        if 0 <= voltage <= 3.3:
            self.stop_voltage()
            self.dac.set_voltage_output(voltage)
            print(f"✓ Spanning ingesteld op {voltage}V")
            time.sleep(2)
        else:
            print("✗ Spanning moet tussen 0 en 3.3V zijn")
            time.sleep(2)
    
    def set_constant_current(self, current_ma):
        """Stel vaste stroom in"""
        if 4 <= current_ma <= 20:
            self.stop_current()
            self.dac.set_current_output(current_ma)
            print(f"✓ Stroom ingesteld op {current_ma}mA")
            time.sleep(2)
        else:
            print("✗ Stroom moet tussen 4 en 20mA zijn")
            time.sleep(2)
    
    def start_voltage_waveform(self, wave_type, min_v, max_v, frequency):
        """Start voltage waveform in aparte thread"""
        self.stop_voltage()
        self.voltage_running = True
        
        def voltage_loop():
            while self.voltage_running:
                voltage = self.waveform.generate(wave_type, min_v, max_v, frequency)
                self.dac.set_voltage_output(voltage)
                time.sleep(0.01)  # 100Hz update rate
        
        self.voltage_thread = threading.Thread(target=voltage_loop, daemon=True)
        self.voltage_thread.start()
        print(f"✓ Spanningsbron gestart: {wave_type} {min_v}-{max_v}V @ {frequency}Hz")
        time.sleep(2)
    
    def start_current_waveform(self, wave_type, min_i, max_i, frequency):
        """Start current waveform in aparte thread"""
        self.stop_current()
        self.current_running = True
        
        def current_loop():
            while self.current_running:
                current = self.waveform.generate(wave_type, min_i, max_i, frequency)
                self.dac.set_current_output(current)
                time.sleep(0.01)  # 100Hz update rate
        
        self.current_thread = threading.Thread(target=current_loop, daemon=True)
        self.current_thread.start()
        print(f"✓ Stroombron gestart: {wave_type} {min_i}-{max_i}mA @ {frequency}Hz")
        time.sleep(2)
    
    def start_voltage_ramp(self, start_v, end_v, duration):
        """Start voltage ramp"""
        self.stop_voltage()
        self.voltage_running = True
        
        def ramp_loop():
            start_time = time.time()
            while self.voltage_running and (time.time() - start_time) < duration:
                elapsed = time.time() - start_time
                progress = elapsed / duration
                voltage = start_v + (end_v - start_v) * progress
                self.dac.set_voltage_output(voltage)
                time.sleep(0.01)
            self.voltage_running = False
        
        self.voltage_thread = threading.Thread(target=ramp_loop, daemon=True)
        self.voltage_thread.start()
        print(f"✓ Voltage ramp gestart: {start_v}V → {end_v}V in {duration}s")
        time.sleep(2)
    
    def start_current_ramp(self, start_i, end_i, duration):
        """Start current ramp"""
        self.stop_current()
        self.current_running = True
        
        def ramp_loop():
            start_time = time.time()
            while self.current_running and (time.time() - start_time) < duration:
                elapsed = time.time() - start_time
                progress = elapsed / duration
                current = start_i + (end_i - start_i) * progress
                self.dac.set_current_output(current)
                time.sleep(0.01)
            self.current_running = False
        
        self.current_thread = threading.Thread(target=ramp_loop, daemon=True)
        self.current_thread.start()
        print(f"✓ Current ramp gestart: {start_i}mA → {end_i}mA in {duration}s")
        time.sleep(2)
    
    def stop_voltage(self):
        """Stop voltage output"""
        self.voltage_running = False
        if self.voltage_thread:
            self.voltage_thread.join(timeout=1)
        self.dac.set_voltage_output(0)
    
    def stop_current(self):
        """Stop current output"""
        self.current_running = False
        if self.current_thread:
            self.current_thread.join(timeout=1)
        self.dac.set_current_output(4)  # Minimum 4mA
    
    def read_adc_values(self):
        """Lees en toon ADC waarden"""
        self.clear_screen()
        print("=" * 60)
        print(" ADC Waarden (ADS1115)")
        print("=" * 60)
        print()
        print("Druk op CTRL+C om te stoppen")
        print()
        
        try:
            while True:
                values = self.adc.read_all_channels()
                print("\r", end="")
                print(f"CH0: {values[0]:7.3f}V  CH1: {values[1]:7.3f}V  "
                      f"CH2: {values[2]:7.3f}V  CH3: {values[3]:7.3f}V", end="")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n\nTerug naar menu...")
            time.sleep(1)
    
    def show_status(self):
        """Toon huidige status"""
        self.clear_screen()
        print("=" * 60)
        print(" Systeem Status")
        print("=" * 60)
        print()
        print(f"Spanningsbron: {'ACTIEF' if self.voltage_running else 'GESTOPT'}")
        print(f"Stroombron:    {'ACTIEF' if self.current_running else 'GESTOPT'}")
        print(f"Relay:         {'ACTIEF' if self.relay_running else 'GESTOPT'}")
        print()
        print("=" * 60)
        input("\nDruk op Enter om terug te gaan...")
    
    def stop_all(self):
        """Stop alle outputs"""
        print("Alle outputs stoppen...")
        self.stop_voltage()
        self.stop_current()
        self.relay.stop()
        self.relay_running = False
        print("✓ Alles gestopt")
        time.sleep(1)
    
    def cleanup(self):
        """Cleanup voor afsluiten"""
        self.stop_all()
        print("Opruimen en afsluiten...")
        time.sleep(0.5)
    
    def run(self):
        """Hoofdloop van de applicatie"""
        try:
            while True:
                self.show_main_menu()
                choice = input("Keuze: ").strip()
                
                if choice == "1":
                    self.voltage_source_menu()
                elif choice == "2":
                    self.current_source_menu()
                elif choice == "3":
                    self.relay_menu()
                elif choice == "4":
                    self.read_adc_values()
                elif choice == "5":
                    self.show_status()
                elif choice == "6":
                    self.stop_all()
                elif choice == "7":
                    self.cleanup()
                    print("Tot ziens!")
                    break
                else:
                    print("Ongeldige keuze, probeer opnieuw...")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\nOnderbroken door gebruiker...")
            self.cleanup()
        except Exception as e:
            print(f"\nFout opgetreden: {e}")
            self.cleanup()
            sys.exit(1)


if __name__ == "__main__":
    controller = BeagleBoneController()
    controller.run()
