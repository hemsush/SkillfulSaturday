import pygame
import random
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 900, 520
FPS = 30

TITLE = "IntelliSpell – AI Word Challenge"
SCHOOL = "Motilal Forma Santana Dharma Higher Secondary School"
EVENT = "Skillful Saturday"

LIVES_PER_WORD = 3
MAX_FAILED_WORDS = 5

# Base word pool (good real words)
WORDS = [
    "school", "pencil", "teacher", "planet", "forest", "garden", "friend",
    "python", "robot", "future", "science", "energy", "library", "picture",
    "student", "computer", "keyboard", "battery", "language", "festival",
    "history", "morning", "evening", "reading", "writing", "respect",
    "courage", "holiday", "practice", "creative", "learning", "technology",
    "curiosity", "imagination", "celebrate", "together", "solution", "problem"
]

# If deck finishes, generate new unique words automatically
AUTO_GENERATE_WHEN_EMPTY = True
GENERATED_WORDS_COUNT = 60  # how many new words to add when empty
# ----------------------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ai_hint(word):
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": (
                    "Give ONE simple hint for kids to guess this word. "
                    "Do NOT reveal the word. Keep it short.\n"
                    f"Word: {word}"
                )
            }],
            temperature=0.7
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return f"Hint: The word has {len(word)} letters."

def mask_word(word, revealed):
    return " ".join(
        word[i].upper() if i in revealed else "_"
        for i in range(len(word))
    )

def reveal_letter(word, revealed):
    hidden = [i for i in range(len(word)) if i not in revealed]
    if hidden:
        revealed.add(random.choice(hidden))

def generate_word():
    """Make a pronounceable-ish random word so the game stays unique."""
    vowels = "aeiou"
    consonants = "bcdfghjklmnpqrstvwxyz"
    length = random.randint(5, 9)
    w = []
    start_consonant = random.choice([True, False])
    for i in range(length):
        use_consonant = (i % 2 == 0 and start_consonant) or (i % 2 == 1 and not start_consonant)
        w.append(random.choice(consonants if use_consonant else vowels))
    return "".join(w)

def build_deck():
    """Shuffle words into a 'deck' so no repeats within a game."""
    deck = WORDS[:]
    random.shuffle(deck)
    return deck

def refill_deck(deck):
    """If deck is empty, optionally add new unique generated words."""
    if not AUTO_GENERATE_WHEN_EMPTY:
        return build_deck()

    new_words = set()
    while len(new_words) < GENERATED_WORDS_COUNT:
        new_words.add(generate_word())

    deck = list(new_words)
    random.shuffle(deck)
    return deck

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Segoe UI", 36, bold=True)
font_mid = pygame.font.SysFont("Segoe UI", 24)
font_small = pygame.font.SysFont("Segoe UI", 18)

# ---------------- GAME STATE ----------------
phase = "NAME"  # NAME, PLAY, SHOW_ANSWER, GAME_OVER
player_name = ""
typed = ""

deck = build_deck()     # unique words per run
current_word = ""
revealed = set()
lives = LIVES_PER_WORD
failed_words = 0
score = 0
hint_text = ""
show_answer_timer = 0
# -------------------------------------------

def next_unique_word():
    """Pop next word from deck; refill if empty."""
    global deck
    if not deck:
        deck = refill_deck(deck)
    return deck.pop()

def new_word():
    global current_word, revealed, lives, hint_text, typed
    current_word = next_unique_word()
    revealed = set()
    lives = LIVES_PER_WORD
    typed = ""
    hint_text = ai_hint(current_word)

running = True
while running:
    clock.tick(FPS)
    now = pygame.time.get_ticks()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:

            if phase == "NAME":
                if e.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif e.key == pygame.K_RETURN and player_name.strip():
                    phase = "PLAY"
                    new_word()
                elif e.unicode.isprintable():
                    if len(player_name) < 18:
                        player_name += e.unicode

            elif phase == "PLAY":
                if e.key == pygame.K_BACKSPACE:
                    typed = typed[:-1]
                elif e.key == pygame.K_RETURN:
                    if typed.lower().strip() == current_word:
                        score += 10
                        new_word()
                    else:
                        lives -= 1
                        reveal_letter(current_word, revealed)
                        typed = ""

                        if lives == 0:
                            failed_words += 1
                            phase = "SHOW_ANSWER"
                            show_answer_timer = now + 2000
                elif e.unicode.isalpha():
                    typed += e.unicode.lower()

            elif phase == "GAME_OVER":
                if e.key == pygame.K_RETURN:
                    # restart game
                    phase = "NAME"
                    player_name = ""
                    typed = ""
                    deck = build_deck()
                    current_word = ""
                    revealed = set()
                    lives = LIVES_PER_WORD
                    failed_words = 0
                    score = 0
                    hint_text = ""

    if phase == "SHOW_ANSWER" and now > show_answer_timer:
        if failed_words >= MAX_FAILED_WORDS:
            phase = "GAME_OVER"
        else:
            phase = "PLAY"
            new_word()

    # ---------------- DRAW ----------------
    screen.fill((20, 24, 45))
    screen.blit(font_small.render(f"{EVENT} | {SCHOOL}", True, (200, 200, 200)), (20, 15))
    screen.blit(font_big.render(TITLE, True, (255, 255, 255)), (20, 45))

    if player_name:
        screen.blit(font_mid.render(f"Player: {player_name}", True, (180, 220, 255)), (20, 95))

    screen.blit(
        font_mid.render(f"Score: {score}   Failed: {failed_words}/{MAX_FAILED_WORDS}", True, (180, 255, 200)),
        (20, 125)
    )

    if phase == "NAME":
        screen.blit(font_mid.render("Enter  your name and press ENTER:", True, (255, 255, 180)), (20, 200))
        screen.blit(font_mid.render(player_name, True, (255, 255, 255)), (20, 240))

    elif phase == "PLAY":
        screen.blit(font_mid.render("Guess the word:", True, (255, 255, 180)), (20, 190))
        screen.blit(font_big.render(mask_word(current_word, revealed), True, (255, 255, 255)), (20, 230))

        screen.blit(font_mid.render("AI Hint:", True, (200, 200, 255)), (20, 290))
        # keep hint in one/two lines if long
        hint = hint_text
        if len(hint) > 55:
            hint = hint[:55] + "..."
        screen.blit(font_mid.render(hint, True, (255, 255, 255)), (20, 320))

        screen.blit(font_mid.render(f"Lives left: {lives}", True, (255, 200, 200)), (20, 360))
        screen.blit(font_mid.render("Your answer:", True, (200, 255, 200)), (20, 400))
        screen.blit(font_mid.render(typed.upper(), True, (255, 255, 255)), (20, 430))

    elif phase == "SHOW_ANSWER":
        screen.blit(font_big.render("Right Answer:", True, (255, 180, 180)), (20, 240))
        screen.blit(font_big.render(current_word.upper(), True, (255, 255, 255)), (20, 290))

    elif phase == "GAME_OVER":
        screen.blit(font_big.render("GAME OVER", True, (255, 100, 100)), (20, 230))
        screen.blit(font_mid.render(f"Final Score: {score}", True, (255, 255, 255)), (20, 280))
        screen.blit(font_mid.render("Press ENTER to restart", True, (200, 200, 200)), (20, 320))

    pygame.display.flip()

pygame.quit()
