import pygame
import sys
import random
import numpy as np  # Required for generating sound waves

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound effects

# Load background music
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.3)  # Set volume
pygame.mixer.music.play(-1)  # Loop indefinitely

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Fonts
pygame.font.init()
TITLE_FONT = pygame.font.Font(None, 74)
MENU_FONT = pygame.font.Font(None, 36)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("LiteBike")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Player and CPU settings
PLAYER_SPEED = 10
CPU_SPEED = 10
GRID_SIZE = 10

# High score file
HIGH_SCORE_FILE = "highscores.txt"

def load_high_scores():
    """Load high scores from a file. Create the file if it doesn't exist."""
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            scores = [line.strip().split(",") for line in file.readlines()]
            return [(name, int(score)) for name, score in scores]
    except FileNotFoundError:
        # Create the file if it doesn't exist
        with open(HIGH_SCORE_FILE, "w") as file:
            pass  # Create an empty file
        return []

def save_high_scores(high_scores):
    """Save high scores to a file."""
    with open(HIGH_SCORE_FILE, "w") as file:
        for name, score in high_scores:
            file.write(f"{name},{score}\n")

def draw_high_scores(high_scores):
    """Display the high scores on the start screen."""
    y_offset = SCREEN_HEIGHT // 2 + 50
    for i, (name, score) in enumerate(high_scores[:5]):  # Show top 5 scores
        score_text = MENU_FONT.render(f"{i + 1}. {name}: {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, y_offset))
        y_offset += 30

# Function to generate a tone
def generate_tone(frequency, duration, volume=0.5, sample_rate=44100):
    """Generate a tone with a given frequency, duration, and volume."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Sine wave
    wave = (wave * 32767).astype(np.int16)  # Convert to 16-bit PCM format

    # Make the array 2-dimensional for stereo sound
    stereo_wave = np.column_stack((wave, wave))

    sound = pygame.sndarray.make_sound(stereo_wave)
    sound.set_volume(volume)
    return sound

# Generate tones for events
start_tone = generate_tone(440, 0.5)  # A4 (440 Hz) for 0.5 seconds
win_tone = generate_tone(880, 0.5)    # A5 (880 Hz) for 0.5 seconds
lose_tone = generate_tone(220, 0.5)   # A3 (220 Hz) for 0.5 seconds
collision_tone = generate_tone(330, 0.2)  # E4 (330 Hz) for 0.2 seconds

def draw_start_screen(high_scores):
    """Display the start screen with a title, instructions, and high scores."""
    screen.fill(BLACK)

    # Title text
    title_text = TITLE_FONT.render("LiteBike", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(title_text, title_rect)

    # Instructions text
    instructions_text = MENU_FONT.render("Press ENTER to Start", True, WHITE)
    instructions_rect = instructions_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(instructions_text, instructions_rect)

    # High scores
    draw_high_scores(high_scores)

    pygame.display.flip()

def input_name(score):
    """Allow the player to input a 3-character name for their score."""
    name = ""
    while True:
        screen.fill(BLACK)

        # Prompt text
        prompt_text = MENU_FONT.render("Enter Your Name (3 Letters):", True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(prompt_text, prompt_rect)

        # Display current name
        name_text = TITLE_FONT.render(name, True, GREEN)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(name_text, name_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(name) == 3:
                    return name  # Return the name when Enter is pressed
                elif event.key == pygame.K_BACKSPACE and len(name) > 0:
                    name = name[:-1]  # Remove the last character
                elif len(name) < 3 and event.unicode.isalpha():
                    name += event.unicode.upper()  # Add a new character

def draw_score(score):
    """Display the current score on the screen."""
    score_text = MENU_FONT.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def draw_win_screen(level, score):
    """Display the win screen with the current level and score."""
    screen.fill(BLACK)

    # Play win tone
    win_tone.play()

    # Win text
    win_text = TITLE_FONT.render("You Win!", True, GREEN)
    win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(win_text, win_rect)

    # Level text
    level_text = MENU_FONT.render(f"Level {level} Complete!", True, WHITE)
    level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(level_text, level_rect)

    # Score text
    score_text = MENU_FONT.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))
    screen.blit(score_text, score_rect)

    pygame.display.flip()
    pygame.time.wait(2000)  # Pause for 2 seconds before the next level

def draw_defeat_screen(score, high_scores):
    """Display the defeat screen, input name, update high scores, and return to the main screen."""
    # Input name
    name = input_name(score)

    # Add the new score to the high scores
    high_scores.append((name, score))
    high_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by score (descending)
    save_high_scores(high_scores)

    # Display the updated high scores
    screen.fill(BLACK)
    defeat_text = TITLE_FONT.render("Defeat!", True, RED)
    defeat_rect = defeat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(defeat_text, defeat_rect)

    draw_high_scores(high_scores)

    pygame.display.flip()
    pygame.time.wait(3000)  # Pause for 3 seconds before returning to the main menu

    # Return to the main screen
    return

def is_collision(pos, trail):
    """Check if a position collides with a trail or is out of bounds."""
    x, y = pos
    if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT:
        return True
    if pos in trail:
        return True
    return False

def get_safe_cpu_direction(cpu_pos, cpu_direction, player_trail, cpu_trail):
    """Determine a safe and strategic direction for the CPU to move."""
    possible_directions = [
        (CPU_SPEED, 0),  # Right
        (-CPU_SPEED, 0),  # Left
        (0, CPU_SPEED),  # Down
        (0, -CPU_SPEED)  # Up
    ]

    # Remove the direction that would cause the CPU to double back
    opposite_direction = (-cpu_direction[0], -cpu_direction[1])
    if opposite_direction in possible_directions:
        possible_directions.remove(opposite_direction)

    # Evaluate each direction
    direction_scores = {}
    for direction in possible_directions:
        next_pos = (cpu_pos[0] + direction[0], cpu_pos[1] + direction[1])
        if is_collision(next_pos, player_trail + cpu_trail):
            # Assign a very low score to directions that lead to collisions
            direction_scores[direction] = -1
        else:
            # Assign a score based on how open the space is in that direction
            direction_scores[direction] = evaluate_open_space(next_pos, player_trail + cpu_trail)

    # Choose the direction with the highest score
    best_direction = max(direction_scores, key=direction_scores.get)

    # If all directions are unsafe, keep moving in the current direction
    if direction_scores[best_direction] == -1:
        return cpu_direction

    return best_direction

def evaluate_open_space(pos, trail):
    """Evaluate how open the space is from a given position."""
    open_space = 0
    directions = [
        (GRID_SIZE, 0),  # Right
        (-GRID_SIZE, 0),  # Left
        (0, GRID_SIZE),  # Down
        (0, -GRID_SIZE)  # Up
    ]

    # Check each direction for open space
    for direction in directions:
        current_pos = (pos[0] + direction[0], pos[1] + direction[1])
        while not is_collision(current_pos, trail):
            open_space += 1
            current_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])

    return open_space

def predict_player_position(player_pos, player_direction, steps=5):
    """Predict the player's future position based on their current direction."""
    predicted_pos = [
        player_pos[0] + player_direction[0] * steps,
        player_pos[1] + player_direction[1] * steps
    ]
    return predicted_pos

def main_game(level, score, high_scores):
    """Main game loop."""
    running = True
    player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2]
    cpu_pos = [3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2]
    player_direction = (PLAYER_SPEED, 0)  # Start moving right
    cpu_direction = random.choice([(CPU_SPEED, 0), (-CPU_SPEED, 0), (0, CPU_SPEED), (0, -CPU_SPEED)])  # Random start
    player_trail = []
    cpu_trail = []

    # Play start tone
    start_tone.play()

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                new_direction = player_direction
                if event.key == pygame.K_UP:
                    new_direction = (0, -PLAYER_SPEED)
                elif event.key == pygame.K_DOWN:
                    new_direction = (0, PLAYER_SPEED)
                elif event.key == pygame.K_LEFT:
                    new_direction = (-PLAYER_SPEED, 0)
                elif event.key == pygame.K_RIGHT:
                    new_direction = (PLAYER_SPEED, 0)

                # Prevent doubling back
                if new_direction != (-player_direction[0], -player_direction[1]):
                    player_direction = new_direction

        # Update player position
        player_pos[0] += player_direction[0]
        player_pos[1] += player_direction[1]

        # Update CPU position
        cpu_direction = get_safe_cpu_direction(cpu_pos, cpu_direction, player_trail, cpu_trail)
        cpu_pos[0] += cpu_direction[0]
        cpu_pos[1] += cpu_direction[1]

        # Add positions to trails
        player_trail.append(tuple(player_pos))
        cpu_trail.append(tuple(cpu_pos))

        # Update score for distance traveled
        score += 1

        # Check for collisions
        if is_collision(tuple(player_pos), player_trail[:-1] + cpu_trail):
            collision_tone.play()  # Play collision tone
            return False, score  # Indicate the player lost

        if is_collision(tuple(cpu_pos), cpu_trail[:-1] + player_trail):
            collision_tone.play()  # Play collision tone
            score += 100  # Bonus for destroying a CPU bike
            return True, score  # Indicate the player won

        # Clear the screen
        screen.fill(BLACK)

        # Draw the grid
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, WHITE, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, WHITE, (0, y), (SCREEN_WIDTH, y), 1)

        # Draw the player and CPU trails
        for segment in player_trail:
            pygame.draw.rect(screen, BLUE, (*segment, GRID_SIZE, GRID_SIZE))
        for segment in cpu_trail:
            pygame.draw.rect(screen, RED, (*segment, GRID_SIZE, GRID_SIZE))

        # Draw the player and CPU
        pygame.draw.rect(screen, GREEN, (*player_pos, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, RED, (*cpu_pos, GRID_SIZE, GRID_SIZE))

        # Draw the score
        draw_score(score)

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(15)

def main():
    """Main function to handle the start screen and game loop."""
    in_start_screen = True
    level = 1
    score = 0

    # Load high scores
    high_scores = load_high_scores()

    while in_start_screen:
        draw_start_screen(high_scores)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                in_start_screen = False

    # Start the game loop
    while True:
        player_won, score = main_game(level, score, high_scores)
        if player_won:
            level += 1
        else:
            draw_defeat_screen(score, high_scores)
            break  # Return to the main menu after defeat

    main()  # Restart the game from the main menu

if __name__ == "__main__":
    main()