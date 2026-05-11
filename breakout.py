import pygame
import sys
import time


pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_SIZE = 10
BRICK_WIDTH = 70
BRICK_HEIGHT = 20
BRICK_ROWS = 6  
BRICK_COLS = 10
FPS = 60
GAME_DURATION = 60  

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
STEEL = (112, 128, 144)  

# Brick colors by row (breakable ones)
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = 7
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        self.rect.x = self.x
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, GRAY, self.rect, 3)  # Border
    
    def reset(self):
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.rect.x = self.x

class Ball:
    def __init__(self):
        self.size = BALL_SIZE
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.dx = 4
        self.dy = -4
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
    
    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Wall collisions (left, right, top)
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.size:
            self.dx = -self.dx
        if self.y <= 0:
            self.dy = -self.dy
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        # Add a little glow effect
        pygame.draw.circle(screen, (200, 200, 200), self.rect.center, self.size//2, 2)
    
    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.dx = 4
        self.dy = -4
        self.rect.x = self.x
        self.rect.y = self.y

class Brick:
    def __init__(self, x, y, color, breakable=True):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color
        self.breakable = breakable
        self.visible = True
        self.hit_points = 2 if not breakable else 1  # Unbreakable blocks need 2 hits
    
    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)
            if self.breakable:
                pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border for breakable
            else:
                # Special pattern for unbreakable blocks
                pygame.draw.rect(screen, DARK_GRAY, self.rect, 3)
                # Draw cross pattern
                mid_x = self.rect.x + BRICK_WIDTH // 2
                mid_y = self.rect.y + BRICK_HEIGHT // 2
                pygame.draw.line(screen, DARK_GRAY, (mid_x - 10, mid_y), (mid_x + 10, mid_y), 2)
                pygame.draw.line(screen, DARK_GRAY, (mid_x, mid_y - 5), (mid_x, mid_y + 5), 2)
    
    def hit(self):
        """Return True if brick should be destroyed"""
        if not self.breakable:
            # Unbreakable blocks don't break on first hit
            self.hit_points -= 1
            if self.hit_points <= 0:
                self.visible = False
                return True
            
            self.color = STEEL
            return False
        else:
            self.visible = False
            return True

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout - Unbreakable Blocks & Timer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.score = 0
        self.lives = 3
        self.running = True
        self.paused = False
        self.game_over = False
        
        # Timer variables
        self.start_time = time.time()
        self.time_left = GAME_DURATION
        
        
        self.particles = []
        
        self.create_bricks()
    
    def create_bricks(self):
        """Create the brick wall with unbreakable blocks"""
        start_x = (SCREEN_WIDTH - (BRICK_COLS * BRICK_WIDTH)) // 2
        start_y = 50
        
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * BRICK_WIDTH
                y = start_y + row * BRICK_HEIGHT
                
                # Decide if this brick is unbreakable
                # Pattern: Unbreakable blocks in specific positions
                is_breakable = True
                
                # Create a pattern of unbreakable blocks
                # Every 3rd column in rows 2 and 4
                if (row == 2 or row == 4) and (col % 3 == 0):
                    is_breakable = False
                    color = STEEL
                # Protective wall at the edges in row 1
                elif row == 1 and (col == 0 or col == BRICK_COLS - 1):
                    is_breakable = False
                    color = STEEL
                # Center cluster in row 3
                elif row == 3 and (col == 4 or col == 5):
                    is_breakable = False
                    color = STEEL
                else:
                    color = BRICK_COLORS[row % len(BRICK_COLORS)]
                
                brick = Brick(x, y, color, is_breakable)
                self.bricks.append(brick)
    
    def create_particles(self, x, y, color):
        """Create particle effect when brick breaks"""
        for _ in range(8):
            self.particles.append({
                'x': x + BRICK_WIDTH // 2,
                'y': y + BRICK_HEIGHT // 2,
                'dx': (pygame.time.get_ticks() % 100 - 50) / 10,
                'dy': (pygame.time.get_ticks() % 100 - 50) / 10,
                'life': 30,
                'color': color
            })
    
    def update_particles(self):
        """Update and remove particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """Draw particle effects"""
        for particle in self.particles:
            alpha = particle['life'] / 30
            size = int(3 * alpha)
            if size > 0:
                pygame.draw.circle(self.screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), size)
    
    def handle_collisions(self):
        # Ball vs Paddle
        if self.ball.rect.colliderect(self.paddle.rect):
            # Calculate offset from paddle center to change ball angle
            offset = (self.ball.rect.centerx - self.paddle.rect.centerx) / (self.paddle.width / 2)
            self.ball.dx = offset * 5
            self.ball.dy = -abs(self.ball.dy)
            # Add a bit of speed variation
            self.ball.dx = max(-7, min(7, self.ball.dx))
        
        # Ball vs Bricks
        for brick in self.bricks:
            if brick.visible and self.ball.rect.colliderect(brick.rect):
                # Add particle effect
                self.create_particles(brick.rect.x, brick.rect.y, brick.color)
                
                # Handle brick hit
                destroyed = brick.hit()
                
                if destroyed:
                    if brick.breakable:
                        # Breakable blocks give 10 points
                        self.score += 10
                    else:
                        # Unbreakable blocks give 20 points (bonus)
                        self.score += 20
                
                # Reverse ball direction
                self.ball.dy = -self.ball.dy
                break  # Only hit one brick per frame
        
        # Remove destroyed bricks
        self.bricks = [brick for brick in self.bricks if brick.visible]
    
    def check_game_state(self):
        # Update timer
        if not self.game_over and not self.paused:
            self.time_left = max(0, GAME_DURATION - (time.time() - self.start_time))
            
            # Time's up!
            if self.time_left <= 0:
                self.game_over = True
        
        # Ball lost (bottom)
        if self.ball.y >= SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.paddle.reset()
                self.ball.reset()
                # Pause briefly after losing a life
                pygame.time.wait(500)
        
        # Win condition
        # Check if only unbreakable blocks remain
        breakable_remaining = any(brick.breakable for brick in self.bricks)
        if not breakable_remaining and len(self.bricks) > 0:
            # Only unbreakable blocks left - player wins!
            self.game_over = True
        elif len(self.bricks) == 0:
            # All blocks destroyed
            self.game_over = True
    
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives (draw as hearts or number)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        
        # Timer with progress bar
        timer_text = self.font.render(f"Time: {int(self.time_left)}s", True, WHITE)
        self.screen.blit(timer_text, (SCREEN_WIDTH // 2 - 40, 10))
        
        # Timer progress bar
        bar_width = 200
        bar_height = 10
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 45
        progress = self.time_left / GAME_DURATION
        
        # Background of progress bar
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        # Progress fill
        if progress > 0.5:
            color = GREEN
        elif progress > 0.25:
            color = YELLOW
        else:
            color = RED
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, int(bar_width * progress), bar_height))
        
        # Instructions
        if not self.game_over:
            controls_text = self.small_font.render("A D to move | SPACE to pause | Esc to QUIT", True, GRAY)
            self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
        
        # Pause text
        if self.paused and not self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.big_font.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(pause_text, text_rect)
            
            resume_text = self.small_font.render("Press SPACE to resume", True, WHITE)
            resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(resume_text, resume_rect)
        
        # Game Over text
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Determine win/loss message
            breakable_remaining = any(brick.breakable for brick in self.bricks)
            if len(self.bricks) == 0:
                message = f" PERFECT VICTORY! "
                sub_message = f"All blocks destroyed! Final Score: {self.score}"
            elif not breakable_remaining and len(self.bricks) > 0:
                message = f" YOU WIN! "
                sub_message = f"You cleared all breakable blocks! Score: {self.score}"
            elif self.time_left <= 0:
                message = f" TIME'S UP! "
                sub_message = f"Final Score: {self.score}"
            else:
                message = f" GAME OVER "
                sub_message = f"Final Score: {self.score}"
            
            game_over_text = self.big_font.render(message, True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
            self.screen.blit(game_over_text, text_rect)
            
            score_text = self.font.render(sub_message, True, YELLOW)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.small_font.render("Press R to restart | Q to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        """Reset entire game"""
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paused = False
        self.particles = []
        self.start_time = time.time()
        self.time_left = GAME_DURATION
        self.create_bricks()
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_over:
                        self.paused = not self.paused
                    
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    
                    if event.key == pygame.K_q and self.game_over:
                        self.running = False
                    
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Game logic (only if not paused and not game over)
            if not self.paused and not self.game_over:
                # Handle paddle movement
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    self.paddle.move("left")
                if keys[pygame.K_d]:
                    self.paddle.move("right")
                
                # Update ball position
                self.ball.move()
                
                # Update particles
                self.update_particles()
                
                # Check collisions
                self.handle_collisions()
                
                # Check win/loss
                self.check_game_state()
            
            # Drawing
            self.screen.fill(BLACK)
            
            # Draw game elements
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            
            for brick in self.bricks:
                brick.draw(self.screen)
            
            self.draw_particles()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()