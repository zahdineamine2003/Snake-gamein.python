import pygame
import random
from config import *
import os
import math

class Map:
    def __init__(self, map_type=MapType.EMPTY):
        self.map_type = map_type
        self.obstacles = []
        self.portals = []
        self.food_position = None
        self.load_assets()
        self.generate_map()

    def load_assets(self):
        self.assets = {
            'floor': pygame.image.load(os.path.join(IMAGE_PATH, 'floor.png')).convert_alpha(),
            'obstacle': pygame.image.load(os.path.join(IMAGE_PATH, 'obstacle.png')).convert_alpha(),
            'portal1': pygame.image.load(os.path.join(IMAGE_PATH, 'portal_1.png')).convert_alpha(),
            'portal2': pygame.image.load(os.path.join(IMAGE_PATH, 'portal_2.png')).convert_alpha(),
            'food': pygame.image.load(os.path.join(IMAGE_PATH, 'food.png')).convert_alpha()
        }

    def generate_map(self):
        self.obstacles.clear()
        self.portals.clear()

        if self.map_type == MapType.OBSTACLES:
            self._generate_obstacles()
        elif self.map_type == MapType.MAZE:
            self._generate_maze()
        elif self.map_type == MapType.PORTAL:
            self._generate_portals()

        self.spawn_food()

    def _generate_obstacles(self):
        # Clear existing obstacles
        self.obstacles.clear()
        
        # Generate a more organized pattern of obstacles
        pattern_type = random.choice(['symmetric', 'corners', 'diagonal'])
        
        if pattern_type == 'symmetric':
            # Create symmetric obstacle pattern
            for x in range(2, GRID_WIDTH - 2, 4):
                for y in range(2, GRID_HEIGHT - 2, 4):
                    if random.random() < 0.7:  # 70% chance to place obstacle
                        self.obstacles.append((x, y))
                        # Add symmetric counterpart
                        self.obstacles.append((GRID_WIDTH - 1 - x, y))
                        
        elif pattern_type == 'corners':
            # Create corner patterns with paths between them
            corner_size = 3
            # Top-left corner
            for x in range(corner_size):
                for y in range(corner_size):
                    if x + y < corner_size - 1:
                        self.obstacles.append((x + 1, y + 1))
            
            # Top-right corner
            for x in range(GRID_WIDTH - corner_size, GRID_WIDTH):
                for y in range(corner_size):
                    if (GRID_WIDTH - 1 - x) + y < corner_size - 1:
                        self.obstacles.append((x - 1, y + 1))
            
            # Bottom-left corner
            for x in range(corner_size):
                for y in range(GRID_HEIGHT - corner_size, GRID_HEIGHT):
                    if x + (GRID_HEIGHT - 1 - y) < corner_size - 1:
                        self.obstacles.append((x + 1, y - 1))
            
            # Bottom-right corner
            for x in range(GRID_WIDTH - corner_size, GRID_WIDTH):
                for y in range(GRID_HEIGHT - corner_size, GRID_HEIGHT):
                    if (GRID_WIDTH - 1 - x) + (GRID_HEIGHT - 1 - y) < corner_size - 1:
                        self.obstacles.append((x - 1, y - 1))
                        
        else:  # diagonal
            # Create diagonal patterns
            for i in range(2, min(GRID_WIDTH, GRID_HEIGHT) - 2, 3):
                if random.random() < 0.7:  # 70% chance to place diagonal
                    for offset in range(3):
                        if i + offset < min(GRID_WIDTH, GRID_HEIGHT) - 2:
                            self.obstacles.append((i + offset, i + offset))
                            self.obstacles.append((i + offset, GRID_HEIGHT - 1 - (i + offset)))

    def _generate_maze(self):
        # Generate a clearer maze pattern
        self.obstacles.clear()
        
        # Create vertical passages
        num_passages = random.randint(2, 3)
        passage_spacing = GRID_WIDTH // (num_passages + 1)
        
        for i in range(1, num_passages + 1):
            x = i * passage_spacing
            gap_start = random.randint(3, GRID_HEIGHT // 2 - 2)
            gap_end = random.randint(GRID_HEIGHT // 2 + 2, GRID_HEIGHT - 3)
            
            for y in range(GRID_HEIGHT):
                if y < gap_start or y > gap_end:
                    self.obstacles.append((x, y))
        
        # Add some horizontal connectors
        for x in range(2, GRID_WIDTH - 2, passage_spacing):
            y = random.randint(3, GRID_HEIGHT - 3)
            for dx in range(passage_spacing - 2):
                if (x + dx, y) not in self.obstacles:
                    self.obstacles.append((x + dx, y))

    def _generate_portals(self):
        # Generate clearer portal placement
        self.portals.clear()
        
        # Place portals in more strategic locations
        portal_pairs = [
            # Left-right pair
            [(2, GRID_HEIGHT//4), (GRID_WIDTH-3, GRID_HEIGHT//4)],
            # Top-bottom pair
            [(GRID_WIDTH//4, 2), (GRID_WIDTH//4, GRID_HEIGHT-3)]
        ]
        
        for pair in portal_pairs:
            self.portals.extend(pair)

    def spawn_food(self):
        valid_positions = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pos = (x, y)
                if pos not in self.obstacles and pos not in self.portals:
                    valid_positions.append(pos)

        if valid_positions:
            self.food_position = random.choice(valid_positions)

    def is_collision(self, position):
        return position in self.obstacles

    def check_portal(self, position):
        if position in self.portals:
            portal_index = self.portals.index(position)
            # If even index, teleport to next portal; if odd, teleport to previous portal
            target_index = portal_index + 1 if portal_index % 2 == 0 else portal_index - 1
            return self.portals[target_index]
        return None

    def draw(self, screen):
        # Draw play field background
        field_color_1 = (144, 238, 144)  # Light green
        field_color_2 = (152, 251, 152)  # Slightly lighter green
        
        # Draw checkered pattern
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(
                    x * GRID_SIZE,
                    y * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE
                )
                color = field_color_1 if (x + y) % 2 == 0 else field_color_2
                pygame.draw.rect(screen, color, rect)

        # Draw food with animation
        if self.food_position:
            food_x = self.food_position[0] * GRID_SIZE
            food_y = self.food_position[1] * GRID_SIZE
            # Add subtle bobbing animation
            offset = abs(math.sin(pygame.time.get_ticks() / 200)) * 2  # Reduced offset
            food_img = pygame.transform.scale(self.assets['food'], 
                (GRID_SIZE, GRID_SIZE))  # Match grid size exactly
            screen.blit(food_img, (food_x, food_y - offset))

        # Draw obstacles (if any)
        for obstacle in self.obstacles:
            obstacle_x = obstacle[0] * GRID_SIZE
            obstacle_y = obstacle[1] * GRID_SIZE
            obstacle_img = pygame.transform.scale(self.assets['obstacle'], 
                (GRID_SIZE, GRID_SIZE))  # Match grid size exactly
            screen.blit(obstacle_img, (obstacle_x, obstacle_y))

        # Draw portals (if any)
        for i, portal in enumerate(self.portals):
            portal_x = portal[0] * GRID_SIZE
            portal_y = portal[1] * GRID_SIZE
            portal_img = self.assets['portal1'] if i % 2 == 0 else self.assets['portal2']
            portal_img = pygame.transform.scale(portal_img, 
                (GRID_SIZE, GRID_SIZE))  # Match grid size exactly
            screen.blit(portal_img, (portal_x, portal_y)) 