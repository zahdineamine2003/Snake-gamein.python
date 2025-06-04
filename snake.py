import pygame
from config import *
import random
from collections import deque
import os
import math

class Snake:
    def __init__(self, x, y):
        self.reset(x, y)
        self.skin = SnakeSkin.CLASSIC
        self.evolution_level = Evolution.BASIC
        self.abilities = {
            'teleport': {'unlocked': False, 'cooldown': 0},
            'dash': {'unlocked': False, 'cooldown': 0},
            'clone': {'unlocked': False, 'cooldown': 0}
        }
        self.load_assets()
        self.load_sounds()
        self.effects = []  # List to store visual effects
        
    def load_assets(self):
        self.assets = {}
        for skin in SnakeSkin:
            self.assets[skin] = {
                'head': pygame.image.load(os.path.join(IMAGE_PATH, f'snake_head_{skin.value}.png')).convert_alpha(),
                'body': pygame.image.load(os.path.join(IMAGE_PATH, f'snake_body_{skin.value}.png')).convert_alpha()
            }

    def load_sounds(self):
        self.sounds = {}
        sound_files = {
            'eat': 'eat.wav',
            'die': 'die.wav',
            'teleport': 'teleport.wav',
            'dash': 'dash.wav',
            'clone': 'clone.wav',
            'evolve': 'evolve.wav'
        }
        
        for sound_name, filename in sound_files.items():
            try:
                sound_path = os.path.join(SOUND_PATH, filename)
                self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                self.sounds[sound_name].set_volume(SOUND_VOLUME)
            except:
                print(f"Could not load sound: {filename}")

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def reset(self, x, y):
        self.length = INITIAL_SNAKE_LENGTH
        self.positions = deque([(x, y)])
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.speed = INITIAL_SPEED
        self.growing = False
        self.alive = True
        self.last_move_time = pygame.time.get_ticks()
        self.effects = []
        
    def update(self, current_time):
        # Update cooldowns
        for ability in self.abilities.values():
            if ability['cooldown'] > 0:
                ability['cooldown'] = max(0, ability['cooldown'] - (current_time - self.last_move_time))

        # Update visual effects
        self.effects = [effect for effect in self.effects if effect['duration'] > 0]
        for effect in self.effects:
            effect['duration'] -= current_time - self.last_move_time

        # Check if it's time to move
        move_delay = 1000 // self.speed
        if current_time - self.last_move_time >= move_delay:
            self.direction = self.next_direction
            self.move()
            self.last_move_time = current_time

    def move(self):
        if not self.alive:
            return

        # Calculate new head position
        current_head = self.positions[0]
        dx, dy = self.direction.value
        new_x = (current_head[0] + dx) % GRID_WIDTH  # Wrap around horizontally
        new_y = (current_head[1] + dy) % GRID_HEIGHT # Wrap around vertically
        new_head = (new_x, new_y)

        # Check for self collision
        if new_head in list(self.positions)[1:]:
            self.alive = False
            self.play_sound('die')
            self.add_effect('death', current_head)
            return

        # Add new head
        self.positions.appendleft(new_head)

        # Remove tail if not growing
        if not self.growing:
            self.positions.pop()
        else:
            self.growing = False

    def grow(self):
        self.growing = True
        self.length += 1
        self.score += POINTS_PER_FOOD
        self.speed = min(MAX_SPEED, self.speed + SPEED_INCREMENT)
        self.play_sound('eat')
        self.add_effect('eat', self.positions[0])
        self.check_evolution()

    def add_effect(self, effect_type, position):
        if effect_type == 'eat':
            self.effects.append({
                'type': 'eat',
                'position': position,
                'duration': 500,
                'radius': 0
            })
        elif effect_type == 'death':
            self.effects.append({
                'type': 'death',
                'position': position,
                'duration': 1000,
                'radius': 0
            })
        elif effect_type == 'teleport':
            self.effects.append({
                'type': 'teleport',
                'position': position,
                'duration': 300,
                'radius': GRID_SIZE
            })
        elif effect_type == 'dash':
            self.effects.append({
                'type': 'dash',
                'position': position,
                'duration': 200,
                'particles': [(random.randint(-10, 10), random.randint(-10, 10)) for _ in range(10)]
            })

    def is_valid_position(self, pos):
        # All positions are valid with wrap-around
        return True

    def check_evolution(self):
        if self.score >= EVOLUTION_POINTS:
            if self.evolution_level == Evolution.BASIC:
                self.evolve_to_teleporter()
            elif self.evolution_level == Evolution.TELEPORTER:
                self.evolve_to_dasher()
            elif self.evolution_level == Evolution.DASHER:
                self.evolve_to_cloner()

    def evolve_to_teleporter(self):
        self.evolution_level = Evolution.TELEPORTER
        self.abilities['teleport']['unlocked'] = True
        self.play_sound('evolve')
        self.add_effect('evolve', self.positions[0])

    def evolve_to_dasher(self):
        self.evolution_level = Evolution.DASHER
        self.abilities['dash']['unlocked'] = True
        self.play_sound('evolve')
        self.add_effect('evolve', self.positions[0])

    def evolve_to_cloner(self):
        self.evolution_level = Evolution.CLONER
        self.abilities['clone']['unlocked'] = True
        self.play_sound('evolve')
        self.add_effect('evolve', self.positions[0])

    def teleport(self):
        if not self.abilities['teleport']['unlocked'] or self.abilities['teleport']['cooldown'] > 0:
            return False

        # Find valid teleport location
        valid_positions = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pos = (x, y)
                if pos not in self.positions and self.is_valid_position(pos):
                    valid_positions.append(pos)

        if valid_positions:
            old_head = self.positions[0]
            new_head = random.choice(valid_positions)
            self.positions.appendleft(new_head)
            self.positions.pop()
            self.abilities['teleport']['cooldown'] = TELEPORT_COOLDOWN
            self.play_sound('teleport')
            self.add_effect('teleport', old_head)
            self.add_effect('teleport', new_head)
            return True
        return False

    def dash(self):
        if not self.abilities['dash']['unlocked'] or self.abilities['dash']['cooldown'] > 0:
            return False

        # Dash 3 spaces in current direction
        dx, dy = self.direction.value
        current_head = self.positions[0]
        new_head = (current_head[0] + dx * 3, current_head[1] + dy * 3)

        if self.is_valid_position(new_head) and new_head not in self.positions:
            self.positions.appendleft(new_head)
            self.positions.pop()
            self.abilities['dash']['cooldown'] = DASH_COOLDOWN
            self.play_sound('dash')
            self.add_effect('dash', current_head)
            return True
        return False

    def clone(self):
        if not self.abilities['clone']['unlocked'] or self.abilities['clone']['cooldown'] > 0:
            return False

        # Create a temporary clone that lasts for a few seconds
        clone_positions = list(self.positions)
        self.abilities['clone']['cooldown'] = CLONE_COOLDOWN
        self.play_sound('clone')
        self.add_effect('clone', self.positions[0])
        return clone_positions

    def change_skin(self, new_skin):
        if isinstance(new_skin, SnakeSkin):
            self.skin = new_skin

    def draw(self, screen):
        # Draw snake segments first
        for i, pos in enumerate(self.positions):
            x, y = pos
            rect = pygame.Rect(
                x * GRID_SIZE,
                y * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            
            # Use assets if available
            try:
                if i == 0:  # Head
                    # Rotate head image based on direction
                    rotation = {
                        Direction.UP: 0,
                        Direction.RIGHT: 270,
                        Direction.DOWN: 180,
                        Direction.LEFT: 90
                    }[self.direction]
                    
                    head_img = pygame.transform.scale(self.assets[self.skin]['head'], 
                                                    (GRID_SIZE, GRID_SIZE))
                    head_img = pygame.transform.rotate(head_img, rotation)
                    screen.blit(head_img, rect)
                else:  # Body
                    body_img = pygame.transform.scale(self.assets[self.skin]['body'], 
                                                   (GRID_SIZE, GRID_SIZE))
                    screen.blit(body_img, rect)
            except:
                # Fallback to basic rendering if assets fail
                color = self.get_segment_color(i)
                pygame.draw.rect(screen, color, rect)
                
                # Draw eyes on head segment
                if i == 0:
                    eye_size = GRID_SIZE // 6
                    eye_offset = GRID_SIZE // 4
                    
                    # Base eye positions (facing right)
                    left_eye = (rect.left + eye_offset, rect.top + eye_offset)
                    right_eye = (rect.left + eye_offset, rect.bottom - eye_offset - eye_size)
                    
                    # Adjust eye positions based on direction
                    if self.direction == Direction.UP:
                        left_eye = (rect.left + eye_offset, rect.top + eye_offset)
                        right_eye = (rect.right - eye_offset - eye_size, rect.top + eye_offset)
                    elif self.direction == Direction.DOWN:
                        left_eye = (rect.left + eye_offset, rect.bottom - eye_offset - eye_size)
                        right_eye = (rect.right - eye_offset - eye_size, rect.bottom - eye_offset - eye_size)
                    elif self.direction == Direction.LEFT:
                        left_eye = (rect.left + eye_offset, rect.top + eye_offset)
                        right_eye = (rect.left + eye_offset, rect.bottom - eye_offset - eye_size)
                    elif self.direction == Direction.RIGHT:
                        left_eye = (rect.right - eye_offset - eye_size, rect.top + eye_offset)
                        right_eye = (rect.right - eye_offset - eye_size, rect.bottom - eye_offset - eye_size)
                    
                    pygame.draw.rect(screen, WHITE, (*left_eye, eye_size, eye_size))
                    pygame.draw.rect(screen, WHITE, (*right_eye, eye_size, eye_size))

        # Draw effects
        for effect in self.effects:
            if effect['type'] == 'eat':
                radius = int((500 - effect['duration']) / 500 * GRID_SIZE)
                alpha = int(effect['duration'] / 500 * 255)
                effect_surface = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, (255, 255, 0), 
                                (GRID_SIZE, GRID_SIZE), radius)
                effect_surface.set_alpha(alpha)
                screen.blit(effect_surface, 
                          (effect['position'][0] * GRID_SIZE - GRID_SIZE//2,
                           effect['position'][1] * GRID_SIZE - GRID_SIZE//2))
            
            elif effect['type'] == 'death':
                radius = int((1000 - effect['duration']) / 1000 * GRID_SIZE * 2)
                alpha = int(effect['duration'] / 1000 * 255)
                effect_surface = pygame.Surface((GRID_SIZE * 4, GRID_SIZE * 4), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, (255, 0, 0), 
                                (GRID_SIZE * 2, GRID_SIZE * 2), radius)
                effect_surface.set_alpha(alpha)
                screen.blit(effect_surface, 
                          (effect['position'][0] * GRID_SIZE - GRID_SIZE,
                           effect['position'][1] * GRID_SIZE - GRID_SIZE))
            
            elif effect['type'] == 'teleport':
                alpha = int(effect['duration'] / 300 * 255)
                effect_surface = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, (0, 255, 255), 
                                (GRID_SIZE, GRID_SIZE), effect['radius'])
                effect_surface.set_alpha(alpha)
                screen.blit(effect_surface, 
                          (effect['position'][0] * GRID_SIZE - GRID_SIZE//2,
                           effect['position'][1] * GRID_SIZE - GRID_SIZE//2))
            
            elif effect['type'] == 'dash':
                alpha = int(effect['duration'] / 200 * 255)
                for particle in effect['particles']:
                    x = effect['position'][0] * GRID_SIZE + particle[0]
                    y = effect['position'][1] * GRID_SIZE + particle[1]
                    particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surface, (0, 255, 255), (2, 2), 2)
                    particle_surface.set_alpha(alpha)
                    screen.blit(particle_surface, (x-2, y-2))

    def get_segment_color(self, index):
        # This method is kept for fallback if assets fail to load
        if self.skin == SnakeSkin.CLASSIC:
            return GREEN if index == 0 else (0, 200, 0)
        elif self.skin == SnakeSkin.NEON:
            return (0, 255, 255) if index == 0 else (0, 200, 200)
        elif self.skin == SnakeSkin.PIXEL:
            return BLUE if index == 0 else (0, 0, 200)
        elif self.skin == SnakeSkin.RAINBOW:
            hue = (index * 15) % 360
            return pygame.Color(0)  # This will be replaced with HSV conversion
        return GREEN  # Default fallback 