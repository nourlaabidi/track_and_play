from pygame.locals import *
import pygame
import time
import cv2
from ultralytics import YOLO
import numpy as np

model = YOLO('100ep16batchs.pt')
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cv2.namedWindow('Camera Feed')
cv2.moveWindow('Camera Feed', 1200, 0)

def draw_detection(frame, box, label, confidence):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    label_text = f"{label} {confidence:.2f}"
    (label_width, label_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.rectangle(frame, (x1, y1 - 20), (x1 + label_width, y1), (0, 255, 0), -1)
    cv2.putText(frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, (0, 0, 0), 1, cv2.LINE_AA)

map1 ="""                             
                            
wssss        sss  ss   ss  sw
w                           w
w      sss                  w
w           sss           www
www  wwwwww               s w
w      w          w         w
w   wwwww     ssssw  ww  wwww
w      wwwwww     w     w   w
w    w      s   www  wwww   w
w      w          w     w   w
w   wwwwwwwwwwwww w     w   w
w      w          wwwwwww   w
w                           w
wwwwwwwwwwwwwwwwwwwwwwwwwwwww""".splitlines()

WINDOW_SIZE = 1150, 640
game_map = map1

# Initialize Pygame and Audio
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.quit()
pygame.mixer.init(22050, -16, 2, 512)
pygame.mixer.set_num_channels(32)

# Load sounds
jump_sound = pygame.mixer.Sound('data/audio/jump.wav')
grass_sound = pygame.mixer.Sound('data/audio/grass_0.wav')
pygame.mixer.music.load('data/audio/music2.wav')
pygame.mixer.music.play(-1)

# Initialize game window and display
pygame.display.set_caption('Game')
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((WINDOW_SIZE[0] // 2.5, WINDOW_SIZE[1] // 2.5))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
font2 = pygame.font.Font(None, 16)

# Movement variables
moving_right = False
moving_left = False
gravity = 0
air_timer = 0

# Load images
player_image = pygame.image.load('imgs\\player.png')
player_jump = pygame.image.load('imgs\\player_up2.png')
player_jumpl = pygame.transform.flip(player_jump, 1, 0)
player_climb = pygame.image.load('imgs\\player_climb.png')
player_climbl = pygame.transform.flip(player_climb, 1, 0)
player_stand = pygame.image.load('imgs\\player_stand.png')
p_right = player_image
p_left = pygame.transform.flip(player_image, 1, 0)
player_img = p_right
bg = pygame.image.load("imgs\\bg.png")

# Game rectangles and variables
player_rect = pygame.Rect(70, 100, 5, 13)
starting_pos = 100
health = pygame.image.load("imgs\\door.png")
health_rect = pygame.Rect(150, 225, 16, 16)
stamina = 100

def get_gesture():
    success, frame = cap.read()
    if not success:
        return None
        
    # Redimensionner le frame
    frame = cv2.resize(frame, (320, 240))
    
    results = model(frame)
    
    if len(results) > 0 and len(results[0].boxes) > 0:
        boxes = results[0].boxes
        confidences = boxes.conf.cpu().numpy()
        if len(confidences) > 0:
            max_conf_idx = np.argmax(confidences)
            if confidences[max_conf_idx] > 0.5:
                class_id = int(boxes.cls[max_conf_idx])
                
                class_mapping = {
                    3: 'up',
                    0: 'down',
                    2: 'right',
                    1: 'left'
                }
                
                predicted_class = class_mapping.get(class_id)
                if predicted_class:
                    draw_detection(frame, boxes[max_conf_idx], 
                                predicted_class, 
                                confidences[max_conf_idx])
                
                cv2.imshow('Camera Feed', frame)
                cv2.waitKey(1)
                return predicted_class
    
    cv2.imshow('Camera Feed', frame)
    cv2.waitKey(1)
    return None

def load_tiles():
    symb_img = [
                (" ", "space"),
                ("d", "door"),
                ("w", "wall"),
                ("s", "wall_s")]
    dr = "imgs\\"
    tl = {}
    for i in symb_img:
        tl[i[0]] = pygame.image.load(f'{dr}{i[1]}.png')
    return tl

tl = load_tiles()

def collision_test(rect, tiles):
    global stamina
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    if rect.colliderect(health_rect):
        if stamina < 100:
            stamina += 10
            print("Recovering")
    return hit_list

collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
goingright = 0

def move(rect, movement, tiles):
    global player_img, air_timer, gravity, collision_types, moving_right, moving_left
    global goingright, stamina, player_altitude, starting_pos

    player_altitude = player_rect.y
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    
    rect.x += movement[0]
    tile = collision_test(rect, tiles)
    if tile != []:
        tile = tile[0]
        if moving_right:
            rect.right = tile.left
            collision_types['right'] = True
            goingright = 1
            gravity = -1
            player_img = player_climb
            stamina -= 0.02
        elif moving_left:
            goingright = 0
            rect.left = tile.right
            collision_types['left'] = True
            gravity = -1
            player_img = player_climbl
            stamina -= 0.02
            
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            if (rect.bottom - starting_pos) > 50:
                print(rect.bottom - starting_pos)
                stamina -= 30
                pygame.mixer.Sound.play(grass_sound)
                time.sleep(2)
            starting_pos = rect.bottom
            rect.bottom = tile.top
            collision_types['bottom'] = True
            if not moving_left and not moving_right and gravity > 0:
                player_img = player_stand
        elif movement[1] < 0:
            player_img = player_jump
            gravity = -3
            attached = rect.top = tile.bottom
            stamina -= 0.03

    if collision_types['bottom']:
        air_timer = 0
        gravity = 0
    else:
        air_timer += 1
    return rect

def display_tiles():
    tile_rects = []
    y = 0
    for line_of_symbols in game_map:
        x = 0
        for symbol in line_of_symbols:
            if symbol == "\n":
                symbol = " "
            display.blit(tl[symbol], (x * 16, y * 16))
            if symbol not in " h":
                tile_rects.append(pygame.Rect(x * 16, y * 16, 16, 15))
            x += 1
        y += 1
    return tile_rects

player_altitude = player_rect.y

def display_player(pim):
    display.blit(health, (150, 225))
    display.blit(pim, (player_rect.x, player_rect.y))

def display_bg():
    display.blit(bg, (0, 0))

def _display(fnt, what, color, where):
    text_to_show = font.render(what, 0, pygame.Color(color))
    display.blit(text_to_show, where)

def display_text():
    _display(font, str(int(clock.get_fps())), "white", (0,0))
    _display(font2, "Wall climber", 'blue', (100,0))
    _display(font2, "Stamina: " + str(int(stamina)), 'coral', (300,0))
    _display(font2, "altitude: " + str(int(player_altitude)), 'coral', (300, 40))

def clear_screen():
    display.fill((73, 184, 250))

VELOCITY = 1

def move_player():
    global loop, player_rect, moving_right, air_timer, moving_left, gravity
    global collision_types, player_img, stamina
    
    player_movement = [0, 0]
    
    gesture = get_gesture()
    
    if gesture == 'right':
        moving_right = True
        moving_left = False
        player_img = p_right
    elif gesture == 'left':
        moving_left = True
        moving_right = False
        player_img = p_left
    else:
        moving_right = False
        moving_left = False
    
    if gesture == 'up':
        if air_timer < 6:
            gravity = -5
            stamina -= 3
            pygame.mixer.Sound.play(jump_sound)
    elif gesture == 'down':
        if air_timer == 0:
            player_img = player_jump
            gravity = +1

    if moving_right:
        player_movement[0] += VELOCITY
        stamina += 0.005
    if moving_left:
        player_movement[0] -= VELOCITY
        stamina += 0.005
    player_movement[1] += gravity

    gravity += 0.3
    if gravity > 3:
        gravity = 3

    player_rect = move(player_rect, player_movement, tile_rects)

    for event in pygame.event.get():
        if event.type == QUIT:
            loop = 0
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            loop = 0

    return player_img

def scale_screen():
    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

def run_game():
    global loop, stamina, tile_rects, player_img
    
    loop = 1
    while loop:
        stamina -= 0.001
        clear_screen()
        tile_rects = display_tiles()
        player_img = move_player()
        display_player(player_img)
        display_text()
        scale_screen()
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    run_game()
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()