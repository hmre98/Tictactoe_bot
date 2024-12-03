import pygame as pg
import random
from sklearn.linear_model import LinearRegression


X_train = [  
    [2, 1, 1, 2],  
    [1, 2, 0, 3],
    [0, 0, 1, 4],
]
y_train = [1, -1, 0]  

model = LinearRegression()
model.fit(X_train, y_train)

setdepth=10
draw = False
XO = 'x'  
winner = None
TTT = [[None] * 3, [None] * 3, [None] * 3]
game_started = False
linearPlayMode = False  

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
    global linearPlayMode
    global setdepth
    screen.fill(white)
    draw_text("Choose difficulty (Press 3,4,5)", 30, black, (width / 2, 20))
    if setdepth==2:
        draw_text("Easy", 30, black, (width / 2, 50))
    elif setdepth==5:
        draw_text("Medium", 30, black, (width / 2, 50))
    elif setdepth==10:
        draw_text("Hard", 30, black, (width / 2, 50))
    draw_text("LinearRegression (6)", 30, black, (width / 2, 90))
    if linearPlayMode is True:
        draw_text("Enabled", 30, black, (width / 2, 110))
    else:
        draw_text("Disabled", 30, black, (width / 2, 110))
    draw_text("1. Player (X)", 30, black, (width / 2, height / 2 + 20))
    draw_text("Who starts?", 40, black, (width / 2, height / 2 - 30))
    draw_text("1. Player (X)", 30, black, (width / 2, height / 2 + 20))
    draw_text("2. Bot (O)", 30, black, (width / 2, height / 2 + 60))
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
        if XO == 'o' and winner is None and draw is False:
            botMove()

def botMove():
    global XO
    move = bestMove()
    if move is not None:
        row, col = move
        drawXO(row + 1, col + 1)
        check_win()

def bestMove():
    best_score = -float('inf')
    move = None
    teszt=[]

    if linearPlayMode is True:
        for row in range(3):
            for col in range(3):
                if TTT[row][col] is None:  
                    TTT[row][col] = 'o'
                    features = extract_features(TTT)
                    score = model.predict([features])[0]
                    TTT[row][col] = None
                    if score > best_score:
                        best_score = score
                        move = (row, col)
        return move

    for row in range(3):
        for col in range(3):
            if TTT[row][col] is None:
                TTT[row][col] = 'o'
                score = minimax(TTT, 0, False,best_score)
                TTT[row][col] = None
                if score >= best_score:
                    best_score = score
                    move = (row, col)
                    teszt.append((best_score,move))
    teszt=[s for i,s in teszt if i==best_score]
    if len(teszt)!=0:
        return random.choice(teszt)

def minimax(board, depth, is_maximizing,tracking):
    global setdepth
    if check_winner(board, 'o'):  
        return 1  
    elif check_winner(board, 'x'):  
        return -1  
    elif all(all(row) for row in board):
        return 0 
    elif depth==setdepth:
        return tracking

    if is_maximizing:
        best_score = -float('inf')
        for row in range(3):
            for col in range(3):
                if board[row][col] is None:
                    board[row][col] = 'o'
                    score = minimax(board, depth + 1, False,tracking)
                    board[row][col] = None
                    best_score = max(score, best_score)
        #print(best_score)
        return best_score
    else:
        best_score = float('inf')
        for row in range(3):
            for col in range(3):
                if board[row][col] is None:
                    board[row][col] = 'x'
                    score = minimax(board, depth + 1, True,tracking)
                    board[row][col] = None
                    best_score = min(score, best_score)
        #print(best_score)
        return best_score

def check_winner(board, player):
    for row in range(3):
        if board[row] == [player, player, player]:
            return True
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] == player:
            return True
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False

def extract_features(board):
    two_in_a_row = 0
    two_in_a_row_opponent = 0
    empty_corners = 0
    center_control = 0
    
    for row in range(3):
        if board[row].count('o') == 2 and board[row].count(None) == 1:
            two_in_a_row += 1
        if board[row].count('x') == 2 and board[row].count(None) == 1:
            two_in_a_row_opponent += 1
            
    for col in range(3):
        column = [board[row][col] for row in range(3)]
        if column.count('o') == 2 and column.count(None) == 1:
            two_in_a_row += 1
        if column.count('x') == 2 and column.count(None) == 1:
            two_in_a_row_opponent += 1
            
    diagonal1 = [board[i][i] for i in range(3)]
    diagonal2 = [board[i][2 - i] for i in range(3)]
    
    if diagonal1.count('o') == 2 and diagonal1.count(None) == 1:
        two_in_a_row += 1
    if diagonal1.count('x') == 2 and diagonal1.count(None) == 1:
        two_in_a_row_opponent += 1
        
    if diagonal2.count('o') == 2 and diagonal2.count(None) == 1:
        two_in_a_row += 1
    if diagonal2.count('x') == 2 and diagonal2.count(None) == 1:
        two_in_a_row_opponent += 1

    center_control = 1 if board[1][1] == 'o' else 0
    
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    empty_corners = sum(1 for x, y in corners if board[x][y] is None)
    
    return [two_in_a_row, two_in_a_row_opponent, center_control, empty_corners]

def reset_game():
    global TTT, winner, XO, draw, game_started
    XO = 'x'
    draw = False
    game_opening()
    winner = None
    TTT = [[None] * 3, [None] * 3, [None] * 3]
    game_started = False

show_menu()
run=True
while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run=False
        elif event.type == pg.KEYDOWN:
            if not game_started:
                if event.key == pg.K_1:
                    XO = 'x'
                    game_started = True
                    game_opening()
                elif event.key == pg.K_2:
                    XO = 'o'
                    game_started = True
                    game_opening()
                    botMove()
                elif event.key == pg.K_3:
                    setdepth=2
                    print(setdepth)
                    show_menu()
                elif event.key == pg.K_4:
                    setdepth=5
                    print(setdepth)
                    show_menu()
                elif event.key == pg.K_5:
                    setdepth=10 
                    print(setdepth)
                    show_menu()
                elif event.key == pg.K_6:
                    linearPlayMode=True if linearPlayMode is False else False
                    show_menu()
        elif event.type == pg.MOUSEBUTTONDOWN and game_started:
            userClick()
            if winner or draw:
                pg.time.delay(2000)
                reset_game()
                show_menu()
    pg.display.update()

pg.quit()
