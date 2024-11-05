import time
import win32api, win32con
import pyautogui
import mouse

# Every valid tile in this coordinate system
VALID_TILES = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
               (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
               (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
               (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
               (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
               (5, 2), (5, 3), (5, 4),
               (6, 3)
               ]

# The coordinates of the bottom row of this board
BUTTOM_ROW = [(3, 0), (4, 1), (5, 2), (6, 3), (5, 4), (4, 5), (3, 6)]

# A mapping of coordinate to x, y position of the screen
COORDINATES = [
    [(786, 482), (846, 451), (899, 418), (961, 382), (1013, 416), (1069, 446), (1127, 485)], 
    [(787, 583), (843, 519), (903, 485), (961, 451), (1013, 476), (1072, 516), (1127, 549)], 
    [(788, 615), (846, 575), (900, 548), (961, 516), (1014, 550), (1072, 574), (1130, 611)], 
    [(788, 676), (846, 641), (900, 612), (961, 581), (1013, 609), (1070, 640), (1127, 673)], 
    [(-10, -10), (844, 705), (905, 679), (961, 646), (1015, 678), (1072, 711), (-100, -10)], 
    [(-10, -10), (-10, -10), (900, 743), (961, 712), (1015, 736), (-100, -10), (-100, -10)], 
    [(-10, -10), (-10, -10), (-10, -10), (961, 773), (-100, -10), (-100, -10), (-100, -10)]
]


def image_input():
    """
    take a ss, returns list of list of boolean operators as board state.
    gray (2) == False, black (1) == True
    """
    time.sleep(5)
    img = pyautogui.screenshot()
    ret = [[] for i in range(7)]
    for i in ret:
        for j in range(7):
            i.append(False)

    for i in VALID_TILES:
        r,g,b = img.getpixel(COORDINATES[i[0]][i[1]])
        if g > 50:
            ret[i[0]][i[1]] = False
        else:
            ret[i[0]][i[1]] = True
    return ret


def solve(board_state) -> list:
    """
    returns which button to press to solve the puzzle
    """
    ret = []
    order = [(0, 3), (0, 2), (0, 4), (0, 1), (0, 5), (0, 0), (0, 6),
             (1, 3), (1, 2), (1, 4), (1, 1), (1, 5), (1, 0), (1, 6),
             (2, 3), (2, 2), (2, 4), (2, 1), (2, 5), (2, 0), (2, 6),
             (3, 3), (3, 2), (3, 4), (3, 1), (3, 5),
             (4, 3), (4, 2), (4, 4),
             (5, 3)]
    
    # Propagate downwards
    for i in order:
        if not board_state[i[0]][i[1]] and (i[0] + 1, i[1]) in VALID_TILES:
            press(i[0] + 1, i[1], board_state)
            ret.append((i[0] + 1, i[1]))
    
    # Check if parity works out (12.5% chance)
    res = True
    for i in VALID_TILES:
        if not board_state[i[0]][i[1]]:
            res = False
            break
    if res:
        return ret
    
    # parity time
    parity_bits = []
    for i in BUTTOM_ROW:
        # Look at the buttom row to determine the parity
        parity_bits.append(board_state[i[0]][i[1]])
    
    # Turn the list into a tuple, for use in dict
    lookup_key = tuple(parity_bits)
    
    solve_parity_clicks = parity_lookup(lookup_key)

    for i in solve_parity_clicks:
        ret.append(i)

    # Propagate again; this time solving this board
    for i in order:
        if not board_state[i[0]][i[1]] and (i[0] + 1, i[1]) in VALID_TILES:
            press(i[0] + 1, i[1], board_state)
            # Clicking the same buttom twice is equivalent to not clicking at all 
            if (i[0] + 1, i[1]) in ret:
                ret.remove((i[0] + 1, i[1]))
            else:
                ret.append((i[0] + 1, i[1]))
    
    # Return a list of coordinates to click on
    return ret


def parity_lookup(lookup_key):
    # Populate the parity dictionary
    lookup_dict = dict()
    lookup_dict[(True, True, False, True, False, True, True)] = [(0, 3), (0, 6)]
    lookup_dict[(True, False, True, False, True, False, True)] = [(0, 4), (0, 5)]
    lookup_dict[(True, False, False, False, False, False, True)] = [(0, 1), (0, 3), (0, 4), (0, 6)]
    lookup_dict[(False, True, True, False, True, True, False)] = [(0, 3), (0, 5)]
    lookup_dict[(False, True, False, False, False, True, False)] = [(0, 3)]
    lookup_dict[(False, False, True, True, True, False, False)] = [(0, 4), (0, 5), (0, 6)]
    lookup_dict[(False, False, False, True, False, False, False)] = [(0, 2), (0, 3), (0, 5)]
    
    return lookup_dict[lookup_key]


def press(x, y, board_state) -> None:
    """
    emulates a button press on the coordinate x, y
    """
    # The adjancies of this coordinate system depends on y
    offset3 = [(0, -1), (0, 0), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1)]
    offsetL = [(0, -1), (0, 0), (0, 1), (-1, -1), (-1, 0), (1, 0), (1, 1)]
    offsetR = [(0, -1), (0, 0), (0, 1), (-1, 1), (-1, 0), (1, 0), (1, -1)]
    if y == 3:
        for i in offset3:
            if (x + i[0], y + i[1]) in VALID_TILES:
                board_state[x + i[0]][y + i[1]] ^= True
    elif y < 3:
        for i in offsetL:
            if (x + i[0], y + i[1]) in VALID_TILES:
                board_state[x + i[0]][y + i[1]] ^= True
    else:
        for i in offsetR:
            if (x + i[0], y + i[1]) in VALID_TILES:
                board_state[x + i[0]][y + i[1]] ^= True
        

def mouse_press_list(to_press) -> None:
    """
    Take in a list of buttons to press, and move the mouse to press them
    """
    for i in to_press:
        mouse_click2(COORDINATES[i[0]][i[1]][0], COORDINATES[i[0]][i[1]][1])


def mouse_click(x, y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(0.15)


def mouse_click2(x, y):
    # Somehow a little more reliable than mouse_click
    mouse.move(x, y, absolute=True, duration=0.05)
    time.sleep(0.05)
    mouse.click('left')
    time.sleep(0.15)


bs = image_input()
# print(bs)
tpl = solve(bs)
mouse_press_list(tpl)
print("Yes")
