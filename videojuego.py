# videojuego.py

import pygame
import random
import math
from PIL import Image, ImageSequence # Importar Pillow para GIFs

# 1. Inicialización de Pygame
pygame.init()

# --- Configuración General ---
# Obtener la resolución actual de la pantalla para el modo de pantalla completa
INFO = pygame.display.Info()
SCREEN_WIDTH = INFO.current_w
SCREEN_HEIGHT = INFO.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN) # ¡Pantalla completa!
pygame.display.set_caption("Las Aventuras De Tralalero Tralala")

# --- Colores ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE_LIGHT = (173, 216, 230) # Fondo suave
YELLOW_LIGHT = (255, 255, 150) # Para objetos o UI
BUTTON_COLOR = (100, 100, 255) # Un color base para los botones
HOVER_COLOR = (150, 150, 255) # Color al pasar el ratón por encima
SOLID_OBSTACLE_COLOR = (139, 69, 19) # Color marrón para los obstáculos sólidos (ej. rocas, troncos)
DEADLY_OBSTACLE_COLOR = (255, 0, 0) # Color rojo brillante para obstáculos mortales (ej. lava, pinchos)
ENEMY_COLOR = (150, 0, 0) # Color para los enemigos
PLAYER_ATTACK_COLOR = (255, 165, 0) # Naranja para indicar ataque
ENEMY_ATTACK_COLOR = (255, 0, 0) # Color para indicar ataque del enemigo
POPUP_BACKGROUND_COLOR = (200, 200, 200, 180) # Gris semi-transparente para el fondo del popup
HEALTH_BAR_COLOR = (50, 200, 50) # Color para la barra de vida del enemigo
HEALTH_BAR_BACKGROUND_COLOR = (100, 0, 0) # Fondo de la barra de vida del enemigo
PLAYER_HEALTH_BAR_COLOR = (0, 255, 0)  # Color para la barra de vida del jugador
PLAYER_HEALTH_BAR_BACKGROUND_COLOR = (255, 0, 0) # Fondo de la barra de vida del jugador


# --- Fuentes ---
font_large = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.15)) # Para el título, Game Over
font_medium = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.1)) # Para las opciones o botones
font_small = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.07)) # Para mensajes más pequeños

# Fuentes específicas para el juego
font_operation = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.1)) # Para la operación
font_counter = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.06)) # Para el contador de objetos
font_goal = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.08)) # Para los números de las metas
font_feedback = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.065)) # Para mensajes de retroalimentación
font_lives = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.06)) # Para mostrar las vidas
font_health = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.06)) # Para mostrar la vida del jugador
font_button = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.05)) # Para el texto de los botones
font_popup_title = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.09)) # Para títulos de popups
font_popup_text = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.04)) # Para texto de popups

# --- Sonidos (Asegúrate de que los archivos .wav existan en la misma carpeta) ---
try:
    sound_collect = pygame.mixer.Sound("assets/audios/collect.wav")
    sound_correct = pygame.mixer.Sound("assets/audios/correct.wav")
    sound_incorrect = pygame.mixer.Sound("assets/audios/incorrect.wav")
    sound_hit_deadly = pygame.mixer.Sound("assets/audios/hit_deadly.wav")
    sound_enemy_hit = pygame.mixer.Sound("assets/audios/enemy_hit.wav")
    sound_player_hit = pygame.mixer.Sound("assets/audios/player_hit.wav")
    sound_enemy_death = pygame.mixer.Sound("assets/audios/enemy_death.wav")
    sound_win = pygame.mixer.Sound("assets/audios/win.wav") # Nuevo sonido de victoria
    sound_game_over = pygame.mixer.Sound("assets/audios/game_over.wav") # Nuevo sonido de game over
except pygame.error as e:
    print(f"Advertencia: No se pudieron cargar los sonidos: {e}. Asegúrate de que existan los archivos 'collect.wav', 'correct.wav', 'incorrect.wav', 'hit_deadly.wav', 'enemy_hit.wav', 'player_hit.wav', 'enemy_death.wav', 'win.wav', 'game_over.wav' en la misma carpeta.")
    sound_collect = None
    sound_correct = None
    sound_incorrect = None
    sound_hit_deadly = None
    sound_enemy_hit = None
    sound_player_hit = None
    sound_enemy_death = None
    sound_win = None
    sound_game_over = None

# --- Constantes de Juego ---
PLAYER_INITIAL_HEALTH = 100
ENEMY_ATTACK_DAMAGE = 10
DEADLY_OBSTACLE_DAMAGE = 10
PLAYER_ATTACK_COOLDOWN = 500 # milisegundos
PLAYER_ATTACK_DAMAGE = 25 # Daño que hace el jugador al enemigo (Aumentado para que mueran más rápido)
PLAYER_ATTACK_ANIM_DURATION = 10 # Duración de la animación de ataque del jugador
ENEMY_ATTACK_ANIM_DURATION = 100 # Duración de la animación de ataque del enemigo
UI_BAR_HEIGHT = int(SCREEN_HEIGHT * 0.1) # Altura de la barra de UI superior
INVULNERABILITY_DURATION = 1250 # milisegundos de invulnerabilidad después de ser golpeado
ENEMY_INITIAL_HEALTH = 100 # Salud inicial de los enemigos
ENEMY_AGGRO_RADIUS = int(SCREEN_WIDTH * 0.2) # Radio para que el enemigo se vuelva agresivo por proximidad

# --- Clases de Juego ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Cargar imagen del jugador
        self.image = pygame.image.load("assets/imagenes/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.1))) # Tamaño ajustado
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.collected_objects = 0
        self.prev_rect = self.rect.copy() # Para revertir posición en colisiones con obstáculos
        self.health = PLAYER_INITIAL_HEALTH
        self.max_health = PLAYER_INITIAL_HEALTH # MODIFICADO: Añadir max_health para la barra
        self.is_attacking = False
        self.last_attack_time = 0
        self.attack_anim_start_time = 0 # Nuevo para la animación
        self.last_hit_time = 0 # Nuevo: para la invulnerabilidad
    def update(self, keys):
        self.prev_rect = self.rect.copy() # Guarda la posición anterior
        # Resetear estado de ataque de la animación
        if pygame.time.get_ticks() - self.attack_anim_start_time > PLAYER_ATTACK_ANIM_DURATION:
            self.is_attacking = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        # Ataque con la tecla ESPACIO
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and current_time - self.last_attack_time > PLAYER_ATTACK_COOLDOWN:
            self.is_attacking = True
            self.last_attack_time = current_time
            self.attack_anim_start_time = current_time # Iniciar el temporizador de animación
        # Mantener al jugador dentro de los límites de la pantalla (excluyendo el área de la UI superior)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(UI_BAR_HEIGHT, self.rect.top) # Evitar que suba a la zona de la operación
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)
    def revert_position(self):
        self.rect = self.prev_rect.copy() # Vuelve a la posición guardada
    def add_object(self):
        self.collected_objects += 1
        if sound_collect:
            sound_collect.play()
    def drop_object(self):
        if self.collected_objects > 0:
            self.collected_objects -= 1
            if sound_collect: # Podrías usar otro sonido, o el mismo
                sound_collect.play()
    def reset_objects(self):
        self.collected_objects = 0
    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time > INVULNERABILITY_DURATION: #
            self.health -= amount
            if self.health < 0:
                self.health = 0
            if sound_player_hit:
                sound_player_hit.play()
            self.last_hit_time = current_time # Reiniciar el temporizador de invulnerabilidad
    def reset_health(self):
        self.health = PLAYER_INITIAL_HEALTH
    def draw_health_bar(self, surface):
        if self.health > 0 : # Solo dibujar si tiene vida
            bar_width = self.rect.width * 0.8 # Un poco más ancha que el jugador
            bar_height = 8 # Altura de la barra
            bar_x = self.rect.centerx - bar_width // 2 # Centrada sobre el jugador
            bar_y = self.rect.top - 15 # 15 píxeles por encima del jugador

            # Fondo de la barra de vida
            pygame.draw.rect(surface, PLAYER_HEALTH_BAR_BACKGROUND_COLOR, (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            # Barra de vida actual
            current_health_width = (self.health / self.max_health) * bar_width
            if current_health_width > 0: # Solo dibujar la barra verde si hay vida
                 pygame.draw.rect(surface, PLAYER_HEALTH_BAR_COLOR, (bar_x, bar_y, current_health_width, bar_height), border_radius=3)


class CollectibleObject(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Cargar imagen del objeto
        self.image = pygame.image.load("assets/imagenes/star.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.03), int(SCREEN_HEIGHT * 0.04))) # Tamaño ajustado
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False
class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y, value):
        super().__init__()
        self.value = value
        # Cargar imagen de la meta
        self.image = pygame.image.load("assets/imagenes/goal.png").convert_alpha()
        # Reducir el tamaño de la imagen de la meta
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.09))) # ¡Tamaño más pequeño!
        self.rect = self.image.get_rect(center=(x, y))
        # Crear un rect de colisión más pequeño que la imagen
        self.collision_rect = pygame.Rect(0, 0, self.image.get_width() * 0.7, self.image.get_height() * 0.7)
        self.collision_rect.center = self.rect.center # Centrar el rect de colisión
        # Renderizar el número de la meta en la imagen
        text_surface = font_goal.render(str(self.value), True, BLACK)
        text_rect = text_surface.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))
        self.image.blit(text_surface, text_rect)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obs_type="solid"): # obs_type: "solid" o "deadly"
        super().__init__()
        self.type = obs_type
        # Para empezar, un simple rectángulo. Puedes reemplazar con una imagen.
        self.image = pygame.Surface((width, height))
        if self.type == "solid":
            # self.image.fill(SOLID_OBSTACLE_COLOR) # Color marrón para un obstáculo sólido # Comentado para priorizar imagen
            try: # Cargar imagen de roca
                self.image = pygame.image.load("assets/imagenes/rock.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except pygame.error:
                self.image.fill(SOLID_OBSTACLE_COLOR) # Si la imagen no se carga, usa el color
        elif self.type == "deadly":
            # self.image.fill(DEADLY_OBSTACLE_COLOR) # Color rojo para un obstáculo mortal # Comentado para priorizar imagen
            try: # Cargar imagen de lava
                self.image = pygame.image.load("assets/imagenes/lava.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except pygame.error:
                self.image.fill(DEADLY_OBSTACLE_COLOR) # Si la imagen no se carga, usa el color
        self.rect = self.image.get_rect(center=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/imagenes/enemy.png").convert_alpha() # Cargar imagen del enemigo
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.09))) # Tamaño del enemigo
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 4
        self.health = ENEMY_INITIAL_HEALTH
        self.max_health = ENEMY_INITIAL_HEALTH # Para la barra de vida
        self.attack_cooldown = 500 # Cooldown para atacar al jugador (milisegundos)
        self.last_attack_time = 0
        self.damage_taken_this_attack = False # Nuevo: Para evitar daño múltiple por un solo ataque de jugador
        self.is_aggressive = False # Nuevo: el enemigo es pasivo al inicio
        self.is_attacking_anim = False # Nuevo: para la animación de ataque del enemigo
        self.attack_anim_start_time = 0 # Nuevo: para el temporizador de la animación
    def update(self, player_rect):
        # Resetear estado de ataque de la animación
        if pygame.time.get_ticks() - self.attack_anim_start_time > ENEMY_ATTACK_ANIM_DURATION:
            self.is_attacking_anim = False
        # Comprobar proximidad del jugador para volverse agresivo
        distance_to_player = math.hypot(self.rect.centerx - player_rect.centerx, self.rect.centery - player_rect.centery)
        if distance_to_player < ENEMY_AGGRO_RADIUS:
            self.is_aggressive = True
        if self.is_aggressive: # Solo persigue al jugador si es agresivo
            # Moverse hacia el jugador
            if self.rect.x < player_rect.x:
                self.rect.x += self.speed
            elif self.rect.x > player_rect.x:
                self.rect.x -= self.speed
            if self.rect.y < player_rect.y:
                self.rect.y += self.speed
            elif self.rect.y > player_rect.y:
                self.rect.y -= self.speed
        # Mantener al enemigo dentro de los límites de la pantalla (excluyendo el área de la UI superior)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(UI_BAR_HEIGHT, self.rect.top) # Evitar que suba a la zona de la operación
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)
        self.damage_taken_this_attack = False # Resetear al inicio del update del enemigo
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        if sound_enemy_hit:
            sound_enemy_hit.play()
        self.damage_taken_this_attack = True # Marca que fue dañado
        self.is_aggressive = True # El enemigo se vuelve agresivo al ser atacado
    def can_attack(self):
        return pygame.time.get_ticks() - self.last_attack_time > self.attack_cooldown
    def attack(self, player_obj):
        if self.can_attack():
            player_obj.take_damage(ENEMY_ATTACK_DAMAGE)
            self.last_attack_time = pygame.time.get_ticks()
            self.is_attacking_anim = True # Iniciar animación de ataque del enemigo
            self.attack_anim_start_time = pygame.time.get_ticks() # Iniciar temporizador de animación
    def draw_health_bar(self, surface):
        if self.health > 0: # Solo dibujar si tiene vida
            bar_width = self.rect.width * 0.8
            bar_height = 5
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.top - 15 # Encima del enemigo
            # Fondo de la barra de vida
            pygame.draw.rect(surface, HEALTH_BAR_BACKGROUND_COLOR, (bar_x, bar_y, bar_width, bar_height), border_radius=2)
            # Barra de vida actual
            current_health_width = (self.health / self.max_health) * bar_width
            if current_health_width > 0: # Solo dibujar la barra verde si hay vida
                pygame.draw.rect(surface, HEALTH_BAR_COLOR, (bar_x, bar_y, current_health_width, bar_height), border_radius=2)

# --- Variables Globales del Juego ---
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.15) # Altura inicial un poco más arriba
player = Player(PLAYER_START_X, PLAYER_START_Y) # Posición inicial del jugador
all_sprites = pygame.sprite.Group()
collectible_objects = pygame.sprite.Group()
goals = pygame.sprite.Group()
obstacles = pygame.sprite.Group() #grupo para obstáculos
enemies = pygame.sprite.Group() # grupo para enemigos
all_sprites.add(player)
current_operation = ""
correct_answer = 0
feedback_message = ""
feedback_color = BLACK
feedback_timer = 0
FEEDBACK_DURATION = 1500 # milisegundos para mostrar el feedback
game_state = "menu" # Posibles estados: "menu", "playing", "feedback", "level_complete", "game_over", "show_answer_popup", "controls_info"
level = 1
operation_type = "suma" # Tipo de operación actual
max_number_in_op = 10 # Dificultad actual (rango máximo de números en la operación)
max_multiplier_divisor = 5 # Dificultad actual para multiplicación/división
win_frame_index = 0
last_win_frame_time = 0
last_level_played = 0 # Inicialmente 0 o 1, dependiendo de tu lógica
last_level_operation_text = ""
last_level_correct_answer = 0
# Vidas del jugador para el nivel actual (se reinicia en cada nivel)
player_current_level_lives = 1
# Vidas que determinan los "juegos" antes de volver al checkpoint
player_checkpoint_lives = 3
# Variables de Checkpoint
checkpoint_level = 1 # Nivel desde el que se reiniciará
checkpoint_op_type = "suma" # Tipo de operación del checkpoint
checkpoint_max_num = 10 # Dificultad del checkpoint
checkpoint_max_mult_div = 5 # Dificultad de multiplicador/divisor del checkpoint
# Variables para la ventana emergente
popup_message = ""
popup_correct_answer = 0
# --- Variables para animaciones de victoria/derrota (GIFs) ---
win_gif_frames = []
lose_gif_frames = []
win_frame_index = 0
lose_frame_index = 0
last_win_frame_time = 0
last_lose_frame_time = 0
GIF_FRAME_DURATION = 100 # milisegundos por frame (ajusta para la velocidad del GIF)
def load_gif_frames(gif_path, scale_factor_width, scale_factor_height):
    frames = []
    try:
        img = Image.open(gif_path)
        for frame in ImageSequence.Iterator(img):
            # Convertir el frame a un formato que Pygame pueda usar
            # Redimensionar antes de convertir a Pygame para mejor rendimiento
            frame_resized = frame.resize((int(SCREEN_WIDTH * scale_factor_width), int(SCREEN_HEIGHT * scale_factor_height)))
            # Convertir el frame a un modo compatible con Pygame (RGBA para transparencia)
            frame_rgba = frame_resized.convert("RGBA")
            # Crear la superficie de Pygame
            pygame_frame = pygame.image.fromstring(frame_rgba.tobytes(), frame_rgba.size, frame_rgba.mode)
            frames.append(pygame_frame)
        return frames
    except FileNotFoundError:
        print(f"Error: GIF '{gif_path}' no encontrado.")
        return []
    except Exception as e:
        print(f"Error al cargar GIF '{gif_path}': {e}")
        return []
win_gif_frames = load_gif_frames("assets/gifs/win_animation.gif", 0.4, 0.4)
lose_gif_frames = load_gif_frames("assets/gifs/lose_animation.gif", 0.4, 0.4)
# --- Imágenes para los controles (si existen) ---
control_images = {}
KEY_IMAGE_SIZE = int(SCREEN_WIDTH * 0.05) # Tamaño de las imágenes de las teclas
try:
    control_images['arrow_up'] = pygame.transform.scale(pygame.image.load("assets/imagenes/arrow_up.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))
    control_images['arrow_left'] = pygame.transform.scale(pygame.image.load("assets/imagenes/arrow_left.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))
    control_images['arrow_down'] = pygame.transform.scale(pygame.image.load("assets/imagenes/arrow_down.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))
    control_images['arrow_right'] = pygame.transform.scale(pygame.image.load("assets/imagenes/arrow_right.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))
    control_images['w_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/w_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))
    control_images['a_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/a_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))
    control_images['s_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/s_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))
    control_images['d_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/d_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))
    control_images['spacebar_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/spacebar_key.png").convert_alpha(), (KEY_IMAGE_SIZE * 1.5, KEY_IMAGE_SIZE)) # Más ancha
    control_images['q_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/q_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))
except pygame.error as e:
    print(f"Advertencia: No se pudieron cargar todas las imágenes de teclas: {e}. Se usará texto en su lugar.")
    control_images = {} # Limpiar si no se cargaron todas
# --- Funciones Auxiliares ---
def draw_text(surface, text, font, color, x, y, center=True):
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(x=x, y=y)
    surface.blit(text_surface, text_rect)
def draw_wrapped_text(surface, text, font, color, rect, alignment="center"):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        # Prueba si añadiendo la palabra actual la línea excede el ancho
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= rect.width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line)) # Añadir la última línea
    y_offset = rect.top
    for line in lines:
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect()
        if alignment == "center":
            text_rect.centerx = rect.centerx
        elif alignment == "left":
            text_rect.left = rect.left
        elif alignment == "right":
            text_rect.right = rect.right
        text_rect.top = y_offset
        surface.blit(text_surface, text_rect)
        y_offset += font.get_height() # Espacio entre líneas
def draw_button(surface, rect, text, font, base_color, hover_color=None):
    mouse_pos = pygame.mouse.get_pos()
    current_color = base_color
    if rect.collidepoint(mouse_pos) and hover_color:
        current_color = hover_color
    pygame.draw.rect(surface, current_color, rect, border_radius=10)
    draw_text(surface, text, font, BLACK, rect.centerx, rect.centery)
    return rect
# --- Funciones de Lógica del Juego ---
def generate_operation(op_type, max_num, max_mult_div):
    global current_operation, correct_answer
    num1 = 0
    num2 = 0
    correct_answer = 0

    if op_type == "suma":
        num1 = random.randint(1, max_num)
        num2 = random.randint(1, max_num)
        correct_answer = num1 + num2
        current_operation = f"{num1} + {num2} = ?"
    elif op_type == "resta":
        num1 = random.randint(1, max_num)
        num2 = random.randint(1, max_num)
        if num1 < num2: # Asegurarse de que el resultado no sea negativo
            num1, num2 = num2, num1
        correct_answer = num1 - num2
        current_operation = f"{num1} - {num2} = ?"
    elif op_type == "multiplicacion":
        # Usar min(10, max_mult_div + 5) para los números en la multiplicación
        num1 = random.randint(1, min(10, max_mult_div + 5))
        num2 = random.randint(1, min(10, max_mult_div + 5))
        correct_answer = num1 * num2
        current_operation = f"{num1} x {num2} = ?"
    elif op_type == "division":
        # Asegurarse de que la división sea exacta y el cociente sea manejable
        divisor = random.randint(2, min(10, max_mult_div + 5))
        cociente = random.randint(1, min(10, max_mult_div + 5))
        num1 = divisor * cociente # El dividendo es el producto del divisor y el cociente
        num2 = divisor # El divisor es el mismo
        correct_answer = cociente
        current_operation = f"{num1} / {num2} = ?"
    # Generar respuestas incorrectas "cercanas"
    incorrect_answers = set()
    while len(incorrect_answers) < 2:
        offset = random.choice([-3, -2, -1, 1, 2, 3]) # Pequeños offsets
        incorrect_ans = correct_answer + offset
        # Asegurarse de que las incorrectas no sean la correcta y sean positivas
        if incorrect_ans > 0 and incorrect_ans != correct_answer and incorrect_ans not in incorrect_answers:
            incorrect_answers.add(incorrect_ans)
    return list(incorrect_answers) # Retorna las incorrectas para usarlas en generar metas
def show_correct_answer_popup(message):
    global game_state, popup_message, popup_correct_answer, last_level_correct_answer # Asegúrate de que last_level_correct_answer sea global aquí
    game_state = "show_answer_popup"
    popup_message = message
    popup_correct_answer = last_level_correct_answer # ¡MODIFICADO! Ahora muestra la respuesta del nivel ANTERIOR
def handle_player_death_logic():
    global player_checkpoint_lives, game_state, feedback_message, feedback_color, feedback_timer
    player_checkpoint_lives -= 1
    if sound_incorrect: # Sonido de fallo es más general para cualquier muerte en el nivel (por meta o daño)
         sound_incorrect.play()
    if player_checkpoint_lives <= 0:
        # Se ha perdido el juego, mostrar mensaje de Game Over con la respuesta
        game_state = "game_over" # Cambiar a estado game_over directamente
        if sound_game_over: sound_game_over.play()
    else: # Si aún quedan vidas de checkpoint, reiniciar el nivel actual
        # Reiniciar el nivel con 1 vida de nivel y salud completa
        generate_level(operation_type, max_number_in_op, max_multiplier_divisor)
        player.reset_health() # Restaurar la salud del jugador
        show_correct_answer_popup(f"¡Cuidado! Vidas de checkpoint restantes: {player_checkpoint_lives}. La respuesta correcta era:")
def generate_level(op_type, max_num_op, max_mult_div_op):
    global current_operation, correct_answer, feedback_message, feedback_color, feedback_timer, player_current_level_lives
    # Limpiar grupos anteriores
    collectible_objects.empty()
    goals.empty()
    obstacles.empty()
    enemies.empty() # Limpiar enemigos anteriores
    all_sprites.empty() # Limpia todos los sprites, luego añade los nuevos y el jugador
    all_sprites.add(player) # Asegúrate de que el jugador siempre esté en el grupo
    player.reset_objects()
    player_current_level_lives = 1 # ¡Una vida por nivel!
    player.reset_health() # Se restaura la salud del jugador al inicio de cada nivel
    feedback_message = ""
    feedback_timer = 0
    incorrect_answers_for_goals = generate_operation(op_type, max_num_op, max_mult_div_op) # Genera la operación y las incorrectas
    # Generar las 3 metas
    goal_positions = [
        (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + SCREEN_HEIGHT * 0.1),
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + SCREEN_HEIGHT * 0.1),
        (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2 + SCREEN_HEIGHT * 0.1)
    ]
    random.shuffle(goal_positions) # Mezclar para que la correcta no siempre esté en el mismo sitio
    # Asignar la respuesta correcta a una meta aleatoria
    all_possible_answers = incorrect_answers_for_goals
    all_possible_answers.insert(random.randint(0, 2), correct_answer) # Insertar la correcta en una posición aleatoria
    # Crear los objetos Goal y obtener sus rectángulos para el área de exclusión
    goal_exclusion_zones = []
    for i in range(3):
        goal = Goal(goal_positions[i][0], goal_positions[i][1], all_possible_answers[i])
        goals.add(goal)
        all_sprites.add(goal) # Añadir a todos los sprites para dibujar
        # Calcular el área de exclusión alrededor de cada meta
        EXCLUSION_MARGIN_GOAL = int(SCREEN_WIDTH * 0.08) # Margen alrededor de las metas
        exclusion_rect_goal = goal.rect.inflate(goal.rect.width + EXCLUSION_MARGIN_GOAL, goal.rect.height + EXCLUSION_MARGIN_GOAL)
        goal_exclusion_zones.append(exclusion_rect_goal)
    # --- Zona de exclusión para el jugador (donde no aparecerán objetos ni obstáculos) ---
    PLAYER_EXCLUSION_RADIUS = int(min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.2) # Radio de exclusión alrededor del jugador
    player_exclusion_zone = pygame.Rect(0, 0, PLAYER_EXCLUSION_RADIUS * 2, PLAYER_EXCLUSION_RADIUS * 2)
    player_exclusion_zone.center = (PLAYER_START_X, PLAYER_START_Y) # Centrar en la posición inicial del jugador
    # --- Generación de Obstáculos ---
    num_obstacles = random.randint(4, 8) # Número aleatorio de obstáculos
    obstacle_sizes = [
        (int(SCREEN_WIDTH * 0.05), int(SCREEN_HEIGHT * 0.07)),
        (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.09)),
        (int(SCREEN_WIDTH * 0.06), int(SCREEN_HEIGHT * 0.1)),
        (int(SCREEN_WIDTH * 0.09), int(SCREEN_HEIGHT * 0.07))
    ] # Diferentes tamaños de obstáculos
    # Zonas que deben evitar los obstáculos: jugador (inicial), metas y un área cerca del inicio
    forbidden_zones_for_obstacles = []
    forbidden_zones_for_obstacles.extend(goal_exclusion_zones) # Obstáculos no cerca de metas
    forbidden_zones_for_obstacles.append(player_exclusion_zone) # ¡Evitar la zona del jugador!
    # También evitamos la zona de la UI superior
    forbidden_zones_for_obstacles.append(pygame.Rect(0, 0, SCREEN_WIDTH, UI_BAR_HEIGHT + 20))
    # Definir cuántos serán mortales (porcentaje o número fijo)
    num_deadly_obstacles = random.randint(1, 4) # Entre 1 y 4 obstáculos mortales
    for i in range(num_obstacles):
        obs_width, obs_height = random.choice(obstacle_sizes)
        attempts = 0
        max_attempts_obs = 100 # Para evitar bucles infinitos
        found_valid_pos_obs = False
        obs_type = "solid"
        if i < num_deadly_obstacles: # Asignar los primeros 'num_deadly_obstacles' como mortales
            obs_type = "deadly"
        while not found_valid_pos_obs and attempts < max_attempts_obs:
            obs_x = random.randint(obs_width // 2, SCREEN_WIDTH - obs_width // 2)
            obs_y = random.randint(UI_BAR_HEIGHT + obs_height // 2, SCREEN_HEIGHT - obs_height // 2 - 20) # Evitar la parte inferior también
            temp_obs_rect = pygame.Rect(0, 0, obs_width, obs_height)
            temp_obs_rect.center = (obs_x, obs_y)
            # Verificar solapamiento con zonas prohibidas y otros obstáculos ya generados
            is_overlapping_obs = False
            for zone in forbidden_zones_for_obstacles:
                if temp_obs_rect.colliderect(zone):
                    is_overlapping_obs = True
                    break
            if not is_overlapping_obs: # Si no solapa con zonas prohibidas, verificar con otros obstáculos
                for existing_obs in obstacles:
                    if temp_obs_rect.colliderect(existing_obs.rect.inflate(int(SCREEN_WIDTH * 0.02), int(SCREEN_HEIGHT * 0.02))): # Un pequeño margen entre obstáculos
                        is_overlapping_obs = True
                        break
            if not is_overlapping_obs:
                found_valid_pos_obs = True
            attempts += 1
        if found_valid_pos_obs:
            obstacle = Obstacle(obs_x, obs_y, obs_width, obs_height, obs_type)
            obstacles.add(obstacle)
            all_sprites.add(obstacle)
            # Añadir el rect del nuevo obstáculo a las zonas prohibidas para los siguientes objetos y obstáculos
            forbidden_zones_for_obstacles.append(obstacle.rect.inflate(int(SCREEN_WIDTH * 0.02), int(SCREEN_HEIGHT * 0.02))) # Añadir con un pequeño margen
    # --- Generar enemigos ---
    num_enemies_to_spawn = 0
    # Generar enemigos solo en niveles IMPARES (nivel 1, 3, 5, etc.)
    if level % 2 != 0 and level >= 1: # Empezar a generar enemigos desde el nivel 1 si es impar
        num_enemies_to_spawn = random.randint(1, 1 + level // 5) # Más enemigos en niveles más altos, cada 5 niveles aumenta 1
    for _ in range(num_enemies_to_spawn):
        found_valid_pos_enemy = False
        attempts = 0
        max_attempts_enemy = 100
        while not found_valid_pos_enemy and attempts < max_attempts_enemy:
            enemy_x = random.randint(SCREEN_WIDTH // 4, SCREEN_WIDTH * 3 // 4)
            enemy_y = random.randint(UI_BAR_HEIGHT + 30, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.15))
            temp_enemy_rect = pygame.Rect(0,0, int(SCREEN_WIDTH * 0.06), int(SCREEN_HEIGHT * 0.08))
            temp_enemy_rect.center = (enemy_x, enemy_y)
            is_overlapping_enemy = False
            for zone in forbidden_zones_for_obstacles: # Usamos las mismas zonas para enemigos
                if temp_enemy_rect.colliderect(zone):
                    is_overlapping_enemy = True
                    break
            if not is_overlapping_enemy:
                for existing_enemy in enemies:
                    if temp_enemy_rect.colliderect(existing_enemy.rect.inflate(int(SCREEN_WIDTH * 0.02), int(SCREEN_HEIGHT * 0.02))):
                        is_overlapping_enemy = True
                        break
            if not is_overlapping_enemy:
                found_valid_pos_enemy = True
            attempts += 1
        if found_valid_pos_enemy:
            enemy = Enemy(enemy_x, enemy_y)
            enemies.add(enemy)
            all_sprites.add(enemy)
            forbidden_zones_for_obstacles.append(enemy.rect.inflate(int(SCREEN_WIDTH * 0.04), int(SCREEN_HEIGHT * 0.04))) # Añadir al grupo de zonas prohibidas
    # --- Generar objetos coleccionables ---
    # Calcular cuántos objetos faltan para la respuesta correcta, si generamos enemigos, generamos menos objetos inicialmente
    initial_objects_needed = correct_answer - num_enemies_to_spawn # Cada enemigo derrotado da un objeto
    num_objects_to_spawn = max(0, initial_objects_needed) + random.randint(5,10) # Algunos extra además de los necesarios
    # Combina las zonas de exclusión de metas, obstáculos, enemigos y la zona del jugador para los objetos coleccionables
    all_exclusion_zones_for_objects = list(goal_exclusion_zones)
    for obs in obstacles:
        all_exclusion_zones_for_objects.append(obs.rect.inflate(int(SCREEN_WIDTH * 0.04), int(SCREEN_HEIGHT * 0.04)))
    for enemy in enemies:
        all_exclusion_zones_for_objects.append(enemy.rect.inflate(int(SCREEN_WIDTH * 0.06), int(SCREEN_HEIGHT * 0.06))) # Evitar que objetos aparezcan justo sobre enemigos
    all_exclusion_zones_for_objects.append(player_exclusion_zone) # ¡Aquí también excluimos la zona del jugador para los objetos!
    # Define un margen mínimo entre objetos coleccionables
    OBJECT_SPACING_MARGIN = int(SCREEN_WIDTH * 0.05) # Mínima distancia entre centros de objetos
    generated_object_positions = [] # Para almacenar las posiciones de los objetos ya generados
    for _ in range(num_objects_to_spawn):
        found_valid_pos = False
        attempts = 0
        max_attempts_obj = 150 # Para evitar bucles infinitos en la generación de objetos
        while not found_valid_pos and attempts < max_attempts_obj:
            # Posiciones aleatorias para los objetos, evitando la zona de la UI superior y la parte inferior
            obj_x = random.randint(int(SCREEN_WIDTH * 0.03), SCREEN_WIDTH - int(SCREEN_WIDTH * 0.03))
            obj_y = random.randint(UI_BAR_HEIGHT + int(SCREEN_HEIGHT * 0.03), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.1)) # Evitar zona de metas en el medio y parte inferior
            temp_obj_rect = pygame.Rect(0,0, int(SCREEN_WIDTH * 0.03), int(SCREEN_HEIGHT * 0.04)) # Rect provisional para comprobar la posición
            temp_obj_rect.center = (obj_x, obj_y)
            is_overlapping = False
            # Verificar solapamiento con zonas de exclusión (metas, obstáculos, enemigos, y AHORA la zona del jugador)
            for zone in all_exclusion_zones_for_objects:
                if temp_obj_rect.colliderect(zone):
                    is_overlapping = True
                    break
            # Verificar solapamiento con otros objetos ya generados
            if not is_overlapping:
                for existing_pos in generated_object_positions:
                    distance = ((obj_x - existing_pos[0])**2 + (obj_y - existing_pos[1])**2)**0.5
                    if distance < OBJECT_SPACING_MARGIN:
                        is_overlapping = True
                        break
            if not is_overlapping:
                found_valid_pos = True
            attempts += 1
        if found_valid_pos: # Si encontramos una posición válida, creamos el objeto
            obj = CollectibleObject(obj_x, obj_y)
            collectible_objects.add(obj)
            all_sprites.add(obj) # Añadir a todos los sprites para dibujar
            generated_object_positions.append((obj_x, obj_y)) # Guardar la posición
    player.rect.center = (PLAYER_START_X, PLAYER_START_Y) # Resetear posición del jugador a la posición inicial definida
def reset_game_to_checkpoint():
    global level, operation_type, max_number_in_op, max_multiplier_divisor, player_checkpoint_lives, checkpoint_level, checkpoint_op_type, checkpoint_max_num, checkpoint_max_mult_div
    level = checkpoint_level # Vuelve al nivel del checkpoint
    operation_type = checkpoint_op_type # Vuelve al tipo de operación del checkpoint
    max_number_in_op = checkpoint_max_num # Vuelve a la dificultad del checkpoint
    max_multiplier_divisor = checkpoint_max_mult_div # Vuelve a la dificultad de mult/div del checkpoint
    player_checkpoint_lives = 3 # ¡Siempre 3 vidas al reiniciar desde un checkpoint!
    player.reset_health() # También restaurar la salud del jugador
    generate_level(operation_type, max_number_in_op, max_multiplier_divisor) # Genera el nivel desde el checkpoint
def show_controls_popup():
    global game_state
    game_state = "controls_info"
def draw_controls_popup(surface):
    # Crear una superficie semi-transparente para el fondo oscuro
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Negro con 180 de opacidad (de 255)
    surface.blit(overlay, (0, 0))
    # Dimensiones de la ventana emergente
    popup_width = int(SCREEN_WIDTH * 0.7)
    popup_height = int(SCREEN_HEIGHT * 0.8)
    popup_x = SCREEN_WIDTH // 2 - popup_width // 2
    popup_y = SCREEN_HEIGHT // 2 - popup_height // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(surface, WHITE, popup_rect, border_radius=15)
    pygame.draw.rect(surface, BLACK, popup_rect, 5, border_radius=15) # Borde
    draw_text(surface, "Controles y Objetivo del Juego", font_popup_title, BLACK, SCREEN_WIDTH // 2, popup_y + int(popup_height * 0.08))
    # ---Mostrar controles con imágenes y texto ---
    controls_start_y = popup_y + int(popup_height * 0.08)
    line_height = int(font_popup_text.get_height() * 3.2) # Espacio entre líneas
    key_image_y_offset = int(line_height * 0.8) # Offset para centrar la imagen de la tecla verticalmente
    control_definitions = [
        (("arrow_up", "arrow_left", "arrow_down", "arrow_right"), "Moverse (Teclas de Flecha)"),
        (("w_key", "a_key", "s_key", "d_key"), "Moverse (W, A, S, D)"),
        ("spacebar_key", "Atacar"),
        ("q_key", "Soltar Objeto")
    ]
    current_y = controls_start_y
    for item in control_definitions:
        x_offset = popup_x + 40 # Posición inicial X para el texto
        if isinstance(item[0], tuple): # Múltiples imágenes de teclas
            for key_img_name in item[0]:
                if key_img_name in control_images:
                    img = control_images[key_img_name]
                    img_rect = img.get_rect(midleft=(x_offset, current_y + key_image_y_offset))
                    surface.blit(img, img_rect)
                    x_offset += img.get_width() + 5 # Espacio entre imágenes
            draw_text(surface, item[1], font_popup_text, BLACK, x_offset + (popup_width - x_offset - (popup_x + 40)) // 2, current_y + key_image_y_offset, center=False)
        else: # Una sola imagen de tecla
            key_img_name = item[0]
            if key_img_name in control_images:
                img = control_images[key_img_name]
                img_rect = img.get_rect(midleft=(x_offset, current_y + key_image_y_offset))
                surface.blit(img, img_rect)
                draw_text(surface, item[1], font_popup_text, BLACK, img_rect.right + 20, current_y + key_image_y_offset, center=False)
            else: # Fallback a texto si no hay imagen
                draw_text(surface, f"{item[0].replace('_key', '').upper()} : {item[1]}", font_popup_text, BLACK, x_offset, current_y + key_image_y_offset, center=False)
        current_y += line_height
    # Objetivo del juego
    objective_text_start_y = current_y + int(popup_height * 0.05)
    draw_text(surface, "OBJETIVO DEL JUEGO:", font_popup_text, BLACK, popup_x + 40, objective_text_start_y, center=False)
    objective_lines = [
        "Resuelve la operación matemática en la parte superior.",
        "Recolecta la cantidad de zapatos que es la respuesta correcta.",
        "Lleva los zapatos recolectados a la meta con la respuesta correcta."
        "",
        "¡Cuidado con los obstáculos mortales y los enemigos!",
        "Derrotar enemigos te dará un zapato.",
        "Cada 5 niveles se guarda un checkpoint y recuperas vidas.",
        "¡Evita quedarte sin vidas de checkpoint!"
    ]
    obj_line_y = objective_text_start_y + font_popup_text.get_height() + 10
    for line in objective_lines:
        draw_text(surface, line, font_popup_text, BLACK, popup_x + 60, obj_line_y, center=False)
        obj_line_y += font_popup_text.get_height() + 5
    # Botón "Entendido"
    button_width = int(SCREEN_WIDTH * 0.15)
    button_height = int(SCREEN_HEIGHT * 0.07)
    # Ajuste de la posición del botón para que no se solape con el texto y esté centrado
    button_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - button_width // 2,
        popup_y + popup_height - button_height - 20, # 20px desde el borde inferior del popup
        button_width,
        button_height
    )
    # Dibuja el botón y retorna su rect. La lógica de clic se maneja en el bucle principal.
    return draw_button(surface, button_rect, "Entendido", font_button, BUTTON_COLOR, HOVER_COLOR)
# --- Bucle Principal del Juego ---
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu":
                # Botones del menú
                # Reiniciar todas las variables de nivel y checkpoint al elegir un modo de juego
                level = 1
                checkpoint_level = 1
                player_checkpoint_lives = 3
                player.reset_health() # Asegurar salud completa al iniciar
                # Ajustar posiciones y tamaños de botones para pantalla completa
                button_width = int(SCREEN_WIDTH * 0.3)
                button_height = int(SCREEN_HEIGHT * 0.1)
                # ¡Ajuste de posiciones de los botones para dejar espacio al título!
                sum_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 2.2, button_width, button_height) # Ajustado
                subtract_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 1, button_width, button_height) # Ajustado
                multiply_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 0.2, button_width, button_height) # Ajustado
                divide_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 1.4, button_width, button_height) # Ajustado
                controls_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 2.6, button_width, button_height) # Nuevo botón Controles
                exit_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 3.8, button_width, button_height) # Nuevo botón Salir, ajustado
                if sum_btn_rect.collidepoint(event.pos):
                    operation_type = "suma"
                    max_number_in_op = 10 # Inicio para sumas/restas
                    max_multiplier_divisor = 2 # Ajustado para que la primera etapa de mult/div sea consistente
                    checkpoint_op_type = operation_type
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    game_state = "playing"
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)
                elif subtract_btn_rect.collidepoint(event.pos):
                    operation_type = "resta"
                    max_number_in_op = 10
                    max_multiplier_divisor = 2 # Ajustado
                    checkpoint_op_type = operation_type
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    game_state = "playing"
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)
                elif multiply_btn_rect.collidepoint(event.pos):
                    operation_type = "multiplicacion"
                    max_number_in_op = 10 # Para el tamaño del resultado
                    max_multiplier_divisor = 2 # Inicio para multiplicaciones (será 2 en nivel 1-5)
                    checkpoint_op_type = operation_type
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    game_state = "playing"
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)
                elif divide_btn_rect.collidepoint(event.pos):
                    operation_type = "division"
                    max_number_in_op = 20 # Para el tamaño del resultado (dividendo)
                    max_multiplier_divisor = 2 # Inicio para divisiones (será 2 en nivel 1-5)
                    checkpoint_op_type = operation_type
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    game_state = "playing"
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)
                elif controls_btn_rect.collidepoint(event.pos): # Lógica del botón Controles
                    show_controls_popup()
                elif exit_btn_rect.collidepoint(event.pos): # Lógica del botón Salir
                    running = False
            elif game_state == "playing":
                # Botón para volver al menú de operadores en el estado "playing"
                menu_btn_rect = pygame.Rect(SCREEN_WIDTH - int(SCREEN_WIDTH * 0.15) - 20, 10, int(SCREEN_WIDTH * 0.15), UI_BAR_HEIGHT - 20)
                if menu_btn_rect.collidepoint(event.pos):
                    game_state = "menu"
                    # Resetear todo como si fuera un inicio de juego nuevo
                    level = 1
                    checkpoint_level = 1
                    player_checkpoint_lives = 3
                    player.reset_health()
                    player.reset_objects()
                    collectible_objects.empty()
                    goals.empty()
                    obstacles.empty()
                    enemies.empty()
                    all_sprites.empty()
                    all_sprites.add(player) # Asegurarse de que el jugador siga en el grupo
                    feedback_message = ""
                    feedback_timer = 0
            elif game_state == "level_complete":
                if sound_win: sound_win.stop() # Detener sonido de victoria si está reproduciéndose
                level += 1
                # --- Lógica de progresión de dificultad ---
                if operation_type in ["suma", "resta"]:
                    if level <= 5:
                        max_number_in_op = 10
                    elif level <= 10:
                        max_number_in_op = 20
                    elif level <= 15:
                        max_number_in_op = 30
                    else:
                        max_number_in_op = 50
                elif operation_type in ["multiplicacion", "division"]:
                    if level <= 5: # Niveles 1-5
                        max_multiplier_divisor = 2
                    elif level <= 10: # Niveles 6-10
                        max_multiplier_divisor = 6
                    elif level <= 15: # Niveles 11-15
                        max_multiplier_divisor = 10
                    else: # Niveles > 15
                        max_multiplier_divisor = 16 # MODIFICADO: Ajustado a 16
                    if operation_type == "division":
                        # El dividendo se calcula en generate_operation basado en divisor y cociente,
                        # que a su vez usan max_multiplier_divisor.
                        # max_number_in_op no se usa directamente para controlar el dividendo aquí.
                        pass

                # MODIFICADO: Se elimina el cambio aleatorio de operation_type para mantener la elección del menú.
                # if level > 1 and (level - 1) % 5 == 0:
                #     operation_type = random.choice(["suma", "resta", "multiplicacion", "division"])

                # --- Lógica de Checkpoint ---
                # Checkpoint cada 5 niveles completados (es decir, al INICIO del nivel 6, 11, 16...)
                # (level -1) es el número de niveles completados.
                # Entonces, si (level-1) es 5, 10, 15...
                if (level - 1) > 0 and (level - 1) % 5 == 0 : # (level-1) para que sea después de completar el nivel 5, 10, etc.
                    checkpoint_level = level
                    checkpoint_op_type = operation_type # operation_type ya no cambia aleatoriamente
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    player_checkpoint_lives = 3
                    # Pequeño mensaje de feedback para el checkpoint
                    feedback_message = "¡Checkpoint Guardado! ¡Vidas Recargadas!"
                    feedback_color = GREEN # O un color distintivo para checkpoints
                    feedback_timer = pygame.time.get_ticks() # Para mostrarlo un momento

                player.reset_health()
                game_state = "playing"
                generate_level(operation_type, max_number_in_op, max_multiplier_divisor)

            elif game_state == "game_over":
                # Si el jugador hace clic en Game Over, reinicia desde el último checkpoint
                game_over_continue_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.15), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08))
                game_over_menu_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.25), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08)) # Ajustada Y
                if game_over_continue_btn_rect.collidepoint(event.pos):
                    if sound_game_over: sound_game_over.stop() # Detener sonido de game over
                    game_state = "playing"
                    reset_game_to_checkpoint()
                elif game_over_menu_btn_rect.collidepoint(event.pos):
                    if sound_game_over: sound_game_over.stop() # Detener sonido de game over
                    game_state = "menu"
                    # Resetear todo como si fuera un inicio de juego nuevo
                    level = 1
                    checkpoint_level = 1
                    player_checkpoint_lives = 3
                    player.reset_health()
                    player.reset_objects()
                    collectible_objects.empty()
                    goals.empty()
                    obstacles.empty()
                    enemies.empty()
                    all_sprites.empty()
                    all_sprites.add(player)
                    feedback_message = ""
                    feedback_timer = 0
            elif game_state == "show_answer_popup":
                # Lógica del botón "Cerrar" en la ventana emergente
                popup_button_width = int(SCREEN_WIDTH * 0.15)
                popup_button_height = int(SCREEN_HEIGHT * 0.07)
                popup_button_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - popup_button_width // 2,
                    SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.17),
                    popup_button_width,
                    popup_button_height
                )
                if popup_button_rect.collidepoint(event.pos):
                    # Si el jugador ha perdido todas sus vidas de checkpoint, vamos a Game Over
                    if player_checkpoint_lives <= 0:
                        game_state = "game_over"
                        if sound_game_over: sound_game_over.play()
                    else: # Si aún le quedan vidas, volvemos a playing para que se regenere el nivel
                        game_state = "playing"
            # NUEVO: Lógica de clic para el botón "Entendido" en el popup de controles
            elif game_state == "controls_info":
                button_width = int(SCREEN_WIDTH * 0.15)
                button_height = int(SCREEN_HEIGHT * 0.07)
                # Recalculando la posición del botón 'Entendido' para el clic
                popup_width_ctrl = int(SCREEN_WIDTH * 0.7) # Renombrado para evitar conflicto con popup_width global
                popup_height_ctrl = int(SCREEN_HEIGHT * 0.8) # Renombrado
                popup_y_ctrl = SCREEN_HEIGHT // 2 - popup_height_ctrl // 2 # Renombrado

                button_rect_for_click_check = pygame.Rect(
                    SCREEN_WIDTH // 2 - button_width // 2,
                    popup_y_ctrl + popup_height_ctrl - button_height - 20, # Usa la misma lógica que en draw_controls_popup
                    button_width,
                    button_height
                )
                if button_rect_for_click_check.collidepoint(event.pos):
                     game_state = "menu" # Vuelve al menú
        if event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if event.key == pygame.K_q: # Tecla 'Q' para soltar objetos
                    player.drop_object()
    # --- Actualizaciones del Juego ---
    if game_state == "playing":
        keys = pygame.key.get_pressed()
        player.update(keys)
        enemies.update(player.rect) # Actualiza la posición de los enemigos
        # Colisión del jugador con obstáculos
        collided_obstacles = pygame.sprite.spritecollide(player, obstacles, False) # False: no remueve el obstáculo
        for obs in collided_obstacles:
            if obs.type == "solid":
                player.revert_position() # Mueve al jugador a su posición anterior si choca con un obstáculo sólido
            elif obs.type == "deadly":
                player.take_damage(DEADLY_OBSTACLE_DAMAGE) # Daño por obstáculo mortal
                player.revert_position() # Empuja al jugador un poco para evitar daño continuo
                if player.health <= 0: # Verificar si la salud llegó a 0 *después* de aplicar el daño
                    handle_player_death_logic()
                    break # Salir del bucle si el jugador muere
        # Colisión del jugador con enemigos
        collided_enemies = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in collided_enemies:
            # Condición para que el enemigo reciba daño solo una vez por ataque del jugador
            if player.is_attacking and not enemy.damage_taken_this_attack:
                enemy.take_damage(PLAYER_ATTACK_DAMAGE) # El jugador hace daño al enemigo
                if enemy.health <= 0:
                    if sound_enemy_death:
                        sound_enemy_death.play()
                    enemy.kill() # Elimina al enemigo
                    # Generar un objeto coleccionable en la posición del enemigo derrotado
                    new_obj = CollectibleObject(enemy.rect.centerx, enemy.rect.centery)
                    collectible_objects.add(new_obj)
                    all_sprites.add(new_obj)
            elif not player.is_attacking:
                if enemy.is_aggressive:
                    enemy.attack(player)
        # Colisión con objetos coleccionables
        collected = pygame.sprite.spritecollide(player, collectible_objects, True) # True: remueve el objeto
        for obj in collected:
            player.add_object()
        # Colisión con metas
        collided_goal = None
        for goal in goals:
            # Usamos el collision_rect de la meta para una colisión más precisa
            if player.rect.colliderect(goal.collision_rect):
                collided_goal = goal
                break # Solo procesar una colisión de meta a la vez
        if collided_goal: # Si el jugador colisionó con CUALQUIER meta (con su collision_rect)
            last_level_correct_answer=correct_answer
            if player.collected_objects == correct_answer:
                if collided_goal.value == correct_answer:
                    feedback_message = "¡Correcto! ¡Siguiente Nivel!"
                    feedback_color = GREEN
                    if sound_correct: sound_correct.play()
                    if sound_win: sound_win.play() # Reproducir sonido de victoria
                    game_state = "level_complete"
                    # El feedback_timer se gestionará en la sección de dibujado si es necesario para "Level Complete"
                else: # Cantidad correcta pero meta incorrecta
                    player_current_level_lives -= 1 # Resta una vida por error
                    if sound_incorrect: sound_incorrect.play()
                    if player_current_level_lives <= 0:
                        handle_player_death_logic() # Llama a la función de muerte si se agotan vidas del nivel
                    else:
                        show_correct_answer_popup(f"Cantidad correcta, pero meta incorrecta. La respuesta correcta era:")
            else: # Cantidad de objetos incorrecta
                player_current_level_lives -= 1 # Resta una vida por error
                if sound_incorrect: sound_incorrect.play()
                if player_current_level_lives <= 0:
                    handle_player_death_logic() # Llama a la función de muerte si se agotan vidas del nivel
                else:
                    show_correct_answer_popup(f"Necesitas {correct_answer} objetos. Tienes {player.collected_objects}. La respuesta correcta era:")
            # Después de la interacción con la meta, mover al jugador un poco para evitar múltiples colisiones instantáneas
            # Solo si no se completó el nivel, para no interferir con la transición.
            if game_state != "level_complete":
                 player.rect.center = (player.rect.centerx, player.rect.centery + int(SCREEN_HEIGHT * 0.05))

        # Comprobar si el jugador ha muerto por salud
        if player.health <= 0 and game_state == "playing": # Asegurarse de que no se llama varias veces
            handle_player_death_logic()

        # Manejo del feedback_timer para mensajes temporales (como el de checkpoint)
        if feedback_message and feedback_timer > 0:
            if pygame.time.get_ticks() - feedback_timer > FEEDBACK_DURATION:
                feedback_message = ""
                feedback_timer = 0


    # --- Dibujado / Renderizado ---
    screen.fill(BLUE_LIGHT)
    if game_state == "menu":
        draw_text(screen, "Las Aventuras De Tralalero Tralala", font_large, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)
        button_width = int(SCREEN_WIDTH * 0.3)
        button_height = int(SCREEN_HEIGHT * 0.1)
        sum_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 2.2, button_width, button_height), "Sumas", font_button, BUTTON_COLOR, HOVER_COLOR)
        subtract_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 1, button_width, button_height), "Restas", font_button, BUTTON_COLOR, HOVER_COLOR)
        multiply_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 0.2, button_width, button_height), "Multiplicación", font_button, BUTTON_COLOR, HOVER_COLOR)
        divide_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 1.4, button_width, button_height), "Divisiones", font_button, BUTTON_COLOR, HOVER_COLOR)
        controls_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 2.6, button_width, button_height), "Controles", font_button, YELLOW_LIGHT, (255, 255, 200))
        exit_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 3.8, button_width, button_height), "Salir", font_button, RED, (255, 100, 100))
    elif game_state in ["playing", "feedback", "level_complete", "show_answer_popup"]: # Dibuja el juego de fondo si el popup está activo
        # Dibujar área de UI superior
        pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, UI_BAR_HEIGHT))
        # Mostrar la operación actual - Centrado
        draw_text(screen, current_operation, font_operation, BLACK, SCREEN_WIDTH // 2, UI_BAR_HEIGHT // 2)
        # Mostrar vidas de checkpoint (izquierda)
        draw_text(screen, f"Vidas: {player_checkpoint_lives}", font_lives, BLACK, int(SCREEN_WIDTH * 0.1), UI_BAR_HEIGHT // 2)
        # Mostrar nivel (izquierda, debajo de vidas o al lado)
        draw_text(screen, f"Nivel: {level}", font_lives, BLACK, int(SCREEN_WIDTH * 0.25), UI_BAR_HEIGHT // 2)
        # Mostrar salud del jugador (derecha, al lado de objetos)
        draw_text(screen, f"Salud: {player.health}", font_health, BLACK, SCREEN_WIDTH - int(SCREEN_WIDTH * 0.25), UI_BAR_HEIGHT // 2)
        # Botón para volver al menú de operadores
        menu_btn_rect = pygame.Rect(SCREEN_WIDTH - int(SCREEN_WIDTH * 0.15) - 20, 10, int(SCREEN_WIDTH * 0.15), UI_BAR_HEIGHT - 20)
        draw_button(screen, menu_btn_rect, "Menú", font_button, BUTTON_COLOR, HOVER_COLOR)

        # Dibujar todos los sprites (jugador, objetos, metas, obstáculos, enemigos)
        all_sprites.draw(screen)
        player.draw_health_bar(screen) # MODIFICADO: Dibujar barra de vida del jugador

        # Dibujar barras de vida de los enemigos
        for enemy in enemies:
            enemy.draw_health_bar(screen)
        # Si el jugador está atacando, dibujar un indicador visual
        if player.is_attacking and pygame.time.get_ticks() - player.attack_anim_start_time < PLAYER_ATTACK_ANIM_DURATION:
            attack_indicator_rect = pygame.Rect(0, 0, player.rect.width + 20, player.rect.height + 20)
            attack_indicator_rect.center = player.rect.center
            pygame.draw.circle(screen, PLAYER_ATTACK_COLOR, attack_indicator_rect.center, attack_indicator_rect.width // 2, 3)
        # Dibujar animación de ataque de los enemigos
        for enemy in enemies:
            if enemy.is_attacking_anim and pygame.time.get_ticks() - enemy.attack_anim_start_time < ENEMY_ATTACK_ANIM_DURATION:
                enemy_attack_rect = enemy.rect.inflate(10, 10) # Ligeramente más grande que el enemigo
                pygame.draw.rect(screen, ENEMY_ATTACK_COLOR, enemy_attack_rect, 2) # Dibujar un borde rojo

        # Mostrar mensaje de feedback (si hay alguno y el estado no es el popup)
        if feedback_message and game_state != "show_answer_popup" and game_state != "level_complete": # No mostrar durante popup o level_complete screen
            if feedback_timer > 0: # Solo si es un mensaje temporal como el de checkpoint
                 draw_text(screen, feedback_message, font_feedback, feedback_color, SCREEN_WIDTH // 2, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.07))
            elif game_state == "feedback": # Para otros feedbacks que usan el estado "feedback" (si lo hubiera)
                 draw_text(screen, feedback_message, font_feedback, feedback_color, SCREEN_WIDTH // 2, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.07))


        if game_state == "level_complete":
            # Animación de victoria (GIF)
            if win_gif_frames:
                current_time = pygame.time.get_ticks()
                if current_time - last_win_frame_time > GIF_FRAME_DURATION:
                    win_frame_index = (win_frame_index + 1) % len(win_gif_frames)
                    last_win_frame_time = current_time
                current_win_frame = win_gif_frames[win_frame_index]
                image_rect = current_win_frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - int(SCREEN_HEIGHT * 0.1)))
                screen.blit(current_win_frame, image_rect)
            draw_text(screen, "¡NIVEL COMPLETADO!", font_large, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.1))
            draw_text(screen, "¡Haz clic para el siguiente nivel!", font_feedback, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.2))
            # Mostrar el mensaje de checkpoint aquí también si fue guardado
            if feedback_message and "Checkpoint" in feedback_message: # Específico para el mensaje de checkpoint
                draw_text(screen, feedback_message, font_feedback, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.28))


        # Mostrar contador de objetos (abajo a la derecha) - DIBUJAR AL FINAL PARA ESTAR SIEMPRE AL FRENTE
        draw_text(screen, f"Objetos: {player.collected_objects}", font_counter, BLACK, SCREEN_WIDTH - int(SCREEN_WIDTH * 0.1), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.05))

        # --- Dibuja la ventana emergente si el estado es show_answer_popup ---
        if game_state == "show_answer_popup":
            # Crear una superficie semi-transparente para el fondo oscuro
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) # Negro con 180 de opacidad (de 255)
            screen.blit(overlay, (0, 0))
            # Dimensiones de la ventana emergente
            popup_width_show = int(SCREEN_WIDTH * 0.6) # Renombrado
            popup_height_show = int(SCREEN_HEIGHT * 0.5) # Renombrado
            popup_x_show = SCREEN_WIDTH // 2 - popup_width_show // 2 # Renombrado
            popup_y_show = SCREEN_HEIGHT // 2 - popup_height_show // 2 # Renombrado
            popup_rect = pygame.Rect(popup_x_show, popup_y_show, popup_width_show, popup_height_show)
            pygame.draw.rect(screen, WHITE, popup_rect, border_radius=15)
            pygame.draw.rect(screen, BLACK, popup_rect, 5, border_radius=15) # Borde
            # Área para el mensaje principal (dentro del popup)
            message_area_rect = pygame.Rect(popup_x_show + 20, popup_y_show + 20, popup_width_show - 40, popup_height_show * 0.4)
            draw_wrapped_text(screen, popup_message, font_medium, BLACK, message_area_rect)
            # Respuesta correcta
            draw_text(screen, str(popup_correct_answer), font_large, GREEN, SCREEN_WIDTH // 2, popup_y_show + int(popup_height_show * 0.65))
            # Botón "Cerrar"
            popup_button_width = int(SCREEN_WIDTH * 0.15)
            popup_button_height = int(SCREEN_HEIGHT * 0.07)
            popup_button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - popup_button_width // 2,
                popup_y_show + int(popup_height_show * 0.85), # Posición debajo del mensaje de la respuesta
                popup_button_width,
                popup_button_height
            )
            draw_button(screen, popup_button_rect, "Cerrar", font_button, BUTTON_COLOR, HOVER_COLOR)
    elif game_state == "game_over":
        # Animación de derrota (GIF)
        if lose_gif_frames:
            current_time = pygame.time.get_ticks()
            if current_time - last_lose_frame_time > GIF_FRAME_DURATION:
                lose_frame_index = (lose_frame_index + 1) % len(lose_gif_frames)
                last_lose_frame_time = current_time
            current_lose_frame = lose_gif_frames[lose_frame_index]
            image_rect = current_lose_frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - int(SCREEN_HEIGHT * 0.15)))
            screen.blit(current_lose_frame, image_rect)
        draw_text(screen, "¡GAME OVER!", font_large, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.05))
        draw_text(screen, f"Alcanzaste el Nivel: {level}", font_medium, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.15)) # Ajustada Y
        # Botones de Game Over
        game_over_continue_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.25), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08)) # Ajustada Y
        draw_button(screen, game_over_continue_btn_rect, "Continuar", font_button, BUTTON_COLOR, HOVER_COLOR)
    elif game_state == "controls_info":
        # El draw_controls_popup ahora devuelve el rect del botón, lo usamos para la detección de clic
        controls_button_rect = draw_controls_popup(screen)
        # Nota: La detección de clic para este botón se movió al inicio del bucle de eventos para mejor manejo.
    pygame.display.flip()
    clock.tick(60)
pygame.quit()