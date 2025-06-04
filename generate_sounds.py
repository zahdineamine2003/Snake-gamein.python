import os
import numpy as np
from scipy.io import wavfile
from config import SOUND_PATH

def generate_sound(frequency, duration, amplitude=0.5, sample_rate=44100):
    """Generate a simple sine wave sound"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    note = np.sin(2 * np.pi * frequency * t) * amplitude
    return note

def apply_envelope(sound, attack=0.1, decay=0.1, sustain=0.5, release=0.1):
    """Apply ADSR envelope to the sound"""
    samples = len(sound)
    attack_samples = int(attack * samples)
    decay_samples = int(decay * samples)
    sustain_samples = int(sustain * samples)
    release_samples = samples - attack_samples - decay_samples - sustain_samples
    
    envelope = np.ones(samples)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[attack_samples:attack_samples+decay_samples] = np.linspace(1, 0.7, decay_samples)
    envelope[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = 0.7
    envelope[-release_samples:] = np.linspace(0.7, 0, release_samples)
    
    return sound * envelope

def create_eat_sound():
    """Create a short 'pop' sound for eating"""
    sound = generate_sound(800, 0.1)
    sound = apply_envelope(sound, 0.1, 0.2, 0.0, 0.7)
    return sound

def create_die_sound():
    """Create a descending tone for death"""
    t = np.linspace(0, 0.5, 22050)
    freq = np.linspace(400, 100, len(t))
    sound = np.sin(2 * np.pi * freq * t) * 0.5
    sound = apply_envelope(sound, 0.1, 0.1, 0.2, 0.6)
    return sound

def create_teleport_sound():
    """Create a 'whoosh' sound for teleporting"""
    t = np.linspace(0, 0.3, 13230)
    freq = np.linspace(100, 1000, len(t))
    sound = np.sin(2 * np.pi * freq * t) * 0.5
    sound = apply_envelope(sound, 0.1, 0.1, 0.1, 0.7)
    return sound

def create_dash_sound():
    """Create a quick 'swoosh' sound for dashing"""
    t = np.linspace(0, 0.2, 8820)
    freq = np.linspace(500, 1000, len(t))
    sound = np.sin(2 * np.pi * freq * t) * 0.5
    sound = apply_envelope(sound, 0.1, 0.2, 0.0, 0.7)
    return sound

def create_clone_sound():
    """Create a 'poof' sound for cloning"""
    sound1 = generate_sound(400, 0.2)
    sound2 = generate_sound(600, 0.2)
    sound = (sound1 + sound2) / 2
    sound = apply_envelope(sound, 0.1, 0.3, 0.0, 0.6)
    return sound

def create_evolve_sound():
    """Create an ascending tone for evolution"""
    t = np.linspace(0, 0.5, 22050)
    freq = np.linspace(200, 800, len(t))
    sound = np.sin(2 * np.pi * freq * t) * 0.5
    sound = apply_envelope(sound, 0.1, 0.2, 0.1, 0.6)
    return sound

def create_click_sound():
    """Create a short click sound"""
    sound = generate_sound(1000, 0.05)
    sound = apply_envelope(sound, 0.01, 0.04, 0.0, 0.95)
    return sound

def create_hover_sound():
    """Create a soft hover sound"""
    sound = generate_sound(500, 0.1)
    sound = apply_envelope(sound, 0.1, 0.2, 0.0, 0.7)
    return sound

def create_background_music():
    """Create a simple background melody"""
    duration = 5.0
    t = np.linspace(0, duration, int(44100 * duration))
    
    # Create a simple melody
    melody = (np.sin(2 * np.pi * 200 * t) * 0.3 + 
             np.sin(2 * np.pi * 300 * t) * 0.2 +
             np.sin(2 * np.pi * 400 * t) * 0.1)
    
    # Add some variation
    melody *= (1 + 0.2 * np.sin(2 * np.pi * 0.5 * t))
    
    return melody

def save_sound(sound, filename):
    """Save the sound as a WAV file"""
    # Ensure the sound is in the correct range
    sound = np.int16(sound * 32767)
    wavfile.write(filename, 44100, sound)

def generate_all_sounds():
    """Generate all game sound effects"""
    if not os.path.exists(SOUND_PATH):
        os.makedirs(SOUND_PATH)

    # Generate and save all sounds
    sounds = {
        'eat.wav': create_eat_sound(),
        'die.wav': create_die_sound(),
        'teleport.wav': create_teleport_sound(),
        'dash.wav': create_dash_sound(),
        'clone.wav': create_clone_sound(),
        'evolve.wav': create_evolve_sound(),
        'click.wav': create_click_sound(),
        'hover.wav': create_hover_sound(),
        'background.wav': create_background_music()
    }

    for filename, sound in sounds.items():
        filepath = os.path.join(SOUND_PATH, filename)
        save_sound(sound, filepath)
        print(f"Generated {filename}")

if __name__ == "__main__":
    generate_all_sounds() 