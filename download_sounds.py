import os
import urllib.request
from config import SOUND_PATH

def download_sounds():
    """Download game sound effects from reliable sources"""
    
    # Create sounds directory if it doesn't exist
    if not os.path.exists(SOUND_PATH):
        os.makedirs(SOUND_PATH)

    # Sound file URLs from reliable sources
    sound_urls = {
        'eat.wav': 'https://www.soundjay.com/button/sounds/button-14.mp3',
        'die.wav': 'https://www.soundjay.com/mechanical/sounds/crash-1.mp3',
        'background.mp3': 'https://www.soundjay.com/nature/sounds/rain-02.mp3',
        'click.wav': 'https://www.soundjay.com/button/sounds/button-1.mp3',
        'hover.wav': 'https://www.soundjay.com/button/sounds/button-16.mp3',
        'teleport.wav': 'https://www.soundjay.com/button/sounds/button-3.mp3',
        'dash.wav': 'https://www.soundjay.com/button/sounds/button-09.mp3',
        'clone.wav': 'https://www.soundjay.com/button/sounds/button-21.mp3',
        'evolve.wav': 'https://www.soundjay.com/button/sounds/button-37.mp3'
    }

    # Download each sound file
    for filename, url in sound_urls.items():
        target_path = os.path.join(SOUND_PATH, filename)
        if not os.path.exists(target_path):
            try:
                print(f"Downloading {filename}...")
                urllib.request.urlretrieve(url, target_path)
                print(f"Successfully downloaded {filename}")
            except Exception as e:
                print(f"Failed to download {filename}: {str(e)}")
                # Create a fallback sound file (silent)
                try:
                    with open(target_path, 'wb') as f:
                        # Write minimal valid WAV file header (44 bytes)
                        f.write(bytes.fromhex('52494646' '24000000' '57415645' '666D7420'
                                           '10000000' '01000100' '44AC0000' '88580100'
                                           '02001000' '64617461' '00000000'))
                    print(f"Created empty fallback sound for {filename}")
                except:
                    print(f"Could not create fallback sound for {filename}")

if __name__ == "__main__":
    download_sounds() 