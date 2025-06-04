import os
import urllib.request
import pygame
import io
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
from config import *

def download_sounds():
    """Download game sound effects and music"""
    sound_urls = {
        'eat.wav': 'https://raw.githubusercontent.com/clear-code-projects/Snake/main/Sound/eat.wav',
        'die.wav': 'https://raw.githubusercontent.com/clear-code-projects/Snake/main/Sound/die.wav',
        'teleport.wav': 'https://freesound.org/data/previews/521/521642_11110746-lq.mp3',
        'dash.wav': 'https://freesound.org/data/previews/117/117740_2188080-lq.mp3',
        'clone.wav': 'https://freesound.org/data/previews/270/270545_5123851-lq.mp3',
        'evolve.wav': 'https://freesound.org/data/previews/320/320655_5260872-lq.mp3',
        'click.wav': 'https://freesound.org/data/previews/522/522720_11110746-lq.mp3',
        'hover.wav': 'https://freesound.org/data/previews/256/256116_3263906-lq.mp3',
        'background.mp3': 'https://freesound.org/data/previews/382/382310_7037-lq.mp3'
    }

    if not os.path.exists(SOUND_PATH):
        os.makedirs(SOUND_PATH)

    for filename, url in sound_urls.items():
        try:
            urllib.request.urlretrieve(url, os.path.join(SOUND_PATH, filename))
        except:
            print(f"Could not download {filename}")

def create_snake_assets():
    """Create modern voxel-style snake assets with enhanced effects"""
    if not os.path.exists(IMAGE_PATH):
        os.makedirs(IMAGE_PATH)

    skins = {
        'classic': [(0, 200, 0), (0, 255, 0)],
        'neon': [(0, 200, 200), (0, 255, 255)],
        'pixel': [(0, 0, 200), (0, 100, 255)],
        'rainbow': [(255, 0, 0), (255, 128, 0)]
    }

    for skin_name, (body_color, head_color) in skins.items():
        # Create snake head with enhanced 3D effect
        head_size = GRID_SIZE
        head_img = Image.new('RGBA', (head_size, head_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(head_img)
        
        # Enhanced 3D effect
        draw.rectangle([2, 2, head_size-3, head_size-3], fill=head_color)
        draw.polygon([(2, 2), (head_size-3, 2), (head_size-5, 4)], fill=tuple(map(lambda x: int(x*0.8), head_color)))
        draw.polygon([(2, 2), (2, head_size-3), (4, head_size-5)], fill=tuple(map(lambda x: int(x*0.6), head_color)))
        
        # Enhanced shine effect
        draw.ellipse([4, 4, 8, 8], fill=(255, 255, 255, 128))
        draw.ellipse([3, 3, 6, 6], fill=(255, 255, 255, 180))
        
        # Apply subtle glow effect
        head_img = head_img.filter(ImageFilter.GaussianBlur(0.5))
        
        head_img.save(os.path.join(IMAGE_PATH, f'snake_head_{skin_name}.png'))

        # Create enhanced body segment
        body_img = Image.new('RGBA', (head_size, head_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(body_img)
        
        draw.rectangle([2, 2, head_size-3, head_size-3], fill=body_color)
        draw.polygon([(2, 2), (head_size-3, 2), (head_size-5, 4)], fill=tuple(map(lambda x: int(x*0.8), body_color)))
        draw.polygon([(2, 2), (2, head_size-3), (4, head_size-5)], fill=tuple(map(lambda x: int(x*0.6), body_color)))
        
        # Apply subtle glow
        body_img = body_img.filter(ImageFilter.GaussianBlur(0.5))
        
        body_img.save(os.path.join(IMAGE_PATH, f'snake_body_{skin_name}.png'))

def create_map_assets():
    """Create modern map tiles and obstacles with enhanced effects"""
    tile_size = GRID_SIZE

    # Create enhanced floor tile with pattern
    floor = Image.new('RGBA', (tile_size, tile_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(floor)
    
    # Create checkerboard pattern
    for i in range(0, tile_size, 4):
        for j in range(0, tile_size, 4):
            if (i + j) % 8 == 0:
                draw.rectangle([i, j, i+3, j+3], fill=(60, 60, 60))
            else:
                draw.rectangle([i, j, i+3, j+3], fill=(50, 50, 50))
    
    floor.save(os.path.join(IMAGE_PATH, 'floor.png'))

    # Create enhanced obstacle with metallic effect
    obstacle = Image.new('RGBA', (tile_size, tile_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(obstacle)
    
    # Base shape with metallic gradient
    for y in range(tile_size):
        color_value = 150 + int(20 * (y / tile_size))
        draw.line([(2, y), (tile_size-3, y)], fill=(color_value, color_value, color_value))
    
    # Add spikes with shine
    spike_points = [(tile_size//2, 2), (tile_size-4, tile_size-4), (4, tile_size-4)]
    draw.polygon(spike_points, fill=(200, 200, 200))
    
    # Add shine effect
    shine_layer = Image.new('RGBA', (tile_size, tile_size), (0, 0, 0, 0))
    shine_draw = ImageDraw.Draw(shine_layer)
    shine_draw.polygon([(2, 2), (tile_size//2, 2), (2, tile_size//2)], 
                      fill=(255, 255, 255, 30))
    
    obstacle = Image.alpha_composite(obstacle, shine_layer)
    obstacle.save(os.path.join(IMAGE_PATH, 'obstacle.png'))

    # Create enhanced portals with dynamic glow
    portal_colors = [(0, 0, 255), (128, 0, 128)]
    for i, color in enumerate(portal_colors):
        portal = Image.new('RGBA', (tile_size, tile_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(portal)
        
        # Create multiple layers of glow
        for radius in range(tile_size//2, 0, -2):
            alpha = int(255 * (radius/(tile_size//2)))
            glow_color = (*color, alpha)
            draw.ellipse([tile_size//2 - radius, tile_size//2 - radius,
                         tile_size//2 + radius, tile_size//2 + radius],
                        fill=glow_color)
        
        # Add central bright spot
        draw.ellipse([tile_size//2 - 2, tile_size//2 - 2,
                     tile_size//2 + 2, tile_size//2 + 2],
                    fill=(255, 255, 255, 200))
        
        portal = portal.filter(ImageFilter.GaussianBlur(1))
        portal.save(os.path.join(IMAGE_PATH, f'portal_{i+1}.png'))

def create_food_asset():
    """Create enhanced animated food orb"""
    size = GRID_SIZE
    food = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(food)
    
    # Create multi-layered glow effect
    colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0)]
    for i, color in enumerate(colors):
        for radius in range(size//2, size//4, -2):
            alpha = int(255 * (radius/(size//2)))
            glow_color = (*color, alpha)
            offset = i * 2
            draw.ellipse([size//2 - radius + offset, size//2 - radius + offset,
                         size//2 + radius - offset, size//2 + radius - offset],
                        fill=glow_color)
    
    # Add bright center
    draw.ellipse([size//2 - 3, size//2 - 3, size//2 + 3, size//2 + 3], 
                 fill=(255, 255, 255, 255))
    
    # Apply final glow effect
    food = food.filter(ImageFilter.GaussianBlur(1))
    food.save(os.path.join(IMAGE_PATH, 'food.png'))

def create_ui_assets():
    """Create modern UI elements with enhanced styling"""
    button_styles = {
        'primary': {
            'base': (41, 128, 185),
            'hover': (52, 152, 219),
            'border': (25, 79, 114)
        },
        'secondary': {
            'base': (52, 73, 94),
            'hover': (75, 101, 132),
            'border': (32, 45, 58)
        },
        'danger': {
            'base': (192, 57, 43),
            'hover': (231, 76, 60),
            'border': (146, 43, 33)
        },
        'success': {
            'base': (39, 174, 96),
            'hover': (46, 204, 113),
            'border': (27, 128, 71)
        }
    }

    button_width = 200
    button_height = 40
    corner_radius = 5

    for style_name, colors in button_styles.items():
        # Create normal button
        button = Image.new('RGBA', (button_width, button_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(button)
        
        # Draw rounded rectangle
        draw.rounded_rectangle([0, 0, button_width, button_height], 
                             corner_radius, fill=colors['base'])
        
        # Add gradient effect
        gradient = Image.new('RGBA', (button_width, button_height//2), (255, 255, 255, 30))
        button.paste(gradient, (0, 0), gradient)
        
        # Add border
        draw.rounded_rectangle([0, 0, button_width, button_height], 
                             corner_radius, outline=colors['border'], width=2)
        
        # Save normal state
        button.save(os.path.join(IMAGE_PATH, f'button_{style_name}_normal.png'))
        
        # Create hover state
        hover = button.copy()
        draw = ImageDraw.Draw(hover)
        draw.rounded_rectangle([0, 0, button_width, button_height], 
                             corner_radius, fill=colors['hover'])
        
        # Add enhanced hover effect
        gradient = Image.new('RGBA', (button_width, button_height//2), (255, 255, 255, 50))
        hover.paste(gradient, (0, 0), gradient)
        
        # Add glow effect
        hover = hover.filter(ImageFilter.GaussianBlur(0.5))
        
        hover.save(os.path.join(IMAGE_PATH, f'button_{style_name}_hover.png'))

def download_font():
    """Download modern font for UI"""
    font_url = "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf"
    font_path = os.path.join(FONT_PATH, "PressStart2P.ttf")
    
    if not os.path.exists(FONT_PATH):
        os.makedirs(FONT_PATH)
    
    try:
        urllib.request.urlretrieve(font_url, font_path)
    except:
        print("Could not download font, using system default")

def generate_assets():
    """Generate all game assets"""
    print("Downloading sounds...")
    download_sounds()
    
    print("Generating snake assets...")
    create_snake_assets()
    
    print("Generating map assets...")
    create_map_assets()
    
    print("Generating food asset...")
    create_food_asset()
    
    print("Generating UI assets...")
    create_ui_assets()
    
    print("Downloading font...")
    download_font()
    
    print("Asset generation complete!")

if __name__ == "__main__":
    generate_assets() 