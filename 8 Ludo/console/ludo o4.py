import random

TRACK_LEN=52
HOME_LAPS=1
START_INDICES=[0,13]

def roll_dice():
    return random.randint(1,6)

def init_pawns():
    pos = [ [START_INDICES[i]]*4 for i in range(2) ]
    laps = [ [0]*4 for _ in range(2) ]
    return pos, laps

def get_block_positions(pos, laps, player):
    counts = {}
    for p, l in zip(pos[player], laps[player]):
        if l==0:
            counts[p] = counts.get(p,0) + 1
    return {p for p,count in counts.items() if count>=2}

def get_playable_moves(player, roll, pos, laps):
    start = START_INDICES[player]
    opp = 1-player
    block_opp = get_block_positions(pos, laps, opp)
    valid = []
    for i in range(4):
        if laps[player][i] >= HOME_LAPS and pos[player][i] == start:
            continue
        cur = pos[player][i]
        lp = laps[player][i]
        new = cur + roll
        new_laps = lp
        if new >= TRACK_LEN:
            new_laps += 1
            new = new - TRACK_LEN
        if new_laps >= HOME_LAPS and new == start:
            valid.append(i)
            continue
        if new_laps==0 and new in block_opp:
            continue
        valid.append(i)
    return valid

def move_pawn(player, i, roll, pos, laps):
    start = START_INDICES[player]
    opp = 1-player
    cur = pos[player][i]
    lp = laps[player][i]
    new = cur + roll
    new_laps = lp
    if new >= TRACK_LEN:
        new_laps += 1
        new = new - TRACK_LEN
    finished = False
    if new_laps >= HOME_LAPS and new == start:
        finished = True
    pos[player][i] = new
    laps[player][i] = new_laps
    extra = False
    if not finished and new_laps==0:
        opp_indices = [j for j,(p,l) in enumerate(zip(pos[opp],laps[opp])) if p==new and l==0]
        if len(opp_indices)==1:
            j=opp_indices[0]
            pos[opp][j] = START_INDICES[opp]
            laps[opp][j] = 0
            extra = True
    return extra

def check_win(player, pos, laps):
    start = START_INDICES[player]
    return all(laps[player][i]>=HOME_LAPS and pos[player][i]==start for i in range(4))

def main():
    pos, laps = init_pawns()
    current = 0
    while True:
        roll = roll_dice()
        print(f"Player {current+1} rolled {roll}")
        valid = get_playable_moves(current, roll, pos, laps)
        if not valid:
            print("No valid moves")
            current = 1-current
            continue
        print("Pawns:")
        for i in valid:
            print(f"{i+1}: pos={pos[current][i]} laps={laps[current][i]}")
        choice = input("Choose pawn: ").strip()
        if not choice.isdigit():
            print("Invalid input"); continue
        i = int(choice)-1
        if i not in valid:
            print("Invalid move"); continue
        extra = move_pawn(current, i, roll, pos, laps)
        if check_win(current, pos, laps):
            print(f"Player {current+1} wins")
            break
        if roll!=6 and not extra:
            current = 1-current

if __name__=='__main__':
    main()
