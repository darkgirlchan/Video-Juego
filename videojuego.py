import pygame
import random
import math

# 1. Inicialización de Pygame
pygame.init()

# --- Configuración General ---
# Obtener la resolución actual de la pantalla para el modo de pantalla completa
INFO = pygame.display.Info()
SCREEN_WIDTH = INFO.current_w
SCREEN_HEIGHT = INFO.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN) # ¡Pantalla completa!
pygame.display.set_caption("El Recolector Numérico")

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

# --- Sonidos (Asegúrate de que los archivos .wav existan en la misma carpeta) ---
try:
    sound_collect = pygame.mixer.Sound("collect.wav") # Sonido al recoger
    sound_correct = pygame.mixer.Sound("correct.wav") # Sonido al entrar en meta correcta
    sound_incorrect = pygame.mixer.Sound("incorrect.wav") # Sonido al fallar en meta
    sound_hit_deadly = pygame.mixer.Sound("hit_deadly.wav") # Sonido al chocar con obstáculo mortal (¡Necesitarás este archivo!)
    sound_enemy_hit = pygame.mixer.Sound("enemy_hit.wav") # Sonido al golpear a un enemigo
    sound_player_hit = pygame.mixer.Sound("player_hit.wav") # Sonido cuando el jugador es golpeado
    sound_enemy_death = pygame.mixer.Sound("enemy_death.wav") # Sonido de muerte de enemigo
except pygame.error as e:
    print(f"Advertencia: No se pudieron cargar los sonidos: {e}. Asegúrate de que existan los archivos 'collect.wav', 'correct.wav', 'incorrect.wav', 'hit_deadly.wav', 'enemy_hit.wav', 'player_hit.wav', 'enemy_death.wav' en la misma carpeta.")
    sound_collect = None
    sound_correct = None
    sound_incorrect = None
    sound_hit_deadly = None
    sound_enemy_hit = None
    sound_player_hit = None
    sound_enemy_death = None

# --- Constantes de Juego ---
PLAYER_INITIAL_HEALTH = 100
ENEMY_ATTACK_DAMAGE = 15
DEADLY_OBSTACLE_DAMAGE = 25
PLAYER_ATTACK_COOLDOWN = 5000 # milisegundos
PLAYER_ATTACK_DAMAGE = 20 # Daño que hace el jugador al enemigo
PLAYER_ATTACK_ANIM_DURATION = 100 # Duración de la animación de ataque del jugador
ENEMY_ATTACK_ANIM_DURATION = 100 # Duración de la animación de ataque del enemigo
UI_BAR_HEIGHT = int(SCREEN_HEIGHT * 0.1) # Altura de la barra de UI superior

# --- Clases de Juego ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Cargar imagen del jugador
        self.image = pygame.image.load("player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.1))) # Tamaño ajustado
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.collected_objects = 0
        self.prev_rect = self.rect.copy() # Para revertir posición en colisiones con obstáculos
        self.health = PLAYER_INITIAL_HEALTH
        self.is_attacking = False
        self.last_attack_time = 0
        self.attack_anim_start_time = 0 # Nuevo para la animación

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

    def reset_objects(self):
        self.collected_objects = 0

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        if sound_player_hit:
            sound_player_hit.play()

    def reset_health(self):
        self.health = PLAYER_INITIAL_HEALTH

class CollectibleObject(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Cargar imagen del objeto
        self.image = pygame.image.load("star.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.03), int(SCREEN_HEIGHT * 0.04))) # Tamaño ajustado
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y, value):
        super().__init__()
        self.value = value
        # Cargar imagen de la meta
        self.image = pygame.image.load("goal.png").convert_alpha()
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
            self.image.fill(SOLID_OBSTACLE_COLOR) # Color marrón para un obstáculo sólido
            # O cargar imagen: self.image = pygame.image.load("rock.png").convert_alpha(); self.image = pygame.transform.scale(self.image, (width, height))
        elif self.type == "deadly":
            self.image.fill(DEADLY_OBSTACLE_COLOR) # Color rojo para un obstáculo mortal
            # O cargar imagen: self.image = pygame.image.load("lava.png").convert_alpha(); self.image = pygame.transform.scale(self.image, (width, height))
        
        self.rect = self.image.get_rect(center=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("enemy.png").convert_alpha() # Cargar imagen del enemigo
        self.image = pygame.transform.scale(self.image, (int(SCREEN_WIDTH * 0.07), int(SCREEN_HEIGHT * 0.09))) # Tamaño del enemigo
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 4 
        self.health = 100
        self.attack_cooldown = 4000 # Cooldown para atacar al jugador (milisegundos)
        self.last_attack_time = 0
        self.damage_taken_this_attack = False # Nuevo: Para evitar daño múltiple por un solo ataque de jugador
        self.is_aggressive = False # Nuevo: el enemigo es pasivo al inicio
        self.is_attacking_anim = False # Nuevo: para la animación de ataque del enemigo
        self.attack_anim_start_time = 0 # Nuevo: para el temporizador de la animación

    def update(self, player_rect):
        # Resetear estado de ataque de la animación
        if pygame.time.get_ticks() - self.attack_anim_start_time > ENEMY_ATTACK_ANIM_DURATION:
            self.is_attacking_anim = False

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

# --- Variables Globales del Juego ---
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100) # Posición inicial del jugador
all_sprites = pygame.sprite.Group()
collectible_objects = pygame.sprite.Group()
goals = pygame.sprite.Group()
obstacles = pygame.sprite.Group() # Nuevo grupo para obstáculos
enemies = pygame.sprite.Group() # Nuevo grupo para enemigos

all_sprites.add(player)

current_operation = ""
correct_answer = 0
feedback_message = ""
feedback_color = BLACK
feedback_timer = 0
FEEDBACK_DURATION = 1500 # milisegundos para mostrar el feedback

game_state = "menu" # Posibles estados: "menu", "playing", "feedback", "level_complete", "game_over"
level = 1
operation_type = "suma" # Tipo de operación actual
max_number_in_op = 10 # Dificultad actual (rango máximo de números en la operación)
max_multiplier_divisor = 5 # Dificultad actual para multiplicación/división

# Vidas del jugador para el nivel actual (se reinicia en cada nivel)
player_current_level_lives = 1 

# Vidas que determinan los "juegos" antes de volver al checkpoint
player_checkpoint_lives = 3 

# Variables de Checkpoint
checkpoint_level = 1 # Nivel desde el que se reiniciará
checkpoint_op_type = "suma" # Tipo de operación del checkpoint
checkpoint_max_num = 10 # Dificultad del checkpoint
checkpoint_max_mult_div = 5 # Dificultad de multiplicador/divisor del checkpoint

# --- Funciones Auxiliares ---

def draw_text(surface, text, font, color, x, y, center=True):
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(x=x, y=y)
    surface.blit(text_surface, text_rect)

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
    num1 = random.randint(1, max_num)
    num2 = random.randint(1, max_num)

    if op_type == "suma":
        correct_answer = num1 + num2
        current_operation = f"{num1} + {num2} = ?"
    elif op_type == "resta":
        if num1 < num2: # Asegurarse de que el resultado no sea negativo
            num1, num2 = num2, num1
        correct_answer = num1 - num2
        current_operation = f"{num1} - {num2} = ?"
    elif op_type == "multiplicacion":
        # Usar max_mult_div para los números en la multiplicación
        num1 = random.randint(1, max_mult_div)
        num2 = random.randint(1, max_mult_div)
        correct_answer = num1 * num2
        current_operation = f"{num1} x {num2} = ?"
    elif op_type == "division":
        # Asegurarse de que la división sea exacta y el cociente sea manejable
        # Usar max_mult_div para el divisor y el cociente para controlar la dificultad
        correct_answer_temp = random.randint(1, max_mult_div) 
        num2_temp = random.randint(1, max_mult_div) 
        
        # Evitar divisiones por cero o con cero
        if correct_answer_temp == 0 or num2_temp == 0:
            return generate_operation(op_type, max_num, max_mult_div) 
            
        num1 = correct_answer_temp * num2_temp
        correct_answer = correct_answer_temp
        current_operation = f"{num1} / {num2_temp} = ?"
    
    # Generar respuestas incorrectas "cercanas"
    incorrect_answers = set()
    while len(incorrect_answers) < 2:
        offset = random.choice([-3, -2, -1, 1, 2, 3]) # Pequeños offsets
        incorrect_ans = correct_answer + offset
        # Asegurarse de que las incorrectas no sean la correcta y sean positivas
        if incorrect_ans > 0 and incorrect_ans != correct_answer and incorrect_ans not in incorrect_answers:
            incorrect_answers.add(incorrect_ans)
    return list(incorrect_answers) # Retorna las incorrectas para usarlas en generar metas

def handle_player_death_logic():
    global player_checkpoint_lives, game_state, feedback_message, feedback_color, feedback_timer
    
    if player.health <= 0: # Si la salud llega a 0, se pierde una vida de checkpoint
        player_checkpoint_lives -= 1 
        if sound_hit_deadly: # Reproducir sonido de daño mortal si no es por una meta
             sound_hit_deadly.play()
    else: # Si el jugador muere por fallar una meta (vidas del nivel a 0)
        player_checkpoint_lives -= 1 
        if sound_incorrect: # Reproducir sonido de fallo si es por una meta
             sound_incorrect.play()

    if player_checkpoint_lives <= 0:
        game_state = "game_over"
        feedback_message = "¡Perdiste todas tus vidas!"
        feedback_color = RED
        feedback_timer = pygame.time.get_ticks()
    else: # Si aún quedan vidas de checkpoint, reinicia el nivel actual
        # Reiniciar el nivel con 1 vida de nivel y salud completa
        generate_level(operation_type, max_number_in_op, max_multiplier_divisor) 
        player.reset_health() # Restaurar la salud del jugador
        feedback_message = f"¡Cuidado! Vidas de checkpoint restantes: {player_checkpoint_lives}"
        feedback_color = RED
        feedback_timer = pygame.time.get_ticks()

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
    
    # Área inicial del jugador + un margen para que no aparezcan pegados
    player_spawn_area = player.rect.inflate(player.rect.width * 1.5, player.rect.height * 1.5) 
    forbidden_zones_for_obstacles.append(player_spawn_area) 

    # También evitamos la zona de la UI superior
    forbidden_zones_for_obstacles.append(pygame.Rect(0, 0, SCREEN_WIDTH, UI_BAR_HEIGHT + 20)) 

    # Definir cuántos serán mortales (porcentaje o número fijo)
    num_deadly_obstacles = random.randint(1, 3) # Entre 1 y 3 obstáculos mortales

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
        # else:
            # print(f"Advertencia: No se pudo encontrar una posición válida para un obstáculo {obs_type}.")

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
    
    # Combina las zonas de exclusión de metas, obstáculos y enemigos para los objetos coleccionables
    all_exclusion_zones_for_objects = list(goal_exclusion_zones)
    for obs in obstacles:
        all_exclusion_zones_for_objects.append(obs.rect.inflate(int(SCREEN_WIDTH * 0.04), int(SCREEN_HEIGHT * 0.04)))
    for enemy in enemies:
        all_exclusion_zones_for_objects.append(enemy.rect.inflate(int(SCREEN_WIDTH * 0.06), int(SCREEN_HEIGHT * 0.06))) # Evitar que objetos aparezcan justo sobre enemigos

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
            # Verificar solapamiento con zonas de exclusión (metas, obstáculos y enemigos)
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
        # else:
            # print("Advertencia: No se pudo encontrar una posición válida para un objeto.")

    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.15)) # Resetear posición del jugador

def reset_game_to_checkpoint():
    global level, operation_type, max_number_in_op, max_multiplier_divisor, player_checkpoint_lives, checkpoint_level, checkpoint_op_type, checkpoint_max_num, checkpoint_max_mult_div
    
    level = checkpoint_level # Vuelve al nivel del checkpoint
    operation_type = checkpoint_op_type # Vuelve al tipo de operación del checkpoint
    max_number_in_op = checkpoint_max_num # Vuelve a la dificultad del checkpoint
    max_multiplier_divisor = checkpoint_max_mult_div # Vuelve a la dificultad de mult/div del checkpoint
    player_checkpoint_lives = 3 # ¡Siempre 3 vidas al reiniciar desde un checkpoint!
    player.reset_health() # También restaurar la salud del jugador

    generate_level(operation_type, max_number_in_op, max_multiplier_divisor) # Genera el nivel desde el checkpoint

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
                
                sum_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 2.5, button_width, button_height)
                subtract_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_height // 2, SCREEN_HEIGHT // 2 - button_height * 1.25, button_width, button_height)
                multiply_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2, button_width, button_height)
                divide_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 1.25, button_width, button_height)
                exit_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 2.5, button_width, button_height) # Nuevo botón Salir


                if sum_btn_rect.collidepoint(event.pos):
                    operation_type = "suma"
                    max_number_in_op = 10 # Inicio para sumas/restas
                    max_multiplier_divisor = 5 # No se usa en sumas/restas, pero se inicializa
                    checkpoint_op_type = operation_type
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    game_state = "playing"
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)
                elif subtract_btn_rect.collidepoint(event.pos):
                    operation_type = "resta"
                    max_number_in_op = 10
                    max_multiplier_divisor = 5
                    checkpoint_op_type = operation_type
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    game_state = "playing"
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)
                elif multiply_btn_rect.collidepoint(event.pos):
                    operation_type = "multiplicacion"
                    max_number_in_op = 10 # Para el tamaño del resultado
                    max_multiplier_divisor = 5 # Inicio para multiplicaciones
                    checkpoint_op_type = operation_type
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    game_state = "playing"
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)
                elif divide_btn_rect.collidepoint(event.pos):
                    operation_type = "division"
                    max_number_in_op = 20 # Para el tamaño del resultado (dividendo)
                    max_multiplier_divisor = 5 # Inicio para divisiones (divisor y cociente)
                    checkpoint_op_type = operation_type
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    game_state = "playing"
                    generate_level(operation_type, max_number_in_op, max_multiplier_divisor)
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
                # Al hacer clic después de completar un nivel, pasar al siguiente
                level += 1
                
                # --- Lógica de progresión de dificultad ---
                # Progresión para números de suma/resta
                if operation_type in ["suma", "resta"]:
                    if level <= 5: 
                        max_number_in_op = 10
                    elif level <= 10: 
                        max_number_in_op = 20
                    elif level <= 15:
                        max_number_in_op = 30
                    else:
                        max_number_in_op = 50 # Y así sucesivamente
                
                # Progresión para multiplicadores/divisores en multiplicación/división
                elif operation_type in ["multiplicacion", "division"]:
                    if level <= 5:
                        max_multiplier_divisor = 5
                    elif level <= 10:
                        max_multiplier_divisor = 10
                    elif level <= 15:
                        max_multiplier_divisor = 12
                    else:
                        max_multiplier_divisor = 15 # Y así sucesivamente
                    # Para divisiones, el número a dividir también puede aumentar un poco más
                    if operation_type == "division":
                        max_number_in_op = max_multiplier_divisor * 5 # Aumenta el dividendo
                
                # Tipo de operación cambia cada 5 niveles
                if level > 1 and (level - 1) % 5 == 0:
                    operation_type = random.choice(["suma", "resta", "multiplicacion", "division"])

                # --- Lógica de Checkpoint ---
                # Si el nivel que acaba de completar es un múltiplo de 10, guardar checkpoint
                if (level - 1) % 10 == 0 and level > 1:
                    checkpoint_level = level
                    checkpoint_op_type = operation_type
                    checkpoint_max_num = max_number_in_op
                    checkpoint_max_mult_div = max_multiplier_divisor
                    player_checkpoint_lives = 3 # Se recargan las 3 vidas de checkpoint
                    
                player.reset_health() # Restaurar salud del jugador al iniciar un nuevo nivel
                game_state = "playing"
                generate_level(operation_type, max_number_in_op, max_multiplier_divisor)

            elif game_state == "game_over":
                # Si el jugador hace clic en Game Over, reinicia desde el último checkpoint
                # O si hace clic en el botón de cambiar operador
                game_over_continue_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.15), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08))
                game_over_menu_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.25), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08))

                if game_over_continue_btn_rect.collidepoint(event.pos):
                    game_state = "playing"
                    reset_game_to_checkpoint()
                elif game_over_menu_btn_rect.collidepoint(event.pos):
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
                if sound_hit_deadly:
                    sound_hit_deadly.play()
                player.revert_position() # Empuja al jugador un poco para evitar daño continuo
                if player.health <= 0:
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
            elif not player.is_attacking: # Si el jugador NO está atacando y el enemigo es agresivo, el enemigo ataca al jugador
                # Aquí, la variable `damage_taken_this_attack` del enemigo debe ser False
                # para que el enemigo pueda volver a ser dañado en un nuevo ataque del jugador.
                # Ya la reseteamos al inicio del `enemy.update()`.
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
            if player.collected_objects == correct_answer:
                if collided_goal.value == correct_answer:
                    feedback_message = "¡Correcto! ¡Siguiente Nivel!"
                    feedback_color = GREEN
                    if sound_correct: sound_correct.play()
                    game_state = "level_complete"
                else: # Cantidad correcta pero meta incorrecta
                    feedback_message = "Cantidad correcta, pero meta incorrecta. ¡Intenta de nuevo!"
                    feedback_color = RED
                    if sound_incorrect: sound_incorrect.play()
                    feedback_timer = pygame.time.get_ticks()
                    
                    player_current_level_lives -= 1 # Resta una vida por error
                    if player_current_level_lives <= 0:
                        handle_player_death_logic() # Llama a la función de muerte si se agotan vidas del nivel
            else: # Cantidad de objetos incorrecta
                feedback_message = f"Necesitas {correct_answer} objetos. Tienes {player.collected_objects}."
                feedback_color = RED
                if sound_incorrect: sound_incorrect.play()
                feedback_timer = pygame.time.get_ticks()
                
                player_current_level_lives -= 1 # Resta una vida por error
                if player_current_level_lives <= 0:
                    handle_player_death_logic() # Llama a la función de muerte si se agotan vidas del nivel
            
            # Después de la interacción con la meta, mover al jugador un poco para evitar múltiples colisiones instantáneas
            player.rect.center = (player.rect.centerx, player.rect.centery + int(SCREEN_HEIGHT * 0.05))
            # No break, para que se pueda seguir moviendo aunque colisione con una meta y falle

        # Lógica para ocultar el mensaje de feedback
        if feedback_timer != 0 and pygame.time.get_ticks() - feedback_timer > FEEDBACK_DURATION:
            feedback_message = ""
            feedback_timer = 0
        
        # Comprobar si el jugador ha muerto por salud
        if player.health <= 0 and game_state == "playing": # Asegurarse de que no se llama varias veces
            handle_player_death_logic()


    # --- Dibujado / Renderizado ---
    screen.fill(BLUE_LIGHT)

    if game_state == "menu":
        draw_text(screen, "El Recolector Numérico", font_large, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        
        button_width = int(SCREEN_WIDTH * 0.3)
        button_height = int(SCREEN_HEIGHT * 0.1)

        sum_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 2.5, button_width, button_height), "Sumas", font_button, BUTTON_COLOR, HOVER_COLOR)
        subtract_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height * 1.25, button_width, button_height), "Restas", font_button, BUTTON_COLOR, HOVER_COLOR)
        multiply_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2, button_width, button_height), "Multiplicación", font_button, BUTTON_COLOR, HOVER_COLOR)
        divide_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 1.25, button_width, button_height), "Divisiones", font_button, BUTTON_COLOR, HOVER_COLOR)
        exit_btn_rect = draw_button(screen, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height * 2.5, button_width, button_height), "Salir", font_button, RED, (255, 100, 100))


    elif game_state == "playing" or game_state == "feedback" or game_state == "level_complete":
        # Dibujar área de UI superior
        pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, UI_BAR_HEIGHT))
        
        # Mostrar la operación actual - Centrado
        draw_text(screen, current_operation, font_operation, BLACK, SCREEN_WIDTH // 2, UI_BAR_HEIGHT // 2)
        
        # Mostrar contador de objetos (derecha)
        draw_text(screen, f"Objetos: {player.collected_objects}", font_counter, BLACK, SCREEN_WIDTH - int(SCREEN_WIDTH * 0.1), UI_BAR_HEIGHT // 2)
        
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

        # Mostrar mensaje de feedback
        if feedback_message:
            draw_text(screen, feedback_message, font_feedback, feedback_color, SCREEN_WIDTH // 2, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.07))
            
        if game_state == "level_complete":
             draw_text(screen, "¡Haz clic para el siguiente nivel!", font_feedback, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.15))

    elif game_state == "game_over":
        draw_text(screen, "¡GAME OVER!", font_large, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - int(SCREEN_HEIGHT * 0.1))
        draw_text(screen, f"Alcanzaste el Nivel: {level}", font_medium, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.03))
        # draw_text(screen, f"Vidas de Checkpoint Restantes: {player_checkpoint_lives}", font_medium, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.06)) # Esta línea es redundante si siempre se reinicia con 3 vidas
        
        # Botones de Game Over
        game_over_continue_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.15), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08))
        draw_button(screen, game_over_continue_btn_rect, "Continuar", font_button, BUTTON_COLOR, HOVER_COLOR)
        
        game_over_menu_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - int(SCREEN_WIDTH * 0.2) // 2, SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.25), int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.08))
        draw_button(screen, game_over_menu_btn_rect, "Cambiar Operador", font_button, BUTTON_COLOR, HOVER_COLOR)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()