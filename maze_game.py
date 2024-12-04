from maze_generator import *
import cv2
from ultralytics import YOLO
import numpy as np
import os

# Button class definition
class Button:
    def __init__(self, x, y, width, height, text, text_size=30, color=(100, 100, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, text_size)
        self.is_hovered = False

    def draw(self, surface):
        # Semi-transparent background
        s = pygame.Surface((self.rect.width, self.rect.height))
        s.set_alpha(128)
        s.fill(self.color)
        surface.blit(s, (self.rect.x, self.rect.y))
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        # Text
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Food:
    def __init__(self):
        self.img = pygame.image.load('img/food.png').convert_alpha()
        self.img = pygame.transform.scale(self.img, (TILE - 10, TILE - 10))
        self.rect = self.img.get_rect()
        self.set_pos()

    def set_pos(self):
        self.rect.topleft = randrange(cols) * TILE + 5, randrange(rows) * TILE + 5

    def draw(self):
        game_surface.blit(self.img, self.rect)

def is_collide(x, y):
    tmp_rect = player_rect.move(x, y)
    if tmp_rect.collidelist(walls_collide_list) == -1:
        return False
    return True

def eat_food():
    for food in food_list:
        if player_rect.collidepoint(food.rect.center):
            food.set_pos()
            return True
    return False

def is_game_over():
    global time, score, record, FPS
    if time < 0:
        pygame.time.wait(700)
        player_rect.center = TILE // 2, TILE // 2
        [food.set_pos() for food in food_list]
        set_record(record, score)
        record = get_record()
        time, score, FPS = 120, 0, 60

def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')
            return 0

def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))

def draw_detection(frame, box, label, confidence):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    label_text = f"{label} {confidence:.2f}"
    (label_width, label_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.rectangle(frame, (x1, y1 - 20), (x1 + label_width, y1), (0, 255, 0), -1)
    cv2.putText(frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, (0, 0, 0), 1, cv2.LINE_AA)

def run_game():
    global time, score, record, FPS, direction, recent_predictions, game_surface, surface
    global player_rect, walls_collide_list, food_list, player_img, bg, bg_game

    # Initialize camera and YOLO model
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    model = YOLO('100ep16batchs.pt')

    # Position the game window
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

    # Game initialization
    FPS = 60
    pygame.init()
    game_surface = pygame.Surface(RES)
    surface = pygame.display.set_mode((WIDTH + 150, HEIGHT))
    pygame.display.set_caption('Maze Game')
    clock = pygame.time.Clock()

    # Images
    bg_game = pygame.image.load('img/bg_1.jpg').convert()
    bg_game = pygame.transform.scale(bg_game, RES)
    bg = pygame.image.load('img/bg_main.jpg').convert()
    bg = pygame.transform.scale(bg, (150, HEIGHT))

    # Create back button
    # Create back button
    back_button = Button(WIDTH + 15, HEIGHT - 45, 120, 35, "Back to Menu", text_size=25)

    # Get maze
    maze = generate_maze()

    # Player settings
    player_speed = 3
    player_img = pygame.image.load('img/0.png').convert_alpha()
    player_img = pygame.transform.scale(player_img, (TILE - 2 * maze[0].thickness, TILE - 2 * maze[0].thickness))
    player_rect = player_img.get_rect()
    player_rect.center = TILE // 2, TILE // 2

    directions = {
        'up': (0, -player_speed),
        'down': (0, player_speed),
        'left': (-player_speed, 0),
        'right': (player_speed, 0)
    }
    direction = (0, 0)

    # Food settings
    food_list = [Food() for i in range(3)]

    # Collision list
    walls_collide_list = sum([cell.get_rects() for cell in maze], [])

    # Timer, score, record
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    time = 120
    score = 0
    record = get_record()

    # Fonts
    font = pygame.font.SysFont('Impact', 60)
    text_font = pygame.font.SysFont('Impact', 30)

    # Movement smoothing
    prediction_confidence_threshold = 0.7
    smoothing_frames = 3
    recent_predictions = []

    # Position camera window
    cv2.namedWindow('Camera Feed with Detections')
    cv2.moveWindow('Camera Feed with Detections', WIDTH + 150, 0)

    try:
        while True:
            surface.blit(bg, (WIDTH, 0))
            surface.blit(game_surface, (0, 0))
            game_surface.blit(bg_game, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                
                if back_button.handle_event(event):
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                
                if event.type == pygame.USEREVENT:
                    time -= 1

            # Camera processing and gameplay code
            ret, frame = cap.read()
            if ret:
                results = model(frame)
                
                if len(results) > 0 and len(results[0].boxes) > 0:
                    boxes = results[0].boxes
                    confidences = boxes.conf.cpu().numpy()
                    if len(confidences) > 0:
                        max_conf_idx = np.argmax(confidences)
                        if confidences[max_conf_idx] > prediction_confidence_threshold:
                            class_id = int(boxes.cls[max_conf_idx])
                            predicted_class = results[0].names[class_id]
                            
                            class_mapping = {
                                3: 'up',
                                0: 'down',
                                2: 'right',
                                1: 'left'
                            }
                            
                            predicted_class = class_mapping.get(class_id, None)
                            if predicted_class:
                                draw_detection(frame, boxes[max_conf_idx], 
                                            predicted_class, 
                                            confidences[max_conf_idx])
                                
                                recent_predictions.append(predicted_class)
                                if len(recent_predictions) > smoothing_frames:
                                    recent_predictions.pop(0)
                                
                                if len(recent_predictions) == smoothing_frames:
                                    current_prediction = max(set(recent_predictions), key=recent_predictions.count)
                                    if current_prediction in directions:
                                        direction = directions[current_prediction]

                cv2.imshow('Camera Feed with Detections', frame)
                cv2.waitKey(1)

            if not is_collide(*direction):
                player_rect.move_ip(direction)

            [cell.draw(game_surface) for cell in maze]

            if eat_food():
                FPS += 10
                score += 1
            is_game_over()

            game_surface.blit(player_img, player_rect)
            [food.draw() for food in food_list]

            # Draw stats - Positions modifiées
            # Draw stats - Positions encore plus ajustées
            surface.blit(text_font.render('TIME', True, pygame.Color('cyan'), True), (WIDTH + 35, 30))
            surface.blit(font.render(f'{time}', True, pygame.Color('cyan')), (WIDTH + 35, 70))
            surface.blit(text_font.render('score:', True, pygame.Color('forestgreen'), True), (WIDTH + 25, 130))
            surface.blit(font.render(f'{score}', True, pygame.Color('forestgreen')), (WIDTH + 35, 170))
            surface.blit(text_font.render('record:', True, pygame.Color('magenta'), True), (WIDTH + 15, 230))
            surface.blit(font.render(f'{record}', True, pygame.Color('magenta')), (WIDTH + 35, 270))

            # Draw back button
            back_button.draw(surface)

            pygame.display.flip()
            clock.tick(FPS)

    except KeyboardInterrupt:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_game()
    pygame.quit()