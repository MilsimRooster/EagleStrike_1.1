import pygame
import random
import os
import datetime
import sys
import math
import webbrowser

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    full_path = os.path.join(base_path, relative_path)
    log(f"Loading resource: {full_path}")
    return full_path

log_file = os.path.join(os.path.abspath("."), "eagle_strike_log.txt")
def log(message):
    with open(log_file, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

log("Starting Eagle Strike...")

try:
    pygame.init()
except Exception as e:
    log(f"Pygame initialization failed: {e}")
    raise

try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.set_num_channels(8)
except pygame.error as e:
    log(f"Audio initialization failed: {e}—running without sound")
    pygame.mixer.quit()

try:
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()
    log(f"Detected {joystick_count} joystick(s)")
except Exception as e:
    log(f"Joystick initialization failed: {e}")

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eagle Strike v1.1")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (150, 150, 150)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_BLUE = (0, 255, 255)
NEON_GREEN = (57, 255, 20)

HIGH_SCORE_FILE = resource_path("highscore.txt")

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError) as e:
        log(f"High score load failed: {e}—defaulting to 0")
        return 0

def save_high_score(score):
    try:
        current_high_score = load_high_score()
        if score > current_high_score:
            with open(HIGH_SCORE_FILE, "w") as f:
                f.write(str(score))
            log(f"New high score saved: {score}")
            return score
        return current_high_score
    except Exception as e:
        log(f"High score save failed: {e}")
        return load_high_score()

def load_sprite_frames(filename_prefix, frame_count, size_x, size_y, fallback_color):
    frames = []
    for i in range(frame_count):
        filename = f"{filename_prefix}{i+1}.png"
        try:
            sprite = pygame.image.load(resource_path(filename)).convert_alpha()
            sprite = pygame.transform.scale(sprite, (size_x, size_y))
            frames.append(sprite)
        except Exception as e:
            log(f"Failed to load {filename}: {e}—using fallback")
            surf = pygame.Surface((size_x, size_y), pygame.SRCALPHA)
            surf.fill(fallback_color)
            frames.append(surf)
    if not frames:
        log(f"No frames loaded for {filename_prefix}—using single fallback")
        surf = pygame.Surface((size_x, size_y), pygame.SRCALPHA)
        surf.fill(fallback_color)
        frames.append(surf)
    return frames

def load_sprite(filename, size_x, size_y, fallback_color):
    try:
        sprite = pygame.image.load(resource_path(filename)).convert_alpha()
        return pygame.transform.scale(sprite, (size_x, size_y))
    except Exception as e:
        log(f"Failed to load {filename}: {e}—using fallback")
        surf = pygame.Surface((size_x, size_y), pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf

def load_sound(filename):
    try:
        sound = pygame.mixer.Sound(resource_path(filename))
        return sound
    except Exception as e:
        log(f"Failed to load sound {filename}: {e}")
        return None

def load_music(filename):
    try:
        pygame.mixer.music.load(resource_path(filename))
        return True
    except Exception as e:
        log(f"Failed to load music {filename}: {e}")
        return False

player_size = 40
alien_size = 30
boss_size = 100
power_up_size = 20
battle_buddy_size = 30
player_frames = load_sprite_frames("dropship", 2, player_size, player_size, WHITE)
bug_frames = load_sprite_frames("terminid", 2, alien_size, alien_size, WHITE)
bot_frames = load_sprite_frames("automaton", 2, alien_size, alien_size, WHITE)
squid_frames = load_sprite_frames("illuminate", 2, alien_size, alien_size, WHITE)
hunter_frames = load_sprite_frames("hunter", 2, alien_size, alien_size, RED)
boss1_frames = load_sprite_frames("boss1", 2, boss_size, boss_size, RED)
boss2_frames = load_sprite_frames("boss2", 2, boss_size, boss_size, PURPLE)
boss3_frames = load_sprite_frames("boss3", 2, boss_size, boss_size, ORANGE)
boss_types = [boss1_frames, boss2_frames, boss3_frames]
power_up_sprites = {
    "rate": load_sprite("rate_of_fire.png", power_up_size, power_up_size, GREEN),
    "reinforce": load_sprite("reinforce.png", power_up_size, power_up_size, WHITE),
    "diver_pod": load_sprite("diver_pod.png", power_up_size, power_up_size, WHITE),
    "resupply": load_sprite("resupply.png", power_up_size, power_up_size, YELLOW),
    "hellbomb": load_sprite("hellbomb.png", power_up_size, power_up_size, ORANGE),
    "mg94": load_sprite("mg94.png", power_up_size, power_up_size, GREEN),
    "eat17": load_sprite("eat17.png", power_up_size, power_up_size, ORANGE),
    "shield": load_sprite("shield.png", power_up_size, power_up_size, BLUE),
    "trishot": load_sprite("trishot.png", power_up_size, power_up_size, RED),
    "quad": load_sprite("quadshot.png", power_up_size, power_up_size, PURPLE),
    "burst": load_sprite("burst.png", power_up_size, power_up_size, CYAN),
    "eagle_sweat": load_sprite("eagle_sweat.png", power_up_size, power_up_size, YELLOW),
    "battle_buddy": load_sprite("battle_buddy.png", power_up_size, power_up_size, NEON_GREEN)
}
start_screen_sprite = load_sprite("start_screen.png", WIDTH, HEIGHT, BLACK)
battle_buddy_sprite = load_sprite("battle_buddy.png", battle_buddy_size, battle_buddy_size, NEON_GREEN)

intro_frames = [load_sprite(f"intro{i}.png", WIDTH, HEIGHT, BLACK) for i in range(1, 9)]
intro_music = load_sound("intro_music.wav")
if intro_music: intro_music.set_volume(0.2)

shoot_sound = load_sound("shoot.wav")
if shoot_sound: shoot_sound.set_volume(0.1)
boom_sound = load_sound("boom.wav")
if boom_sound: boom_sound.set_volume(0.15)
hit_sound = load_sound("hit.wav")
if hit_sound: hit_sound.set_volume(0.08)
ship_hit_sound = load_sound("ship_hit.wav")
if ship_hit_sound: ship_hit_sound.set_volume(0.1)
hunter_thrust_sound = load_sound("thrust.wav")
if hunter_thrust_sound: hunter_thrust_sound.set_volume(0.05)
level_up_sound = load_sound("level_up.wav")
if level_up_sound: level_up_sound.set_volume(0.15)
boss_level_sound = load_sound("boss_intro.wav")
if boss_level_sound: boss_level_sound.set_volume(0.2)
eagle_sweat_sound = load_sound("eagle_sweat_trigger.wav")
if eagle_sweat_sound: eagle_sweat_sound.set_volume(0.18)
battle_buddy_sound = load_sound("battle_buddy.wav")
if battle_buddy_sound: battle_buddy_sound.set_volume(0.18)
power_up_sounds = [load_sound(f"power_up{i}.wav") for i in range(1, 7)]
power_up_sounds = [s for s in power_up_sounds if s]
for s in power_up_sounds: s.set_volume(0.08)

MUSIC_TRACKS = [f"background_music{i}.wav" for i in range(1, 11)]
loaded_music = [track for track in MUSIC_TRACKS if load_music(track)]
music_enabled = bool(loaded_music)
current_track = None
master_volume = 0.2
high_score = load_high_score()
first_level_1_start = True

def play_music_for_level(level):
    global current_track
    if not music_enabled: return
    try:
        track_index = (level - 1) % len(loaded_music)
        new_track = loaded_music[track_index]
        if new_track != current_track:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(resource_path(new_track))
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(master_volume * 0.1)
            current_track = new_track
            log(f"Playing music: {new_track} for Level {level}")
    except Exception as e:
        log(f"Music play failed for Level {level}: {e}")

def update_volumes():
    try:
        for sound, vol in [(shoot_sound, 0.1), (boom_sound, 0.15), (hit_sound, 0.08), (ship_hit_sound, 0.1),
                           (hunter_thrust_sound, 0.05), (level_up_sound, 0.15), (boss_level_sound, 0.2),
                           (eagle_sweat_sound, 0.18), (battle_buddy_sound, 0.18)]:
            if sound: sound.set_volume(master_volume * vol)
        for sound in power_up_sounds: sound.set_volume(master_volume * 0.08)
        if music_enabled: pygame.mixer.music.set_volume(master_volume * 0.1)
    except Exception as e:
        log(f"Volume update failed: {e}")

update_volumes()

player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - 100
player_dx = 0
player_dy = 0
player_angle = 90  # Start facing up
player_speed = 5
player_frame = 0
player_frame_timer = 0
player_frame_speed = 10
player_health = 500
PLAYER_MAX_HEALTH = 500
aliens = []
shots = []
enemy_shots = []
power_ups = []
battle_buddy_shots = []
alien_speed = 2
hunter_speed = 4
boss_speed_base = 2.0
spawn_timer = 0
spawn_interval = 15
shot_speed = -12
shot_length = 20
shot_width = 4
shot_cooldown = 15
shot_timer = 0
enemy_shot_speed = 5
enemy_shot_length = 15
enemy_shot_width = 3
enemy_shot_chance = 0.01
boss_shot_chance_base = 0.03
battle_buddy_active = False
battle_buddy_timer = 0
battle_buddy_x = 0
battle_buddy_y = 0
battle_buddy_shot_cooldown = 10
battle_buddy_shot_timer = 0
score = 0
level = 1
divers_rescued = 3
double_shot = False
double_shot_timer = 0
piercing_shot = False
piercing_shot_timer = 0
trishot = False
trishot_timer = 0
quad_shot = False
quad_shot_timer = 0
burst_mode = False
burst_timer = 0
shield_active = False
shield_timer = 0
eagle_sweat_active = False
eagle_sweat_timer = 0
paused = False
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 48)
stars = []
planet_surface = None
level_up_text = None
level_up_duration = 60
dual_blasts = False
base_level = 1
alien_frame_speed = 8
boss_frame_speed = 10
BASE_THRESHOLD = 5000
BOSS_HEALTH_BASE = 900
joystick = None

PLANET_TYPES = [
    {"name": "Desert", "ground_color": (194, 178, 128), "feature_color": (255, 204, 102), "features": "dunes"},
    {"name": "Forest", "ground_color": (34, 139, 34), "feature_color": (0, 100, 0), "features": "trees"},
    {"name": "Volcanic", "ground_color": (50, 50, 50), "feature_color": (255, 69, 0), "features": "lava"},
    {"name": "Icy", "ground_color": (173, 216, 230), "feature_color": (255, 255, 255), "features": "snow"},
    {"name": "Swamp", "ground_color": (85, 107, 47), "feature_color": (139, 69, 19), "features": "pools"},
    {"name": "Tundra", "ground_color": (200, 200, 220), "feature_color": (150, 150, 170), "features": "rocks"},
    {"name": "Jungle", "ground_color": (0, 128, 0), "feature_color": (0, 80, 0), "features": "trees"},
    {"name": "Canyon", "ground_color": (165, 42, 42), "feature_color": (139, 69, 19), "features": "cliffs"},
    {"name": "Ocean", "ground_color": (0, 105, 148), "feature_color": (0, 191, 255), "features": "waves"},
    {"name": "Savanna", "ground_color": (154, 205, 50), "feature_color": (139, 134, 78), "features": "grass"},
    {"name": "Crystal", "ground_color": (135, 206, 235), "feature_color": (0, 191, 255), "features": "crystals"},
    {"name": "Ash", "ground_color": (105, 105, 105), "feature_color": (169, 169, 169), "features": "debris"},
    {"name": "Mesa", "ground_color": (210, 105, 30), "feature_color": (255, 140, 0), "features": "plateaus"},
    {"name": "Bog", "ground_color": (47, 79, 79), "feature_color": (107, 142, 35), "features": "muck"},
    {"name": "Badlands", "ground_color": (139, 69, 19), "feature_color": (205, 133, 63), "features": "ridges"},
    {"name": "Coral", "ground_color": (255, 105, 180), "feature_color": (255, 20, 147), "features": "reefs"},
    {"name": "Plains", "ground_color": (124, 252, 0), "feature_color": (173, 255, 47), "features": "hills"},
    {"name": "Fungal", "ground_color": (153, 50, 204), "feature_color": (186, 85, 211), "features": "mushrooms"},
    {"name": "Salt", "ground_color": (245, 245, 220), "feature_color": (255, 250, 240), "features": "flats"},
    {"name": "Lunar", "ground_color": (112, 128, 144), "feature_color": (192, 192, 192), "features": "craters"}
]

class Star:
    def __init__(self, level):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, max(3, level))
        self.speed = random.uniform(0.5, 1.0 + level * 0.2)
        self.color = random.choice([WHITE, GRAY, YELLOW, ORANGE, BLUE, PURPLE, CYAN])

    def move(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        try:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        except Exception as e:
            log(f"Star draw failed: {e}")

class PlanetSurface:
    def __init__(self, level):
        self.offset_y = 0
        self.ground_layers = []
        self.features = []
        self.bases = []
        self.meteors = []
        self.nebulae = []
        self.meteor_timer = 0
        self.meteor_active = False
        self.level = level
        log(f"Initializing PlanetSurface for Level {self.level}")
        self.update_ground_layers()
        self.generate_features()
        self.generate_bases()
        self.generate_nebulae()
        log(f"PlanetSurface initialized for Level {self.level}: {len(self.ground_layers)} layers, {len(self.features)} features, {len(self.bases)} bases, {len(self.nebulae)} nebulae")

    def update_ground_layers(self):
        try:
            planet_type = (self.level - 1) % 20
            log(f"Updating ground layers for Level {self.level}, planet_type {planet_type}")
            self.ground_layers = []
            if planet_type < 5:  # Levels 1-5: Desert range
                self.ground_layers.append({"type": "earth", "color": (200, 100, 50), "height": HEIGHT * 3})  # Rusty orange
                log(f"Set rusty orange for Level {self.level}")
            elif planet_type < 10:  # Levels 6-10: Grass range
                self.ground_layers.append({"type": "earth", "color": (50, 150, 50), "height": HEIGHT * 3})  # Vibrant green
                log(f"Set vibrant green for Level {self.level}")
            elif planet_type < 15:  # Levels 11-15: Rocky range
                self.ground_layers.append({"type": "earth", "color": (80, 60, 60), "height": HEIGHT * 3})  # Dark reddish-brown
                log(f"Set dark reddish-brown for Level {self.level}")
            else:  # Levels 16-20: Mixed range
                self.ground_layers.append({"type": "earth", "color": (120, 80, 40), "height": HEIGHT * 3})  # Warm brown
                log(f"Set warm brown for Level {self.level}")
            log(f"Ground layers updated: {[(l['type'], l['color']) for l in self.ground_layers]}")
        except Exception as e:
            log(f"Ground layers update failed for Level {self.level}: {e}")
            self.ground_layers.append({"type": "earth", "color": (200, 100, 50), "height": HEIGHT * 3})  # Fallback

    def generate_features(self):
        try:
            for _ in range(50):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT * 4)
                feature_roll = random.random()
                if feature_roll < 0.6:
                    width = random.randint(20, 60)
                    height = random.randint(15, 40)
                    self.features.append({"type": "forest", "x": x, "y": y, "width": width, "height": height, "offset": random.randint(-3, 3)})
                elif feature_roll < 0.9:
                    width = random.randint(40, 80)
                    height = random.randint(10, 25)
                    self.features.append({"type": "river", "x": x, "y": y, "width": width, "height": height, "offset": random.randint(-3, 3)})
                else:
                    width = random.randint(20, 50)
                    height = random.randint(10, 30)
                    self.features.append({"type": "earth", "x": x, "y": y, "width": width, "height": height, "offset": random.randint(-3, 3)})
        except Exception as e:
            log(f"Feature generation failed: {e}")

    def generate_bases(self):
        try:
            for _ in range(5):
                x = random.randint(0, WIDTH - 25)
                y = random.randint(0, HEIGHT * 4)
                base_type = random.choice(["circle", "rect", "diamond"])
                size = random.randint(10, 20)
                self.bases.append({"type": base_type, "x": x, "y": y, "size": size, "offset": random.randint(-3, 3)})
        except Exception as e:
            log(f"Base generation failed: {e}")

    def generate_nebulae(self):
        try:
            self.nebulae = []
            for _ in range(3):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT * 2)
                base_width = random.randint(100, 200)  # Smaller nebulae
                base_height = random.randint(80, 150)
                speed = random.uniform(0.2, 0.5)
                nebula_surf = pygame.Surface((base_width, base_height), pygame.SRCALPHA)
                colors = [(ORANGE, 40), (NEON_PINK, 35), (NEON_BLUE, 30), (NEON_GREEN, 25)]  # Subtle opacity
                for _ in range(5):
                    oval_width = random.randint(20, 60)
                    oval_height = random.randint(20, 80)
                    offset_x = random.randint(-base_width // 4, base_width // 4)
                    offset_y = random.randint(-base_height // 4, base_height // 4)
                    angle = random.uniform(0, 360)
                    color = random.choice(colors)
                    oval_surf = pygame.Surface((oval_width * 2, oval_height * 2), pygame.SRCALPHA)
                    for px in range(oval_width * 2):
                        for py in range(oval_height * 2):
                            center_x, center_y = oval_width, oval_height
                            dist_x = (px - center_x) / oval_width
                            dist_y = (py - center_y) / oval_height
                            dist = math.hypot(dist_x, dist_y)
                            if dist <= 1:
                                alpha = int(color[1] * (1 - dist * 0.9))
                                if alpha > 0:
                                    oval_surf.set_at((px, py), (*color[0][:3], alpha))
                    oval_surf = pygame.transform.rotate(oval_surf, angle)
                    nebula_surf.blit(oval_surf, (base_width // 2 + offset_x - oval_width, 
                                               base_height // 2 + offset_y - oval_height))
                for px in range(0, base_width, 8):
                    for py in range(0, base_height, 8):
                        if random.random() < 0.1:  # Sparse dither
                            alpha = random.randint(10, 20)
                            nebula_surf.set_at((px, py), (*random.choice([ORANGE, NEON_PINK, NEON_BLUE, NEON_GREEN])[:3], alpha))
                self.nebulae.append([x, y, nebula_surf, speed])
        except Exception as e:
            log(f"Nebulae generation failed: {e}")

    def move(self):
        log(f"Moving PlanetSurface for Level {self.level}, offset_y was {self.offset_y}")
        try:
            self.offset_y += 1
            if self.offset_y >= HEIGHT * 2:
                self.offset_y = 0
                self.ground_layers = []
                self.features = []
                self.bases = []
                self.meteors = []
                self.nebulae = []
                self.update_ground_layers()
                self.generate_features()
                self.generate_bases()
                self.generate_nebulae()
                log(f"PlanetSurface reset for Level {self.level}")

            meteors_to_remove = []
            for meteor in self.meteors:
                meteor[1] += meteor[3]
                if meteor[1] > HEIGHT:
                    meteors_to_remove.append(meteor)
                global player_x, player_y, player_size, player_health
                meteor_size = 20
                if (meteor[1] + meteor_size > player_y and meteor[1] < player_y + player_size and 
                    meteor[0] + meteor_size > player_x and meteor[0] < player_x + player_size):
                    player_health -= 25
                    if ship_hit_sound: ship_hit_sound.play()
                    meteors_to_remove.append(meteor)

            for meteor in meteors_to_remove:
                if meteor in self.meteors:
                    self.meteors.remove(meteor)

            for nebula in self.nebulae:
                nebula[1] += nebula[3]
                if nebula[1] > HEIGHT * 2 + nebula[2].get_height():
                    nebula[1] = -nebula[2].get_height()
                    nebula[0] = random.randint(0, WIDTH)

            if self.level > 1 and random.random() < 0.01 and not self.meteor_active:
                self.meteor_active = True
                self.meteor_timer = 300
                for _ in range(2):
                    meteor_x = random.randint(0, WIDTH - meteor_size)
                    meteor_y = -20
                    meteor_speed = random.uniform(3, 6)
                    self.meteors.append([meteor_x, meteor_y, 0, meteor_speed])

            if self.meteor_active:
                self.meteor_timer -= 1
                if self.meteor_timer <= 0:
                    self.meteor_active = False
                    self.meteors = []
                elif random.random() < 0.05:
                    meteor_x = random.randint(0, WIDTH - meteor_size)
                    meteor_y = -20
                    meteor_speed = random.uniform(3, 6)
                    self.meteors.append([meteor_x, meteor_y, 0, meteor_speed])
        except Exception as e:
            log(f"Planet move failed for Level {self.level}: {e}")

    def draw(self, screen):
        log(f"Drawing PlanetSurface for Level {self.level} at offset_y {self.offset_y}")
        try:
            self.update_ground_layers()
            y_offset = 0
            for layer in self.ground_layers:
                pygame.draw.rect(screen, layer["color"], (0, y_offset - self.offset_y - HEIGHT * 2, WIDTH, layer["height"]))
                darker = (max(0, layer["color"][0] - 30), max(0, layer["color"][1] - 30), max(0, layer["color"][2] - 30))
                pygame.draw.rect(screen, darker, (0, y_offset - self.offset_y + layer["height"] - HEIGHT * 2 - 3, WIDTH, 3))
                y_offset += layer["height"]

            for nebula in self.nebulae:
                x, y, nebula_surf, _ = nebula
                y_pos = (y - self.offset_y) % (HEIGHT * 2) - HEIGHT
                screen.blit(nebula_surf, (x - nebula_surf.get_width() // 2, y_pos))

            for feature in self.features:
                y_pos = (feature["y"] - self.offset_y) % (HEIGHT * 4) - HEIGHT * 2 + feature["offset"]
                if feature["type"] == "forest":
                    pygame.draw.rect(screen, (30, 100, 30), (feature["x"], y_pos, feature["width"], feature["height"]))
                    pygame.draw.rect(screen, (0, 50, 0, 80), (feature["x"] + 1, y_pos + 1, feature["width"], feature["height"]), 1)
                elif feature["type"] == "river":
                    pygame.draw.rect(screen, (0, 120, 180), (feature["x"], y_pos, feature["width"], feature["height"]))
                    pygame.draw.rect(screen, (0, 50, 100, 80), (feature["x"] + 1, y_pos + 1, feature["width"], feature["height"]), 1)
                elif feature["type"] == "earth":
                    pygame.draw.rect(screen, (150, 90, 40), (feature["x"], y_pos, feature["width"], feature["height"]))
                    pygame.draw.rect(screen, (100, 60, 20, 80), (feature["x"] + 1, y_pos + 1, feature["width"], feature["height"]), 1)

            for base in self.bases:
                y_pos = (base["y"] - self.offset_y) % (HEIGHT * 4) - HEIGHT * 2 + base["offset"]
                if base["type"] == "circle":
                    pygame.draw.circle(screen, (255, 69, 0), (int(base["x"] + base["size"] // 2), int(y_pos + base["size"] // 2)), base["size"] // 2)
                    pygame.draw.circle(screen, (255, 255, 255), (int(base["x"] + base["size"] // 2), int(y_pos + base["size"] // 2)), base["size"] // 4, 1)
                    pygame.draw.circle(screen, (200, 0, 0, 60), (int(base["x"] + base["size"] // 2 + 1), int(y_pos + base["size"] // 2 + 1)), base["size"] // 2, 1)
                elif base["type"] == "rect":
                    pygame.draw.rect(screen, (139, 69, 19), (base["x"], y_pos, base["size"], base["size"]))
                    pygame.draw.rect(screen, (100, 50, 0, 60), (base["x"] + 1, y_pos + 1, base["size"], base["size"]), 1)
                elif base["type"] == "diamond":
                    points = [(base["x"] + base["size"] // 2, y_pos), 
                              (base["x"] + base["size"], y_pos + base["size"] // 2), 
                              (base["x"] + base["size"] // 2, y_pos + base["size"]), 
                              (base["x"], y_pos + base["size"] // 2)]
                    pygame.draw.polygon(screen, (255, 100, 0), points)
                    shadow_points = [(p[0] + 1, p[1] + 1) for p in points]
                    pygame.draw.polygon(screen, (200, 0, 0, 60), shadow_points, 1)

            for meteor in self.meteors:
                meteor_x, meteor_y = meteor[0], meteor[1]
                pygame.draw.circle(screen, (150, 75, 0), (int(meteor_x + 10), int(meteor_y + 10)), 10)
                pygame.draw.circle(screen, (255, 165, 0), (int(meteor_x + 10), int(meteor_y + 10)), 12, 1)
            log(f"Drew PlanetSurface successfully for Level {self.level}")
        except Exception as e:
            log(f"Planet draw failed for Level {self.level}: {e}")

def generate_background(level):
    global stars, planet_surface
    try:
        star_count = 100 if level == 1 else 0  # Stars for Level 1, planet for 2+
        stars = [Star(level) for _ in range(star_count)]
        planet_surface = PlanetSurface(level)
        log(f"Generated background for Level {level}: {star_count} stars")
        play_music_for_level(level)
    except Exception as e:
        log(f"Background generation failed: {e}")
        stars = []
        planet_surface = PlanetSurface(1)

def draw_glow(surface, x, y, size, color, is_enemy=False):
    try:
        if is_enemy:
            color = random.choice([YELLOW, ORANGE, NEON_PINK, NEON_BLUE, NEON_GREEN, CYAN, PURPLE])
        if not isinstance(color, tuple) or len(color) < 3:
            log(f"Invalid color detected: {color}, defaulting to WHITE")
            color = WHITE
        
        for i in range(3):
            glow_size = size + (i + 1) * 6
            alpha = max(0, min(255, 20 - i * 5))
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            r, g, b = [max(0, min(255, c)) for c in color[:3]]
            pygame.draw.rect(glow_surf, (r, g, b, alpha), (0, 0, glow_size, glow_size), border_radius=size // 2)
            surface.blit(glow_surf, (x - (glow_size - size) // 2, y - (glow_size - size) // 2))
    except Exception as e:
        log(f"Glow draw failed: {e}")

def play_intro():
    global first_level_1_start, joystick
    try:
        if intro_music:
            intro_music.play()
        for frame in intro_frames:
            screen.blit(frame, (0, 0))
            pygame.display.flip()
            pygame.time.wait(750)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        intro_music.stop()
                        return True
                elif event.type == pygame.JOYBUTTONDOWN and joystick:
                    if joystick.get_button(5):  # PS5 Options button
                        intro_music.stop()
                        return True
        intro_music.stop()
        return True
    except Exception as e:
        log(f"Intro playback failed: {e}")
        return True

def start_screen():
    global level, base_level, joystick
    selected_level = 1
    screen.blit(start_screen_sprite, (0, 0))
    power_up_items = [
        (power_up_sprites["rate"], "Rate of Fire: Faster Shots"),
        (power_up_sprites["reinforce"], "Reinforce: +100 HP"),
        (power_up_sprites["diver_pod"], "Diver Pod: +1 Diver"),
        (power_up_sprites["resupply"], "Resupply: Double Shots (5s)"),
        (power_up_sprites["hellbomb"], "Hellbomb: Clear All Enemies"),
        (power_up_sprites["mg94"], "MG-94: Faster Shots"),
        (power_up_sprites["eat17"], "EAT-17: Magnet + Pierce (5s)"),
        (power_up_sprites["shield"], "Shield: Invincibility (5s)"),
        (power_up_sprites["trishot"], "Trishot: Triple Shots (5s)"),
        (power_up_sprites["quad"], "Quadshot: Four Shots (5s)"),
        (power_up_sprites["burst"], "Burst: Rapid Fire (5s)"),
        (power_up_sprites["eagle_sweat"], "Eagle Sweat: Double Score (10s)"),
        (power_up_sprites["battle_buddy"], "Battle Buddy: Wingman (30s)")
    ]
    enemy_items = [
        (bug_frames[0], "Bugs"),
        (bot_frames[0], "Bots"),
        (squid_frames[0], "Squids"),
        (hunter_frames[0], "Hunter")
    ]
    controls = [
        ("Left Stick", "Move"),
        ("Right Stick", "Rotate"),
        ("R2", "Shoot"),
        ("P / Options", "Pause")
    ]
    pygame.joystick.quit()
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        log(f"Joystick initialized in start screen: {joystick.get_name()}")
    else:
        joystick = None

    while True:
        try:
            screen.blit(start_screen_sprite, (0, 0))
            high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
            screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 10))
            screen.blit(font.render("Power-Ups", True, WHITE), (50, 50))
            for i, (sprite, text) in enumerate(power_up_items):
                y_pos = 80 + i * 40
                draw_glow(screen, 50 - 5, y_pos - 5, power_up_size, WHITE)
                screen.blit(sprite, (50, y_pos))
                screen.blit(font.render(text, True, WHITE), (80, y_pos + 5))
            screen.blit(font.render("Enemies", True, WHITE), (400, 50))
            for i, (sprite, text) in enumerate(enemy_items):
                y_pos = 80 + i * 40
                draw_glow(screen, 400 - 5, y_pos - 5, alien_size, YELLOW)
                screen.blit(sprite, (400, y_pos))
                screen.blit(font.render(text, True, WHITE), (435, y_pos + 5))
            screen.blit(font.render("Select Starting Level (1-20):", True, WHITE), (400, 300))
            level_text = font.render(str(selected_level), True, WHITE)
            screen.blit(level_text, (400 + 100 - level_text.get_width() // 2, 330))
            screen.blit(font.render("Press Space / Cross to Start", True, WHITE), (400 + 50, 360))
            screen.blit(font.render("Controls", True, WHITE), (550, 50))
            for i, (key, action) in enumerate(controls):
                y_pos = 80 + i * 40
                draw_glow(screen, 550 - 5, y_pos - 5, 20, BLUE)
                key_text = font.render(key, True, WHITE)
                action_text = font.render(action, True, WHITE)
                screen.blit(key_text, (550, y_pos + 5))
                screen.blit(action_text, (600 + key_text.get_width(), y_pos + 5))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        level = selected_level
                        base_level = selected_level
                        log(f"Starting game at Level {level}")
                        return True
                    elif event.key == pygame.K_UP:
                        selected_level = min(20, selected_level + 1)
                    elif event.key == pygame.K_DOWN:
                        selected_level = max(1, selected_level - 1)
                elif event.type == pygame.JOYBUTTONDOWN and joystick:
                    if joystick.get_button(0):  # PS5 Cross button
                        level = selected_level
                        base_level = selected_level
                        log(f"Starting game at Level {level} via joystick")
                        return True
                elif event.type == pygame.JOYAXISMOTION and joystick:
                    if joystick.get_axis(1) < -0.5:  # Left stick up
                        selected_level = min(20, selected_level + 1)
                    elif joystick.get_axis(1) > 0.5:  # Left stick down
                        selected_level = max(1, selected_level - 1)
                elif event.type == pygame.JOYDEVICEADDED:
                    if pygame.joystick.get_count() > 0 and not joystick:
                        joystick = pygame.joystick.Joystick(event.device_index)
                        joystick.init()
                        log(f"Joystick connected: {joystick.get_name()}")

        except Exception as e:
            log(f"Start screen error: {e}")
            return False

def pause_screen():
    global master_volume, high_score, score, joystick
    try:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        slider_x, slider_y = WIDTH // 2 - 100, HEIGHT // 2 - 10
        slider_rect = pygame.Rect(slider_x, slider_y, 200, 10)
        knob_x = slider_x + int(master_volume * 200) - 5
        knob_rect = pygame.Rect(knob_x, slider_y - 5, 10, 20)
        dragging = False

        while True:
            screen.blit(start_screen_sprite, (0, 0))
            screen.blit(overlay, (0, 0))
            screen.blit(title_font.render("Paused", True, WHITE), (WIDTH // 2 - 60, HEIGHT // 2 - 120))
            screen.blit(font.render("Master Volume", True, WHITE), (WIDTH // 2 - 50, HEIGHT // 2 - 40))
            screen.blit(font.render(f"High Score: {high_score}", True, WHITE), (WIDTH // 2 - 50, HEIGHT // 2 - 70))
            pygame.draw.rect(screen, GRAY, slider_rect)
            pygame.draw.rect(screen, WHITE, knob_rect)
            screen.blit(font.render("Save High Score", True, WHITE), (WIDTH // 2 - 100, HEIGHT // 2 + 20))
            screen.blit(font.render("Load High Score", True, WHITE), (WIDTH // 2 + 50, HEIGHT // 2 + 20))
            screen.blit(font.render("Press P / Options to Resume", True, WHITE), (WIDTH // 2 - 70, HEIGHT // 2 + 60))
            screen.blit(font.render("Press R / Share to Reset", True, WHITE), (WIDTH // 2 - 60, HEIGHT // 2 + 80))
            screen.blit(font.render("Press Q / Square to Quit", True, WHITE), (WIDTH // 2 - 50, HEIGHT // 2 + 100))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        return True
                    elif event.key == pygame.K_r:
                        return "reset"
                    elif event.key == pygame.K_q:
                        return False
                elif event.type == pygame.JOYBUTTONDOWN and joystick:
                    if joystick.get_button(5):  # PS5 Options button
                        return True
                    elif joystick.get_button(4):  # PS5 Share button
                        return "reset"
                    elif joystick.get_button(2):  # PS5 Square button
                        return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if knob_rect.collidepoint(event.pos):
                        dragging = True
                    elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 120, 20).collidepoint(event.pos):
                        high_score = save_high_score(score)
                    elif pygame.Rect(WIDTH // 2 + 50, HEIGHT // 2 + 20, 120, 20).collidepoint(event.pos):
                        high_score = load_high_score()
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                elif event.type == pygame.MOUSEMOTION and dragging:
                    knob_x = max(slider_x, min(slider_x + 200, event.pos[0]))
                    master_volume = (knob_x - slider_x) / 200
                    update_volumes()
                    knob_rect.x = knob_x - 5
    except Exception as e:
        log(f"Pause screen error: {e}")
        return False

def get_boss_difficulty(level, base_level):
    boss_encounter = (level - base_level) // 5
    level_factor = max(1, base_level // 5)
    health = BOSS_HEALTH_BASE * (1 + level_factor) + (boss_encounter * 300)
    speed = boss_speed_base + (boss_encounter * 0.5)
    shot_chance = boss_shot_chance_base + (boss_encounter * 0.02)
    return health, speed, min(shot_chance, 0.1)

def spawn_alien():
    if level % 5 == 0 and boss_types and not any(len(a) == 7 for a in aliens):
        x = random.randint(0, WIDTH - boss_size)
        frames = boss_types[(level // 5 - 1) % len(boss_types)]
        boss_health, boss_speed, boss_shot_chance = get_boss_difficulty(level, base_level)
        aliens.append([x, 0, frames, True, boss_health, 0, 0])
        for i in range(6):
            angle = math.radians(i * 60)
            enemy_shots.append([x + boss_size//2, boss_size//2, 
                              enemy_shot_speed * math.cos(angle), 
                              enemy_shot_speed * math.sin(angle), 120])
        for _ in range(3):
            x = random.randint(0, WIDTH - alien_size)
            roll = random.random()
            if roll < 0.33:
                aliens.append([x, 0, bug_frames, False, 0, 0])
            elif roll < 0.66:
                aliens.append([x, 0, bot_frames, False, 0, 0])
            else:
                aliens.append([x, 0, squid_frames, False, 0, 0])
    elif not (level % 5 == 0):
        x = random.randint(0, WIDTH - alien_size)
        roll = random.random()
        if roll < 0.05:
            aliens.append([x, 0, hunter_frames, True, 0, 0])
        elif roll < 0.10:  # 5% chance to spawn a pack of hunters
            for _ in range(3):  # Spawn 3 hunters in a pack
                pack_x = random.randint(0, WIDTH - alien_size)
                aliens.append([pack_x, 0, hunter_frames, True, 0, 0])
        elif roll < 0.40:
            aliens.append([x, 0, bug_frames, False, 0, 0])
        elif roll < 0.70:
            aliens.append([x, 0, bot_frames, False, 0, 0])
        else:
            aliens.append([x, 0, squid_frames, False, 0, 0])

def spawn_power_up(x, y):
    try:
        roll = random.random()
        if roll < 0.15: power_ups.append([x, y, power_up_sprites["rate"]])
        elif roll < 0.30: power_ups.append([x, y, power_up_sprites["reinforce"]])
        elif roll < 0.40: power_ups.append([x, y, power_up_sprites["diver_pod"]])
        elif roll < 0.55: power_ups.append([x, y, power_up_sprites["resupply"]])
        elif roll < 0.57: power_ups.append([x, y, power_up_sprites["hellbomb"]])  # Reduced to 2% (from 10%)
        elif roll < 0.62: power_ups.append([x, y, power_up_sprites["mg94"]])
        elif roll < 0.72: power_ups.append([x, y, power_up_sprites["eat17"]])
        elif roll < 0.82: power_ups.append([x, y, power_up_sprites["shield"]])
        elif roll < 0.87: power_ups.append([x, y, power_up_sprites["trishot"]])
        elif roll < 0.92: power_ups.append([x, y, power_up_sprites["quad"]])
        elif roll < 0.97: power_ups.append([x, y, power_up_sprites["burst"]])
        elif roll < 0.99: power_ups.append([x, y, power_up_sprites["eagle_sweat"]])
        elif roll < 1.0: power_ups.append([x, y, power_up_sprites["battle_buddy"]])
    except Exception as e:
        log(f"Power-up spawn failed: {e}")

def game_over_screen(final_score, kill_streak, highest_kill_streak, capture_streak, highest_capture_streak):
    global high_score, joystick
    try:
        high_score = save_high_score(final_score)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        text_elements = [
            ("Eagle Down!", title_font),
            (f"Final Points: {final_score}", font),
            (f"High Score: {high_score}", font),
            (f"Final Level: {level}", font),
            (f"Kill Streak: {kill_streak}", font),
            (f"Best Kill Streak: {highest_kill_streak}", font),
            (f"Capture Streak: {capture_streak}", font),
            (f"Best Capture Streak: {highest_capture_streak}", font),
            ("Press R / Share to Return", font),
            ("Press Q / Square to Quit", font),
            ("Partially Coded by Grok", font),
            ("Developed by MilsimRooster", font),
            ("Music by Colm R McGuinness, Jonathan Young, Boris Harizanov", font),
        ]
        total_items = len(text_elements) + 1
        line_spacing = 30
        total_height = (len(text_elements) - 1) * line_spacing + title_font.get_height() + (font.get_height() * (total_items - 1)) + 40
        start_y = 50  # Fixed offset from top to shift everything down
        
        share_button_text = font.render("Share Score to X", True, WHITE)
        share_button_rect = share_button_text.get_rect(center=(WIDTH // 2, 0))
        share_button_padding = 10
        share_button_bg = pygame.Rect(
            share_button_rect.left - share_button_padding,
            0,
            share_button_rect.width + 2 * share_button_padding,
            share_button_rect.height + 2 * share_button_padding
        )

        while True:
            screen.blit(start_screen_sprite, (0, 0))
            screen.blit(overlay, (0, 0))
            current_y = start_y
            for i, (text, fnt) in enumerate(text_elements):
                rendered = fnt.render(text, True, WHITE)
                if i == 0:
                    screen.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, current_y))
                    current_y += fnt.get_height() + line_spacing
                elif i == 10:  # "Coded by Grok" gets extra spacing before credits
                    screen.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, current_y))
                    current_y += line_spacing * 2
                else:
                    screen.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, current_y))
                    current_y += line_spacing
                if i == 9:  # After "Press Q / Square to Quit"
                    share_button_rect.centery = current_y + line_spacing + share_button_rect.height // 2
                    share_button_bg.top = share_button_rect.top - share_button_padding
                    current_y += share_button_bg.height + line_spacing

            mouse_pos = pygame.mouse.get_pos()
            if share_button_bg.collidepoint(mouse_pos):
                pygame.draw.rect(screen, NEON_GREEN, share_button_bg, border_radius=5)
            else:
                pygame.draw.rect(screen, GRAY, share_button_bg, border_radius=5)
            screen.blit(share_button_text, share_button_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return True
                    elif event.key == pygame.K_q:
                        return False
                elif event.type == pygame.JOYBUTTONDOWN and joystick:
                    if joystick.get_button(4):  # PS5 Share button
                        return True
                    elif joystick.get_button(2):  # PS5 Square button
                        return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if share_button_bg.collidepoint(event.pos):
                        share_text = f"I scored {final_score} points in Eagle Strike! High Score: {high_score}. Kill Streak: {highest_kill_streak}. Capture Streak: {highest_capture_streak}. Beat me if you can! #EagleStrike"
                        x_url = f"https://x.com/intent/post?text={share_text.replace(' ', '%20')}"
                        try:
                            webbrowser.open(x_url)
                            log(f"Opened browser to share score on X.com: {x_url}")
                        except Exception as e:
                            log(f"Failed to open X.com share URL: {e}")

            clock.tick(60)
    except Exception as e:
        log(f"Game over screen error: {e}")
        return False

def run_game():
    global player_x, player_y, player_dx, player_dy, player_angle, score, aliens, shots, enemy_shots, power_ups, spawn_timer, shot_timer, shot_cooldown, divers_rescued, double_shot, double_shot_timer, piercing_shot, piercing_shot_timer, trishot, trishot_timer, quad_shot, quad_shot_timer, burst_mode, burst_timer, shield_active, shield_timer, eagle_sweat_active, eagle_sweat_timer, battle_buddy_active, battle_buddy_timer, battle_buddy_x, battle_buddy_y, battle_buddy_shot_timer, battle_buddy_shots, paused, level, stars, planet_surface, player_frame, player_frame_timer, level_up_text, player_size, player_frames, dual_blasts, base_level, player_health, first_level_1_start, joystick
   
    if pygame.joystick.get_count() > 0 and not joystick:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    player_x = WIDTH // 2 - player_size // 2
    player_y = HEIGHT - 100
    player_dx = 0
    player_dy = 0
    player_angle = 90
    score = 0
    aliens = []
    shots = []
    enemy_shots = []
    power_ups = []
    battle_buddy_shots = []
    spawn_timer = 0
    spawn_interval = 15
    shot_timer = 0
    shot_cooldown = 15
    divers_rescued = 3
    player_health = 200
    PLAYER_MAX_HEALTH = 200
    double_shot = False
    double_shot_timer = 0
    piercing_shot = False
    piercing_shot_timer = 0
    trishot = False
    trishot_timer = 0
    quad_shot = False
    quad_shot_timer = 0
    burst_mode = False
    burst_timer = 0
    shield_active = False
    shield_timer = 0
    eagle_sweat_active = False
    eagle_sweat_timer = 0
    battle_buddy_active = False
    battle_buddy_timer = 0
    battle_buddy_x = player_x + player_size + 10
    battle_buddy_y = player_y - battle_buddy_size
    battle_buddy_shot_timer = 0
    paused = False
    player_frame = 0
    player_frame_timer = 0
    level_up_text = None
    dual_blasts = level >= 10
    kill_streak = 0
    highest_kill_streak = 0
    capture_streak = 0
    highest_capture_streak = 0
    break_free_used = False
    
    if dual_blasts:
        player_size = 60
        player_frames = load_sprite_frames("dropship", 2, player_size, player_size, WHITE)
        player_x = WIDTH // 2 - player_size // 2
    
    if level == 1 and first_level_1_start:
        if not play_intro():
            return False
        first_level_1_start = False
    
    generate_background(level)
    if level % 5 == 0 and boss_types:
        spawn_alien()
    frame_count = 0

    running = True
    while running:
        if paused:
            result = pause_screen()
            if result is True:
                paused = False
                continue
            elif result == "reset":
                return True
            else:
                return False

        frame_count += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_b and not break_free_used:
                    break_free_used = True
                    for alien in aliens:
                        if len(alien) == 7:
                            x, y = alien[0], alien[1]
                            dx = player_x + player_size // 2 - x
                            dy = player_y + player_size // 2 - y
                            dist = max(1, math.hypot(dx, dy))
                            push_force = 200
                            alien[0] -= (dx / dist) * push_force
                            alien[1] -= (dy / dist) * push_force
                            if boom_sound: boom_sound.play()
                            break
            elif event.type == pygame.JOYBUTTONDOWN and joystick:
                if joystick.get_button(4):
                    paused = not paused
                elif joystick.get_button(3) and not break_free_used:
                    break_free_used = True
                    for alien in aliens:
                        if len(alien) == 7:
                            x, y = alien[0], alien[1]
                            dx = player_x + player_size // 2 - x
                            dy = player_y + player_size // 2 - y
                            dist = max(1, math.hypot(dx, dy))
                            push_force = 200
                            alien[0] -= (dx / dist) * push_force
                            alien[1] -= (dy / dist) * push_force
                            if boom_sound: boom_sound.play()
                            break
            elif event.type == pygame.JOYDEVICEADDED:
                if pygame.joystick.get_count() > 0 and not joystick:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joystick.init()

        if divers_rescued <= 0:
            break

        boss_level = level % 5 == 0
        if not boss_level and score >= (level - base_level + 1) * BASE_THRESHOLD:
            level += 1
            if level >= 10 and not dual_blasts:
                player_size = 60
                player_frames = load_sprite_frames("dropship", 2, player_size, player_size, WHITE)
                player_x = WIDTH // 2 - player_size // 2
                player_dx = 0
                player_dy = 0
                player_angle = 90
                dual_blasts = True
            aliens.clear()
            shots.clear()
            enemy_shots.clear()
            battle_buddy_shots.clear()
            power_ups.clear()
            generate_background(level)  # Single reset on level-up
            if level_up_sound: level_up_sound.play()
            if level % 5 == 0 and boss_types:
                spawn_alien()
            level_up_text = [title_font.render(f"Level {level}", True, WHITE), WIDTH // 2, HEIGHT // 2, 255, level_up_duration]
            spawn_interval = 15

        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            if not boss_level:
                spawn_alien()
            elif boss_level and any(len(a) == 7 for a in aliens):
                if random.random() < 0.1:
                    x = random.randint(0, WIDTH - alien_size)
                    roll = random.random()
                    if roll < 0.33:
                        aliens.append([x, 0, bug_frames, False, 0, 0])
                    elif roll < 0.66:
                        aliens.append([x, 0, bot_frames, False, 0, 0])
                    else:
                        aliens.append([x, 0, squid_frames, False, 0, 0])
            spawn_timer = 0

        if joystick:
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            if abs(x_axis) > 0.1:
                player_dx += x_axis * 0.5
                player_dx = max(-player_speed, min(player_speed, player_dx))
            if abs(y_axis) > 0.1:
                player_dy += y_axis * 0.5
                player_dy = max(-player_speed, min(player_speed, player_dy))

            rot_axis = joystick.get_axis(2)
            if abs(rot_axis) > 0.1:
                player_angle += rot_axis * 2

            player_x += player_dx
            player_y += player_dy
            player_dx *= 0.95
            player_dy *= 0.95
            player_x = max(0, min(WIDTH - player_size, player_x))
            player_y = max(0, min(HEIGHT - player_size, player_y))

            r2_value = (joystick.get_axis(5) + 1) / 2
            fire_active = r2_value > 0.5
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player_dx -= 0.5
                player_dx = max(-player_speed, min(player_speed, player_dx))
            if keys[pygame.K_RIGHT]:
                player_dx += 0.5
                player_dx = max(-player_speed, min(player_speed, player_dx))
            if keys[pygame.K_UP]:
                player_dy -= 0.5
                player_dy = max(-player_speed, min(player_speed, player_dy))
            if keys[pygame.K_DOWN]:
                player_dy += 0.5
                player_dy = max(-player_speed, min(player_speed, player_dy))

            player_x += player_dx
            player_y += player_dy
            player_dx *= 0.95
            player_dy *= 0.95
            player_x = max(0, min(WIDTH - player_size, player_x))
            player_y = max(0, min(HEIGHT - player_size, player_y))

            fire_active = keys[pygame.K_SPACE]

        if fire_active and shot_timer <= 0:
            angle_rad = math.radians(player_angle)
            shot_dx = math.cos(angle_rad) * shot_speed
            shot_dy = math.sin(angle_rad) * shot_speed
            shot_x = player_x + player_size // 2 - math.cos(angle_rad) * (player_size // 2)
            shot_y = player_y + player_size // 2 - math.sin(angle_rad) * (player_size // 2)
            if burst_mode:
                shots.append([shot_x, shot_y, piercing_shot, shot_dx, shot_dy])
                shot_timer = 1
            elif quad_shot:
                for offset in [-15, -5, 5, 15]:
                    offset_rad = math.radians(player_angle + offset)
                    shots.append([shot_x, shot_y, piercing_shot, math.cos(offset_rad) * shot_speed, math.sin(offset_rad) * shot_speed])
                shot_timer = shot_cooldown
            elif trishot:
                for offset in [-10, 0, 10]:
                    offset_rad = math.radians(player_angle + offset)
                    shots.append([shot_x, shot_y, piercing_shot, math.cos(offset_rad) * shot_speed, math.sin(offset_rad) * shot_speed])
                shot_timer = shot_cooldown
            elif double_shot or dual_blasts:
                for offset in [-5, 5]:
                    offset_rad = math.radians(player_angle + offset)
                    shots.append([shot_x, shot_y, piercing_shot, math.cos(offset_rad) * shot_speed, math.sin(offset_rad) * shot_speed])
                shot_timer = shot_cooldown
            else:
                shots.append([shot_x, shot_y, piercing_shot, shot_dx, shot_dy])
                shot_timer = shot_cooldown
            if shoot_sound: shoot_sound.play()

        player_frame_timer += 1
        if player_frame_timer >= player_frame_speed:
            player_frame_timer = 0
            player_frame = (player_frame + 1) % len(player_frames)

        if battle_buddy_active:
            battle_buddy_x = player_x + player_size + 10
            battle_buddy_y = player_y - battle_buddy_size
            battle_buddy_timer -= 1
            if battle_buddy_timer <= 0:
                battle_buddy_active = False
                battle_buddy_shots.clear()

            battle_buddy_shot_timer -= 1
            if battle_buddy_shot_timer <= 0 and aliens:
                nearest_alien = min(aliens, key=lambda a: math.hypot(a[0] - battle_buddy_x, a[1] - battle_buddy_y))
                if nearest_alien:
                    dx = nearest_alien[0] - battle_buddy_x
                    dy = nearest_alien[1] - battle_buddy_y
                    dist = max(1, math.hypot(dx, dy))
                    battle_buddy_shots.append([battle_buddy_x + battle_buddy_size // 2, battle_buddy_y, shot_speed * dx / dist, shot_speed * dy / dist])
                    if shoot_sound: shoot_sound.play()
                battle_buddy_shot_timer = battle_buddy_shot_cooldown

        aliens_to_remove = []
        shots_to_remove = []
        shots_to_add = []
        enemy_shots_to_remove = []
        battle_buddy_shots_to_remove = []
        power_ups_to_remove = []

        for alien in aliens:
            is_boss = len(alien) == 7
            x, y = alien[0], alien[1]
            frames, is_special, frame, frame_timer = alien[2], alien[3], alien[-2], alien[-1]
            size = boss_size if is_boss else alien_size
            speed = alien_speed
            shot_chance = enemy_shot_chance
            if is_boss:
                _, speed, shot_chance = get_boss_difficulty(level, base_level)
            elif is_special:
                speed = hunter_speed

            if is_boss or is_special:
                dx = player_x + player_size // 2 - x
                dy = player_y + player_size // 2 - y
                dist = max(1, math.hypot(dx, dy))
                alien[0] += speed * dx / dist
                alien[1] += speed * dy / dist
                if hunter_thrust_sound and random.random() < 0.05 and not is_boss: hunter_thrust_sound.play()
            else:
                alien[1] += speed

            if alien[1] > HEIGHT:
                aliens_to_remove.append(alien)

            if random.random() < shot_chance and frame_count > 60:
                if is_boss:
                    center_x, center_y = x + size // 2, y + size // 2
                    for i in range(6):
                        angle = math.radians(i * 60 + frame_count % 360)
                        speed_variation = enemy_shot_speed * (1 + random.uniform(0, 0.5))
                        enemy_shots.append([center_x, center_y, speed_variation * math.cos(angle), speed_variation * math.sin(angle), 120])
                elif not is_special:
                    enemy_shots.append([x + size // 2, y + size, 0, enemy_shot_speed, 120])

            alien[-1] += 1
            if alien[-1] >= (boss_frame_speed if is_boss else alien_frame_speed):
                alien[-1] = 0
                alien[-2] = (alien[-2] + 1) % len(frames)

        for shot in shots:
            shot[0] += shot[3]
            shot[1] += shot[4]
            if shot[1] < -shot_length or shot[1] > HEIGHT or shot[0] < 0 or shot[0] > WIDTH:
                shots_to_remove.append(shot)

        for b_shot in battle_buddy_shots:
            b_shot[0] += b_shot[2]
            b_shot[1] += b_shot[3]
            if b_shot[1] < -shot_length or b_shot[1] > HEIGHT or b_shot[0] < 0 or b_shot[0] > WIDTH:
                battle_buddy_shots_to_remove.append(b_shot)

        for e_shot in enemy_shots:
            e_shot[0] += e_shot[2]
            e_shot[1] += e_shot[3]
            e_shot[4] -= 1
            if e_shot[4] <= 0 or e_shot[1] > HEIGHT or e_shot[0] < 0 or e_shot[0] > WIDTH:
                enemy_shots_to_remove.append(e_shot)

        for pu in power_ups:
            pu_x, pu_y = pu[0], pu[1]
            if piercing_shot:
                dx = player_x + player_size // 2 - pu_x
                dy = player_y + player_size // 2 - pu_y
                dist = max(1, math.hypot(dx, dy))
                pu[0] += 3 * dx / dist
                pu[1] += 3 * dy / dist
            else:
                pu[1] += 3
            if pu[1] > HEIGHT:
                power_ups_to_remove.append(pu)
                capture_streak = 0

        for shot in shots:
            shot_x, shot_y, piercing = shot[:3]
            for alien in aliens:
                if alien in aliens_to_remove:
                    continue
                is_boss = len(alien) == 7
                x, y = alien[0], alien[1]
                size = boss_size if is_boss else alien_size
                if y < shot_y + shot_length and y + size > shot_y and x - 5 < shot_x < x + size + 5:
                    if is_boss:
                        alien[4] -= 5
                        if alien[4] <= 0:
                            aliens_to_remove.append(alien)
                            score += 500 * (2 if eagle_sweat_active else 1)
                            kill_streak += 1
                            highest_kill_streak = max(highest_kill_streak, kill_streak)
                            if kill_streak == 5:
                                player_health = min(PLAYER_MAX_HEALTH, player_health + 50)
                            elif kill_streak == 10:
                                shot_cooldown = max(5, shot_cooldown - 2)
                            elif kill_streak == 15:
                                score += 1000
                                spawn_power_up(player_x, player_y)
                            spawn_power_up(x, y)
                            if boss_level:
                                level += 1
                                if level >= 10 and not dual_blasts:
                                    player_size = 60
                                    player_frames = load_sprite_frames("dropship", 2, player_size, player_size, WHITE)
                                    player_x = WIDTH // 2 - player_size // 2
                                    player_dx = 0
                                    player_dy = 0
                                    player_angle = 90
                                    dual_blasts = True
                                aliens.clear()
                                shots.clear()
                                enemy_shots.clear()
                                battle_buddy_shots.clear()
                                power_ups.clear()
                                generate_background(level)
                                if level_up_sound: level_up_sound.play()
                                if level % 5 == 0 and boss_types:
                                    spawn_alien()
                                level_up_text = [title_font.render(f"Level {level}", True, WHITE), WIDTH // 2, HEIGHT // 2, 255, level_up_duration]
                                spawn_interval = 15
                    else:
                        aliens_to_remove.append(alien)
                        score += 10 * (2 if eagle_sweat_active else 1)
                        kill_streak += 1
                        highest_kill_streak = max(highest_kill_streak, kill_streak)
                        if kill_streak == 5:
                            player_health = min(PLAYER_MAX_HEALTH, player_health + 50)
                        elif kill_streak == 10:
                            shot_cooldown = max(5, shot_cooldown - 2)
                        elif kill_streak == 15:
                            score += 1000
                            spawn_power_up(player_x, player_y)
                        spawn_power_up(x, y)
                    if hit_sound: hit_sound.play()
                    if piercing and random.random() < 0.5:
                        shots_to_add.extend([[shot_x, shot_y, False, offset, shot_speed] for offset in [-5, 5]])
                    if not piercing:
                        shots_to_remove.append(shot)
                    break

        for b_shot in battle_buddy_shots:
            shot_x, shot_y = b_shot[0], b_shot[1]
            for alien in aliens:
                if alien in aliens_to_remove:
                    continue
                is_boss = len(alien) == 7
                x, y = alien[0], alien[1]
                size = boss_size if is_boss else alien_size
                if y < shot_y + shot_length and y + size > shot_y and x - 5 < shot_x < x + size + 5:
                    if is_boss:
                        alien[4] -= 5
                        if alien[4] <= 0:
                            aliens_to_remove.append(alien)
                            score += 500 * (2 if eagle_sweat_active else 1)
                            kill_streak += 1
                            highest_kill_streak = max(highest_kill_streak, kill_streak)
                            if kill_streak == 5:
                                player_health = min(PLAYER_MAX_HEALTH, player_health + 50)
                            elif kill_streak == 10:
                                shot_cooldown = max(5, shot_cooldown - 2)
                            elif kill_streak == 15:
                                score += 1000
                                spawn_power_up(player_x, player_y)
                            spawn_power_up(x, y)
                            if boss_level:
                                level += 1
                                if level >= 10 and not dual_blasts:
                                    player_size = 60
                                    player_frames = load_sprite_frames("dropship", 2, player_size, player_size, WHITE)
                                    player_x = WIDTH // 2 - player_size // 2
                                    player_dx = 0
                                    player_dy = 0
                                    player_angle = 90
                                    dual_blasts = True
                                aliens.clear()
                                shots.clear()
                                enemy_shots.clear()
                                battle_buddy_shots.clear()
                                power_ups.clear()
                                generate_background(level)
                                if level_up_sound: level_up_sound.play()
                                if level % 5 == 0 and boss_types:
                                    spawn_alien()
                                level_up_text = [title_font.render(f"Level {level}", True, WHITE), WIDTH // 2, HEIGHT // 2, 255, level_up_duration]
                                spawn_interval = 15
                    else:
                        aliens_to_remove.append(alien)
                        score += 10 * (2 if eagle_sweat_active else 1)
                        kill_streak += 1
                        highest_kill_streak = max(highest_kill_streak, kill_streak)
                        if kill_streak == 5:
                            player_health = min(PLAYER_MAX_HEALTH, player_health + 50)
                        elif kill_streak == 10:
                            shot_cooldown = max(5, shot_cooldown - 2)
                        elif kill_streak == 15:
                            score += 1000
                            spawn_power_up(player_x, player_y)
                        spawn_power_up(x, y)
                    if hit_sound: hit_sound.play()
                    battle_buddy_shots_to_remove.append(b_shot)
                    break

        if not shield_active:
            for alien in aliens:
                is_boss = len(alien) == 7
                a_x, a_y = alien[0], alien[1]
                size = boss_size if is_boss else alien_size
                if a_y + size > player_y and a_y < player_y + player_size and a_x + size > player_x and a_x < player_x + player_size:
                    player_health -= 50
                    capture_streak = 0
                    if ship_hit_sound: ship_hit_sound.play()
                    break
            
            for e_shot in enemy_shots:
                e_x, e_y = e_shot[0], e_shot[1]
                if e_y + enemy_shot_length > player_y and e_y < player_y + player_size and e_x - enemy_shot_width < player_x + player_size and e_x + enemy_shot_width > player_x:
                    player_health -= 35 if not len(alien) == 7 else 25
                    capture_streak = 0
                    enemy_shots_to_remove.append(e_shot)
                    if ship_hit_sound: hit_sound.play()

            if player_health <= 0:
                divers_rescued -= 1
                kill_streak = 0
                capture_streak = 0
                player_health = 200
                player_x = WIDTH // 2 - player_size // 2
                player_y = HEIGHT - 100
                player_dx = 0
                player_dy = 0
                player_angle = 90
                break_free_used = False
                new_aliens = [alien for alien in aliens if len(alien) == 7]
                aliens.clear()
                aliens.extend(new_aliens)
                shots.clear()
                enemy_shots.clear()
                battle_buddy_shots.clear()
                power_ups.clear()

        for pu in power_ups:
            pu_x, pu_y, pu_sprite = pu
            if pu_y + power_up_size > player_y and pu_y < player_y + player_size and pu_x + power_up_size > player_x and pu_x < player_x + player_size:
                power_ups_to_remove.append(pu)
                capture_streak += 1
                highest_capture_streak = max(highest_capture_streak, capture_streak)
                if capture_streak == 3:
                    score += 100
                elif capture_streak == 5:
                    spawn_power_up(player_x, player_y)
                elif capture_streak == 10:
                    divers_rescued += 1
                if power_up_sounds: random.choice(power_up_sounds).play()
                if pu_sprite == power_up_sprites["rate"]:
                    shot_cooldown = max(10, shot_cooldown - 5)
                elif pu_sprite == power_up_sprites["reinforce"]:
                    player_health = min(PLAYER_MAX_HEALTH, player_health + 100)
                elif pu_sprite == power_up_sprites["diver_pod"]:
                    divers_rescued += 1
                elif pu_sprite == power_up_sprites["resupply"]:
                    double_shot = True
                    double_shot_timer = 300
                elif pu_sprite == power_up_sprites["hellbomb"]:
                    score += len(aliens) * 50 * (2 if eagle_sweat_active else 1)
                    aliens.clear()
                    enemy_shots.clear()
                    battle_buddy_shots.clear()
                    power_ups.clear()
                    if boom_sound: boom_sound.play()
                    if boss_level:
                        level += 1
                        if level >= 10 and not dual_blasts:
                            player_size = 60
                            player_frames = load_sprite_frames("dropship", 2, player_size, player_size, WHITE)
                            player_x = WIDTH // 2 - player_size // 2
                            player_dx = 0
                            player_dy = 0
                            player_angle = 90
                            dual_blasts = True
                        aliens.clear()
                        shots.clear()
                        enemy_shots.clear()
                        battle_buddy_shots.clear()
                        power_ups.clear()
                        generate_background(level)
                        if level_up_sound: level_up_sound.play()
                        if level % 5 == 0 and boss_types:
                            spawn_alien()
                        level_up_text = [title_font.render(f"Level {level}", True, WHITE), WIDTH // 2, HEIGHT // 2, 255, level_up_duration]
                        spawn_interval = 15
                elif pu_sprite == power_up_sprites["mg94"]:
                    shot_cooldown = 5
                elif pu_sprite == power_up_sprites["eat17"]:
                    piercing_shot = True
                    piercing_shot_timer = 300
                elif pu_sprite == power_up_sprites["shield"]:
                    shield_active = True
                    shield_timer = 300
                elif pu_sprite == power_up_sprites["trishot"]:
                    trishot = True
                    trishot_timer = 300
                elif pu_sprite == power_up_sprites["quad"]:
                    quad_shot = True
                    quad_shot_timer = 300
                elif pu_sprite == power_up_sprites["burst"]:
                    burst_mode = True
                    burst_timer = 300
                elif pu_sprite == power_up_sprites["eagle_sweat"]:
                    eagle_sweat_active = True
                    eagle_sweat_timer = 600
                    if eagle_sweat_sound: eagle_sweat_sound.play()
                elif pu_sprite == power_up_sprites["battle_buddy"]:
                    battle_buddy_active = True
                    battle_buddy_timer = 1800
                    battle_buddy_shot_timer = battle_buddy_shot_cooldown
                    if battle_buddy_sound: battle_buddy_sound.play()

        shot_timer = max(0, shot_timer - 1)
        if double_shot_timer > 0:
            double_shot_timer -= 1
            if double_shot_timer <= 0: double_shot = False
        if piercing_shot_timer > 0:
            piercing_shot_timer -= 1
            if piercing_shot_timer <= 0: piercing_shot = False
        if trishot_timer > 0:
            trishot_timer -= 1
            if trishot_timer <= 0: trishot = False
        if quad_shot_timer > 0:
            quad_shot_timer -= 1
            if quad_shot_timer <= 0: quad_shot = False
        if burst_timer > 0:
            burst_timer -= 1
            if burst_timer <= 0: burst_mode = False
        if shield_timer > 0:
            shield_timer -= 1
            if shield_timer <= 0: shield_active = False
        if eagle_sweat_timer > 0:
            eagle_sweat_timer -= 1
            if eagle_sweat_timer <= 0: eagle_sweat_active = False

        if level_up_text:
            text_surface, x, y, alpha, timer = level_up_text
            y -= 2
            alpha -= 255 // level_up_duration
            timer -= 1
            if timer <= 0 or alpha <= 0:
                level_up_text = None
            else:
                level_up_text = [text_surface, x, y, max(0, alpha), timer]

        for lst, to_remove in [(aliens, aliens_to_remove), (shots, shots_to_remove), 
                               (enemy_shots, enemy_shots_to_remove), (battle_buddy_shots, battle_buddy_shots_to_remove), 
                               (power_ups, power_ups_to_remove)]:
            for item in to_remove:
                if item in lst: lst.remove(item)
        shots.extend(shots_to_add)

        for star in stars: star.move()
        if planet_surface: planet_surface.move()

        screen.fill((10, 10, 20))  # Base layer, covered by PlanetSurface
        for star in stars: star.draw(screen)
        if planet_surface: planet_surface.draw(screen)

        rotated_player = pygame.transform.rotate(player_frames[player_frame], player_angle - 90)
        player_rect = rotated_player.get_rect(center=(player_x + player_size // 2, player_y + player_size // 2))
        draw_glow(screen, player_x, player_y, player_size, RED if divers_rescued < 3 else WHITE)
        screen.blit(rotated_player, player_rect.topleft)
        if shield_active:
            pygame.draw.rect(screen, BLUE, (player_x - 5, player_y - 5, player_size + 10, player_size + 10), 2)

        if battle_buddy_active:
            draw_glow(screen, battle_buddy_x, battle_buddy_y, battle_buddy_size, NEON_GREEN)
            screen.blit(battle_buddy_sprite, (battle_buddy_x, battle_buddy_y))

        for alien in aliens:
            x, y, frames, _, frame = alien[0], alien[1], alien[2], alien[3], alien[-2]
            size = boss_size if len(alien) == 7 else alien_size
            draw_glow(screen, x, y, size, YELLOW, is_enemy=True)
            if frame < len(frames):
                screen.blit(frames[frame], (x, y))

        for shot in shots:
            shot_x, shot_y, _, dx, dy = shot
            pygame.draw.line(screen, YELLOW, (shot_x, shot_y), (shot_x + dx * 0.5, shot_y + dy * 0.5), shot_width)
            pygame.draw.line(screen, ORANGE, (shot_x + dx * 0.5, shot_y + dy * 0.5), (shot_x + dx, shot_y + dy), shot_width - 1)

        for b_shot in battle_buddy_shots:
            shot_x, shot_y, dx, dy = b_shot
            pygame.draw.line(screen, NEON_GREEN, (shot_x, shot_y), (shot_x + dx * 0.5, shot_y + dy * 0.5), shot_width)
            pygame.draw.line(screen, CYAN, (shot_x + dx * 0.5, shot_y + dy * 0.5), (shot_x + dx, shot_y + dy), shot_width - 1)

        for e_shot in enemy_shots:
            e_x, e_y, dx, dy, lifetime = e_shot
            end_x = e_x + dx * enemy_shot_length / enemy_shot_speed
            end_y = e_y + dy * enemy_shot_length / enemy_shot_speed
            gradient_surf = pygame.Surface((enemy_shot_length * 2, enemy_shot_width * 3), pygame.SRCALPHA)
            for i in range(enemy_shot_length):
                alpha = int(255 * (lifetime / 120) * (1 - i / enemy_shot_length))
                pygame.draw.line(gradient_surf, (255, 0, 0, alpha), (i * 2, 0), (i * 2, enemy_shot_width * 3))
                if i > enemy_shot_length // 4 and i < enemy_shot_length * 3 // 4:
                    core_alpha = int(255 * (lifetime / 120))
                    pygame.draw.line(gradient_surf, (255, 255, 255, core_alpha), (i * 2, enemy_shot_width), (i * 2, enemy_shot_width * 2))
            angle = math.degrees(math.atan2(dy, dx))
            gradient_surf = pygame.transform.rotate(gradient_surf, -angle)
            screen.blit(gradient_surf, gradient_surf.get_rect(center=(e_x, e_y)).topleft)
            glow_surf = pygame.Surface((enemy_shot_width * 6, enemy_shot_width * 6), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 0, 0, 100), (enemy_shot_width * 3, enemy_shot_width * 3), enemy_shot_width * 3)
            screen.blit(glow_surf, (e_x - enemy_shot_width * 3, e_y - enemy_shot_width * 3))

        for pu in power_ups:
            draw_glow(screen, pu[0], pu[1], power_up_size, WHITE)
            screen.blit(pu[2], (pu[0], pu[1]))

        if level_up_text:
            text_surface, x, y, alpha, _ = level_up_text
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, text_surface.get_rect(center=(x, y)))

        if eagle_sweat_active:
            sweat_text = font.render("Eagle Sweat Active!", True, YELLOW)
            screen.blit(sweat_text, (WIDTH // 2 - sweat_text.get_width() // 2, HEIGHT - 30))
        if battle_buddy_active:
            buddy_text = font.render("Battle Buddy Active!", True, NEON_GREEN)
            screen.blit(buddy_text, (WIDTH // 2 - buddy_text.get_width() // 2, HEIGHT - 50))

        for alien in aliens:
            if len(alien) == 7:
                health = alien[4]
                max_health, _, _ = get_boss_difficulty(level, base_level)
                pygame.draw.rect(screen, RED, (WIDTH - 210, 10, 200, 20))
                pygame.draw.rect(screen, GREEN, (WIDTH - 210, 10, 200 * (health / max_health), 20))
                screen.blit(font.render(f"Boss HP: {health}/{max_health}", True, WHITE), (WIDTH - 210, 35))
                break

        screen.blit(font.render(f"Points: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"High: {high_score}", True, WHITE), (10, 40))
        screen.blit(font.render(f"Divers Rescued: {divers_rescued}", True, WHITE), (10, 70))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 100))
        pygame.draw.rect(screen, RED, (10, 130, 100, 10))
        pygame.draw.rect(screen, GREEN, (10, 130, 100 * (player_health / PLAYER_MAX_HEALTH), 10))
        screen.blit(font.render(f"HP: {player_health}/{PLAYER_MAX_HEALTH}", True, WHITE), (10, 145))
        screen.blit(font.render(f"Kill Streak: {kill_streak}", True, WHITE), (10, 175))
        screen.blit(font.render(f"Best Streak: {highest_kill_streak}", True, WHITE), (10, 205))
        screen.blit(font.render(f"Capture Streak: {capture_streak}", True, WHITE), (10, 235))
        screen.blit(font.render(f"Best Capture: {highest_capture_streak}", True, WHITE), (10, 265))

        pygame.display.flip()
        clock.tick(60)

    if divers_rescued <= 0:
        if music_enabled: pygame.mixer.music.stop()
        return game_over_screen(score, kill_streak, highest_kill_streak, capture_streak, highest_capture_streak)
    return False

game_active = True
generate_background(level)
while game_active:
    try:
        if start_screen():
            game_result = run_game()
            if game_result is True:
                continue
            else:
                game_active = False
        else:
            game_active = False
    except Exception as e:
        log(f"Main loop error: {e}")
        game_active = False

log("Exiting Eagle Strike...")
if music_enabled: pygame.mixer.music.stop()
pygame.joystick.quit()
pygame.quit()