# videojuego.py

import pygame  # importa la libreria para crear juegos
import random  # importa funciones para generar numeros aleatorios
import math  # importa funciones matematicas
from PIL import Image, ImageSequence # importa pillow para trabajar con imagenes gif

# 1 inicializacion de pygame
pygame.init()  # comienza pygame

#configuracion general
# obtiene la resolucion actual de la pantalla para pantalla completa
INFO = pygame.display.Info()  # informacion del sistema
SCREEN_WIDTH = INFO.current_w  # ancho de la pantalla
SCREEN_HEIGHT = INFO.current_h  # altura de la pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN) # pantalla completa
pygame.display.set_caption("Las Aventuras De Tralalero Tralala")  # titulo de la ventana

#colores
WHITE = (255, 255, 255)  # color blanco
BLACK = (0, 0, 0)  # color negro
GREEN = (0, 200, 0)  # color verde
RED = (200, 0, 0)  # color rojo
BLUE_LIGHT = (173, 216, 230) # color azul claro para fondo
YELLOW_LIGHT = (255, 255, 150) # color amarillo claro para objetos
BUTTON_COLOR = (100, 100, 255) # color base para botones
HOVER_COLOR = (150, 150, 255) # color cuando el raton pasa encima
SOLID_OBSTACLE_COLOR = (139, 69, 19) # color marron para obstaculos solidos
DEADLY_OBSTACLE_COLOR = (255, 0, 0) # color rojo para obstaculos mortales
ENEMY_COLOR = (150, 0, 0) # color para enemigos
PLAYER_ATTACK_COLOR = (255, 165, 0) # color naranja para ataque
ENEMY_ATTACK_COLOR = (255, 0, 0) # color para ataque enemigo
POPUP_BACKGROUND_COLOR = (200, 200, 200, 180) # color gris transparente para popups
HEALTH_BAR_COLOR = (50, 200, 50) # color verde para barra de vida
HEALTH_BAR_BACKGROUND_COLOR = (100, 0, 0) # color rojo oscuro para fondo de barra
PLAYER_HEALTH_BAR_COLOR = (0, 255, 0)  # color verde para barra de vida jugador
PLAYER_HEALTH_BAR_BACKGROUND_COLOR = (255, 0, 0) # color rojo para fondo de barra jugador


# --- fuentes ---
font_large = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.15)) # fuente grande para titulos
font_medium = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.1)) # fuente mediana para opciones
font_small = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.07)) # fuente pequena para mensajes

# fuentes especificas para el juego
font_operation = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.1)) # fuente para operaciones
font_counter = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.06)) # fuente para contadores
font_goal = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.08)) # fuente para numeros de metas
font_feedback = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.065)) # fuente para mensajes de feedback
font_lives = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.06)) # fuente para vidas
font_health = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.06)) # fuente para salud
font_button = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.05)) # fuente para botones
font_popup_title = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.09)) # fuente para titulos de popup
font_popup_text = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.04)) # fuente para texto de popup

# --- sonidos (asegurate de que los archivos wav existan) ---
try:  # intenta cargar los sonidos
    sound_collect = pygame.mixer.Sound("assets/audios/collect.wav")  # sonido al recolectar
    sound_correct = pygame.mixer.Sound("assets/audios/correct.wav")  # sonido respuesta correcta
    sound_incorrect = pygame.mixer.Sound("assets/audios/incorrect.wav")  # sonido respuesta incorrecta
    sound_hit_deadly = pygame.mixer.Sound("assets/audios/hit_deadly.wav")  # sonido golpe mortal
    sound_enemy_hit = pygame.mixer.Sound("assets/audios/enemy_hit.wav")  # sonido golpe enemigo
    sound_player_hit = pygame.mixer.Sound("assets/audios/player_hit.wav")  # sonido golpe jugador
    sound_enemy_death = pygame.mixer.Sound("assets/audios/enemy_death.wav")  # sonido muerte enemigo
    sound_win = pygame.mixer.Sound("assets/audios/win.wav") # sonido victoria
    sound_game_over = pygame.mixer.Sound("assets/audios/game_over.wav") # sonido game over
except pygame.error as e:  # si hay error al cargar sonidos
    print(f"advertencia no se pudieron cargar los sonidos {e} asegurate de que existan los archivos")  # mensaje error
    sound_collect = None  # sonido recolectar nulo
    sound_correct = None  # sonido correcto nulo
    sound_incorrect = None  # sonido incorrecto nulo
    sound_hit_deadly = None  # sonido golpe mortal nulo
    sound_enemy_hit = None  # sonido golpe enemigo nulo
    sound_player_hit = None  # sonido golpe jugador nulo
    sound_enemy_death = None  # sonido muerte enemigo nulo
    sound_win = None  # sonido victoria nulo
    sound_game_over = None  # sonido game over nulo

#constantes de juego
PLAYER_INITIAL_HEALTH = 100  # salud inicial jugador
ENEMY_ATTACK_DAMAGE = 10  # dano ataque enemigo
DEADLY_OBSTACLE_DAMAGE = 10  # dano obstaculo mortal
PLAYER_ATTACK_COOLDOWN = 500 # tiempo entre ataques jugador en milisegundos
PLAYER_ATTACK_DAMAGE = 25 # dano que hace el jugador al enemigo
PLAYER_ATTACK_ANIM_DURATION = 10 # duracion animacion ataque jugador
ENEMY_ATTACK_ANIM_DURATION = 100 # duracion animacion ataque enemigo
UI_BAR_HEIGHT = int(SCREEN_HEIGHT * 0.1) # altura barra superior
INVULNERABILITY_DURATION = 1250 # tiempo invulnerabilidad despues de golpe en milisegundos
ENEMY_INITIAL_HEALTH = 100 # salud inicial enemigos
ENEMY_AGGRO_RADIUS = int(SCREEN_WIDTH * 0.2) # radio para activar enemigos

#clases de juego

class Player(pygame.sprite.Sprite):  # clase jugador
    def __init__(self, x, y):  # constructor
        super().__init__()  # llama al constructor padre
        # cargar imagen del jugador
        self.image = pygame.image.load("assets/imagenes/player.png").convert_alpha()  # carga imagen
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.1))) # escala imagen
        self.rect = self.image.get_rect(center=(x, y))  # rectangulo de la imagen
        self.speed = 5  # velocidad movimiento
        self.collected_objects = 0  # objetos recolectados
        self.prev_rect = self.rect.copy() # guarda posicion anterior para colisiones
        self.health = PLAYER_INITIAL_HEALTH  # salud actual
        self.max_health = PLAYER_INITIAL_HEALTH # salud maxima para barra
        self.is_attacking = False  # esta atacando
        self.last_attack_time = 0  # ultimo tiempo de ataque
        self.attack_anim_start_time = 0 # tiempo inicio animacion ataque
        self.last_hit_time = 0 # ultimo tiempo de golpe para invulnerabilidad
    def update(self, keys):  # actualiza estado jugador
        self.prev_rect = self.rect.copy() # guarda posicion anterior
        # resetea estado de ataque de animacion
        if pygame.time.get_ticks() - self.attack_anim_start_time > PLAYER_ATTACK_ANIM_DURATION:  # si termino animacion
            self.is_attacking = False  # deja de atacar
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # tecla izquierda
            self.rect.x -= self.speed  # mueve izquierda
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # tecla derecha
            self.rect.x += self.speed  # mueve derecha
        if keys[pygame.K_UP] or keys[pygame.K_w]:  # tecla arriba
            self.rect.y -= self.speed  # mueve arriba
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  # tecla abajo
            self.rect.y += self.speed  # mueve abajo
        # ataque con tecla espacio
        current_time = pygame.time.get_ticks()  # tiempo actual
        if keys[pygame.K_SPACE] and current_time - self.last_attack_time > PLAYER_ATTACK_COOLDOWN:  # puede atacar
            self.is_attacking = True  # activa ataque
            self.last_attack_time = current_time  # actualiza ultimo ataque
            self.attack_anim_start_time = current_time # inicia temporizador animacion
        # mantener jugador dentro de limites de pantalla
        self.rect.left = max(0, self.rect.left)  # limite izquierdo
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)  # limite derecho
        self.rect.top = max(UI_BAR_HEIGHT, self.rect.top) # evitar zona ui superior
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)  # limite inferior
    def revert_position(self):  # vuelve a posicion anterior
        self.rect = self.prev_rect.copy() # restaura posicion guardada
    def add_object(self):  # anade objeto recolectado
        self.collected_objects += 1  # incrementa contador
        if sound_collect:  # si existe sonido
            sound_collect.play()  # reproduce sonido
    def drop_object(self):  # suelta objeto
        if self.collected_objects > 0:  # si tiene objetos
            self.collected_objects -= 1  # decrementa contador
            if sound_collect: # si existe sonido
                sound_collect.play()  # reproduce sonido
    def reset_objects(self):  # reinicia objetos recolectados
        self.collected_objects = 0  # pone contador a cero
    def take_damage(self, amount):  # recibe dano
        current_time = pygame.time.get_ticks()  # tiempo actual
        if current_time - self.last_hit_time > INVULNERABILITY_DURATION: # si puede recibir dano
            self.health -= amount  # reduce salud
            if self.health < 0:  # si salud negativa
                self.health = 0  # pone salud a cero
            if sound_player_hit:  # si existe sonido
                sound_player_hit.play()  # reproduce sonido
            self.last_hit_time = current_time # reinicia temporizador invulnerabilidad
    def reset_health(self):  # restaura salud
        self.health = PLAYER_INITIAL_HEALTH  # salud inicial
    def draw_health_bar(self, surface):  # dibuja barra de vida
        if self.health > 0 : # solo si tiene vida
            bar_width = self.rect.width * 0.8 # ancho barra
            bar_height = 8 # altura barra
            bar_x = self.rect.centerx - bar_width // 2 # posicion x barra
            bar_y = self.rect.top - 15 # posicion y barra

            # fondo barra de vida
            pygame.draw.rect(surface, PLAYER_HEALTH_BAR_BACKGROUND_COLOR, (bar_x, bar_y, bar_width, bar_height), border_radius=3)  # dibuja rectangulo
            # barra vida actual
            current_health_width = (self.health / self.max_health) * bar_width  # calcula ancho actual
            if current_health_width > 0: # solo dibujar si hay vida
                 pygame.draw.rect(surface, PLAYER_HEALTH_BAR_COLOR, (bar_x, bar_y, current_health_width, bar_height), border_radius=3)  # dibuja barra verde


class CollectibleObject(pygame.sprite.Sprite):  # clase objeto coleccionable
    def __init__(self, x, y):  # constructor
        super().__init__()  # llama constructor padre
        # cargar imagen del objeto
        self.image = pygame.image.load("assets/imagenes/star.png").convert_alpha()  # carga imagen
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.03), int(SCREEN_HEIGHT * 0.04))) # escala imagen
        self.rect = self.image.get_rect(center=(x, y))  # rectangulo imagen
        self.collected = False  # indica si fue recolectado
class Goal(pygame.sprite.Sprite):  # clase meta
    def __init__(self, x, y, value):  # constructor
        super().__init__()  # llama constructor padre
        self.value = value  # valor numerico de la meta
        # cargar imagen de la meta
        self.image = pygame.image.load("assets/imagenes/goal.png").convert_alpha()  # carga imagen
        # reducir tamano imagen
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.09))) # escala imagen
        self.rect = self.image.get_rect(center=(x, y))  # rectangulo imagen
        # crear rectangulo de colision mas pequeno
        self.collision_rect = pygame.Rect(0, 0, self.image.get_width() * 0.7, self.image.get_height() * 0.7)  # rectangulo colision
        self.collision_rect.center = self.rect.center # centra rectangulo colision
        # renderizar numero en la imagen
        text_surface = font_goal.render(str(self.value), True, BLACK)  # texto con valor
        text_rect = text_surface.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))  # posicion texto
        self.image.blit(text_surface, text_rect)  # dibuja texto sobre imagen

class Obstacle(pygame.sprite.Sprite):  # clase obstaculo
    def __init__(self, x, y, width, height, obs_type="solid"): # tipo solido o mortal
        super().__init__()  # llama constructor padre
        self.type = obs_type  # tipo de obstaculo
        # superficie simple o imagen
        self.image = pygame.Surface((width, height))  # crea superficie
        if self.type == "solid":  # obstaculo solido
            # intenta cargar imagen de roca
            try: 
                self.image = pygame.image.load("assets/imagenes/rock.png").convert_alpha()  # carga imagen
                self.image = pygame.transform.scale(self.image, (width, height))  # escala
            except pygame.error:  # si falla carga
                self.image.fill(SOLID_OBSTACLE_COLOR) # usa color solido
        elif self.type == "deadly":  # obstaculo mortal
            try: # intenta cargar imagen lava
                self.image = pygame.image.load("assets/imagenes/lava.png").convert_alpha()  # carga imagen
                self.image = pygame.transform.scale(self.image, (width, height))  # escala
            except pygame.error:  # si falla carga
                self.image.fill(DEADLY_OBSTACLE_COLOR) # usa color solido
        self.rect = self.image.get_rect(center=(x, y))  # rectangulo imagen

class Enemy(pygame.sprite.Sprite):  # clase enemigo
    def __init__(self, x, y):  # constructor
        super().__init__()  # llama constructor padre
        self.image = pygame.image.load("assets/imagenes/enemy.png").convert_alpha() # carga imagen enemigo
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.09))) # escala imagen
        self.rect = self.image.get_rect(center=(x, y))  # rectangulo imagen
        self.speed = 4  # velocidad movimiento
        self.health = ENEMY_INITIAL_HEALTH  # salud actual
        self.max_health = ENEMY_INITIAL_HEALTH # salud maxima para barra
        self.attack_cooldown = 500 # tiempo entre ataques en milisegundos
        self.last_attack_time = 0  # ultimo tiempo de ataque
        self.damage_taken_this_attack = False # evita dano multiple por ataque
        self.is_aggressive = False # enemigo pasivo inicialmente
        self.is_attacking_anim = False # animacion ataque enemigo
        self.attack_anim_start_time = 0 # tiempo inicio animacion ataque
    def update(self, player_rect):  # actualiza enemigo
        # resetea estado animacion ataque
        if pygame.time.get_ticks() - self.attack_anim_start_time > ENEMY_ATTACK_ANIM_DURATION:  # si termino animacion
            self.is_attacking_anim = False  # desactiva animacion
        # comprobar proximidad jugador para volverse agresivo
        distance_to_player = math.hypot(self.rect.centerx - player_rect.centerx, self.rect.centery - player_rect.centery)  # calcula distancia
        if distance_to_player < ENEMY_AGGRO_RADIUS:  # si esta cerca
            self.is_aggressive = True  # se vuelve agresivo
        if self.is_aggressive: # solo persigue si es agresivo
            # moverse hacia jugador
            if self.rect.x < player_rect.x:  # si jugador a la derecha
                self.rect.x += self.speed  # mueve derecha
            elif self.rect.x > player_rect.x:  # si jugador a la izquierda
                self.rect.x -= self.speed  # mueve izquierda
            if self.rect.y < player_rect.y:  # si jugador abajo
                self.rect.y += self.speed  # mueve abajo
            elif self.rect.y > player_rect.y:  # si jugador arriba
                self.rect.y -= self.speed  # mueve arriba
        # mantener enemigo dentro de limites pantalla
        self.rect.left = max(0, self.rect.left)  # limite izquierdo
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)  # limite derecho
        self.rect.top = max(UI_BAR_HEIGHT, self.rect.top) # evitar zona ui superior
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)  # limite inferior
        self.damage_taken_this_attack = False # resetea bandera dano
    def take_damage(self, amount):  # recibe dano
        self.health -= amount  # reduce salud
        if self.health < 0:  # si salud negativa
            self.health = 0  # pone salud a cero
        if sound_enemy_hit:  # si existe sonido
            sound_enemy_hit.play()  # reproduce sonido
        self.damage_taken_this_attack = True # marca que recibio dano
        self.is_aggressive = True # se vuelve agresivo al ser atacado
    def can_attack(self):  # puede atacar
        return pygame.time.get_ticks() - self.last_attack_time > self.attack_cooldown  # devuelve si puede atacar
    def attack(self, player_obj):  # ataca al jugador
        if self.can_attack():  # si puede atacar
            player_obj.take_damage(ENEMY_ATTACK_DAMAGE)  # aplica dano
            self.last_attack_time = pygame.time.get_ticks()  # actualiza ultimo ataque
            self.is_attacking_anim = True # activa animacion ataque
            self.attack_anim_start_time = pygame.time.get_ticks() # inicia temporizador animacion
    def draw_health_bar(self, surface):  # dibuja barra vida enemigo
        if self.health > 0: # solo si tiene vida
            bar_width = self.rect.width * 0.8  # ancho barra
            bar_height = 5  # altura barra
            bar_x = self.rect.centerx - bar_width // 2  # posicion x barra
            bar_y = self.rect.top - 15 # posicion y barra encima del enemigo
            # fondo barra vida
            pygame.draw.rect(surface, HEALTH_BAR_BACKGROUND_COLOR, (bar_x, bar_y, bar_width, bar_height), border_radius=2)  # dibuja rectangulo
            # barra vida actual
            current_health_width = (self.health / self.max_health) * bar_width  # calcula ancho actual
            if current_health_width > 0: # solo dibujar si hay vida
                pygame.draw.rect(surface, HEALTH_BAR_COLOR, (bar_x, bar_y, current_health_width, bar_height), border_radius=2)  # dibuja barra verde

#variables globales del juego
PLAYER_START_X = SCREEN_WIDTH // 2  # posicion inicial x jugador
PLAYER_START_Y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.15) # altura inicial jugador
player = Player(PLAYER_START_X, PLAYER_START_Y) # crea instancia jugador
all_sprites = pygame.sprite.Group()  # grupo todos los sprites
collectible_objects = pygame.sprite.Group()  # grupo objetos coleccionables
goals = pygame.sprite.Group()  # grupo metas
obstacles = pygame.sprite.Group() #grupo para obstaculos
enemies = pygame.sprite.Group() # grupo para enemigos
all_sprites.add(player)  # anade jugador a todos los sprites
current_operation = ""  # operacion actual
correct_answer = 0  # respuesta correcta
feedback_message = ""  # mensaje feedback
feedback_color = BLACK  # color mensaje feedback
feedback_timer = 0  # temporizador mensaje feedback
FEEDBACK_DURATION = 1500 # duracion mensaje feedback en milisegundos
game_state = "menu" # estados posibles menu playing feedback level_complete game_over show_answer_popup controls_info
level = 1  # nivel actual
operation_type = "suma" # tipo operacion actual
max_number_in_op = 10 # dificultad actual para suma/resta
max_multiplier_divisor = 5 # dificultad actual para multiplicacion/division
win_frame_index = 0  # indice frame animacion victoria
last_win_frame_time = 0  # ultimo tiempo frame victoria
last_level_played = 0 # ultimo nivel jugado inicialmente 0
last_level_operation_text = ""  # texto operacion ultimo nivel
last_level_correct_answer = 0  # respuesta correcta ultimo nivel
# vidas del jugador para nivel actual
player_current_level_lives = 1  # vidas por nivel
# vidas que determinan los juegos antes de checkpoint
player_checkpoint_lives = 3  # vidas globales
# variables checkpoint
checkpoint_level = 1 # nivel desde el que reiniciar
checkpoint_op_type = "suma" # tipo operacion checkpoint
checkpoint_max_num = 10 # dificultad checkpoint suma/resta
checkpoint_max_mult_div = 5 # dificultad checkpoint mult/div
# variables ventana emergente
popup_message = ""  # mensaje popup
popup_correct_answer = 0  # respuesta correcta popup
# variables animaciones gif
win_gif_frames = []  # frames animacion victoria
lose_gif_frames = []  # frames animacion derrota
win_frame_index = 0  # indice frame actual victoria
lose_frame_index = 0  # indice frame actual derrota
last_win_frame_time = 0  # ultimo tiempo frame victoria
last_lose_frame_time = 0  # ultimo tiempo frame derrota
GIF_FRAME_DURATION = 100 # duracion por frame en milisegundos
def load_gif_frames(gif_path, scale_factor_width, scale_factor_height):  # carga frames gif
    frames = []  # lista frames
    try:  # intenta cargar gif
        img = Image.open(gif_path)  # abre imagen
        for frame in ImageSequence.Iterator(img):  # itera frames
            # convertir frame a formato pygame
            # redimensionar antes de convertir
            frame_resized = frame.resize((int(SCREEN_WIDTH * scale_factor_width), int(SCREEN_HEIGHT * scale_factor_height)))  # escala frame
            # convertir a modo rgba
            frame_rgba = frame_resized.convert("RGBA")  # conversion
            # crear superficie pygame
            pygame_frame = pygame.image.fromstring(frame_rgba.tobytes(), frame_rgba.size, frame_rgba.mode)  # crea superficie
            frames.append(pygame_frame)  # anade a lista
        return frames  # devuelve frames
    except FileNotFoundError:  # si archivo no encontrado
        print(f"error gif {gif_path} no encontrado")  # mensaje error
        return []  # devuelve lista vacia
    except Exception as e:  # cualquier otro error
        print(f"error al cargar gif {gif_path} {e}")  # mensaje error
        return []  # devuelve lista vacia
win_gif_frames = load_gif_frames("assets/gifs/win_animation.gif", 0.4, 0.4)  # carga animacion victoria
lose_gif_frames = load_gif_frames("assets/gifs/lose_animation.gif", 0.4, 0.4)  # carga animacion derrota
# imagenes para controles
control_images = {}  # diccionario imagenes teclas
KEY_IMAGE_SIZE = int(SCREEN_WIDTH * 0.05) # tamano imagenes teclas
try:  # intenta cargar imagenes de teclas
    control_images['arrow_up'] = pygame.transform.scale(pygame.image.load("assets/imagenes/arrow_up.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))  # flecha arriba
    control_images['arrow_left'] = pygame.transform.scale(pygame.image.load("assets/imagenes/arrow_left.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))  # flecha izquierda
    control_images['arrow_down'] = pygame.transform.scale(pygame.image.load("assets/imagenes/arrow_down.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))  # flecha abajo
    control_images['arrow_right'] = pygame.transform.scale(pygame.image.load("assets/imagenes/arrow_right.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))  # flecha derecha
    control_images['w_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/w_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))  # tecla w
    control_images['a_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/a_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))  # tecla a
    control_images['s_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/s_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))  # tecla s
    control_images['d_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/d_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))  # tecla d
    control_images['spacebar_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/spacebar_key.png").convert_alpha(), (KEY_IMAGE_SIZE * 1.5, KEY_IMAGE_SIZE)) # barra espaciadora mas ancha
    control_images['q_key'] = pygame.transform.scale(pygame.image.load("assets/imagenes/q_key.png").convert_alpha(), (KEY_IMAGE_SIZE, KEY_IMAGE_SIZE))  # tecla q
except pygame.error as e:  # si error al cargar
    print(f"advertencia no se pudieron cargar todas las imagenes de teclas {e} se usara texto")  # mensaje error
    control_images = {} # limpia diccionario
#funciones auxiliares
def draw_text(surface, text, font, color, x, y, center=True):  # dibuja texto
    text_surface = font.render(text, True, color)  # renderiza texto
    if center:  # si centrado
        text_rect = text_surface.get_rect(center=(x, y))  # rectangulo centrado
    else:  # si no centrado
        text_rect = text_surface.get_rect(x=x, y=y)  # rectangulo en posicion
    surface.blit(text_surface, text_rect)  # dibuja texto
def draw_wrapped_text(surface, text, font, color, rect, alignment="center"):  # dibuja texto con ajuste
    words = text.split(' ')  # separa palabras
    lines = []  # lista lineas
    current_line = []  # linea actual
    for word in words:  # por cada palabra
        # prueba si anadiendo palabra excede ancho
        test_line = ' '.join(current_line + [word])  # linea de prueba
        if font.size(test_line)[0] <= rect.width:  # si cabe
            current_line.append(word)  # anade palabra
        else:  # si no cabe
            lines.append(' '.join(current_line))  # anade linea
            current_line = [word]  # nueva linea con palabra
    lines.append(' '.join(current_line)) # anade ultima linea
    y_offset = rect.top  # desplazamiento vertical
    for line in lines:  # por cada linea
        text_surface = font.render(line, True, color)  # renderiza linea
        text_rect = text_surface.get_rect()  # rectangulo texto
        if alignment == "center":  # alineacion centro
            text_rect.centerx = rect.centerx  # centra en x
        elif alignment == "left":  # alineacion izquierda
            text_rect.left = rect.left  # alinea izquierda
        elif alignment == "right":  # alineacion derecha
            text_rect.right = rect.right  # alinea derecha
        text_rect.top = y_offset  # posicion y
        surface.blit(text_surface, text_rect)  # dibuja linea
        y_offset += font.get_height() # espacio entre lineas
def draw_button(surface, rect, text, font, base_color, hover_color=None):  # dibuja boton
    mouse_pos = pygame.mouse.get_pos()  # posicion raton
    current_color = base_color  # color base
    if rect.collidepoint(mouse_pos) and hover_color:  # si raton encima y hay color hover
        current_color = hover_color  # cambia color
    pygame.draw.rect(surface, current_color, rect, border_radius=10)  # dibuja rectangulo redondeado
    draw_text(surface, text, font, BLACK, rect.centerx, rect.centery)  # dibuja texto boton
    return rect  # devuelve rectangulo
# --- funciones de logica del juego ---
def generate_operation(op_type, max_num, max_mult_div):  # genera operacion matematica
    global current_operation, correct_answer  # variables globales
    num1 = 0  # primer numero
    num2 = 0  # segundo numero
    correct_answer = 0  # respuesta correcta

    if op_type == "suma":  # suma
        num1 = random.randint(1, max_num)  # genera num1
        num2 = random.randint(1, max_num)  # genera num2
        correct_answer = num1 + num2  # calcula respuesta
        current_operation = f"{num1} + {num2} = ?"  # texto operacion
    elif op_type == "resta":  # resta
        num1 = random.randint(1, max_num)  # genera num1
        num2 = random.randint(1, max_num)  # genera num2
        if num1 < num2: # asegura resultado no negativo
            num1, num2 = num2, num1  # intercambia valores
        correct_answer = num1 - num2  # calcula respuesta
        current_operation = f"{num1} - {num2} = ?"  # texto operacion
    elif op_type == "multiplicacion":  # multiplicacion
        # usa min para limitar numeros
        num1 = random.randint(1, min(10, max_mult_div + 5))  # genera num1
        num2 = random.randint(1, min(10, max_mult_div + 5))  # genera num2
        correct_answer = num1 * num2  # calcula respuesta
        current_operation = f"{num1} x {num2} = ?"  # texto operacion
    elif op_type == "division":  # division
        # asegura division exacta
        divisor = random.randint(2, min(10, max_mult_div + 5))  # genera divisor
        cociente = random.randint(1, min(10, max_mult_div + 5))  # genera cociente
        num1 = divisor * cociente # calcula dividendo
        num2 = divisor # divisor
        correct_answer = cociente  # respuesta es cociente
        current_operation = f"{num1} / {num2} = ?"  # texto operacion
    # genera respuestas incorrectas cercanas
    incorrect_answers = set()  # conjunto respuestas incorrectas
    while len(incorrect_answers) < 2:  # mientras no tenga 2 incorrectas
        offset = random.choice([-3, -2, -1, 1, 2, 3]) # pequenos offsets
        incorrect_ans = correct_answer + offset  # respuesta incorrecta
        # asegura que sean positivas y distintas
        if incorrect_ans > 0 and incorrect_ans != correct_answer and incorrect_ans not in incorrect_answers:  # valida
            incorrect_answers.add(incorrect_ans)  # anade al conjunto
    return list(incorrect_answers) # retorna incorrectas para metas
def show_correct_answer_popup(message):  # muestra popup respuesta correcta
    global game_state, popup_message, popup_correct_answer, last_level_correct_answer # variables globales
    game_state = "show_answer_popup"  # cambia estado
    popup_message = message  # mensaje popup
    popup_correct_answer = last_level_correct_answer # muestra respuesta del nivel anterior
def handle_player_death_logic():  # maneja muerte jugador
    global player_checkpoint_lives, game_state, feedback_message, feedback_color, feedback_timer  # variables globales
    player_checkpoint_lives -= 1  # reduce vidas checkpoint
    if sound_incorrect: # sonido de fallo
         sound_incorrect.play()  # reproduce sonido
    if player_checkpoint_lives <= 0:  # si no quedan vidas
        # perdio el juego
        game_state = "game_over" # cambia a game over
        if sound_game_over: sound_game_over.play()  # reproduce sonido game over
    else: # si quedan vidas
        # reinicia nivel actual
        generate_level(operation_type, max_number_in_op, max_multiplier_divisor)  # genera nivel
        player.reset_health() # restaura salud jugador
        show_correct_answer_popup(f"cuidado vidas de checkpoint restantes {player_checkpoint_lives} la respuesta correcta era")  # muestra popup
def generate_level(op_type, max_num_op, max_mult_div_op):  # genera nivel
    global current_operation, correct_answer, feedback_message, feedback_color, feedback_timer, player_current_level_lives  # variables globales
    # limpia grupos anteriores
    collectible_objects.empty()  # vacia objetos
    goals.empty()  # vacia metas
    obstacles.empty()  # vacia obstaculos
    enemies.empty() # limpia enemigos
    all_sprites.empty() # limpia todos los sprites
    all_sprites.add(player) # anade jugador
    player.reset_objects()  # reinicia objetos jugador
    player_current_level_lives = 1 # una vida por nivel
    player.reset_health() # restaura salud jugador
    feedback_message = ""  # limpia mensaje feedback
    feedback_timer = 0  # reinicia temporizador
    incorrect_answers_for_goals = generate_operation(op_type, max_num_op, max_mult_div_op) # genera operacion y respuestas
    # genera 3 metas
    goal_positions = [  # posiciones posibles metas
        (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + SCREEN_HEIGHT * 0.1),  # izquierda
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + SCREEN_HEIGHT * 0.1),  # centro
        (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2 + SCREEN_HEIGHT * 0.1)  # derecha
    ]
    random.shuffle(goal_positions) # mezcla posiciones
    # asigna respuesta correcta a meta aleatoria
    all_possible_answers = incorrect_answers_for_goals  # respuestas incorrectas
    all_possible_answers.insert(random.randint(0, 2), correct_answer) # inserta correcta en posicion aleatoria
    # crea objetos goal y zonas exclusion
    goal_exclusion_zones = []  # lista zonas exclusion metas
    for i in range(3):  # para cada meta
        goal = Goal(goal_positions[i][0], goal_positions[i][1], all_possible_answers[i])  # crea meta
        goals.add(goal)  # anade a grupo metas
        all_sprites.add(goal) # anade a todos los sprites
        # calcula area exclusion alrededor meta
        EXCLUSION_MARGIN_GOAL = int(SCREEN_WIDTH * 0.08) # margen exclusion
        exclusion_rect_goal = goal.rect.inflate(goal.rect.width + EXCLUSION_MARGIN_GOAL, goal.rect.height + EXCLUSION_MARGIN_GOAL)  # rectangulo exclusion
        goal_exclusion_zones.append(exclusion_rect_goal)  # anade a lista
    # zona exclusion jugador
    PLAYER_EXCLUSION_RADIUS = int(min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.2) # radio exclusion
    player_exclusion_zone = pygame.Rect(0, 0, PLAYER_EXCLUSION_RADIUS * 2, PLAYER_EXCLUSION_RADIUS * 2)  # rectangulo exclusion
    player_exclusion_zone.center = (PLAYER_START_X, PLAYER_START_Y) # centra en jugador
    # generacion obstaculos
    num_obstacles = random.randint(4, 8) # numero aleatorio obstaculos
    obstacle_sizes = [  # tamanos posibles
        (int(SCREEN_WIDTH * 0.05), int(SCREEN_HEIGHT * 0.07)),  # pequeno
        (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.09)),  # mediano
        (int(SCREEN_WIDTH * 0.06), int(SCREEN_HEIGHT * 0.1)),   # mediano2
        (int(SCREEN_WIDTH * 0.09), int(SCREEN_HEIGHT * 0.07))   # grande
    ]
    # zonas prohibidas para obstaculos
    forbidden_zones_for_obstacles = []  # lista zonas prohibidas
    forbidden_zones_for_obstacles.extend(goal_exclusion_zones) # anade zonas metas
    forbidden_zones_for_obstacles.append(player_exclusion_zone) # anade zona jugador
    # evita zona ui superior
    forbidden_zones_for_obstacles.append(pygame.Rect(0, 0, SCREEN_WIDTH, UI_BAR_HEIGHT + 20))  # zona ui
    # define cuantos obstaculos mortales
    num_deadly_obstacles = random.randint(1, 4) # entre 1 y 4 mortales
    for i in range(num_obstacles):  # por cada obstaculo
        obs_width, obs_height = random.choice(obstacle_sizes)  # elige tamano
        attempts = 0  # intentos
        max_attempts_obs = 100 # max intentos evitar bucles
        found_valid_pos_obs = False  # posicion valida encontrada
        obs_type = "solid"  # tipo solido por defecto
        if i < num_deadly_obstacles: # asigna mortales
            obs_type = "deadly"  # tipo mortal
        while not found_valid_pos_obs and attempts < max_attempts_obs:  # busca posicion valida
            obs_x = random.randint(obs_width // 2, SCREEN_WIDTH - obs_width // 2)  # pos x aleatoria
            obs_y = random.randint(UI_BAR_HEIGHT + obs_height // 2, SCREEN_HEIGHT - obs_height // 2 - 20) # pos y aleatoria
            temp_obs_rect = pygame.Rect(0, 0, obs_width, obs_height)  # rectangulo temporal
            temp_obs_rect.center = (obs_x, obs_y)  # centra
            # verifica solapamiento con zonas prohibidas
            is_overlapping_obs = False  # solapamiento
            for zone in forbidden_zones_for_obstacles:  # por cada zona prohibida
                if temp_obs_rect.colliderect(zone):  # si solapa
                    is_overlapping_obs = True  # marca
                    break  # rompe bucle
            if not is_overlapping_obs: # si no solapa con zonas
                for existing_obs in obstacles:  # verifica con otros obstaculos
                    if temp_obs_rect.colliderect(existing_obs.rect.inflate(int(SCREEN_WIDTH * 0.02), int(SCREEN_HEIGHT * 0.02))): # con margen
                        is_overlapping_obs = True  # marca
                        break  # rompe
            if not is_overlapping_obs:  # si posicion valida
                found_valid_pos_obs = True  # encontrada
            attempts += 1  # incrementa intentos
        if found_valid_pos_obs:  # si encontro posicion
            obstacle = Obstacle(obs_x, obs_y, obs_width, obs_height, obs_type)  # crea obstaculo
            obstacles.add(obstacle)  # anade a grupo
            all_sprites.add(obstacle)  # anade a todos
            # anade a zonas prohibidas para siguientes objetos
            forbidden_zones_for_obstacles.append(obstacle.rect.inflate(int(SCREEN_WIDTH * 0.02), int(SCREEN_HEIGHT * 0.02))) # con margen
    # generar enemigos
    num_enemies_to_spawn = 0  # numero enemigos
    # generar solo en niveles impares
    if level % 2 != 0 and level >= 1: # si nivel impar y mayor 1
        num_enemies_to_spawn = random.randint(1, 1 + level // 5) # mas enemigos en niveles altos
    for _ in range(num_enemies_to_spawn):  # por cada enemigo
        found_valid_pos_enemy = False  # posicion valida
        attempts = 0  # intentos
        max_attempts_enemy = 100  # max intentos
        while not found_valid_pos_enemy and attempts < max_attempts_enemy:  # busca posicion
            enemy_x = random.randint(SCREEN_WIDTH // 4, SCREEN_WIDTH * 3 // 4)  # pos x aleatoria
            enemy_y = random.randint(UI_BAR_HEIGHT + 30, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.15))  # pos y aleatoria
            temp_enemy_rect = pygame.Rect(0,0, int(SCREEN_WIDTH * 0.06), int(SCREEN_HEIGHT * 0.08))  # rect temporal
            temp_enemy_rect.center = (enemy_x, enemy_y)  # centra
            is_overlapping_enemy = False  # solapamiento
            for zone in forbidden_zones_for_obstacles: # usa mismas zonas prohibidas
                if temp_enemy_rect.colliderect(zone):  # si solapa
                    is_overlapping_enemy = True  # marca
                    break  # rompe
            if not is_overlapping_enemy:  # si no solapa con zonas
                for existing_enemy in enemies:  # verifica con otros enemigos
                    if temp_enemy_rect.colliderect(existing_enemy.rect.inflate(int(SCREEN_WIDTH * 0.02), int(SCREEN_HEIGHT * 0.02))):  # con margen
                        is_overlapping_enemy = True  # marca
                        break  # rompe
            if not is_overlapping_enemy:  # si posicion valida
                found_valid_pos_enemy = True  # encontrada
            attempts += 1  # incrementa intentos
        if found_valid_pos_enemy:  # si encontro posicion
            enemy = Enemy(enemy_x, enemy_y)  # crea enemigo
            enemies.add(enemy)  # anade a grupo
            all_sprites.add(enemy)  # anade a todos
            forbidden_zones_for_obstacles.append(enemy.rect.inflate(int(SCREEN_WIDTH * 0.04), int(SCREEN_HEIGHT * 0.04))) # anade a zonas prohibidas
    # generar objetos coleccionables
    # calcular cuantos objetos faltan
    initial_objects_needed = correct_answer - num_enemies_to_spawn # cada enemigo da un objeto
    num_objects_to_spawn = max(0, initial_objects_needed) + random.randint(5,10) # objetos necesarios mas extras
    # combina zonas exclusion
    all_exclusion_zones_for_objects = list(goal_exclusion_zones)  # zonas metas
    for obs in obstacles:  # por cada obstaculo
        all_exclusion_zones_for_objects.append(obs.rect.inflate(int(SCREEN_WIDTH * 0.04), int(SCREEN_HEIGHT * 0.04))) # anade con margen
    for enemy in enemies:  # por cada enemigo
        all_exclusion_zones_for_objects.append(enemy.rect.inflate(int(SCREEN_WIDTH * 0.06), int(SCREEN_HEIGHT * 0.06))) # anade con margen
    all_exclusion_zones_for_objects.append(player_exclusion_zone) # anade zona jugador
    # margen minimo entre objetos
    OBJECT_SPACING_MARGIN = int(SCREEN_WIDTH * 0.05) # distancia minima entre objetos
    generated_object_positions = [] # posiciones objetos generados
    for _ in range(num_objects_to_spawn):  # por cada objeto
        found_valid_pos = False  # posicion valida
        attempts = 0  # intentos
        max_attempts_obj = 150 # max intentos
        while not found_valid_pos and attempts < max_attempts_obj:  # busca posicion
            # posiciones aleatorias
            obj_x = random.randint(int(SCREEN_WIDTH * 0.03), SCREEN_WIDTH - int(SCREEN_WIDTH * 0.03))  # pos x
            obj_y = random.randint(UI_BAR_HEIGHT + int(SCREEN_HEIGHT * 0.03), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.1)) # pos y
            temp_obj_rect = pygame.Rect(0,0, int(SCREEN_WIDTH * 0.03), int(SCREEN_HEIGHT * 0.04)) # rect provisional
            temp_obj_rect.center = (obj_x, obj_y)  # centra
            is_overlapping = False  # solapamiento
            # verifica solapamiento con zonas exclusion
            for zone in all_exclusion_zones_for_objects:  # por cada zona
                if temp_obj_rect.colliderect(zone):  # si solapa
                    is_overlapping = True  # marca
                    break  # rompe
            # verifica solapamiento con otros objetos
            if not is_overlapping:  # si no solapa zonas
                for existing_pos in generated_object_positions:  # por cada posicion existente
                    distance = ((obj_x - existing_pos[0])**2 + (obj_y - existing_pos[1])**2)**0.5  # calcula distancia
                    if distance < OBJECT_SPACING_MARGIN:  # si muy cerca
                        is_overlapping = True  # marca
                        break  # rompe
            if not is_overlapping:  # si posicion valida
                found_valid_pos = True  # encontrada
            attempts += 1  # incrementa intentos
        if found_valid_pos: # si encontro posicion
            obj = CollectibleObject(obj_x, obj_y)  # crea objeto
            collectible_objects.add(obj)  # anade a grupo
            all_sprites.add(obj) # anade a todos
            generated_object_positions.append((obj_x, obj_y)) # guarda posicion
    player.rect.center = (PLAYER_START_X, PLAYER_START_Y) # reset posicion jugador
def reset_game_to_checkpoint():  # reinicia juego desde checkpoint
    global level, operation_type, max_number_in_op, max_multiplier_divisor, player_checkpoint_lives, checkpoint_level, checkpoint_op_type, checkpoint_max_num, checkpoint_max_mult_div  # variables globales
    level = checkpoint_level # vuelve nivel checkpoint
    operation_type = checkpoint_op_type # vuelve tipo operacion checkpoint
    max_number_in_op = checkpoint_max_num # vuelve dificultad suma/resta
    max_multiplier_divisor = checkpoint_max_mult_div # vuelve dificultad mult/div
    player_checkpoint_lives = 3 # siempre 3 vidas al reiniciar
    player.reset_health() # restaura salud jugador
    generate_level(operation_type, max_number_in_op, max_multiplier_divisor) # genera nivel checkpoint
def show_controls_popup():  # muestra popup controles
    global game_state  # variable global
    game_state = "controls_info"  # cambia estado
def draw_controls_popup(surface):  # dibuja popup controles
    # crea superficie semi-transparente fondo oscuro
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  # superficie transparente
    overlay.fill((0, 0, 0, 180)) # negro con opacidad
    surface.blit(overlay, (0, 0))  # dibuja overlay
    # dimensiones ventana emergente
    popup_width = int(SCREEN_WIDTH * 0.7)  # ancho popup
    popup_height = int(SCREEN_HEIGHT * 0.8)  # alto popup
    popup_x = SCREEN_WIDTH // 2 - popup_width // 2  # pos x popup
    popup_y = SCREEN_HEIGHT // 2 - popup_height // 2  # pos y popup
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)  # rect popup
    pygame.draw.rect(surface, WHITE, popup_rect, border_radius=15)  # dibuja fondo popup
    pygame.draw.rect(surface, BLACK, popup_rect, 5, border_radius=15) # borde popup
    draw_text(surface, "controles y objetivo del juego", font_popup_title, BLACK, SCREEN_WIDTH // 2, popup_y + int(popup_height * 0.08))  # titulo
    # mostrar controles con imagenes y texto
    controls_start_y = popup_y + int(popup_height * 0.08)  # pos y inicio controles
    line_height = int(font_popup_text.get_height() * 3.2) # espacio entre lineas
    key_image_y_offset = int(line_height * 0.8) # offset vertical imagenes
    control_definitions = [  # definicion controles
        (("arrow_up", "arrow_left", "arrow_down", "arrow_right"), "moverse (teclas de flecha)"),  # flechas
        (("w_key", "a_key", "s_key", "d_key"), "moverse (w a s d)"),  # wasd
        ("spacebar_key", "atacar"),  # espacio
        ("q_key", "soltar objeto")  # q
    ]
    current_y = controls_start_y  # pos y actual
    for item in control_definitions:  # por cada control
        x_offset = popup_x + 40 # pos x inicial texto
        if isinstance(item[0], tuple): # multiples imagenes
            for key_img_name in item[0]:  # por cada tecla
                if key_img_name in control_images:  # si existe imagen
                    img = control_images[key_img_name]  # obtiene imagen
                    img_rect = img.get_rect(midleft=(x_offset, current_y + key_image_y_offset))  # rect imagen
                    surface.blit(img, img_rect)  # dibuja imagen
                    x_offset += img.get_width() + 5 # espacio entre imagenes
            draw_text(surface, item[1], font_popup_text, BLACK, x_offset + (popup_width - x_offset - (popup_x + 40)) // 2, current_y + key_image_y_offset, center=False)  # dibuja texto
        else: # una sola imagen
            key_img_name = item[0]  # nombre imagen
            if key_img_name in control_images:  # si existe imagen
                img = control_images[key_img_name]  # obtiene imagen
                img_rect = img.get_rect(midleft=(x_offset, current_y + key_image_y_offset))  # rect imagen
                surface.blit(img, img_rect)  # dibuja imagen
                draw_text(surface, item[1], font_popup_text, BLACK, img_rect.right + 20, current_y + key_image_y_offset, center=False)  # dibuja texto
            else: # fallback a texto
                draw_text(surface, f"{item[0].replace('_key', '').upper()} : {item[1]}", font_popup_text, BLACK, x_offset, current_y + key_image_y_offset, center=False)  # dibuja texto alternativo
        current_y += line_height  # siguiente linea
    # objetivo del juego
    objective_text_start_y = current_y + int(popup_height * 0.05)  # pos y objetivo
    draw_text(surface, "objetivo del juego:", font_popup_text, BLACK, popup_x + 40, objective_text_start_y, center=False)  # subtitulo
    objective_lines = [  # lineas objetivo
        "resuelve la operacion matematica en la parte superior",
        "recolecta la cantidad de zapatos que es la respuesta correcta",
        "lleva los zapatos recolectados a la meta con la respuesta correcta"
        "",
        "cuidado con los obstaculos mortales y los enemigos",
        "derrotar enemigos te dara un zapato",
        "cada 5 niveles se guarda un checkpoint y recuperas vidas",
        "evita quedarte sin vidas de checkpoint"
    ]
    obj_line_y = objective_text_start_y + font_popup_text.get_height() + 10  # pos y primera linea
    for line in objective_lines:  # por cada linea
        draw_text(surface, line, font_popup_text, BLACK, popup_x + 60, obj_line_y, center=False)  # dibuja linea
        obj_line_y += font_popup_text.get_height() + 5  # siguiente linea
    # boton entendido
    button_width = int(SCREEN_WIDTH * 0.15)  # ancho boton
    button_height = int(SCREEN_HEIGHT * 0.07)  # alto boton
    # posicion boton
    button_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - button_width // 2,  # centrado x
        popup_y + popup_height - button_height - 20, # 20px desde abajo
        button_width,
        button_height
    )
    # dibuja boton y retorna rect
    return draw_button(surface, button_rect, "entendido", font_button, BUTTON_COLOR, HOVER_COLOR)
#bucle principal del juego
running = True  # controla ejecucion
clock = pygame.time.Clock()  # controla fps
while running:  # bucle principal
    for event in pygame.event.get():  # procesa eventos
        if event.type == pygame.QUIT:  # evento cerrar ventana
            running = False  # termina bucle
        if event.type == pygame.MOUSEBUTTONDOWN:  # clic raton
            if game_state == "menu":  # estado menu
                # botones del menu
                # reinicia variables nivel y checkpoint al elegir modo
                level = 1  # nivel 1
                checkpoint_level = 1  # checkpoint nivel 1
                player_checkpoint_lives = 3  # vidas 3
                player.reset_health() # asegura salud completa
                # ajuste posiciones botones
                button_width = int(SCREEN_WIDTH * 0.3)  # ancho boton
                button_height = int(SCREEN_HEIGHT * 0.1)  # alto boton
                # posiciones botones
                sum_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 2.2, button_width, button_height) # boton suma
                subtract_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 1, button_width, button_height) # boton resta
                multiply_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 0.2, button_width, button_height) # boton multiplicacion
                divide_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 1.4, button_width, button_height) # boton division
                controls_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 2.6, button_width, button_height) # boton controles
                exit_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 3.8, button_width, button_height) # boton salir
                if sum_btn_rect.collidepoint(event.pos):  # clic boton suma
                    operation_type = "suma"  # tipo suma
                    max_number_in_op = 10 # inicio suma/resta
                    max_multiplier_divisor = 2 # ajuste mult/div
                    checkpoint_op_type = operation_type  # checkpoint tipo
                    checkpoint_max_num = max_number_in_op  # checkpoint dificultad
                    checkpoint_max_mult_div = max_multiplier_divisor  # checkpoint mult/div
                    game_state = "playing"  # cambia estado
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)  # genera nivel
                elif subtract_btn_rect.collidepoint(event.pos):  # clic boton resta
                    operation_type = "resta"  # tipo resta
                    max_number_in_op = 10  # dificultad
                    max_multiplier_divisor = 2 # ajuste
                    checkpoint_op_type = operation_type  # checkpoint tipo
                    checkpoint_max_num = max_number_in_op  # checkpoint dificultad
                    checkpoint_max_mult_div = max_multiplier_divisor  # checkpoint mult/div
                    game_state = "playing"  # cambia estado
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)  # genera nivel
                elif multiply_btn_rect.collidepoint(event.pos):  # clic boton multiplicacion
                    operation_type = "multiplicacion"  # tipo multiplicacion
                    max_number_in_op = 10 # para resultado
                    max_multiplier_divisor = 2 # inicio
                    checkpoint_op_type = operation_type  # checkpoint tipo
                    checkpoint_max_num = max_number_in_op  # checkpoint dificultad
                    checkpoint_max_mult_div = max_multiplier_divisor  # checkpoint mult/div
                    game_state = "playing"  # cambia estado
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)  # genera nivel
                elif divide_btn_rect.collidepoint(event.pos):  # clic boton division
                    operation_type = "division"  # tipo division
                    max_number_in_op = 20 # para dividendo
                    max_multiplier_divisor = 2 # inicio
                    checkpoint_op_type = operation_type  # checkpoint tipo
                    checkpoint_max_num = max_number_in_op  # checkpoint dificultad
                    checkpoint_max_mult_div = max_multiplier_divisor  # checkpoint mult/div
                    game_state = "playing"  # cambia estado
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)  # genera nivel
                elif controls_btn_rect.collidepoint(event.pos): # clic boton controles
                    show_controls_popup()  # muestra popup controles
                elif exit_btn_rect.collidepoint(event.pos): # clic boton salir
                    running = False  # termina juego
            elif game_state == "playing":  # estado jugando
                # boton volver al menu
                menu_btn_rect = pygame.Rect(SCREEN_WIDTH - int(SCREEN_WIDTH * 0.15) - 20, 10, int(SCREEN_WIDTH * 0.15), UI_BAR_HEIGHT - 20)  # rect boton menu
                if menu_btn_rect.collidepoint(event.pos):  # clic boton
                    game_state = "menu"  # vuelve al menu
                    # resetea todo
                    level = 1  # nivel 1
                    checkpoint_level = 1  # checkpoint 1
                    player_checkpoint_lives = 3  # vidas 3
                    player.reset_health()  # restaura salud
                    player.reset_objects()  # reinicia objetos
                    collectible_objects.empty()  # vacia objetos
                    goals.empty()  # vacia metas
                    obstacles.empty()  # vacia obstaculos
                    enemies.empty()  # vacia enemigos
                    all_sprites.empty()  # vacia sprites
                    all_sprites.add(player) # anade jugador
                    feedback_message = ""  # limpia mensaje
                    feedback_timer = 0  # reinicia temporizador
            elif game_state == "level_complete":  # nivel completado
                if sound_win: sound_win.stop() # detiene sonido victoria
                level += 1  # siguiente nivel
                # logica progresion dificultad
                if operation_type in ["suma", "resta"]:  # suma o resta
                    if level <= 5:  # niveles 1-5
                        max_number_in_op = 10  # dificultad 10
                    elif level <= 10:  # niveles 6-10
                        max_number_in_op = 20  # dificultad 20
                    elif level <= 15:  # niveles 11-15
                        max_number_in_op = 30  # dificultad 30
                    else:  # niveles >15
                        max_number_in_op = 50  # dificultad 50
                elif operation_type in ["multiplicacion", "division"]:  # mult o div
                    if level <= 5: # niveles 1-5
                        max_multiplier_divisor = 2  # dificultad 2
                    elif level <= 10: # niveles 6-10
                        max_multiplier_divisor = 6  # dificultad 6
                    elif level <= 15: # niveles 11-15
                        max_multiplier_divisor = 10  # dificultad 10
                    else: # niveles >15
                        max_multiplier_divisor = 16 # dificultad 16
                    if operation_type == "division":  # division
                        pass  # no hace nada extra

                # logica checkpoint
                # checkpoint cada 5 niveles completados
                if (level - 1) > 0 and (level - 1) % 5 == 0 : # despues nivel 5 10 etc
                    checkpoint_level = level  # checkpoint nivel actual
                    checkpoint_op_type = operation_type # checkpoint tipo operacion
                    checkpoint_max_num = max_number_in_op  # checkpoint dificultad
                    checkpoint_max_mult_div = max_multiplier_divisor  # checkpoint mult/div
                    player_checkpoint_lives = 3  # recarga vidas
                    # mensaje feedback
                    feedback_message = "checkpoint guardado vidas recargadas"  # mensaje
                    feedback_color = GREEN # color verde
                    feedback_timer = pygame.time.get_ticks() # inicia temporizador

                player.reset_health()  # restaura salud jugador
                game_state = "playing"  # cambia estado
                generate_level(operation_type, max_number_in_op, max_multiplier_divisor)  # genera nivel

            elif game_state == "game_over":  # estado game over
                # botones game over
                game_over_continue_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.15), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08)) # boton continuar
                game_over_menu_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.25), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08)) # boton menu
                if game_over_continue_btn_rect.collidepoint(event.pos):  # clic continuar
                    if sound_game_over: sound_game_over.stop() # detiene sonido game over
                    game_state = "playing"  # cambia estado
                    reset_game_to_checkpoint()  # reinicia desde checkpoint
                elif game_over_menu_btn_rect.collidepoint(event.pos):  # clic menu
                    if sound_game_over: sound_game_over.stop() # detiene sonido game over
                    game_state = "menu"  # vuelve al menu
                    # resetea todo
                    level = 1  # nivel 1
                    checkpoint_level = 1  # checkpoint 1
                    player_checkpoint_lives = 3  # vidas 3
                    player.reset_health()  # restaura salud
                    player.reset_objects()  # reinicia objetos
                    collectible_objects.empty()  # vacia objetos
                    goals.empty()  # vacia metas
                    obstacles.empty()  # vacia obstaculos
                    enemies.empty()  # vacia enemigos
                    all_sprites.empty()  # vacia sprites
                    all_sprites.add(player) # anade jugador
                    feedback_message = ""  # limpia mensaje
                    feedback_timer = 0  # reinicia temporizador
            elif game_state == "show_answer_popup":  # popup respuesta
                # boton cerrar
                popup_button_width = int(SCREEN_WIDTH * 0.15)  # ancho boton
                popup_button_height = int(SCREEN_HEIGHT * 0.07)  # alto boton
                popup_button_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - popup_button_width // 2,  # centrado x
                    SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.17),  # pos y
                    popup_button_width,
                    popup_button_height
                )
                if popup_button_rect.collidepoint(event.pos):  # clic cerrar
                    # si perdio todas vidas
                    if player_checkpoint_lives <= 0:  # sin vidas
                        game_state = "game_over"  # va a game over
                        if sound_game_over: sound_game_over.play()  # reproduce sonido
                    else: # si quedan vidas
                        game_state = "playing"  # vuelve a jugar
            # logica boton entendido popup controles
            elif game_state == "controls_info":  # estado controles
                button_width = int(SCREEN_WIDTH * 0.15)  # ancho boton
                button_height = int(SCREEN_HEIGHT * 0.07)  # alto boton
                # recalcula posicion boton entendido
                popup_width_ctrl = int(SCREEN_WIDTH * 0.7) # ancho popup
                popup_height_ctrl = int(SCREEN_HEIGHT * 0.8) # alto popup
                popup_y_ctrl = SCREEN_HEIGHT // 2 - popup_height_ctrl // 2 # pos y popup

                button_rect_for_click_check = pygame.Rect(  # rect boton
                    SCREEN_WIDTH // 2 - button_width // 2,  # centrado x
                    popup_y_ctrl + popup_height_ctrl - button_height - 20, # misma logica dibujo
                    button_width,
                    button_height
                )
                if button_rect_for_click_check.collidepoint(event.pos):  # clic entendido
                     game_state = "menu" # vuelve al menu
        if event.type == pygame.KEYDOWN:  # tecla presionada
            if game_state == "playing":  # estado jugando
                if event.key == pygame.K_q: # tecla q
                    player.drop_object()  # suelta objeto
    #actualizaciones del juego
    if game_state == "playing":  # estado jugando
        keys = pygame.key.get_pressed()  # teclas presionadas
        player.update(keys)  # actualiza jugador
        enemies.update(player.rect) # actualiza enemigos
        # colision jugador obstaculos
        collided_obstacles = pygame.sprite.spritecollide(player, obstacles, False) # no remueve obstaculo
        for obs in collided_obstacles:  # por cada obstaculo colisionado
            if obs.type == "solid":  # obstaculo solido
                player.revert_position() # vuelve posicion anterior
            elif obs.type == "deadly":  # obstaculo mortal
                player.take_damage(DEADLY_OBSTACLE_DAMAGE) # aplica dano
                player.revert_position() # empuja jugador
                if player.health <= 0: # si salud cero
                    handle_player_death_logic() # maneja muerte
                    break # rompe bucle
        # colision jugador enemigos
        collided_enemies = pygame.sprite.spritecollide(player, enemies, False)  # no remueve enemigo
        for enemy in collided_enemies:  # por cada enemigo colisionado
            # condicion para dano
            if player.is_attacking and not enemy.damage_taken_this_attack:  # jugador ataca
                enemy.take_damage(PLAYER_ATTACK_DAMAGE) # aplica dano enemigo
                if enemy.health <= 0:  # si enemigo muere
                    if sound_enemy_death:  # si existe sonido
                        sound_enemy_death.play()  # reproduce sonido
                    enemy.kill() # elimina enemigo
                    # genera objeto en posicion enemigo
                    new_obj = CollectibleObject(enemy.rect.centerx, enemy.rect.centery)  # crea objeto
                    collectible_objects.add(new_obj)  # anade a grupo
                    all_sprites.add(new_obj) # anade a todos
            elif not player.is_attacking:  # si jugador no ataca
                if enemy.is_aggressive:  # enemigo agresivo
                    enemy.attack(player)  # enemigo ataca
        # colision objetos coleccionables
        collected = pygame.sprite.spritecollide(player, collectible_objects, True) # remueve objeto
        for obj in collected:  # por cada objeto recolectado
            player.add_object()  # anade objeto a jugador
        # colision metas
        collided_goal = None  # meta colisionada
        for goal in goals:  # por cada meta
            # usa collision_rect para colision precisa
            if player.rect.colliderect(goal.collision_rect):  # si colisiona
                collided_goal = goal  # guarda meta
                break # solo una meta
        if collided_goal: # si colisiono con meta
            last_level_correct_answer=correct_answer  # guarda respuesta correcta
            if player.collected_objects == correct_answer:  # objetos correctos
                if collided_goal.value == correct_answer:  # meta correcta
                    feedback_message = "correcto siguiente nivel"  # mensaje
                    feedback_color = GREEN  # color verde
                    if sound_correct: sound_correct.play()  # sonido correcto
                    if sound_win: sound_win.play() # sonido victoria
                    game_state = "level_complete"  # cambia estado
                else: # cantidad correcta meta incorrecta
                    player_current_level_lives -= 1 # resta vida
                    if sound_incorrect: sound_incorrect.play()  # sonido incorrecto
                    if player_current_level_lives <= 0:  # sin vidas nivel
                        handle_player_death_logic() # maneja muerte
                    else:  # quedan vidas
                        show_correct_answer_popup(f"cantidad correcta pero meta incorrecta la respuesta correcta era")  # muestra popup
            else: # cantidad objetos incorrecta
                player_current_level_lives -= 1 # resta vida
                if sound_incorrect: sound_incorrect.play()  # sonido incorrecto
                if player_current_level_lives <= 0:  # sin vidas nivel
                    handle_player_death_logic() # maneja muerte
                else:  # quedan vidas
                    show_correct_answer_popup(f"necesitas {correct_answer} objetos tienes {player.collected_objects} la respuesta correcta era")  # muestra popup
            # mueve jugador para evitar multiples colisiones
            if game_state != "level_complete":  # si no completo nivel
                 player.rect.center = (player.rect.centerx, player.rect.centery + int(SCREEN_HEIGHT * 0.05))  # mueve abajo

        # comprobar si jugador murio por salud
        if player.health <= 0 and game_state == "playing": # si salud cero
            handle_player_death_logic() # maneja muerte

        # manejo feedback_timer para mensajes temporales
        if feedback_message and feedback_timer > 0:  # si hay mensaje temporal
            if pygame.time.get_ticks() - feedback_timer > FEEDBACK_DURATION:  # si paso tiempo
                feedback_message = ""  # limpia mensaje
                feedback_timer = 0  # reinicia temporizador


    #dibujado y renderizado
    screen.fill(BLUE_LIGHT)  # fondo azul claro
    if game_state == "menu":  # estado menu
        draw_text(screen, "las aventuras de tralalero tralala", font_large, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)  # titulo
        button_width = int(SCREEN_WIDTH * 0.3)  # ancho boton
        button_height = int(SCREEN_HEIGHT * 0.1)  # alto boton
        sum_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 2.2, button_width, button_height), "sumas", font_button, BUTTON_COLOR, HOVER_COLOR)  # boton suma
        subtract_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 1, button_width, button_height), "restas", font_button, BUTTON_COLOR, HOVER_COLOR)  # boton resta
        multiply_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 0.2, button_width, button_height), "multiplicacion", font_button, BUTTON_COLOR, HOVER_COLOR)  # boton multiplicacion
        divide_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 1.4, button_width, button_height), "divisiones", font_button, BUTTON_COLOR, HOVER_COLOR)  # boton division
        controls_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 2.6, button_width, button_height), "controles", font_button, YELLOW_LIGHT, (255, 255, 200))  # boton controles
        exit_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 3.8, button_width, button_height), "salir", font_button, RED, (255, 100, 100))  # boton salir
    elif game_state in ["playing", "feedback", "level_complete", "show_answer_popup"]: # dibuja juego de fondo
        # dibuja area ui superior
        pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, UI_BAR_HEIGHT))  # fondo blanco
        # muestra operacion actual
        draw_text(screen, current_operation, font_operation, BLACK, SCREEN_WIDTH // 2, UI_BAR_HEIGHT // 2)  # texto operacion
        # muestra vidas checkpoint izquierda
        draw_text(screen, f"vidas {player_checkpoint_lives}", font_lives, BLACK, int(SCREEN_WIDTH * 0.1), UI_BAR_HEIGHT // 2)  # texto vidas
        # muestra nivel izquierda
        draw_text(screen, f"nivel {level}", font_lives, BLACK, int(SCREEN_WIDTH * 0.25), UI_BAR_HEIGHT // 2)  # texto nivel
        # muestra salud jugador derecha
        draw_text(screen, f"salud {player.health}", font_health, BLACK, SCREEN_WIDTH - int(SCREEN_WIDTH * 0.25), UI_BAR_HEIGHT // 2)  # texto salud
        # boton volver al menu
        menu_btn_rect = pygame.Rect(SCREEN_WIDTH - int(SCREEN_WIDTH * 0.15) - 20, 10, int(SCREEN_WIDTH * 0.15), UI_BAR_HEIGHT - 20)  # rect boton
        draw_button(screen, menu_btn_rect, "menu", font_button, BUTTON_COLOR, HOVER_COLOR)  # dibuja boton

        # dibuja todos los sprites
        all_sprites.draw(screen)  # dibuja grupo
        player.draw_health_bar(screen) # dibuja barra vida jugador

        # dibuja barras vida enemigos
        for enemy in enemies:  # por cada enemigo
            enemy.draw_health_bar(screen)  # dibuja barra
        # si jugador ataca dibuja indicador visual
        if player.is_attacking and pygame.time.get_ticks() - player.attack_anim_start_time < PLAYER_ATTACK_ANIM_DURATION:  # si atacando
            attack_indicator_rect = pygame.Rect(0, 0, player.rect.width + 20, player.rect.height + 20)  # rect indicador
            attack_indicator_rect.center = player.rect.center  # centra
            pygame.draw.circle(screen, PLAYER_ATTACK_COLOR, attack_indicator_rect.center, attack_indicator_rect.width // 2, 3)  # dibuja circulo
        # dibuja animacion ataque enemigos
        for enemy in enemies:  # por cada enemigo
            if enemy.is_attacking_anim and pygame.time.get_ticks() - enemy.attack_anim_start_time < ENEMY_ATTACK_ANIM_DURATION:  # si atacando
                enemy_attack_rect = enemy.rect.inflate(10, 10) # agranda rect
                pygame.draw.rect(screen, ENEMY_ATTACK_COLOR, enemy_attack_rect, 2) # dibuja borde rojo

        # muestra mensaje feedback
        if feedback_message and game_state != "show_answer_popup" and game_state != "level_complete": # no mostrar en popup o level_complete
            if feedback_timer > 0: # mensaje temporal como checkpoint
                 draw_text(screen, feedback_message, font_feedback, feedback_color, SCREEN_WIDTH // 2, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.07))  # dibuja texto
            elif game_state == "feedback": # otros feedbacks
                 draw_text(screen, feedback_message, font_feedback, feedback_color, SCREEN_WIDTH // 2, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.07))  # dibuja texto


        if game_state == "level_complete":  # nivel completado
            # animacion victoria gif
            if win_gif_frames:  # si hay frames
                current_time = pygame.time.get_ticks()  # tiempo actual
                if current_time - last_win_frame_time > GIF_FRAME_DURATION:  # si paso tiempo frame
                    win_frame_index = (win_frame_index + 1) % len(win_gif_frames)  # siguiente frame
                    last_win_frame_time = current_time  # actualiza tiempo
                current_win_frame = win_gif_frames[win_frame_index]  # frame actual
                image_rect = current_win_frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - int(SCREEN_HEIGHT * 0.1)))  # rect imagen
                screen.blit(current_win_frame, image_rect)  # dibuja frame
            draw_text(screen, "nivel completado", font_large, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.1))  # mensaje
            draw_text(screen, "haz clic para el siguiente nivel", font_feedback, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.2))  # instruccion
            # muestra mensaje checkpoint si fue guardado
            if feedback_message and "checkpoint" in feedback_message: # si hay mensaje checkpoint
                draw_text(screen, feedback_message, font_feedback, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.28))  # dibuja texto


        # muestra contador objetos abajo derecha
        draw_text(screen, f"objetos {player.collected_objects}", font_counter, BLACK, SCREEN_WIDTH - int(SCREEN_WIDTH * 0.1), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.05))  # texto contador

        # dibuja ventana emergente show_answer_popup
        if game_state == "show_answer_popup":  # estado popup respuesta
            # crea superficie semi-transparente fondo
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  # superficie transparente
            overlay.fill((0, 0, 0, 180)) # negro opaco
            screen.blit(overlay, (0, 0))  # dibuja overlay
            # dimensiones ventana
            popup_width_show = int(SCREEN_WIDTH * 0.6) # ancho popup
            popup_height_show = int(SCREEN_HEIGHT * 0.5) # alto popup
            popup_x_show = SCREEN_WIDTH // 2 - popup_width_show // 2 # pos x popup
            popup_y_show = SCREEN_HEIGHT // 2 - popup_height_show // 2 # pos y popup
            popup_rect = pygame.Rect(popup_x_show, popup_y_show, popup_width_show, popup_height_show)  # rect popup
            pygame.draw.rect(screen, WHITE, popup_rect, border_radius=15)  # fondo blanco
            pygame.draw.rect(screen, BLACK, popup_rect, 5, border_radius=15) # borde negro
            # area mensaje principal
            message_area_rect = pygame.Rect(popup_x_show + 20, popup_y_show + 20, popup_width_show - 40, popup_height_show * 0.4)  # rect mensaje
            draw_wrapped_text(screen, popup_message, font_medium, BLACK, message_area_rect)  # texto ajustado
            # respuesta correcta
            draw_text(screen, str(popup_correct_answer), font_large, GREEN, SCREEN_WIDTH // 2, popup_y_show + int(popup_height_show * 0.65))  # texto respuesta
            # boton cerrar
            popup_button_width = int(SCREEN_WIDTH * 0.15)  # ancho boton
            popup_button_height = int(SCREEN_HEIGHT * 0.07)  # alto boton
            popup_button_rect = pygame.Rect(  # rect boton
                SCREEN_WIDTH // 2 - popup_button_width // 2,  # centrado x
                popup_y_show + int(popup_height_show * 0.85), # debajo mensaje
                popup_button_width,
                popup_button_height
            )
            draw_button(screen, popup_button_rect, "cerrar", font_button, BUTTON_COLOR, HOVER_COLOR)  # dibuja boton
    elif game_state == "game_over":  # estado game over
        # animacion derrota gif
        if lose_gif_frames:  # si hay frames
            current_time = pygame.time.get_ticks()  # tiempo actual
            if current_time - last_lose_frame_time > GIF_FRAME_DURATION:  # si paso tiempo frame
                lose_frame_index = (lose_frame_index + 1) % len(lose_gif_frames)  # siguiente frame
                last_lose_frame_time = current_time  # actualiza tiempo
            current_lose_frame = lose_gif_frames[lose_frame_index]  # frame actual
            image_rect = current_lose_frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - int(SCREEN_HEIGHT * 0.15)))  # rect imagen
            screen.blit(current_lose_frame, image_rect)  # dibuja frame
        draw_text(screen, "game over", font_large, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.05))  # titulo
        draw_text(screen, f"alcanzaste el nivel {level}", font_medium, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.15)) # nivel alcanzado
        # botones game over
        game_over_continue_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.25), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08)) # boton continuar
        draw_button(screen, game_over_continue_btn_rect, "continuar", font_button, BUTTON_COLOR, HOVER_COLOR)  # dibuja el boton
    elif game_state == "controls_info":  # estado de controles
        # dibuja popup controles
        controls_button_rect = draw_controls_popup(screen)  # dibuja popup y obtiene rect boton
    pygame.display.flip()  # actualiza pantalla
    clock.tick(60)  # se pone para que sean 60 fps
pygame.quit()  # cierra pygame