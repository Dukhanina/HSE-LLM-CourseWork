import copy

ROWS=8
COLS=8

def init_board():
    board=[[None]*COLS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            if (r+c)%2==1:
                if r<3:
                    board[r][c]='w'
                elif r>4:
                    board[r][c]='b'
                else:
                    board[r][c]='.'
    return board

def print_board(b):
    print("  a b c d e f g h")
    for r in range(ROWS-1,-1,-1):
        row=str(r+1)+" "
        for c in range(COLS):
            cell=b[r][c]
            row+= (cell if cell else ' ')+" "
        print(row)
    print()

def to_coord(s):
    c=ord(s[0])-ord('a')
    r=int(s[1])-1
    return (r,c)

def opponent(p): return 'b' if p=='w' else 'w'
def is_playable(r,c): return 0<=r<ROWS and 0<=c<COLS and (r+c)%2==1
def piece_color(p): return p.lower() if p and p!='.' else None

def get_capture_moves(b,r,c):
    p=b[r][c]
    col=piece_color(p)
    king=p.isupper()
    seqs=[]
    def backtrack(board,cr,cc,path):
        found=False
        for dr,dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            if king:
                step=1
                while True:
                    pr,pc=cr+dr*step,cc+dc*step
                    if not is_playable(pr,pc): break
                    if board[pr][pc]=='.': step+=1; continue
                    if piece_color(board[pr][pc])==opponent(col):
                        step2=1
                        while True:
                            lr,lc=pr+dr*step2,pc+dc*step2
                            if not is_playable(lr,lc) or board[lr][lc]!='.': break
                            nb=copy.deepcopy(board)
                            nb[pr][pc]='.'
                            nb[cr][cc]='.'
                            nb[lr][lc]=p
                            backtrack(nb,lr,lc,path+[(lr,lc)])
                            found=True
                            step2+=1
                    break
            else:
                pr,pc=cr+dr,cc+dc
                lr,lc=cr+2*dr,cc+2*dc
                if is_playable(pr,pc) and is_playable(lr,lc) and piece_color(board[pr][pc])==opponent(col) and board[lr][lc]=='.':
                    nb=copy.deepcopy(board)
                    nb[pr][pc]='.'
                    nb[cr][cc]='.'
                    nb[lr][lc]=p
                    backtrack(nb,lr,lc,path+[(lr,lc)])
                    found=True
        if not found and path:
            seqs.append([(r,c)]+path)
    backtrack(b,r,c,[])
    return seqs

def get_simple_moves(b,r,c):
    p=b[r][c]
    col=piece_color(p)
    moves=[]
    for dr,dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        if p.islower():
            if col=='w' and dr>0: continue
            if col=='b' and dr<0: continue
            nr, nc = r+dr, c+dc
            if is_playable(nr,nc) and b[nr][nc]=='.':
                moves.append([(r,c),(nr,nc)])
        else:
            step=1
            while True:
                nr, nc = r+dr*step, c+dc*step
                if not is_playable(nr,nc) or b[nr][nc] != '.': break
                moves.append([(r,c),(nr,nc)])
                step+=1
    return moves

def get_all_valid_moves(b,p):
    caps={}
    for r in range(ROWS):
        for c in range(COLS):
            if piece_color(b[r][c])==p:
                seqs=get_capture_moves(b,r,c)
                if seqs:
                    caps[(r,c)]=seqs
    if caps:
        return caps,True
    simples={}
    for r in range(ROWS):
        for c in range(COLS):
            if piece_color(b[r][c])==p:
                mv=get_simple_moves(b,r,c)
                if mv: simples[(r,c)]=mv
    return simples,False

def apply_move(b,path,p):
    r0,c0=path[0]
    piece=b[r0][c0]
    b[r0][c0]='.'
    for r1,c1 in path[1:]:
        if abs(r1-r0)>1:
            dr=(r1-r0)//abs(r1-r0); dc=(c1-c0)//abs(c1-c0)
            rr,cc=r0+dr,c0+dc
            while (rr,cc)!=(r1,c1):
                if piece_color(b[rr][cc])==opponent(p):
                    b[rr][cc]='.'
                    break
                rr+=dr; cc+=dc
        r0,c0=r1,c1
    if (p=='w' and r0==ROWS-1) or (p=='b' and r0==0):
        piece=piece.upper()
    b[r0][c0]=piece

def check_win(b,p):
    moves,_=get_all_valid_moves(b,p)
    if any(piece_color(b[r][c])==p for r in range(ROWS) for c in range(COLS)) and moves:
        return None
    return 'b' if p=='w' else 'w'

def main():
    board=init_board()
    player='w'
    while True:
        print_board(board)
        winner=check_win(board,player)
        if winner:
            print(('White' if winner=='w' else 'Black')+" wins")
            break
        moves,cap=get_all_valid_moves(board,player)
        inp=input(( 'White' if player=='w' else 'Black')+" move: ")
        parts=inp.split('-')
        try:
            path=[to_coord(p) for p in parts]
        except:
            print("Invalid move"); continue
        ok=False
        for seqs in moves.values():
            for seq in seqs:
                if seq==path:
                    ok=True; break
            if ok: break
        if not ok:
            print("Invalid move"); continue
        apply_move(board,path,player)
        player=opponent(player)

if __name__=='__main__':
    main()
