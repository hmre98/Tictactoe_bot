import pygame as pg
import random

# Q-Learning Parameters
LEARNING_RATE = 0.1  # Alpha tanulási ráta
DISCOUNT_FACTOR = 0.9  # Gamma kedvezményes faktor
EXPLORATION_RATE = 1.0  # Epsilon felfedezési rta
EXPLORATION_DECAY = 0.999 # csökkenés
MIN_EXPLORATION_RATE = 0.01 # minimum

PLAYER_X = "x"
PLAYER_O = "o"

q_table = {}

draw = False
XO = 'x'  
winner = None
TTT = [[None] * 3, [None] * 3, [None] * 3]
game_started = False  

width = 400
height = 400
white = (255, 255, 255)
black = (0, 0, 0)

pg.init()
screen = pg.display.set_mode((width, height + 100))
pg.display.set_caption("Tic Tac Toe")

x_img = pg.image.load('x.png')
o_img = pg.image.load('o.png')
x_img = pg.transform.scale(x_img, (80, 80))
o_img = pg.transform.scale(o_img, (80, 80))

def draw_text(text, size, color, pos):
    font = pg.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, text_surface.get_rect(center=pos))

def show_menu():
    screen.fill(white)
    draw_text("Who starts?", 40, black, (width / 2, height / 2 - 30))
    draw_text("1. Player ", 30, black, (width / 2, height / 2 + 20))
    draw_text("2. Bot ", 30, black, (width / 2, height / 2 + 60))
    pg.display.update()

def game_opening():
    screen.fill(white)
    pg.draw.line(screen, black, (width / 3, 0), (width / 3, height), 7)
    pg.draw.line(screen, black, (width / 3 * 2, 0), (width / 3 * 2, height), 7)
    pg.draw.line(screen, black, (0, height / 3), (width, height / 3), 7)
    pg.draw.line(screen, black, (0, height / 3 * 2), (width, height / 3 * 2), 7)
    draw_status()

def draw_status():
    global draw
    message = XO.upper() + "'s Turn" if winner is None else winner.upper() + " won!"
    if draw:
        message = 'Game Draw!'
    screen.fill(black, (0, 400, 500, 100))
    draw_text(message, 30, white, (width / 2, 500 - 50))
    pg.display.update()

def check_win():
    global TTT, winner, draw
    for row in range(3):
        if TTT[row][0] == TTT[row][1] == TTT[row][2] and TTT[row][0] is not None:
            winner = TTT[row][0]
            pg.draw.line(screen, (250, 0, 0), (0, (row + 1) * height / 3 - height / 6), (width, (row + 1) * height / 3 - height / 6), 4)
            break
    for col in range(3):
        if TTT[0][col] == TTT[1][col] == TTT[2][col] and TTT[0][col] is not None:
            winner = TTT[0][col]
            pg.draw.line(screen, (250, 0, 0), ((col + 1) * width / 3 - width / 6, 0), ((col + 1) * width / 3 - width / 6, height), 4)
            break
    if TTT[0][0] == TTT[1][1] == TTT[2][2] and TTT[0][0] is not None:
        winner = TTT[0][0]
        pg.draw.line(screen, (250, 70, 70), (50, 50), (350, 350), 4)
    if TTT[0][2] == TTT[1][1] == TTT[2][0] and TTT[0][2] is not None:
        winner = TTT[0][2]
        pg.draw.line(screen, (250, 70, 70), (350, 50), (50, 350), 4)
    if all(all(row) for row in TTT) and winner is None:
        draw = True
    draw_status()

def drawXO(row, col):
    global TTT, XO
    posx = row * width / 3 - width / 3 + 30
    posy = col * height / 3 - height / 3 + 30
    TTT[row - 1][col - 1] = XO
    screen.blit(x_img if XO == 'x' else o_img, (posy, posx))
    XO = 'o' if XO == 'x' else 'x'
    pg.display.update()

def userClick():
    x, y = pg.mouse.get_pos()
    if y>height:
         return      
    col = 1 if x < width / 3 else 2 if x < width / 3 * 2 else 3
    row = 1 if y < height / 3 else 2 if y < height / 3 * 2 else 3
    if TTT[row - 1][col - 1] is None:
        drawXO(row, col)
        check_win()
        if  winner is None and draw is False:
            botMove()

def botMove():
    global XO
    actualBoard = flatten_board(TTT)
    state = get_state(actualBoard)
    valid_moves = get_valid_moves(actualBoard)

    move = choose_action(state, valid_moves, exploration_rate=0.1)  # alacsony- tapasztatokra épít

    if move is not None:
        row, col = divmod(move, 3)
        drawXO(row + 1, col + 1)
        check_win()
        

def initialize_board():
    return [None] * 9


def get_valid_moves(board):
    return [i for i, spot in enumerate(board) if spot is None]

def is_winner(board, player):
    win_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  
        [0, 4, 8], [2, 4, 6]             
    ]
    return any(all(board[i] == player for i in pattern) for pattern in win_patterns)

def is_draw(board):
    return None not in board and not is_winner(board, PLAYER_X) and not is_winner(board, PLAYER_O)

def get_state(board):
    return tuple(board)

def choose_action(state, valid_moves, exploration_rate):
    for move in valid_moves:
        board = flatten_board(TTT)
        board[move] = PLAYER_X  
        if is_winner(board, PLAYER_X):
            return move

    for move in valid_moves:
        board = flatten_board(TTT)
        board[move] = PLAYER_O
        if is_winner(board, PLAYER_O):
            return move

    if random.uniform(0, 1) < exploration_rate:
        return random.choice(valid_moves)  
    else:
        q_values = [q_table.get((state, action), 0) for action in valid_moves]
        max_q = max(q_values)
        return random.choice([action for action, q in zip(valid_moves, q_values) if q == max_q])

def update_q_table(state, action, reward, next_state, valid_moves):
    max_future_q = max([q_table.get((next_state, a), 0) for a in valid_moves], default=0)
    current_q = q_table.get((state, action), 0)
    new_q = current_q + LEARNING_RATE * (reward + DISCOUNT_FACTOR * max_future_q - current_q)
    q_table[(state, action)] = new_q

def reward_function(board, player):
    if is_winner(board, player):
        return 1  
    elif is_winner(board, PLAYER_X if player == PLAYER_O else PLAYER_O):
        return -1  
    elif is_draw(board):
        return 0  
    return -0.05  


def train_bot(episodes):
    global EXPLORATION_RATE
    for episode in range(episodes):
        board = initialize_board()
        state = get_state(board)
        done = False
        current_player = PLAYER_X if random.choice([True, False]) else PLAYER_O

        while not done:
            valid_moves = get_valid_moves(board)
            action = choose_action(state, valid_moves, EXPLORATION_RATE)

            board[action] = current_player
            next_state = get_state(board)
            reward = reward_function(board, current_player)
            done = is_winner(board, current_player) or is_draw(board)

            update_q_table(state, action, reward, next_state, get_valid_moves(board))

            state = next_state
            current_player = PLAYER_X if current_player == PLAYER_O else PLAYER_O

        EXPLORATION_RATE = max(MIN_EXPLORATION_RATE, EXPLORATION_RATE * EXPLORATION_DECAY)

def flatten_board(board):
    return [cell for row in board for cell in row]

def reset_game():
    global TTT, winner, XO, draw, game_started
    XO = 'x'
    draw = False
    game_opening()
    winner = None
    TTT = [[None] * 3, [None] * 3, [None] * 3]
    game_started = False

train_bot(10000) #itt kell csökkenteni 

#print(q_table)

show_menu()
run=True
while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run=False
        elif event.type == pg.KEYDOWN:
            if not game_started:
                if event.key == pg.K_1:
                    game_started = True
                    game_opening()
                elif event.key == pg.K_2:
                    game_started = True
                    game_opening()
                    botMove()
        elif event.type == pg.MOUSEBUTTONDOWN and game_started:
            userClick()
            if winner or draw:
                pg.time.delay(2000)
                reset_game()
                show_menu()
    pg.display.update()

pg.quit()