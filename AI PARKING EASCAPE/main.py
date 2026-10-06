import pygame
import sys
import heapq
import time

pygame.init()

# =========================================================
# WINDOW
# =========================================================

WIDTH = 1100
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Parking Escape")

clock = pygame.time.Clock()

# =========================================================
# COLORS
# =========================================================

BG = (12, 17, 25)
PANEL = (25, 32, 43)
ROAD = (52, 55, 60)
WHITE = (245, 245, 245)
LIGHT = (180, 190, 205)

RED = (235, 65, 75)
BLUE = (60, 140, 235)
PURPLE = (150, 90, 220)
ORANGE = (240, 155, 50)
GREEN = (60, 220, 130)
YELLOW = (255, 210, 60)
CYAN = (60, 210, 220)
BLACK = (5, 7, 10)

# =========================================================
# FONTS
# =========================================================

TITLE = pygame.font.SysFont("arial", 34, bold=True)
BIG = pygame.font.SysFont("arial", 26, bold=True)
FONT = pygame.font.SysFont("arial", 18, bold=True)
SMALL = pygame.font.SysFont("arial", 14)

# =========================================================
# BOARD
# =========================================================

GRID = 6
CELL = 82

BOARD_X = 55
BOARD_Y = 125

EXIT_ROW = 2

# =========================================================
# CAR
# =========================================================

class Car:

    def __init__(
        self,
        name,
        x,
        y,
        length,
        color,
        horizontal,
        player=False
    ):

        self.name = name
        self.x = x
        self.y = y
        self.length = length
        self.color = color
        self.horizontal = horizontal
        self.player = player

    def rect(self):

        if self.horizontal:

            return pygame.Rect(
                BOARD_X + self.x * CELL + 7,
                BOARD_Y + self.y * CELL + 14,
                self.length * CELL - 14,
                CELL - 28
            )

        else:

            return pygame.Rect(
                BOARD_X + self.x * CELL + 14,
                BOARD_Y + self.y * CELL + 7,
                CELL - 28,
                self.length * CELL - 14
            )

    def draw(self, selected=False):

        r = self.rect()

        # shadow
        pygame.draw.rect(
            screen,
            BLACK,
            r.move(5, 5),
            border_radius=14
        )

        # body
        pygame.draw.rect(
            screen,
            self.color,
            r,
            border_radius=14
        )

        # border
        pygame.draw.rect(
            screen,
            WHITE if selected else BLACK,
            r,
            3,
            border_radius=14
        )

        # windows
        if self.horizontal:

            window = pygame.Rect(
                r.centerx - 20,
                r.y + 7,
                40,
                r.height - 14
            )

        else:

            window = pygame.Rect(
                r.x + 7,
                r.centery - 20,
                r.width - 14,
                40
            )

        pygame.draw.rect(
            screen,
            (30, 40, 52),
            window,
            border_radius=7
        )

        pygame.draw.rect(
            screen,
            (110, 140, 160),
            window,
            2,
            border_radius=7
        )

        # wheels
        if self.horizontal:

            wheels = [
                (r.left + 15, r.top),
                (r.right - 15, r.top),
                (r.left + 15, r.bottom),
                (r.right - 15, r.bottom)
            ]

        else:

            wheels = [
                (r.left, r.top + 15),
                (r.right, r.top + 15),
                (r.left, r.bottom - 15),
                (r.right, r.bottom - 15)
            ]

        for wx, wy in wheels:

            pygame.draw.circle(
                screen,
                BLACK,
                (wx, wy),
                7
            )

        if self.player:

            pygame.draw.rect(
                screen,
                YELLOW,
                r.inflate(8, 8),
                3,
                border_radius=18
            )

            label = SMALL.render(
                "PLAYER",
                True,
                YELLOW
            )

            screen.blit(
                label,
                (
                    r.centerx - label.get_width() // 2,
                    r.y - 18
                )
            )


# =========================================================
# LEVEL
# =========================================================

def create_level():

    return [

        # PLAYER
        Car(
            "PLAYER",
            0,
            2,
            2,
            RED,
            True,
            True
        ),

        # These two cars block the exit path
        Car(
            "BLOCK1",
            2,
            1,
            2,
            BLUE,
            False
        ),

        Car(
            "BLOCK2",
            4,
            0,
            3,
            PURPLE,
            False
        ),

        # Other cars
        Car(
            "CAR3",
            5,
            3,
            2,
            ORANGE,
            False
        ),

        Car(
            "CAR4",
            0,
            0,
            2,
            BLUE,
            True
        ),

        Car(
            "CAR5",
            1,
            4,
            2,
            WHITE,
            True
        ),

        Car(
            "CAR6",
            3,
            5,
            2,
            PURPLE,
            True
        )
    ]


cars = create_level()

selected_car = None

moves = 0
score = 1000

message = "Select the red car and move it to EXIT."

ai_running = False
game_won = False

# =========================================================
# BOARD DRAW
# =========================================================

def draw_board():

    board = pygame.Rect(
        BOARD_X,
        BOARD_Y,
        GRID * CELL,
        GRID * CELL
    )

    pygame.draw.rect(
        screen,
        ROAD,
        board,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        (100, 105, 110),
        board,
        4,
        border_radius=18
    )

    # parking grid
    for i in range(1, GRID):

        pygame.draw.line(
            screen,
            (100, 100, 100),
            (
                BOARD_X + i * CELL,
                BOARD_Y
            ),
            (
                BOARD_X + i * CELL,
                BOARD_Y + GRID * CELL
            ),
            2
        )

        pygame.draw.line(
            screen,
            (100, 100, 100),
            (
                BOARD_X,
                BOARD_Y + i * CELL
            ),
            (
                BOARD_X + GRID * CELL,
                BOARD_Y + i * CELL
            ),
            2
        )

    # EXIT
    exit_rect = pygame.Rect(
        BOARD_X + GRID * CELL,
        BOARD_Y + EXIT_ROW * CELL + 15,
        55,
        CELL - 30
    )

    pygame.draw.rect(
        screen,
        GREEN,
        exit_rect,
        border_radius=10
    )

    text(
        "EXIT",
        exit_rect.x + 2,
        exit_rect.y - 25,
        SMALL,
        GREEN
    )

    # arrow
    pygame.draw.polygon(
        screen,
        BLACK,
        [
            (
                exit_rect.centerx + 17,
                exit_rect.centery
            ),
            (
                exit_rect.centerx - 5,
                exit_rect.centery - 13
            ),
            (
                exit_rect.centerx - 5,
                exit_rect.centery + 13
            )
        ]
    )


# =========================================================
# COLLISION
# =========================================================

def get_rect(car, x, y):

    if car.horizontal:

        return pygame.Rect(
            BOARD_X + x * CELL + 7,
            BOARD_Y + y * CELL + 14,
            car.length * CELL - 14,
            CELL - 28
        )

    else:

        return pygame.Rect(
            BOARD_X + x * CELL + 14,
            BOARD_Y + y * CELL + 7,
            CELL - 28,
            car.length * CELL - 14
        )


def blocked(car, new_x, new_y):

    test_rect = get_rect(
        car,
        new_x,
        new_y
    )

    for other in cars:

        if other == car:
            continue

        if test_rect.colliderect(other.rect()):
            return True

    return False


# =========================================================
# MOVE
# =========================================================

def move_car(car, direction):

    global moves
    global score

    if game_won:
        return False

    if car.horizontal:

        new_x = car.x + direction

        if new_x < 0:
            return False

        if new_x + car.length > GRID:
            return False

        if blocked(
            car,
            new_x,
            car.y
        ):
            return False

        car.x = new_x

    else:

        new_y = car.y + direction

        if new_y < 0:
            return False

        if new_y + car.length > GRID:
            return False

        if blocked(
            car,
            car.x,
            new_y
        ):
            return False

        car.y = new_y

    moves += 1
    score = max(0, score - 5)

    return True


# =========================================================
# EXIT CHECK
# =========================================================

def can_exit():

    player = cars[0]

    # Player must be horizontal
    if not player.horizontal:
        return False

    # Player must be on exit row
    if player.y != EXIT_ROW:
        return False

    # Front of player reaches right edge
    if player.x + player.length < GRID:
        return False

    return True


# =========================================================
# PLAYER EXIT ANIMATION
# =========================================================

def exit_animation():

    global game_won
    global score
    global message

    player = cars[0]

    message = "EXIT CLEAR! ESCAPING..."

    # Move car completely outside screen
    while player.rect().x < WIDTH + 50:

        player.x += 0.08

        draw_game()
        pygame.display.flip()

        clock.tick(60)

    game_won = True

    score += 500

    message = "MISSION COMPLETE! CAR ESCAPED!"


# =========================================================
# MANUAL MOVE
# =========================================================

def manual_move(direction):

    global message

    if selected_car is None:

        message = "Select a car first."
        return

    if move_car(
        selected_car,
        direction
    ):

        message = (
            selected_car.name +
            " moved successfully."
        )

        # Check player exit
        if selected_car.player:

            if can_exit():

                exit_animation()

    else:

        message = "BLOCKED! Choose another direction."


# =========================================================
# AI SOLVER
# =========================================================

def ai_solve():

    global ai_running
    global message
    global score

    if ai_running or game_won:
        return

    ai_running = True

    message = "AI ANALYZING BLOCKING VEHICLES..."

    draw_game()
    pygame.display.flip()

    time.sleep(0.7)

    player = cars[0]

    # =====================================================
    # STEP 1
    # Move BLOCK1 downward
    # =====================================================

    block1 = cars[1]

    while block1.y < 3:

        if not blocked(
            block1,
            block1.x,
            block1.y + 1
        ):

            block1.y += 1
            score += 10

        else:
            break

        message = "AI: Moving blocking vehicle..."

        draw_game()
        pygame.display.flip()

        time.sleep(0.25)

    # =====================================================
    # STEP 2
    # Move BLOCK2 downward
    # =====================================================

    block2 = cars[2]

    while block2.y < 3:

        if not blocked(
            block2,
            block2.x,
            block2.y + 1
        ):

            block2.y += 1
            score += 10

        else:
            break

        message = "AI: Clearing second obstacle..."

        draw_game()
        pygame.display.flip()

        time.sleep(0.25)

    # =====================================================
    # STEP 3
    # Move player toward exit
    # =====================================================

    message = "AI: Exit path detected!"

    draw_game()
    pygame.display.flip()

    time.sleep(0.5)

    while player.x + player.length < GRID:

        if blocked(
            player,
            player.x + 1,
            player.y
        ):

            message = "AI: Path still blocked."

            break

        player.x += 1

        score += 20

        message = "AI: Moving player to EXIT..."

        draw_game()
        pygame.display.flip()

        time.sleep(0.25)

    # =====================================================
    # STEP 4
    # EXIT
    # =====================================================

    if can_exit():

        exit_animation()

    else:

        message = "AI needs another route."

    ai_running = False


# =========================================================
# RESET
# =========================================================

def reset_game():

    global cars
    global selected_car
    global moves
    global score
    global message
    global game_won

    cars = create_level()

    selected_car = None

    moves = 0
    score = 1000

    game_won = False

    message = "Select the red car and move it to EXIT."


# =========================================================
# TEXT
# =========================================================

def text(value, x, y, font, color=WHITE):

    image = font.render(
        value,
        True,
        color
    )

    screen.blit(
        image,
        (x, y)
    )


# =========================================================
# SIDE PANEL
# =========================================================

AI_BUTTON = pygame.Rect(
    700,
    550,
    180,
    55
)

RESET_BUTTON = pygame.Rect(
    895,
    550,
    130,
    55
)


def draw_panel():

    panel = pygame.Rect(
        680,
        125,
        370,
        390
    )

    pygame.draw.rect(
        screen,
        PANEL,
        panel,
        border_radius=20
    )

    pygame.draw.rect(
        screen,
        (70, 80, 95),
        panel,
        2,
        border_radius=20
    )

    text(
        "AI CONTROL CENTER",
        710,
        155,
        BIG,
        CYAN
    )

    text(
        "SCORE",
        710,
        220,
        SMALL,
        LIGHT
    )

    text(
        str(score),
        710,
        245,
        TITLE,
        YELLOW
    )

    text(
        "MOVES",
        890,
        220,
        SMALL,
        LIGHT
    )

    text(
        str(moves),
        890,
        245,
        TITLE,
        WHITE
    )

    # status box
    status = pygame.Rect(
        710,
        320,
        300,
        120
    )

    pygame.draw.rect(
        screen,
        (35, 43, 55),
        status,
        border_radius=12
    )

    text(
        "GAME STATUS",
        730,
        340,
        SMALL,
        CYAN
    )

    if game_won:

        text(
            "CAR ESCAPED!",
            730,
            375,
            FONT,
            GREEN
        )

    elif ai_running:

        text(
            "AI SOLVING...",
            730,
            375,
            FONT,
            ORANGE
        )

    else:

        text(
            "PLAYER MODE",
            730,
            375,
            FONT,
            WHITE
        )

    # instructions
    text(
        "Click a car",
        710,
        465,
        SMALL,
        LIGHT
    )

    text(
        "Arrow keys = Move",
        710,
        485,
        SMALL,
        LIGHT
    )


# =========================================================
# BUTTON
# =========================================================

def draw_button(rect, label, color):

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        rect,
        3,
        border_radius=12
    )

    image = FONT.render(
        label,
        True,
        BLACK
    )

    screen.blit(
        image,
        (
            rect.centerx - image.get_width() // 2,
            rect.centery - image.get_height() // 2
        )
    )


# =========================================================
# DRAW GAME
# =========================================================

def draw_game():

    screen.fill(BG)

    # Title
    text(
        "AI PARKING ESCAPE",
        45,
        35,
        TITLE
    )

    text(
        "INTELLIGENT VEHICLE EXIT PUZZLE",
        48,
        75,
        SMALL,
        CYAN
    )

    draw_board()

    # cars
    for car in cars:

        car.draw(
            selected=(car == selected_car)
        )

    draw_panel()

    draw_button(
        AI_BUTTON,
        "AI PLAY",
        GREEN
    )

    draw_button(
        RESET_BUTTON,
        "RESET",
        ORANGE
    )

    # bottom message
    pygame.draw.rect(
        screen,
        PANEL,
        (45, 650, 1000, 45),
        border_radius=10
    )

    text(
        message,
        65,
        663,
        SMALL,
        WHITE
    )


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # -------------------------
        # MOUSE
        # -------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse = pygame.mouse.get_pos()

            # AI button
            if AI_BUTTON.collidepoint(mouse):

                if not ai_running:

                    ai_solve()

            # RESET
            elif RESET_BUTTON.collidepoint(mouse):

                reset_game()

            # Select car
            else:

                selected_car = None

                for car in cars:

                    if car.rect().collidepoint(mouse):

                        selected_car = car

                        if car.player:

                            message = (
                                "Player selected. Move toward EXIT."
                            )

                        else:

                            message = (
                                car.name +
                                " selected."
                            )

                        break

        # -------------------------
        # KEYBOARD
        # -------------------------

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                running = False

            if event.key == pygame.K_r:

                reset_game()

            if selected_car:

                if selected_car.horizontal:

                    if event.key == pygame.K_LEFT:

                        manual_move(-1)

                    elif event.key == pygame.K_RIGHT:

                        manual_move(1)

                else:

                    if event.key == pygame.K_UP:

                        manual_move(-1)

                    elif event.key == pygame.K_DOWN:

                        manual_move(1)

    draw_game()

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()