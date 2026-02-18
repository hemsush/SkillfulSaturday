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
USE_OPENAI_CLUES = True
# ----------------------------------------

OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip().strip('"').strip("'")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

STATIC_CLUE_BANK = {
    "school": ["A place where students learn.", "It has classrooms and teachers.", "You go here for education."],
    "pencil": ["You use this for writing.", "It is made of wood and graphite.", "You sharpen it when the tip is dull."],
    "teacher": ["This person helps students learn.", "They explain lessons in class.", "Students ask this person questions."],
    "planet": ["It moves around a star.", "Earth is one of these.", "It is a large object in space."],
    "forest": ["A large area filled with trees.", "Many animals live here.", "It is bigger than a garden or park."],
    "garden": ["A place where plants are grown.", "You may find flowers and vegetables here.", "It can be in front of a house."],
    "friend": ["Someone you like and trust.", "You enjoy spending time together.", "A close companion."],
    "python": ["A popular programming language.", "It is also the name of a snake.", "People use it to write code."],
    "robot": ["A machine that can do tasks.", "It may move and follow instructions.", "Used in factories and science labs."],
    "future": ["The time that has not happened yet.", "It comes after today and tomorrow.", "People plan for this time."],
    "science": ["This subject asks how things work.", "It includes experiments and observations.", "You learn this in a lab and classroom."],
    "energy": ["This is needed to do work or move.", "Food gives your body this.", "Electricity is a common form of this."],
    "library": ["A quiet place with many books.", "People read and study here.", "You can borrow books from this place."],
    "picture": ["This shows an image of something.", "It can be drawn or taken with a camera.", "Another word is a photo or drawing."],
    "student": ["A person who learns in school.", "This person attends classes.", "Teachers teach this person."],
    "computer": ["An electronic machine for work and play.", "It has a screen and keyboard.", "You can code and browse on this device."],
    "keyboard": ["An input device with many keys.", "You press letters and numbers on it.", "You use it to type on a computer."],
    "battery": ["This stores power.", "Phones and toys often need this.", "It provides electricity to devices."],
    "language": ["A system of words and grammar.", "People use it to communicate.", "English, Tamil, and Hindi are examples."],
    "festival": ["A special celebration event.", "People gather with joy and traditions.", "It may include music, food, and decorations."],
    "history": ["This is about past events.", "You learn about old people and places.", "It explains what happened long ago."],
    "morning": ["A part of the day.", "It comes after night.", "It is the time before noon."],
    "evening": ["A part of the day near sunset.", "It comes after afternoon.", "People often relax during this time."],
    "reading": ["An activity with books or text.", "You use your eyes to understand words.", "You do this with stories and lessons."],
    "writing": ["You create words and sentences.", "You can do this with a pen or keyboard.", "It is the opposite skill of reading."],
    "respect": ["A value shown in good behavior.", "You show it by being polite and kind.", "You should give this to elders and others."],
    "courage": ["This means being brave.", "You show it when facing fear.", "Heroes often have this quality."],
    "holiday": ["A day without regular school or work.", "People rest, travel, or celebrate.", "It is a special break day."],
    "practice": ["Doing something again and again.", "It helps you improve a skill.", "You need this to get better."],
    "creative": ["This describes new and original ideas.", "Artists and inventors often are this.", "It means using imagination."],
    "learning": ["The process of gaining knowledge.", "This happens at school and at home.", "Reading and listening help with this."],
    "technology": ["Tools and machines made by humans.", "It includes computers and the internet.", "Modern life uses this every day."],
    "curiosity": ["A strong desire to know more.", "It makes you ask questions.", "Scientists and children often show this."],
    "imagination": ["The ability to form ideas in your mind.", "You use it while creating stories.", "It helps you think beyond what you see."],
    "celebrate": ["To mark a happy event.", "People do this at birthdays and festivals.", "It often includes joy, food, and fun."],
    "together": ["This means with one another.", "Friends or family can do things this way.", "It is the opposite of alone."],
    "solution": ["An answer to a problem.", "You find this after thinking carefully.", "Math questions often have this."],
    "problem": ["A difficulty that needs solving.", "It can be in math or daily life.", "You look for a solution to this."],
}

def static_clues(word):
    lower_word = word.lower()
    if lower_word in STATIC_CLUE_BANK:
        return STATIC_CLUE_BANK[lower_word]

    letters = len(lower_word)
    vowels = sum(1 for ch in lower_word if ch in "aeiou")
    return [
        f"This word has {letters} letters.",
        f"It starts with '{lower_word[0]}' and has {vowels} vowel(s).",
        f"It ends with '{lower_word[-1]}'.",
    ]

def ai_clues(word):
    if not USE_OPENAI_CLUES:
        return static_clues(word)

    if not client:
        print("[OpenAI] Missing OPENAI_API_KEY in environment/.env")
        return static_clues(word)

    try:
        r = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{
                "role": "user",
                "content": (
                    f"Give THREE progressive hints for kids to guess the word '{word}'. "
                    "Each hint should be more helpful than the previous one. "
                    "Do NOT reveal the word in any hint. Keep each hint short.\n"
                    "Format: Hint 1: [first hint]\nHint 2: [second hint]\nHint 3: [third hint]"
                )
            }],
            temperature=0.7
        )
        response = r.choices[0].message.content.strip()
        # Parse the response into a list
        lines = response.split('\n')
        clues = []
        for line in lines:
            if line.startswith('Hint'):
                clue = line.split(': ', 1)[1] if ': ' in line else line
                clues.append(clue.strip())
        return clues if len(clues) == 3 else static_clues(word)
    except Exception as ex:
        print(f"[OpenAI] Clue generation failed for '{word}' with model '{OPENAI_MODEL}': {ex}")
        return static_clues(word)

def mask_word(word, revealed_count=0):
    result = []
    for i, char in enumerate(word):
        if i < revealed_count:
            result.append(char)
        else:
            result.append("_")
    return " ".join(result)



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
phase = "NAME"  # NAME, PLAY, SHOW_CORRECT, SHOW_ANSWER, GAME_OVER
player_name = ""
typed = ""

deck = build_deck()     # unique words per run
current_word = ""
clues = []
current_clue_index = 0
lives = LIVES_PER_WORD
failed_words = 0
score = 0
clue_text = ""
show_answer_timer = 0
show_correct_timer = 0
revealed_count = 0
correct_word = ""
# -------------------------------------------

def next_unique_word():
    """Pop next word from deck; refill if empty."""
    global deck
    if not deck:
        deck = refill_deck(deck)
    return deck.pop()

def new_word():
    global current_word, lives, clue_text, typed, clues, current_clue_index, revealed_count
    current_word = next_unique_word()
    lives = LIVES_PER_WORD
    typed = ""
    clues = ai_clues(current_word)
    current_clue_index = 0
    revealed_count = 0
    clue_text = clues[0] if clues else "No clue available"

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
                        correct_word = current_word
                        phase = "SHOW_CORRECT"
                        show_correct_timer = now + 2000
                    else:
                        lives -= 1
                        revealed_count += 1
                        current_clue_index += 1
                        if current_clue_index < len(clues):
                            clue_text = clues[current_clue_index]
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
                    clues = []
                    current_clue_index = 0
                    lives = LIVES_PER_WORD
                    failed_words = 0
                    score = 0
                    clue_text = ""
                    revealed_count = 0
                    correct_word = ""
                    show_correct_timer = 0

    if phase == "SHOW_ANSWER" and now > show_answer_timer:
        if failed_words >= MAX_FAILED_WORDS:
            phase = "GAME_OVER"
        else:
            phase = "PLAY"
            new_word()
    
    if phase == "SHOW_CORRECT" and now > show_correct_timer:
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
        screen.blit(font_big.render(mask_word(current_word, revealed_count), True, (255, 255, 255)), (20, 230))

        screen.blit(font_mid.render("AI Clue:", True, (200, 200, 255)), (20, 290))
        # keep clue in one/two lines if long
        clue = clue_text
        if len(clue) > 55:
            clue = clue[:55] + "..."
        screen.blit(font_mid.render(clue, True, (255, 255, 255)), (20, 320))

        screen.blit(font_mid.render(f"Lives left: {lives}", True, (255, 200, 200)), (20, 360))
        screen.blit(font_mid.render("Your answer:", True, (200, 255, 200)), (20, 400))
        screen.blit(font_mid.render(typed.upper(), True, (255, 255, 255)), (20, 430))

    elif phase == "SHOW_CORRECT":
        screen.blit(font_big.render("Great! You guessed it right.", True, (100, 255, 100)), (20, 210))
        screen.blit(font_mid.render("Word is:", True, (180, 255, 180)), (20, 270))
        screen.blit(font_big.render(correct_word.upper(), True, (255, 255, 255)), (20, 310))

    elif phase == "SHOW_ANSWER":
        screen.blit(font_big.render("Right Answer:", True, (255, 180, 180)), (20, 240))
        screen.blit(font_big.render(current_word.upper(), True, (255, 255, 255)), (20, 290))

    elif phase == "GAME_OVER":
        screen.blit(font_big.render("GAME OVER", True, (255, 100, 100)), (20, 230))
        screen.blit(font_mid.render(f"Final Score: {score}", True, (255, 255, 255)), (20, 280))
        screen.blit(font_mid.render("Press ENTER to restart", True, (200, 200, 200)), (20, 320))

    pygame.display.flip()

pygame.quit()
