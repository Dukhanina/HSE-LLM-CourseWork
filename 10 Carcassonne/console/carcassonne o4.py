import random

TILE_TYPES = [
    {'name':'road_straight','edges':{'N':'road','E':'field','S':'road','W':'field'},'monastery':False,'shields':0},
    {'name':'road_curve','edges':{'N':'road','E':'road','S':'field','W':'field'},'monastery':False,'shields':0},
    {'name':'city_1','edges':{'N':'city','E':'field','S':'field','W':'field'},'monastery':False,'shields':1},
    {'name':'monastery','edges':{'N':'field','E':'field','S':'field','W':'field'},'monastery':True,'shields':0}
]

def rotate(tile,r):
    dirs=['N','E','S','W']
    e=tile['edges']
    ne={}
    for i,d in enumerate(dirs):
        ne[d]=e[dirs[(i-r)%4]]
    return {'name':tile['name'],'edges':ne,'monastery':tile['monastery'],'shields':tile['shields']}

def init_deck():
    deck=[]
    for t in TILE_TYPES:
        deck += [t.copy() for _ in range(10)]
    random.shuffle(deck)
    return deck

def valid_placement(board,x,y,t):
    if (x,y) in board: return False
    dirs={'N':(0,1),'E':(1,0),'S':(0,-1),'W':(-1,0)}
    has_neighbor=False
    for d,(dx,dy) in dirs.items():
        nx,ny=x+dx,y+dy
        if (nx,ny) in board:
            has_neighbor=True
            opposite={'N':'S','S':'N','E':'W','W':'E'}
            ne=board[(nx,ny)]['edges'][opposite[d]]
            if ne!=t['edges'][d]: return False
    return has_neighbor

def print_board(board):
    print("Current board placements:")
    for (x,y),tile in sorted(board.items()):
        print(f" ({x},{y}): {tile['name']} edges={tile['edges']}")
    print()

def get_placement(board,tile):
    print("Tile to place:", tile['name'], "edges:", tile['edges'])
    while True:
        inp=input("Enter x y rotation(0-3), e.g. '1 0 2': ").strip()
        parts=inp.split()
        if len(parts)!=3:
            print("Invalid input. Please enter three values: x y rotation.")
            continue
        try:
            x=int(parts[0]); y=int(parts[1]); rot=int(parts[2])
        except ValueError:
            print("Coordinates and rotation must be integers.")
            continue
        if rot<0 or rot>3:
            print("Rotation must be 0, 1, 2, or 3.")
            continue
        t=rotate(tile,rot)
        if not valid_placement(board,x,y,t):
            print(f"Cannot place at ({x},{y}) with rotation {rot}. Check matching edges and adjacency.")
            continue
        return x,y,t

def place_meeple(tile,x,y,player,meeples):
    if input("Place meeple? (y/n): ").lower()!='y': return
    feat=input("Feature to claim [N/E/S/W/C]: ").upper()
    if feat=='C' and tile['monastery']:
        meeples.append({'pos':(x,y),'feature':'monastery','player':player})
    elif feat in tile['edges'] and tile['edges'][feat] in ('road','city'):
        for m in meeples:
            if m['pos']==(x,y) and m['feature']==tile['edges'][feat]:
                return
        meeples.append({'pos':(x,y),'feature':tile['edges'][feat],'player':player})

def get_road_cluster(board,start):
    dirs={'N':(0,1),'E':(1,0),'S':(0,-1),'W':(-1,0)}
    seen={start}; stack=[start]
    while stack:
        x,y=stack.pop()
        t=board[(x,y)]
        for d,(dx,dy) in dirs.items():
            if t['edges'][d]=='road':
                nx,ny=x+dx,y+dy
                if (nx,ny) in board:
                    ot=board[(nx,ny)]['edges'][{'N':'S','S':'N','E':'W','W':'E'}[d]]
                    if ot=='road' and (nx,ny) not in seen:
                        seen.add((nx,ny)); stack.append((nx,ny))
    return seen

def road_complete(board,cluster):
    dirs={'N':(0,1),'E':(1,0),'S':(0,-1),'W':(-1,0)}
    for x,y in cluster:
        t=board[(x,y)]
        for d,(dx,dy) in dirs.items():
            if t['edges'][d]=='road':
                nx,ny=x+dx,y+dy
                if (nx,ny) not in cluster and (nx,ny) not in board:
                    return False
    return True

def check_monastery(board,x,y):
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            if dx==0 and dy==0: continue
            if (x+dx,y+dy) not in board: return False
    return True

def score_features(board,meeples,scores):
    for m in meeples[:]:
        x,y=m['pos']
        if m['feature']=='road':
            cluster=get_road_cluster(board,(x,y))
            if road_complete(board,cluster):
                scores[m['player']]+=len(cluster)
                meeples.remove(m)
        if m['feature']=='monastery':
            if check_monastery(board,x,y):
                scores[m['player']]+=9
                meeples.remove(m)

def final_scoring(board,meeples,scores):
    for m in meeples:
        x,y=m['pos']
        if m['feature']=='road':
            cluster=get_road_cluster(board,(x,y))
            scores[m['player']]+=len(cluster)//2
        if m['feature']=='monastery':
            cnt=1
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx==0 and dy==0: continue
                    if (x+dx,y+dy) in board: cnt+=1
            scores[m['player']]+=cnt

def main():
    players=int(input("Number of players: "))
    deck=init_deck()
    board={(0,0):TILE_TYPES[2].copy()}
    meeples=[]; scores=[0]*players; current=0
    while deck:
        tile=deck.pop()
        print(f"\nPlayer {current+1} draws {tile['name']}")
        print_board(board)
        x,y,t=get_placement(board,tile)
        board[(x,y)]=t
        place_meeple(t,x,y,current,meeples)
        score_features(board,meeples,scores)
        print("Scores:",scores)
        current=(current+1)%players
    final_scoring(board,meeples,scores)
    print("\nFinal scores:",scores)
    winner=max(range(players),key=lambda i:scores[i])
    print(f"Player {winner+1} wins")

if __name__=='__main__':
    main()
