import os
import pygame
from .bird import Bird
from .pipe import Pipe

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")

DIFFICULTIES = {
    "easy": {"speed": 3, "gap": 180, "interval": 100},
    "medium": {"speed": 4, "gap": 150, "interval": 90},
    "hard": {"speed": 6, "gap": 120, "interval": 75},
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.menu_title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.menu_font = pygame.font.SysFont("Arial", 22)

        self._init_sounds()
        self.reset_game("medium")

    def _init_sounds(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass

        self.sound_flap = self._load_sound("flap.wav")
        self.sound_score = self._load_sound("score.wav")
        self.sound_die = self._load_sound("die.wav")

    def _load_sound(self, filename):
        path = os.path.join(SOUNDS_DIR, filename)
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception:
                return None
        return None

    def play_sound(self, sound):
        if sound and pygame.mixer.get_init():
            try:
                sound.play()
            except Exception:
                pass

    def trigger_game_over(self):
        if not self.game_over:
            self.game_over = True
            self.play_sound(self.sound_die)

    def reset_game(self, difficulty="medium"):
        self.difficulty = difficulty
        settings = DIFFICULTIES.get(difficulty, DIFFICULTIES["medium"])
        self.pipe_speed = settings["speed"]
        self.pipe_gap = settings["gap"]
        self.pipe_interval = settings["interval"]

        self.bird = Bird(self.width // 4, self.height // 2)
        self._spawn_timer = 0
        self.pipes = [Pipe(self.width + 100, self.height, gap=self.pipe_gap, speed=self.pipe_speed)]

        self.score = 0
        self.game_over = False

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1, pygame.K_e):
                    self.reset_game("easy")
                elif event.key in (pygame.K_2, pygame.K_KP2, pygame.K_m):
                    self.reset_game("medium")
                elif event.key in (pygame.K_3, pygame.K_KP3, pygame.K_h):
                    self.reset_game("hard")
                elif event.key in (pygame.K_4, pygame.K_KP4, pygame.K_q, pygame.K_ESCAPE):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.bird.flap()
            self.play_sound(self.sound_flap)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()
            self.play_sound(self.sound_flap)

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.bird.update()

        # Check ceiling collision
        if self.bird.y - self.bird.radius <= 0:
            self.bird.y = self.bird.radius
            self.trigger_game_over()
            return

        # Check ground collision
        if self.bird.y + self.bird.radius >= self.height:
            self.bird.y = self.height - self.bird.radius
            self.trigger_game_over()
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(Pipe(self.width, self.height, gap=self.pipe_gap, speed=self.pipe_speed))

        for pipe in self.pipes:
            pipe.move()

            # Check collision against pipe rects using the bird's full bounding rect
            if pipe.collides_with(self.bird):
                self.trigger_game_over()
                return

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.play_sound(self.sound_score)

        self.pipes = [p for p in self.pipes if not p.off_screen()]


    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            # Semi-transparent overlay to dim the scene
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            # "GAME OVER" message
            game_over_surf = self.game_over_font.render("GAME OVER", True, (255, 60, 60))
            game_over_rect = game_over_surf.get_rect(center=(self.width // 2, 170))
            screen.blit(game_over_surf, game_over_rect)

            # Final score message
            final_score_surf = self.font.render(f"Final Score: {self.score}", True, WHITE)
            final_score_rect = final_score_surf.get_rect(center=(self.width // 2, 230))
            screen.blit(final_score_surf, final_score_rect)

            # Replay Menu Title
            menu_title_surf = self.menu_title_font.render("Select Difficulty to Replay:", True, (255, 215, 0))
            menu_title_rect = menu_title_surf.get_rect(center=(self.width // 2, 310))
            screen.blit(menu_title_surf, menu_title_rect)

            # Menu Options
            options = [
                ("[1] Easy    (Speed 3, Gap 180)", (100, 255, 100), 365),
                ("[2] Medium  (Speed 4, Gap 150)", (255, 255, 255), 415),
                ("[3] Hard    (Speed 6, Gap 120)", (255, 120, 120), 465),
                ("[4] Exit    (Press 4 or ESC)", (180, 180, 180), 525),
            ]

            for text, color, y_pos in options:
                opt_surf = self.menu_font.render(text, True, color)
                opt_rect = opt_surf.get_rect(center=(self.width // 2, y_pos))
                screen.blit(opt_surf, opt_rect)


