import pygame
import json
import os
import math
import random
from config import *

class Star:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT)
        self.speed = random.randint(1, 3)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(50, 255)

    def update(self):
        self.y = (self.y + self.speed) % WINDOW_HEIGHT
        self.brightness = max(50, min(255, self.brightness + random.randint(-10, 10)))

    def draw(self, screen):
        pygame.draw.circle(screen, (self.brightness, self.brightness, self.brightness), 
                         (self.x, self.y), self.size)

class BackgroundSnake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # Start from either left or right side
        self.direction = random.choice(['left', 'right'])
        if self.direction == 'left':
            self.x = WINDOW_WIDTH + 50
            self.speed = -2
        else:
            self.x = -50
            self.speed = 2
        self.y = random.randint(100, WINDOW_HEIGHT - 100)
        self.length = random.randint(15, 25)
        self.positions = []
        self.active = True
        
    def update(self):
        self.x += self.speed
        # Store last 'length' positions for trail
        self.positions.insert(0, (self.x, self.y + math.sin(self.x * 0.02) * 20))
        self.positions = self.positions[:self.length]
        
        # Check if snake has left the screen
        if (self.direction == 'left' and self.x < -100) or \
           (self.direction == 'right' and self.x > WINDOW_WIDTH + 100):
            self.active = False

    def draw(self, screen):
        # Draw snake segments with fading opacity
        for i, pos in enumerate(self.positions):
            opacity = int(255 * (1 - i/self.length))
            color = (0, opacity//2, 0)  # Dark green with fading opacity
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 5)

class MenuBackground:
    def __init__(self):
        self.stars = [Star() for _ in range(50)]
        self.snakes = []
        self.snake_timer = 0
        self.snake_interval = 300  # New snake every 300 frames
        
    def update(self):
        # Update stars
        for star in self.stars:
            star.update()
            
        # Update snake timer and create new snakes
        self.snake_timer += 1
        if self.snake_timer >= self.snake_interval:
            self.snake_timer = 0
            self.snakes.append(BackgroundSnake())
            
        # Update existing snakes and remove inactive ones
        self.snakes = [snake for snake in self.snakes if snake.active]
        for snake in self.snakes:
            snake.update()
            
    def draw(self, screen):
        screen.fill(BLACK)
        # Draw stars
        for star in self.stars:
            star.draw(screen)
        # Draw snakes
        for snake in self.snakes:
            snake.draw(screen)

class Menu:
    def __init__(self):
        self.load_assets()
        self.selected_option = 0
        self.state = "main"  # main, skins, maps, high_scores
        self.load_high_scores()
        self.load_sounds()
        self.hover_sound_played = False
        self.background = MenuBackground()

    def load_assets(self):
        # Load font
        font_path = os.path.join(FONT_PATH, "PressStart2P.ttf")
        if os.path.exists(font_path):
            self.font_large = pygame.font.Font(font_path, FONT_SIZE_LARGE)
            self.font_medium = pygame.font.Font(font_path, FONT_SIZE_MEDIUM)
        else:
            self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
            self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)

        # Load button images for each style
        self.buttons = {}
        for style in ButtonStyle:
            self.buttons[style] = {
                'normal': pygame.image.load(os.path.join(IMAGE_PATH, f'button_{style.value}_normal.png')).convert_alpha(),
                'hover': pygame.image.load(os.path.join(IMAGE_PATH, f'button_{style.value}_hover.png')).convert_alpha()
            }

    def load_sounds(self):
        self.sounds = {}
        sound_files = {
            'hover': 'hover.wav',
            'click': 'click.wav',
            'background': 'background.mp3'
        }
        
        for sound_name, filename in sound_files.items():
            try:
                sound_path = os.path.join(SOUND_PATH, filename)
                if sound_name == 'background':
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
                else:
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name].set_volume(SOUND_VOLUME)
            except:
                print(f"Could not load sound: {filename}")

        # Start background music
        try:
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except:
            print("Could not play background music")

    def load_high_scores(self):
        self.high_scores = []
        high_scores_file = os.path.join(ASSET_DIR, "high_scores.json")
        if os.path.exists(high_scores_file):
            try:
                with open(high_scores_file, 'r') as f:
                    self.high_scores = json.load(f)
            except:
                pass

    def save_high_scores(self):
        high_scores_file = os.path.join(ASSET_DIR, "high_scores.json")
        with open(high_scores_file, 'w') as f:
            json.dump(self.high_scores, f)

    def add_score(self, score):
        name = self.get_player_name()
        
        # If we have less than 4 scores, just add it
        if len(self.high_scores) < 4:
            self.high_scores.append({"name": name, "score": score})
        else:
            # Check if the new score is higher than the lowest score
            lowest_score = min(self.high_scores, key=lambda x: x["score"])
            if score > lowest_score["score"]:
                # Remove the lowest score and add the new one
                self.high_scores.remove(lowest_score)
                self.high_scores.append({"name": name, "score": score})
        
        # Sort scores and ensure only 4 entries
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:4]  # Strictly keep only top 4
        self.save_high_scores()

    def get_player_name(self):
        name = ""
        input_active = True
        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name:
                        self.play_sound('click')
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                        self.play_sound('click')
                    elif len(name) < 10 and event.unicode.isalnum():  # Allow only alphanumeric
                        name += event.unicode
                        self.play_sound('click')
            
            # Draw name input screen
            screen = pygame.display.get_surface()
            screen.fill(BLACK)
            
            title = self.font_large.render("Enter Your Name:", True, WHITE)
            name_text = self.font_medium.render(name + "_", True, WHITE)
            
            screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//3))
            screen.blit(name_text, (WINDOW_WIDTH//2 - name_text.get_width()//2, WINDOW_HEIGHT//2))
            
            pygame.display.flip()
            
        return name

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            self.play_sound('click')
            if self.state == "main":
                return self.handle_main_menu_input(event)
            elif self.state == "skins":
                return self.handle_skins_menu_input(event)
            elif self.state == "maps":
                return self.handle_maps_menu_input(event)
            elif self.state == "high_scores":
                return self.handle_high_scores_input(event)
        return None

    def handle_main_menu_input(self, event):
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % 4
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % 4
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Start Game
                return {"action": "start_game"}
            elif self.selected_option == 1:  # Skins
                self.state = "skins"
                self.selected_option = 0
            elif self.selected_option == 2:  # High Scores
                self.state = "high_scores"
                self.selected_option = 0
            elif self.selected_option == 3:  # Quit
                return {"action": "quit"}
        return None

    def handle_skins_menu_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.state = "main"
            self.selected_option = 0
        elif event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(SnakeSkin)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(SnakeSkin)
        elif event.key == pygame.K_RETURN:
            return {"action": "change_skin", "skin": list(SnakeSkin)[self.selected_option]}
        return None

    def handle_maps_menu_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.state = "main"
            self.selected_option = 0
        elif event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(MapType)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(MapType)
        elif event.key == pygame.K_RETURN:
            return {"action": "change_map", "map_type": list(MapType)[self.selected_option]}
        return None

    def handle_high_scores_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.state = "main"
            self.selected_option = 0
        return None

    def draw_button(self, screen, text, position, selected=False, style=ButtonStyle.PRIMARY):
        button_img = self.buttons[style]['hover' if selected else 'normal']
        text_surface = self.font_medium.render(text, True, WHITE)
        
        # Calculate required button width based on text
        required_width = max(text_surface.get_width() + 40, button_img.get_width())  # 40px padding
        required_height = max(text_surface.get_height() + 20, button_img.get_height())  # 20px padding
        
        # Scale button image if needed
        if required_width > button_img.get_width() or required_height > button_img.get_height():
            scaled_button = pygame.transform.scale(button_img, (required_width, required_height))
        else:
            scaled_button = button_img
        
        # Center the button horizontally
        button_x = WINDOW_WIDTH//2 - scaled_button.get_width()//2
        screen.blit(scaled_button, (button_x, position))
        
        # Center the text on the button
        text_x = button_x + (scaled_button.get_width() - text_surface.get_width())//2
        text_y = position + (scaled_button.get_height() - text_surface.get_height())//2
        screen.blit(text_surface, (text_x, text_y))

        # Play hover sound
        if selected and not self.hover_sound_played:
            self.play_sound('hover')
            self.hover_sound_played = True
        elif not selected:
            self.hover_sound_played = False

    def draw(self, screen):
        # Update and draw animated background
        self.background.update()
        self.background.draw(screen)
        
        if self.state == "main":
            self.draw_main_menu(screen)
        elif self.state == "skins":
            self.draw_skins_menu(screen)
        elif self.state == "maps":
            self.draw_maps_menu(screen)
        elif self.state == "high_scores":
            self.draw_high_scores(screen)

    def draw_main_menu(self, screen):
        # Draw animated title with glow effect
        title = self.font_large.render("Snake Evolution", True, GREEN)
        glow = self.font_large.render("Snake Evolution", True, (0, 100, 0))
        
        title_x = WINDOW_WIDTH//2 - title.get_width()//2
        title_y = WINDOW_HEIGHT//4
        
        # Animate glow based on time
        glow_offset = abs(math.sin(pygame.time.get_ticks() / 500)) * 3
        
        # Draw glow effect
        screen.blit(glow, (title_x + glow_offset, title_y + glow_offset))
        screen.blit(title, (title_x, title_y))

        # Draw menu options with different button styles
        options = [
            ("Start Game", ButtonStyle.SUCCESS),
            ("Skins", ButtonStyle.PRIMARY),
            ("High Scores", ButtonStyle.SECONDARY),
            ("Quit", ButtonStyle.DANGER)
        ]
        
        button_spacing = 60
        start_y = WINDOW_HEIGHT//2
        
        for i, (option, style) in enumerate(options):
            self.draw_button(screen, option, start_y + i * button_spacing, i == self.selected_option, style)

    def draw_skins_menu(self, screen):
        title = self.font_large.render("Select Skin", True, GREEN)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//4))

        button_spacing = 60
        start_y = WINDOW_HEIGHT//2
        
        for i, skin in enumerate(SnakeSkin):
            self.draw_button(screen, skin.value, start_y + i * button_spacing, 
                           i == self.selected_option, ButtonStyle.PRIMARY)

    def draw_maps_menu(self, screen):
        title = self.font_large.render("Select Map", True, GREEN)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//4))

        button_spacing = 60
        start_y = WINDOW_HEIGHT//2
        
        for i, map_type in enumerate(MapType):
            self.draw_button(screen, map_type.value, start_y + i * button_spacing, 
                           i == self.selected_option, ButtonStyle.PRIMARY)

    def draw_high_scores(self, screen):
        # Draw title with pixel font style
        title = self.font_large.render("High Scores", True, NEON_GREEN)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))

        # Calculate column widths and positions
        rank_width = 80
        name_width = 180
        score_width = 120
        
        total_width = rank_width + name_width + score_width
        start_x = (WINDOW_WIDTH - total_width) // 2
        
        # Draw table background
        table_y = 150
        table_height = 200  # Reduced height for 4 entries
        pygame.draw.rect(screen, (20, 20, 20), 
                        (start_x - 20, table_y - 10, 
                         total_width + 40, table_height), 
                        border_radius=10)

        # Draw table headers with bottom border
        header_y = table_y
        pygame.draw.line(screen, YELLOW, 
                        (start_x - 10, header_y + 35),
                        (start_x + total_width + 10, header_y + 35), 2)

        # Draw headers with pixel font style
        rank_header = self.font_medium.render("Rank", True, YELLOW)
        name_header = self.font_medium.render("Name", True, YELLOW)
        score_header = self.font_medium.render("Score", True, YELLOW)

        screen.blit(rank_header, (start_x + (rank_width - rank_header.get_width())//2, header_y))
        screen.blit(name_header, (start_x + rank_width + (name_width - name_header.get_width())//2, header_y))
        screen.blit(score_header, (start_x + rank_width + name_width + (score_width - score_header.get_width())//2, header_y))

        # Draw scores
        start_y = header_y + 50
        row_height = 40  # Slightly reduced row height

        for i, score in enumerate(self.high_scores):
            # Draw rank with medal color for top 3
            if i == 0:
                rank_color = GOLD
                rank_prefix = "#1"
            elif i == 1:
                rank_color = (192, 192, 192)  # Silver
                rank_prefix = "#2"
            elif i == 2:
                rank_color = (205, 127, 50)   # Bronze
                rank_prefix = "#3"
            else:
                rank_color = WHITE
                rank_prefix = "#4"
            
            # Draw with pixel font style
            rank_text = self.font_medium.render(rank_prefix, True, rank_color)
            name_text = self.font_medium.render(score["name"], True, WHITE)
            score_text = self.font_medium.render(str(score["score"]), True, WHITE)

            # Center align rank, left align name, right align score
            screen.blit(rank_text, 
                       (start_x + (rank_width - rank_text.get_width())//2, 
                        start_y + i * row_height))
            screen.blit(name_text, 
                       (start_x + rank_width + 10, 
                        start_y + i * row_height))
            screen.blit(score_text, 
                       (start_x + rank_width + name_width + score_width - score_text.get_width() - 10, 
                        start_y + i * row_height))

        # Draw back button at the bottom with pixel style
        back_y = table_y + table_height + 30
        self.draw_button(screen, "Back to Menu", back_y, 
                        self.selected_option == 0, ButtonStyle.SECONDARY) 