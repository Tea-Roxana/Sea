from tkinter import *
from tkinter import messagebox
import random

def generate_ai_ships():
    board = [[0]*10 for _ in range(10)]
    ai_ships = [4,3,3,2,2,2,1,1,1,1]
    
    for ship_size in ai_ships:
        placed, attempts = False, 0
        while not placed and attempts < 100:
            direction = random.choice(['г','в'])
            max_x, max_y = (10, 10-ship_size+1) if direction == 'г' else (10-ship_size+1, 10)
            start_x, start_y = random.randint(0, max_x-1), random.randint(0, max_y-1)
            
            can_place = True
            for i in range(ship_size):
                x, y = (start_x, start_y+i) if direction == 'г' else (start_x+i, start_y)
                if not (0<=x<10 and 0<=y<10):
                    can_place = False
                    break
                for dx,dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                    nx, ny = x+dx, y+dy
                    if 0<=nx<10 and 0<=ny<10 and board[nx][ny]==1:
                        can_place = False
                        break
                if not can_place: break
            
            if can_place:
                for i in range(ship_size):
                    x, y = (start_x, start_y+i) if direction == 'г' else (start_x+i, start_y)
                    board[x][y] = 1
                placed = True
            attempts += 1
        
        if not placed: return generate_ai_ships()
    return board

def place_ships():
    entries = {4:[],3:[],2:[],1:[]}
    n_page = Toplevel()
    n_page.title("Расстановка кораблей")
    Label(n_page, text="Впишите координаты начала (х1 у1) и направление (г или в). Например: а 1 в").grid(row=0, column=0, columnspan=3, pady=10)
    
    row = 1
    for count, size in [(1,4),(2,3),(3,2),(4,1)]:
        Label(n_page, text=f"{size}-палубный", font=("Arial",10,"bold")).grid(row=row, column=0, sticky="w", padx=10)
        row += 1
        for _ in range(count):
            Label(n_page, text="Координаты:").grid(row=row, column=0, sticky="w", padx=20)
            entry_ship = Entry(n_page, width=15)
            entry_ship.grid(row=row, column=1, padx=5, pady=2, sticky="we")
            entries[size].append(entry_ship)
            row += 1
    
    Button(n_page, text="Разместить корабли", command=lambda: save_ships(entries, n_page, btn_ship)).grid(row=row, column=0, columnspan=2, pady=20)
    n_page.columnconfigure(1, weight=1)
    n_page.grab_set()

def save_ships(entries, n_page, btn):
    global board_p, board_ai
    board_numeric = [[0]*10 for _ in range(10)]
    
    for size, entry_list in entries.items():
        for entry in entry_list:
            coords = entry.get().strip().split()
            if len(coords) < 3: return False
            try:
                start_x, start_y, direction = letters.index(coords[0].upper()), int(coords[1])-1, coords[2].lower()
                if not (0<=start_x<10 and 0<=start_y<10): return False
                for i in range(size):
                    x, y = (start_x, start_y+i) if direction == 'г' else (start_x+i, start_y)
                    if not (0<=x<10 and 0<=y<10) or board_numeric[x][y]==1: return False
                    board_numeric[x][y] = 1
            except: return False
    
    if check_placement(board_numeric):
        board_p = board_numeric
        for i in range(10):
            for j in range(10):
                if board_numeric[i][j]==1: buttons_p[i][j].config(bg='#639799')
        board_ai = generate_ai_ships()
        n_page.grab_release()
        n_page.destroy()
        btn.destroy()
        return True
    messagebox.showerror("Ошибка", "Некорректная расстановка кораблей!")
    return False

def check_placement(board):
    line = [[0]*12] + [[0]+row+[0] for row in board] + [[0]*12]
    ship = [0,0,0,0]
    
    for j in range(1,11):
        for i in range(1,11):
            if line[j][i]!=0:
                if line[j+1][i+1]!=0 or line[j+1][i-1]!=0 or line[j-1][i+1]!=0 or line[j-1][i-1]!=0: return False
                if line[j][i+1]!=0: line[j][i+1] += line[j][i]
                if line[j+1][i]!=0: line[j+1][i] += line[j][i]
    
    for j in range(1,11):
        for i in range(1,11):
            cell = line[j][i]
            if cell==1: ship[0]+=1
            elif cell==2: ship[1]+=1
            elif cell==3: ship[2]+=1
            elif cell==4: ship[3]+=1
    
    return ship == [10,6,3,1]

def ai_move():
    global ai_possible_moves, last_hit

    if last_hit:
        direction = None
        if len(last_hit)>1:
            row1,col1,row2,col2 = last_hit[0][0],last_hit[0][1],last_hit[1][0],last_hit[1][1]
            direction = 'г' if row1==row2 else 'в' if col1==col2 else None
        
        row,col = last_hit[-1][0],last_hit[-1][1]
        targets = [(row,col-1),(row,col+1)] if direction=='г' else [(row-1,col),(row+1,col)] if direction=='в' else [(row-1,col),(row+1,col),(row,col-1),(row,col+1)]
        
        for r,c in targets:
            if 0<=r<10 and 0<=c<10 and (r,c) in ai_possible_moves:
                ai_possible_moves.remove((r,c))
                return [r,c]
        
        for hit in last_hit[:-1]:
            row,col = hit[0],hit[1]
            for r,c in [(row-1,col),(row+1,col),(row,col-1),(row,col+1)]:
                if 0<=r<10 and 0<=c<10 and (r,c) in ai_possible_moves:
                    ai_possible_moves.remove((r,c))
                    return [r,c]

    for size,count in [(4,ships.count(4)),(3,ships.count(3)),(2,ships.count(2))]:
        if count==0: continue
        for _ in range(10):
            side = random.choice([1,2])
            lines = {4:[4,8],3:[3,6,9] if side==1 else [2,5,8],2:[2,4,6,8]}.get(size,[2,4,6,8])
            line = random.choice(lines)
            fire = random.randint(0,line-1)
            row,col = (line-fire-1,fire) if side==1 else (9-(line-fire)+1,9-fire)
            if 0<=row<10 and 0<=col<10 and (row,col) in ai_possible_moves:
                ai_possible_moves.remove((row,col))
                return [row,col]

    if ai_possible_moves:
        move = random.choice(ai_possible_moves)
        ai_possible_moves.remove(move)
        return list(move)
    return [0,0]

def remove_hits(ship_hits, board, buttons, player_turn):
    global ai_possible_moves, ships, player_ships

    if not ship_hits: return False
    ship_destroyed = all(
        all(board[r][c]!=1 for r,c in [(hit[0]-1,hit[1]),(hit[0]+1,hit[1]),(hit[0],hit[1]-1),(hit[0],hit[1]+1)] 
        if 0<=r<10 and 0<=c<10) for hit in ship_hits
    )
    
    if ship_destroyed:
        if player_turn=="ai": 
            if len(ship_hits) in ships: ships.remove(len(ship_hits))
        else: 
            if len(ship_hits) in player_ships: player_ships.remove(len(ship_hits))

        if check_winner(player_turn): return True
        
        cells_to_mark = set()
        for hit in ship_hits:
            for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                r,c = hit[0]+dr, hit[1]+dc
                if 0<=r<10 and 0<=c<10 and board[r][c]==0: cells_to_mark.add((r,c))

        for r,c in cells_to_mark:
            board[r][c] = -1
            if player_turn=="player":
                buttons[r][c].config(bg='white', text='•')
                player_moves.append((r,c))
            else:
                buttons[r][c].config(bg='light gray', text='•')
                if (r,c) in ai_possible_moves: ai_possible_moves.remove((r,c))
        return True
    return False

def check_winner(turn):
    if (turn=="player" and not player_ships) or (turn=="ai" and not ships):
        winner = "Игрок" if turn=="player" else "Компьютер"
        messagebox.showinfo("Конец игры", f"Победил {winner}!")
        if messagebox.askyesno("Новая игра", "Начать заново?"): restart()
        return True
    return False

def restart():
    global ships, player_ships, buttons_p, buttons_ai, board_p, board_ai
    global player_turn, ai_possible_moves, player_moves, last_hit, last_hit_player
    ships = player_ships = [1,1,1,1,2,2,2,3,3,4]
    buttons_p, buttons_ai = [], []
    board_p, board_ai = [[0]*10 for _ in range(10)], [[0]*10 for _ in range(10)]
    player_turn, last_hit, last_hit_player = "player", [], []
    ai_possible_moves, player_moves = [(r,c) for r in range(10) for c in range(10)], []
    
    for widget in board.winfo_children(): widget.destroy()
    set_board()
    
    global btn_ship
    btn_ship = Button(root, text="Разместить корабли", font=("Arial",10), command=place_ships)
    btn_ship.pack(padx=10, pady=20, anchor="e")

def make_move(row, col):
    global player_turn, last_hit, last_hit_player, player_moves
    if not ships or not player_ships: return
        
    if player_turn == "player":
        if (row,col) in player_moves: return
        if board_ai[row][col] == 1:
            buttons_ai[row][col].config(bg='red', text='X')
            board_ai[row][col], last_hit_player[-1:] = 2, [[row,col]]
            if remove_hits(last_hit_player, board_ai, buttons_ai, player_turn): last_hit_player = []
            player_moves.append((row,col))
        else:
            buttons_ai[row][col].config(bg='white', text='•')
            board_ai[row][col], player_turn = -1, "ai"
            player_moves.append((row,col))

    if player_turn == "ai":
        ai_hit = True
        while ai_hit and player_turn == "ai":
            row_ai, col_ai = ai_move()
            if board_p[row_ai][col_ai] == 1:
                buttons_p[row_ai][col_ai].config(bg='red', text='X')
                board_p[row_ai][col_ai], last_hit[-1:] = 2, [[row_ai,col_ai]]
                if remove_hits(last_hit, board_p, buttons_p, "ai"): last_hit = []
            else:
                buttons_p[row_ai][col_ai].config(bg='white', text='•')
                board_p[row_ai][col_ai], player_turn, ai_hit = -1, "player", False

def set_board():
    for row in range(10):    
        row_buttons_p, row_buttons_ai = [], []
        for col in range(10):
            btn_p = Button(board, text=" ", width=2, height=1, bg="light blue")
            btn_p.grid(row=row, column=col, padx=1, pady=1)
            row_buttons_p.append(btn_p)
            
            btn_ai = Button(board, text=" ", width=2, height=1, command=lambda r=row,c=col: make_move(r,c), bg="light grey")
            btn_ai.grid(row=row, column=col+11, padx=1, pady=1)
            row_buttons_ai.append(btn_ai)
            
        Label(board, text=letters[row], font=("Arial",10,"bold")).grid(row=row, column=10, padx=1, pady=1)
        buttons_p.append(row_buttons_p)
        buttons_ai.append(row_buttons_ai)

root = Tk()
root.title("Морской бой")

Label(root, text="Морской бой", font=("Arial",14)).pack(pady=10, anchor="center")

numbers_frame = Frame(root)
numbers_frame.pack(padx=5, pady=(0,5))

for col in range(10):
    Label(numbers_frame, text=str(col+1), font=("Arial",10,"bold"), width=2).grid(row=0, column=col, padx=2)
    Label(numbers_frame, text="", width=2).grid(row=0, column=10)
    Label(numbers_frame, text=str(col+1), font=("Arial",10,"bold"), width=2).grid(row=0, column=col+11, padx=2)

board = Frame(root)
board.pack(padx=10, pady=10, anchor="e")

letters = ['А','Б','В','Г','Д','Е','Ж','З','И','К']
ships = player_ships = [1,1,1,1,2,2,2,3,3,4]
buttons_p, buttons_ai = [], []
board_p, board_ai = [[0]*10 for _ in range(10)], [[0]*10 for _ in range(10)]
player_turn = "player"
ai_possible_moves, player_moves = [(r,c) for r in range(10) for c in range(10)], []
last_hit, last_hit_player = [], []

set_board()

btn_ship = Button(root, text="Разместить корабли", font=("Arial",10), command=place_ships)
btn_ship.pack(padx=10, pady=20, anchor="e")

root.mainloop()