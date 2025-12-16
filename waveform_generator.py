#!/usr/bin/env python3
"""
Waveform Generator
Genereert verschillende golfvormen voor spanning en stroom outputs
"""

import math
import time


class WaveformGenerator:
    """Generator voor verschillende golfvormen"""
    
    def __init__(self):
        """Initialiseer waveform generator"""
        self.start_time = time.time()
        self.last_time = self.start_time
    
    def reset_time(self):
        """Reset de tijdsbasis"""
        self.start_time = time.time()
        self.last_time = self.start_time
    
    def generate(self, wave_type, min_value, max_value, frequency):
        """
        Genereer een waarde voor de huidige tijd
        
        Args:
            wave_type: Type golfvorm ('sine', 'triangle', 'square', 'sawtooth')
            min_value: Minimum waarde
            max_value: Maximum waarde
            frequency: Frequentie in Hz
            
        Returns:
            Huidige waarde van de golfvorm
        """
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Bereken fase (0 tot 1) voor huidige cyclus
        phase = (elapsed * frequency) % 1.0
        
        # Genereer golfvorm
        if wave_type.lower() == 'sine':
            value = self._sine_wave(phase, min_value, max_value)
        elif wave_type.lower() == 'triangle':
            value = self._triangle_wave(phase, min_value, max_value)
        elif wave_type.lower() == 'square':
            value = self._square_wave(phase, min_value, max_value)
        elif wave_type.lower() == 'sawtooth':
            value = self._sawtooth_wave(phase, min_value, max_value)
        else:
            print(f"✗ Onbekend golftype: {wave_type}")
            value = min_value
        
        return value
    
    def _sine_wave(self, phase, min_val, max_val):
        """
        Genereer sinus golf
        
        Args:
            phase: Fase van 0 tot 1
            min_val: Minimum waarde
            max_val: Maximum waarde
            
        Returns:
            Waarde op huidige fase
        """
        # sin(2π * phase) geeft -1 tot 1
        # Schaal naar min_val tot max_val
        amplitude = (max_val - min_val) / 2.0
        offset = (max_val + min_val) / 2.0
        
        value = offset + amplitude * math.sin(2 * math.pi * phase)
        return value
    
    def _triangle_wave(self, phase, min_val, max_val):
        """
        Genereer driehoek golf
        
        Args:
            phase: Fase van 0 tot 1
            min_val: Minimum waarde
            max_val: Maximum waarde
            
        Returns:
            Waarde op huidige fase
        """
        # Driehoek: lineair stijgend van 0 tot 0.5, dan dalend tot 1
        if phase < 0.5:
            # Stijgend deel
            normalized = phase * 2.0  # 0 tot 1
        else:
            # Dalend deel
            normalized = 2.0 - (phase * 2.0)  # 1 tot 0
        
        value = min_val + (max_val - min_val) * normalized
        return value
    
    def _square_wave(self, phase, min_val, max_val):
        """
        Genereer blokgolf
        
        Args:
            phase: Fase van 0 tot 1
            min_val: Minimum waarde
            max_val: Maximum waarde
            
        Returns:
            Waarde op huidige fase
        """
        # 50% duty cycle
        if phase < 0.5:
            return max_val
        else:
            return min_val
    
    def _sawtooth_wave(self, phase, min_val, max_val):
        """
        Genereer zaagtand golf (lineair stijgend)
        
        Args:
            phase: Fase van 0 tot 1
            min_val: Minimum waarde
            max_val: Maximum waarde
            
        Returns:
            Waarde op huidige fase
        """
        value = min_val + (max_val - min_val) * phase
        return value
    
    def generate_ramp(self, start_val, end_val, duration, elapsed_time):
        """
        Genereer een lineaire ramp
        
        Args:
            start_val: Start waarde
            end_val: Eind waarde
            duration: Totale duur in seconden
            elapsed_time: Verstreken tijd in seconden
            
        Returns:
            Huidige waarde
        """
        if elapsed_time >= duration:
            return end_val
        
        progress = elapsed_time / duration
        value = start_val + (end_val - start_val) * progress
        return value
    
    def generate_exponential(self, start_val, end_val, tau, elapsed_time):
        """
        Genereer exponentiële curve
        
        Args:
            start_val: Start waarde
            end_val: Eind waarde (asymptoot)
            tau: Tijd constante
            elapsed_time: Verstreken tijd
            
        Returns:
            Huidige waarde
        """
        # Exponentiële functie: y = end_val + (start_val - end_val) * e^(-t/tau)
        delta = start_val - end_val
        value = end_val + delta * math.exp(-elapsed_time / tau)
        return value
    
    def generate_custom(self, values, frequency):
        """
        Genereer custom golfvorm uit lijst van waarden
        
        Args:
            values: Liste van waarden (wordt herhaald)
            frequency: Aantal cycli per seconde
            
        Returns:
            Huidige waarde
        """
        if not values:
            return 0.0
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Bereken welke sample we nodig hebben
        samples_per_cycle = len(values)
        total_samples = elapsed * frequency * samples_per_cycle
        index = int(total_samples) % samples_per_cycle
        
        return values[index]


# Test functie
if __name__ == "__main__":
    print("Waveform Generator Test")
    print("=" * 50)
    
    generator = WaveformGenerator()
    
    # Test parameters
    min_val = 0.0
    max_val = 3.3
    frequency = 1.0  # 1 Hz
    duration = 4.0   # 4 seconden
    
    print(f"\nTest golfvormen ({duration}s, {frequency}Hz, {min_val}-{max_val}V)")
    print("=" * 70)
    
    wave_types = ['sine', 'triangle', 'square', 'sawtooth']
    
    for wave_type in wave_types:
        print(f"\n{wave_type.upper()} golf:")
        print("-" * 70)
        
        generator.reset_time()
        start = time.time()
        
        samples = []
        while (time.time() - start) < duration:
            value = generator.generate(wave_type, min_val, max_val, frequency)
            samples.append(value)
            
            # Print elke 0.25 seconde
            elapsed = time.time() - start
            if len(samples) % 25 == 0:
                phase = (elapsed * frequency) % 1.0
                print(f"  t={elapsed:4.2f}s  phase={phase:4.2f}  value={value:5.3f}V")
            
            time.sleep(0.01)
    
    # Test ramp
    print("\n\nRAMP test (0V → 3.3V in 3s):")
    print("-" * 70)
    generator.reset_time()
    start = time.time()
    
    while (time.time() - start) < 3.0:
        elapsed = time.time() - start
        value = generator.generate_ramp(0.0, 3.3, 3.0, elapsed)
        
        if int(elapsed * 10) % 5 == 0:  # Print elke 0.5s
            print(f"  t={elapsed:4.2f}s  value={value:5.3f}V")
        
        time.sleep(0.1)
    
    # Test exponential
    print("\n\nEXPONENTIAL test (0V → 3.3V, tau=1s):")
    print("-" * 70)
    generator.reset_time()
    start = time.time()
    
    while (time.time() - start) < 5.0:
        elapsed = time.time() - start
        value = generator.generate_exponential(0.0, 3.3, 1.0, elapsed)
        
        if int(elapsed * 10) % 5 == 0:  # Print elke 0.5s
            print(f"  t={elapsed:4.2f}s  value={value:5.3f}V")
        
        time.sleep(0.1)
    
    # Test custom
    print("\n\nCUSTOM waveform test (stap functie):")
    print("-" * 70)
    custom_values = [0.0, 1.1, 2.2, 3.3, 2.2, 1.1]
    
    generator.reset_time()
    start = time.time()
    
    while (time.time() - start) < 3.0:
        value = generator.generate_custom(custom_values, 1.0)
        elapsed = time.time() - start
        
        if int(elapsed * 10) % 5 == 0:
            print(f"  t={elapsed:4.2f}s  value={value:5.3f}V")
        
        time.sleep(0.1)
    
    print("\n\n✓ Alle tests voltooid")
