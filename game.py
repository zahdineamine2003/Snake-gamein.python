import pygame
import sys
from config import *
from snake import Snake
from map import Map
from menu import Menu

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Evolution")
        self.clock = pygame.time.Clock()
        
        self.menu = Menu()
        self.reset_game()
        self.game_state = "menu"  # menu, playing, paused, game_over
        
    def reset_game(self):
        """Reset the game state"""
        self.snake = Snake(GRID_WIDTH // 4, GRID_HEIGHT // 2)
        self.map = Map()
        self.paused = False
        
    def handle_input(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if self.game_state == "menu":
                menu_action = self.menu.handle_input(event)
                if menu_action:
                    if menu_action["action"] == "start_game":
                        self.game_state = "playing"
                    elif menu_action["action"] == "quit":
                        return False
                    elif menu_action["action"] == "change_skin":
                        self.snake.change_skin(menu_action["skin"])
                    elif menu_action["action"] == "change_map":
                        self.map = Map(menu_action["map_type"])
                        
            elif self.game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "paused"
                    elif event.key == pygame.K_SPACE:
                        self.snake.teleport()
                    elif event.key == pygame.K_LSHIFT:
                        self.snake.dash()
                    elif event.key == pygame.K_c:
                        self.snake.clone()
                    else:
                        # Snake direction controls
                        direction_keys = {
                            pygame.K_UP: Direction.UP,
                            pygame.K_DOWN: Direction.DOWN,
                            pygame.K_LEFT: Direction.LEFT,
                            pygame.K_RIGHT: Direction.RIGHT,
                            pygame.K_w: Direction.UP,
                            pygame.K_s: Direction.DOWN,
                            pygame.K_a: Direction.LEFT,
                            pygame.K_d: Direction.RIGHT
                        }
                        if event.key in direction_keys:
                            new_dir = direction_keys[event.key]
                            # Prevent 180-degree turns
                            if (self.snake.direction.value[0] + new_dir.value[0] != 0 or
                                self.snake.direction.value[1] + new_dir.value[1] != 0):
                                self.snake.next_direction = new_dir
                                
            elif self.game_state == "paused":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "playing"
                    elif event.key == pygame.K_m:
                        self.game_state = "menu"
                        
            elif self.game_state == "game_over":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.menu.add_score(self.snake.score)
                        self.reset_game()
                        self.game_state = "menu"
                    elif event.key == pygame.K_ESCAPE:
                        return False
                        
        return True

    def update(self):
        """Update game state"""
        if self.game_state == "playing":
            current_time = pygame.time.get_ticks()
            self.snake.update(current_time)
            
            # Check if snake ate food
            if self.snake.positions[0] == self.map.food_position:
                self.snake.grow()
                self.map.spawn_food()
            
            # Check for portal teleportation
            portal_exit = self.map.check_portal(self.snake.positions[0])
            if portal_exit:
                self.snake.positions[0] = portal_exit
            
            # Check for collisions with obstacles
            if self.map.is_collision(self.snake.positions[0]):
                self.snake.alive = False
            
            # Check if snake died
            if not self.snake.alive:
                self.game_state = "game_over"

    def draw(self):
        """Draw the game"""
        self.screen.fill(BLACK)
        
        if self.game_state == "menu":
            self.menu.draw(self.screen)
            
        elif self.game_state in ["playing", "paused", "game_over"]:
            # Draw game elements
            self.map.draw(self.screen)
            self.snake.draw(self.screen)
            
            # Draw score
            score_text = pygame.font.Font(None, FONT_SIZE_MEDIUM).render(
                f"Score: {self.snake.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            # Draw evolution level
            evolution_text = pygame.font.Font(None, FONT_SIZE_MEDIUM).render(
                f"Evolution: {self.snake.evolution_level.name}", True, WHITE)
            self.screen.blit(evolution_text, (10, 40))
            
            # Draw ability cooldowns
            y_offset = 70
            for ability_name, ability in self.snake.abilities.items():
                if ability['unlocked']:
                    cooldown = ability['cooldown'] / 1000  # Convert to seconds
                    color = RED if cooldown > 0 else GREEN
                    cooldown_text = pygame.font.Font(None, FONT_SIZE_SMALL).render(
                        f"{ability_name}: {cooldown:.1f}s", True, color)
                    self.screen.blit(cooldown_text, (10, y_offset))
                    y_offset += 25
            
            # Draw pause overlay
            if self.game_state == "paused":
                pause_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                pause_surface.set_alpha(128)
                pause_surface.fill(BLACK)
                self.screen.blit(pause_surface, (0, 0))
                
                pause_text = pygame.font.Font(None, FONT_SIZE_LARGE).render(
                    "PAUSED", True, WHITE)
                self.screen.blit(pause_text, 
                    (WINDOW_WIDTH//2 - pause_text.get_width()//2, 
                     WINDOW_HEIGHT//2 - pause_text.get_height()//2))
                
                help_text = pygame.font.Font(None, FONT_SIZE_SMALL).render(
                    "Press ESC to resume, M for menu", True, WHITE)
                self.screen.blit(help_text,
                    (WINDOW_WIDTH//2 - help_text.get_width()//2,
                     WINDOW_HEIGHT//2 + pause_text.get_height()))
            
            # Draw game over overlay
            elif self.game_state == "game_over":
                game_over_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                game_over_surface.set_alpha(128)
                game_over_surface.fill(BLACK)
                self.screen.blit(game_over_surface, (0, 0))
                
                game_over_text = pygame.font.Font(None, FONT_SIZE_LARGE).render(
                    "GAME OVER", True, RED)
                self.screen.blit(game_over_text,
                    (WINDOW_WIDTH//2 - game_over_text.get_width()//2,
                     WINDOW_HEIGHT//2 - game_over_text.get_height()//2))
                
                score_text = pygame.font.Font(None, FONT_SIZE_MEDIUM).render(
                    f"Final Score: {self.snake.score}", True, WHITE)
                self.screen.blit(score_text,
                    (WINDOW_WIDTH//2 - score_text.get_width()//2,
                     WINDOW_HEIGHT//2 + game_over_text.get_height()))
                
                help_text = pygame.font.Font(None, FONT_SIZE_SMALL).render(
                    "Press ENTER for menu, ESC to quit", True, WHITE)
                self.screen.blit(help_text,
                    (WINDOW_WIDTH//2 - help_text.get_width()//2,
                     WINDOW_HEIGHT//2 + game_over_text.get_height() + score_text.get_height()))
        
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 