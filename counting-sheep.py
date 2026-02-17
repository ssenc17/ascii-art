import sys
import time
import shutil
import random

_sz = shutil.get_terminal_size((120, 32))
COLS = max(_sz.columns - 1, 100)
ROWS = max(_sz.lines   - 1, 28)

FPS = 16
FRAME_TIME = 1.0 / FPS
JUMP_FRAMES = 40

_NUMBERS = "0123456789"

def _outline(r0, r1, c0, c1):
    pts = []
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if r in (r0, r1) or c in (c0, c1):
                pts.append((r, c))
    return pts

def _flicker(seed):
    return _NUMBERS[(seed + random.randint(0, 9)) % len(_NUMBERS)]

SHEEP_PIXELS = []
SHEEP_PIXELS += _outline(-3, -1, 0, 6)
SHEEP_PIXELS += _outline(-4, -3, 6, 8)
SHEEP_PIXELS += [(0,0), (0,1), (0,5), (0,6)]

SHEEP_W = 9
SHEEP_H = 5

FENCE_W = 12
FENCE_H = 5

def _make_fence():
    rows = []
    for r in range(FENCE_H):
        row = ""
        for c in range(FENCE_W):
            if r == 0 or c in (0, FENCE_W-1):
                row += str((r + c) % 10)
            else:
                row += " "
        rows.append(row)
    return rows

FENCE_ROWS = _make_fence()

GROUND_ROW = ROWS // 2 + 5
FENCE_LC = COLS // 2 - FENCE_W // 2
FENCE_TOP = GROUND_ROW - FENCE_H + 1

X_START = FENCE_LC - SHEEP_W - 10
X_END = FENCE_LC + FENCE_W + 10

def trajectory(t: float):
    x = int(X_START + t * (X_END - X_START))
    lift = int(32 * t * (1 - t))
    return x, lift

def blank():
    return [[' '] * COLS for _ in range(ROWS)]

def put(cv, r, c, ch):
    if 0 <= r < ROWS and 0 <= c < COLS:
        cv[r][c] = ch

def draw_fence(cv):
    for ri, line in enumerate(FENCE_ROWS):
        r = FENCE_TOP + ri
        slant_offset = -ri
        for ci, ch in enumerate(line):
            if ch != ' ':
                put(cv, r, FENCE_LC + ci + slant_offset, ch)

def draw_sheep(cv, anchor_x: int, anchor_y: int):
    for pr, pc in SHEEP_PIXELS:
        put(cv, anchor_y + pr, anchor_x + pc, _flicker(pr + pc))

def draw_scoreboard(cv, sheep_count: int):
    msg = f"  sheep counted: {sheep_count}"
    for ci, ch in enumerate(msg):
        if ci < COLS:
            cv[ROWS - 2][ci] = ch

_ESC = '\033'

def cursor_home():
    sys.stdout.write(f'{_ESC}[H')

def hide_cursor():
    sys.stdout.write(f'{_ESC}[?25l')
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write(f'{_ESC}[?25h')
    sys.stdout.flush()

def clear_screen():
    sys.stdout.write(f'{_ESC}[2J{_ESC}[H')
    sys.stdout.flush()

def main():
    hide_cursor()
    clear_screen()
    frame = 0
    sheep_count = 0
    prev_lines = None

    try:
        while True:
            t0 = time.time()
            t = (frame % JUMP_FRAMES) / JUMP_FRAMES
            if frame % JUMP_FRAMES == 0 and frame > 0:
                sheep_count += 1

            sheep_x, lift = trajectory(t)
            anchor_y = GROUND_ROW - 1 - lift

            cv = blank()
            draw_fence(cv)
            draw_sheep(cv, sheep_x, anchor_y)
            draw_scoreboard(cv, sheep_count)
            cursor_home()
            lines = [''.join(row) for row in cv]

            if lines != prev_lines:
                sys.stdout.write('\n'.join(lines))
                sys.stdout.flush()
                prev_lines = lines
                
            frame += 1
            elapsed = time.time() - t0
            sleep = FRAME_TIME - elapsed

            if sleep > 0:
                time.sleep(sleep)

    except KeyboardInterrupt:
        show_cursor()
        clear_screen()
        print(f"baaaa~ you counted {sheep_count} sheeps. goodnight!")

if __name__ == '__main__':
    main()
