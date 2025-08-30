# Enhanced Car Shooter with Beautiful Transparent Walls (Boost Toggle Fixed)
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Game constants - INCREASED GRID SIZE
GRID_SIZE = 1500
GRID_STEP = 50
CAR_SIZE = 30
BULLET_SPEED = 1200
MAX_BULLETS = 50
JUMP_HEIGHT = 80
JUMP_DURATION = 30
WALL_HEIGHT = 150
NORMAL_SPEED = 200
BOOST_SPEED = 400
ROTATION_SPEED = 90
GUN_ROTATION_SPEED = 60

# Camera variables
camera_mode = 'third_person'
camera_angle = 0
camera_height = 600
camera_distance = 500
camera_zoom = 1.0
camera_shake_timer = 0
camera_shake_intensity = 0

# Player car variables
player_pos = [0, 0, 0]
player_rotation = 0
gun_rotation = 0
car_speed = NORMAL_SPEED
is_jumping = False
jump_timer = 0
jump_start_y = 0

# Bullets and collectibles
bullets = []
bullet_count = MAX_BULLETS
bullet_collectibles = []

# Input state
keys_pressed = set()
mouse_buttons = set()

# Time tracking
last_time = 0

# --- BOOST TOGGLE STATE ---
boost_active = False
shift_down = False
w_down = False
boost_toggle_ready = True

# --- ENEMY ENTITIES ---
MAX_ENEMY_CARS = 5
enemy_cars = []  # [x, y, z, rotation, health, fire_cooldown, touch_timer]
ENEMY_CAR_SIZE = 50 # Increased for visibility

MAX_HUMAN_ENEMIES = 6
human_enemies = []  # [x, y, z, touch_timer]
HUMAN_SIZE = 60  # Increased for visibility

MAX_TURRETS = 3
turrets = []  # [x, y, z, rotation, fire_cooldown, health]
TURRET_SIZE = 40  # Increased for visibility

MAX_MINE_BOTS = 4
mine_bots = []  # [x, y, z]
MINE_SIZE = 18  # Increased for visibility

player_health = 100

# --- ENEMY BULLETS ---
enemy_bullets = []  # [x, y, z, vx, vy, vz, damage]

# Enemy firing ranges
CAR_FIRE_RANGE = 200
HUMAN_FIRE_RANGE = 200
TURRET_FIRE_RANGE = 100


# Add these constants at the top with other constants
MOUNTAIN_SIZE = 200
TREE_SIZE = 80

# Add these global variables with other game variables
mountains = []  # [x, y, z, height, width]
trees = []      # [x, y, z, trunk_height, crown_size]

# --- PIT HOLE FEATURE ---

PIT_RADIUS = 60  # Slightly bigger than car
pit_hole = None  # [x, z]
pit_holes = []

# Cheat mode variables
cheat_mode = False
cheat_target = None  # Current target enemy [type, index]
auto_fire_cooldown = 0
cheat_move_override = False  # When True, auto-movement takes priority


first_person_cheat_mode = False
fp_cheat_target = None
fp_auto_fire_cooldown = 0
fp_movement_override = False  

score = 0

health_collectibles = []

GAME_TIME_LIMIT = 180 # 3 minutes in seconds
game_timer = GAME_TIME_LIMIT
game_over = False

MAX_TIME_PICKUPS = 5
time_pickups = []  # [x, y, z, float_dir, float_speed, rotation]
TIME_PICKUP_AMOUNT = 20  # seconds added per pickup

game_over_spin_speed = 0  # Car spinning speed when game over
game_over_message_timer = 0 

level_up = False
shield_active = False
SHIELD_RADIUS = 80  # Adjust as needed for visual size

shield_rotation = 0.0
def reset_game():
    global player_pos, player_rotation, gun_rotation, bullets, bullet_count
    global camera_mode, camera_angle, camera_height, camera_zoom, is_jumping, jump_timer
    global boost_active, shift_down, w_down, boost_toggle_ready, keys_pressed
    global enemy_cars, human_enemies, turrets, mine_bots, player_health, enemy_bullets
    global mountains, trees
    global pit_holes
    global cheat_mode, cheat_target, auto_fire_cooldown, cheat_move_override  
    global first_person_cheat_mode, fp_cheat_target, fp_auto_fire_cooldown, fp_movement_override  
    global score
    global game_timer, game_over, game_over_spin_speed, game_over_message_timer  
    global level_up, shield_active

    level_up = False
    shield_active = False
    score = 0
    player_pos = [0, 0, 0]
    player_rotation = 0
    gun_rotation = 0
    bullets = []
    bullet_count = MAX_BULLETS

    camera_mode = 'third_person'
    camera_angle = 0
    camera_height = 600
    camera_zoom = 1.0
    is_jumping = False
    jump_timer = 0

    boost_active = False
    shift_down = False
    w_down = False
    boost_toggle_ready = True
    keys_pressed.clear()

    # Reset cheat mode
    cheat_mode = False
    cheat_target = None
    auto_fire_cooldown = 0
    cheat_move_override = False

    # Reset first person cheat mode
    first_person_cheat_mode = False
    fp_cheat_target = None
    fp_auto_fire_cooldown = 0
    fp_movement_override = False

    game_timer = GAME_TIME_LIMIT
    game_over = False
    game_over_spin_speed = 0      
    game_over_message_timer = 0   
    generate_time_pickups()

    # Spawn obstacles first
    spawn_mountains()
    spawn_trees()
    
    enemy_cars = []
    for _ in range(MAX_ENEMY_CARS):
        spawn_enemy_car()
    human_enemies = []
    for _ in range(MAX_HUMAN_ENEMIES):
        spawn_human_enemy()
    turrets = []
    for _ in range(MAX_TURRETS):
        spawn_turret()
    mine_bots = []
    for _ in range(MAX_MINE_BOTS):
        spawn_mine_bot()
    
    enemy_bullets.clear()
    player_health = 100

    generate_bullet_collectibles() 
    generate_health_collectibles()
    spawn_pit_holes(3) 
    print(f"Game Reset! Bullet Count: {bullet_count}")
    print(f"Spawned {len(mountains)} mountains and {len(trees)} trees")
    print(f"Game Reset! Bullet Count: {bullet_count}")
    print(f"Spawned {len(mountains)} mountains and {len(trees)} trees")

def spawn_time_pickup():
    x = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
    z = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
    time_pickups.append([x, 15, z, 1, 10, 0])

def generate_time_pickups():
    global time_pickups
    time_pickups = []
    for _ in range(MAX_TIME_PICKUPS):
        spawn_time_pickup()

def draw_time_pickup(x, y, z, rotation):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)
    glColor3f(1.0, 0.2, 0.8)  # Pink color
    quad = gluNewQuadric()      
    gluSphere(quad, 10, 12, 12)
    # Draw a white clock face (optional)
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glScalef(2, 8, 2)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glScalef(8, 2, 2)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

def update_time_pickups(delta_time):
    global time_pickups, game_timer
    for pickup in time_pickups[:]:
        x, y, z, float_dir, float_speed, rotation = pickup
        # Float animation
        y += float_dir * float_speed * delta_time
        if y > 25:
            float_dir = -1
        elif y < 5:
            float_dir = 1
        rotation += 90 * delta_time
        pickup[1] = y
        pickup[3] = float_dir
        pickup[5] = rotation

        # Check collection
        dx = player_pos[0] - x
        dz = player_pos[2] - z
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < 30:
            time_pickups.remove(pickup)
            game_timer += TIME_PICKUP_AMOUNT
            print(f"Time pickup collected! +{TIME_PICKUP_AMOUNT}s, Timer: {int(game_timer)}s")
            spawn_time_pickup()

def find_nearest_enemy():
    """Find the nearest enemy to the player"""
    nearest_distance = float('inf')
    nearest_enemy = None
    
    # Check enemy cars
    for i, ec in enumerate(enemy_cars):
        dx = player_pos[0] - ec[0]
        dz = player_pos[2] - ec[2]
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = ('car', i, distance)
    
    # Check human enemies
    for i, he in enumerate(human_enemies):
        dx = player_pos[0] - he[0]
        dz = player_pos[2] - he[2]
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = ('human', i, distance)
    
    # Check turrets
    for i, t in enumerate(turrets):
        dx = player_pos[0] - t[0]
        dz = player_pos[2] - t[2]
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = ('turret', i, distance)
    
    # Check mine bots
    for i, mb in enumerate(mine_bots):
        dx = player_pos[0] - mb[0]
        dz = player_pos[2] - mb[2]
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = ('mine', i, distance)
    
    return nearest_enemy

def get_safe_movement_direction(target_x, target_z):
    """Calculate safe movement direction avoiding obstacles"""
    current_x, current_z = player_pos[0], player_pos[2]
    direct_dx = target_x - current_x
    direct_dz = target_z - current_z
    
    # Normalize direction
    distance = math.sqrt(direct_dx*direct_dx + direct_dz*direct_dz)
    if distance < 1:
        return None, None
    
    direct_dx /= distance
    direct_dz /= distance
    
    # Check if direct path is safe
    test_distance = min(100, distance)
    test_x = current_x + direct_dx * test_distance
    test_z = current_z + direct_dz * test_distance
    
    if is_position_safe(test_x, test_z):
        return direct_dx, direct_dz
    
    # Try alternative angles if direct path is blocked
    for angle_offset in [45, -45, 90, -90, 135, -135]:
        angle_rad = math.atan2(direct_dx, direct_dz) + math.radians(angle_offset)
        alt_dx = math.sin(angle_rad)
        alt_dz = math.cos(angle_rad)
        
        alt_test_x = current_x + alt_dx * test_distance
        alt_test_z = current_z + alt_dz * test_distance
        
        if is_position_safe(alt_test_x, alt_test_z):
            return alt_dx, alt_dz
    
    return None, None

def is_position_safe(x, z):
    """Check if a position is safe from obstacles"""
    # Check boundaries
    if abs(x) >= GRID_SIZE - CAR_SIZE or abs(z) >= GRID_SIZE - CAR_SIZE:
        return False
    
    # Check mountains
    if check_mountain_collision(x, z):
        return False
    
    # Check trees
    if check_tree_collision(x, z):
        return False
    
    # Check pit holes
    for pit in pit_holes:
        dx = x - pit[0]
        dz = z - pit[1]
        if math.sqrt(dx*dx + dz*dz) < PIT_RADIUS + CAR_SIZE:
            return False
    
    # Check mine bots (avoid getting too close)
    for mb in mine_bots:
        dx = x - mb[0]
        dz = z - mb[2]
        if math.sqrt(dx*dx + dz*dz) < MINE_SIZE * 2 + CAR_SIZE:
            return False
    
    return True

def update_cheat_mode(delta_time):
    global gun_rotation, player_rotation, cheat_target, auto_fire_cooldown, cheat_move_override

    if not cheat_mode or camera_mode == 'first_person':
        return

    # Find target
    cheat_target = find_nearest_enemy()
    if not cheat_target:
        cheat_move_override = False
        return

    enemy_type, enemy_index, distance = cheat_target

    # Get enemy position and speed
    if enemy_type == 'car' and enemy_index < len(enemy_cars):
        target_pos = enemy_cars[enemy_index]
        enemy_speed = 35
    elif enemy_type == 'human' and enemy_index < len(human_enemies):
        target_pos = human_enemies[enemy_index]
        enemy_speed = 12
    elif enemy_type == 'turret' and enemy_index < len(turrets):
        target_pos = turrets[enemy_index]
        enemy_speed = 0
    elif enemy_type == 'mine' and enemy_index < len(mine_bots):
        target_pos = mine_bots[enemy_index]
        enemy_speed = 18
    else:
        cheat_move_override = False
        return

    target_x, target_z = target_pos[0], target_pos[2]
    dx = target_x - player_pos[0]
    dz = target_z - player_pos[2]

    # Predictive aiming for moving targets
    enemy_vx = enemy_vz = 0
    if enemy_type in ('car', 'human', 'mine'):
        enemy_angle = math.atan2(dx, dz)
        enemy_vx = math.sin(enemy_angle) * enemy_speed
        enemy_vz = math.cos(enemy_angle) * enemy_speed

    bullet_travel_time = distance / BULLET_SPEED
    predicted_x = target_x + enemy_vx * bullet_travel_time
    predicted_z = target_z + enemy_vz * bullet_travel_time

    predicted_dx = predicted_x - player_pos[0]
    predicted_dz = predicted_z - player_pos[2]
    target_angle = math.degrees(math.atan2(predicted_dx, predicted_dz))

    # In third person, rotate the gun
    target_gun_rotation = target_angle - player_rotation
    while target_gun_rotation > 180:
        target_gun_rotation -= 360
    while target_gun_rotation < -180:
        target_gun_rotation += 360

    angle_diff = target_gun_rotation - gun_rotation
    while angle_diff > 180:
        angle_diff -= 360
    while angle_diff < -180:
        angle_diff += 360

    rotation_speed = GUN_ROTATION_SPEED * 1.5
    if abs(angle_diff) > rotation_speed * delta_time:
        if angle_diff > 0:
            gun_rotation += rotation_speed * delta_time
        else:
            gun_rotation -= rotation_speed * delta_time
    else:
        gun_rotation = target_gun_rotation

    # Auto-fire
    auto_fire_cooldown -= delta_time
    if auto_fire_cooldown <= 0 and distance < 800:
        # Only fire if gun is well-aimed
        aim_error = target_gun_rotation - gun_rotation
        while aim_error > 180:
            aim_error -= 360
        while aim_error < -180:
            aim_error += 360
        aim_threshold = 3  # degrees
        if abs(aim_error) < aim_threshold:
            fire_bullet()
            auto_fire_cooldown = 0.5

    # Auto-movement (same as before)
    manual_input = any(key in keys_pressed for key in [ord('W'), ord('w'), ord('A'), ord('a'), ord('S'), ord('s'), ord('D'), ord('d')])
    if not manual_input and distance > 200:
        safe_dx, safe_dz = get_safe_movement_direction(target_x, target_z)
        if safe_dx is not None and safe_dz is not None:
            cheat_move_override = True
            movement_angle = math.degrees(math.atan2(safe_dx, safe_dz))
            angle_diff = movement_angle - player_rotation
            while angle_diff > 180:
                angle_diff -= 360
            while angle_diff < -180:
                angle_diff += 360
            if abs(angle_diff) > ROTATION_SPEED * delta_time:
                if angle_diff > 0:
                    player_rotation += ROTATION_SPEED * delta_time
                else:
                    player_rotation -= ROTATION_SPEED * delta_time
            angle_rad = math.radians(player_rotation)
            new_x = player_pos[0] + math.sin(angle_rad) * car_speed * delta_time
            new_z = player_pos[2] + math.cos(angle_rad) * car_speed * delta_time
            if is_position_safe(new_x, new_z):
                player_pos[0] = new_x
                player_pos[2] = new_z
        else:
            cheat_move_override = False
    else:
        cheat_move_override = False


def is_path_clear(start_x, start_z, end_x, end_z, step_size=20):
    """Check if path from start to end position is clear of obstacles"""
    dx = end_x - start_x
    dz = end_z - start_z
    distance = math.sqrt(dx*dx + dz*dz)
    
    if distance < step_size:
        return is_position_safe(end_x, end_z)
    
    steps = int(distance / step_size)
    step_dx = dx / steps
    step_dz = dz / steps
    
    for i in range(1, steps + 1):
        test_x = start_x + step_dx * i
        test_z = start_z + step_dz * i
        if not is_position_safe(test_x, test_z):
            return False
    
    return True

def update_first_person_cheat_mode(delta_time):
    """Handle first person cheat mode logic - targets car, human, turret, or mine"""
    global gun_rotation, player_rotation, fp_cheat_target, fp_auto_fire_cooldown, fp_movement_override

    if not first_person_cheat_mode or camera_mode != 'first_person':
        fp_movement_override = False
        return

    fp_cheat_target = find_nearest_enemy_for_fp_cheat()
    if not fp_cheat_target:
        fp_movement_override = False
        return

    enemy_type, enemy_index, distance = fp_cheat_target

    # Get enemy position and speed
    if enemy_type == 'car' and enemy_index < len(enemy_cars):
        target_pos = enemy_cars[enemy_index]
        enemy_speed = 35
    elif enemy_type == 'human' and enemy_index < len(human_enemies):
        target_pos = human_enemies[enemy_index]
        enemy_speed = 12
    elif enemy_type == 'turret' and enemy_index < len(turrets):
        target_pos = turrets[enemy_index]
        enemy_speed = 0   # stationary
    elif enemy_type == 'mine' and enemy_index < len(mine_bots):
        target_pos = mine_bots[enemy_index]
        enemy_speed = 18
    else:
        fp_movement_override = False
        return

    target_x, target_z = target_pos[0], target_pos[2]
    dx = target_x - player_pos[0]
    dz = target_z - player_pos[2]

    # Predictive aiming for moving targets, direct for stationary
    enemy_vx = enemy_vz = 0
    if enemy_type in ('car', 'human', 'mine'):
        # They move directly toward player at their speed
        enemy_angle = math.atan2(dx, dz)
        enemy_vx = math.sin(enemy_angle) * enemy_speed
        enemy_vz = math.cos(enemy_angle) * enemy_speed
    # turrets: vx, vz = 0

    # Predict time for bullet to reach target
    bullet_travel_time = distance / BULLET_SPEED
    predicted_x = target_x + enemy_vx * bullet_travel_time
    predicted_z = target_z + enemy_vz * bullet_travel_time

    predicted_dx = predicted_x - player_pos[0]
    predicted_dz = predicted_z - player_pos[2]
    target_angle = math.degrees(math.atan2(predicted_dx, predicted_dz))

    # Rotate car (and gun) smoothly toward target
    angle_diff = target_angle - player_rotation
    while angle_diff > 180:
        angle_diff -= 360
    while angle_diff < -180:
        angle_diff += 360

    rotation_speed = GUN_ROTATION_SPEED * 2  # Faster rotation for cheat
    if abs(angle_diff) > rotation_speed * delta_time:
        if angle_diff > 0:
            player_rotation += rotation_speed * delta_time
        else:
            player_rotation -= rotation_speed * delta_time
    else:
        player_rotation = target_angle

    gun_rotation = 0  # Always zero in first person

    # Auto-fire: only when well-aimed at predicted position
    fp_auto_fire_cooldown -= delta_time
    if fp_auto_fire_cooldown <= 0 and distance < 800:
        # Calculate current aim direction
        current_aim_angle = player_rotation  # gun_rotation is always 0
        aim_error = target_angle - current_aim_angle
        while aim_error > 180:
            aim_error -= 360
        while aim_error < -180:
            aim_error += 360
        aim_threshold = 3  # degrees
        if abs(aim_error) < aim_threshold:
            fire_bullet()
            fp_auto_fire_cooldown = 0.3

    # Auto-movement - only if no manual input detected
    manual_input = any(key in keys_pressed for key in [ord('W'), ord('w'), ord('A'), ord('a'), ord('S'), ord('s'), ord('D'), ord('d')])
    if not manual_input:
        move_forward = True
        if distance < 150:
            move_forward = False
        elif distance > 400:
            move_forward = True
        if move_forward and is_path_clear(player_pos[0], player_pos[2], target_x, target_z):
            fp_movement_override = True
            angle_rad = math.radians(player_rotation)
            move_speed = NORMAL_SPEED if distance > 200 else NORMAL_SPEED * 0.5
            new_x = player_pos[0] + math.sin(angle_rad) * move_speed * delta_time
            new_z = player_pos[2] + math.cos(angle_rad) * move_speed * delta_time
            if is_position_safe(new_x, new_z):
                player_pos[0] = new_x
                player_pos[2] = new_z
        elif not move_forward:
            fp_movement_override = True
            angle_rad = math.radians(player_rotation)
            new_x = player_pos[0] - math.sin(angle_rad) * NORMAL_SPEED * 0.7 * delta_time
            new_z = player_pos[2] - math.cos(angle_rad) * NORMAL_SPEED * 0.7 * delta_time
            if is_position_safe(new_x, new_z):
                player_pos[0] = new_x
                player_pos[2] = new_z
        else:
            safe_dx, safe_dz = get_safe_movement_direction_fp(target_x, target_z)
            if safe_dx is not None and safe_dz is not None:
                fp_movement_override = True
                movement_angle = math.degrees(math.atan2(safe_dx, safe_dz))
                angle_rad = math.radians(movement_angle)
                new_x = player_pos[0] + math.sin(angle_rad) * NORMAL_SPEED * delta_time
                new_z = player_pos[2] + math.cos(angle_rad) * NORMAL_SPEED * delta_time
                if is_position_safe(new_x, new_z):
                    player_pos[0] = new_x
                    player_pos[2] = new_z
            else:
                fp_movement_override = False
    else:
        fp_movement_override = False


def find_nearest_enemy_for_fp_cheat():
    """Find nearest enemy car, human, turret, or mine for first person cheat mode"""
    nearest_distance = float('inf')
    nearest_enemy = None
    for i, ec in enumerate(enemy_cars):
        dx = player_pos[0] - ec[0]
        dz = player_pos[2] - ec[2]
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = ('car', i, distance)
    for i, he in enumerate(human_enemies):
        dx = player_pos[0] - he[0]
        dz = player_pos[2] - he[2]
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = ('human', i, distance)
    for i, t in enumerate(turrets):
        dx = player_pos[0] - t[0]
        dz = player_pos[2] - t[2]
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = ('turret', i, distance)
    for i, mb in enumerate(mine_bots):
        dx = player_pos[0] - mb[0]
        dz = player_pos[2] - mb[2]
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = ('mine', i, distance)
    return nearest_enemy


def get_safe_movement_direction_fp(target_x, target_z):
    """Calculate safe movement direction for first person cheat mode"""
    current_x, current_z = player_pos[0], player_pos[2]
    
    # Try multiple directions to find a safe path
    for angle_offset in [45, -45, 90, -90, 135, -135, 180]:
        angle_rad = math.atan2(target_x - current_x, target_z - current_z) + math.radians(angle_offset)
        test_dx = math.sin(angle_rad)
        test_dz = math.cos(angle_rad)
        
        test_distance = 100
        test_x = current_x + test_dx * test_distance
        test_z = current_z + test_dz * test_distance
        
        if is_position_safe(test_x, test_z) and is_path_clear(current_x, current_z, test_x, test_z):
            return test_dx, test_dz
    
    return None, None

def generate_health_collectibles():
    global health_collectibles
    health_collectibles = []
    for _ in range(12):  # 12 health pickups as requested
        x = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
        z = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
        # Same structure as bullet collectibles: [x, y, z, float_dir, float_speed, rotation]
        health_collectibles.append([x, 15, z, 1, 10, 0])

def draw_health_collectible(x, y, z, rotation):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)
    # Purple outer sphere
    glColor3f(0.5, 0.0, 0.8)  # Purple color
    quad = gluNewQuadric()
    gluSphere(quad, 10, 12, 12)
    # White inner cross/plus symbol for health
    glColor3f(1.0, 1.0, 1.0)
    # Vertical bar of cross
    glPushMatrix()
    glScalef(2, 8, 2)
    glutSolidCube(1)
    glPopMatrix()
    # Horizontal bar of cross
    glPushMatrix()
    glScalef(8, 2, 2)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

def update_health_collectibles(delta_time):
    """Update health collectibles: float up/down, rotate, and handle collection"""
    global health_collectibles, player_health
    for collectible in health_collectibles[:]:
        x, y, z, float_dir, float_speed, rotation = collectible
        # Float animation
        y += float_dir * float_speed * delta_time
        if y > 25:
            float_dir = -1
        elif y < 5:
            float_dir = 1
        rotation += 90 * delta_time
        collectible[1] = y
        collectible[3] = float_dir
        collectible[5] = rotation
        
        # Check collection
        dx = player_pos[0] - x
        dz = player_pos[2] - z
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < 30:  # Same collection distance as bullets
            health_collectibles.remove(collectible)
            # Increase health but cap at 100
            old_health = player_health
            player_health = min(100, player_health + 20)  # +20 health per pickup
            print(f"Health collected! Health: {old_health} -> {player_health}")

def generate_bullet_collectibles():
    global bullet_collectibles
    bullet_collectibles = []
    for _ in range(15):
        x = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
        z = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
        bullet_collectibles.append([x, 15, z, 1, 10, 0])

# --- ENEMY SPAWN --------------------------------------------------------------2
def spawn_enemy_car():
    x = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
    z = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
    enemy_cars.append([x, 0, z, random.uniform(0, 360), 2, 0, 0])

def spawn_human_enemy():
    x = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
    z = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
    # Now includes fire_cooldown (index 4) and rotation (index 5)
    human_enemies.append([x, 0, z, 0, 0, 0])

def spawn_turret():
    x = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
    z = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
    turrets.append([x, 0, z, 0, 0, 3])

def spawn_mine_bot():
    x = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
    z = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
    mine_bots.append([x, 0, z])

# --- ENEMY BULLET LOGIC ---
def fire_enemy_bullet(x, y, z, angle_deg, speed=400, damage=10):
    angle_rad = math.radians(angle_deg)
    vx = math.sin(angle_rad) * speed
    vz = math.cos(angle_rad) * speed
    vy = 0
    enemy_bullets.append([x, y, z, vx, vy, vz, damage])

def update_enemy_bullets(dt):
    global enemy_bullets, player_health
    updated = []
    for b in enemy_bullets:
        b[0] += b[3] * dt
        b[1] += b[4] * dt
        b[2] += b[5] * dt
        dx = player_pos[0] - b[0]
        dz = player_pos[2] - b[2]
        dist = math.sqrt(dx*dx + dz*dz)
        if dist < CAR_SIZE:
            player_health -= b[6]
            print(f"Player hit! Health: {player_health}")
            continue
        if abs(b[0]) < GRID_SIZE and abs(b[2]) < GRID_SIZE:
            updated.append(b)
    enemy_bullets = updated

def draw_enemy_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.2, 0.2)
    quad = gluNewQuadric()
    gluSphere(quad,6, 10, 10)
    glPopMatrix()


#-----------------------------------------------------------------------------------1
# --- ENEMY LOGIC ---
def update_enemy_cars(dt):
    global enemy_cars, player_health ,score
    for ec in enemy_cars:
        dx = player_pos[0] - ec[0]
        dz = player_pos[2] - ec[2]
        dist = math.sqrt(dx*dx + dz*dz)
        if shield_active and dist < SHIELD_RADIUS + ENEMY_CAR_SIZE/2:
            # Respawn enemy car
            ec[0] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
            ec[2] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
            ec[4] = 2
            score += 10
            print("Enemy car destroyed by shield!")
            continue
        if dist > 1:
            angle = math.atan2(dx, dz)
            ec[3] = math.degrees(angle)
            speed = 35
            ec[0] += math.sin(angle) * speed * dt
            ec[2] += math.cos(angle) * speed * dt
        # Fire at player if close
        if dist < CAR_FIRE_RANGE and ec[5] <= 0:
            fire_enemy_bullet(ec[0], ec[1]+ENEMY_CAR_SIZE/2, ec[2], ec[3], speed=1200, damage=2)
            ec[5] = 4.0
        if ec[5] > 0:
            ec[5] -= dt
        # Touch logic
        if dist < ENEMY_CAR_SIZE + CAR_SIZE:
            ec[6] += dt #timer for contact damage
            if ec[6] > 5:
                if not shield_active:
                   player_health -= 2
                ec[6] = 0
        else:
            ec[6] = 0  # 5s exceed hole player life loss, ar abar ec er contact time 0 kore dei

def update_human_enemies(dt):
    global human_enemies, player_health, score
    for he in human_enemies:
        dx = player_pos[0] - he[0]
        dz = player_pos[2] - he[2]
        dist = math.sqrt(dx*dx + dz*dz)
        # Shield collision
        if shield_active and dist < SHIELD_RADIUS + HUMAN_SIZE/2:
            he[0] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
            he[2] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
            score += 15
            print("Human enemy destroyed by shield!")
            continue
        # Calculate rotation to face player
        if dist > 1:
            he[5] = math.degrees(math.atan2(dx, dz))  # Update rotation
            
            # Move towards player (but slower than before to make them more tactical)
            angle = math.atan2(dx, dz)
            speed = 12  # Reduced speed since they can now shoot
            he[0] += math.sin(angle) * speed * dt
            he[2] += math.cos(angle) * speed * dt
        
        # Fire at player if within range
        if dist < HUMAN_FIRE_RANGE and he[4] <= 0:  # 400 unit firing range
            fire_enemy_bullet(he[0], he[1] + HUMAN_SIZE/2, he[2], he[5], speed=1250, damage=2)
            he[4] = 3  # 1.5 second cooldown between shots
            print("Human enemy fired!")
        
        # Update fire cooldown
        if he[4] > 0:
            he[4] -= dt
        
        # Touch damage (reduced since they can now shoot)
        if dist < HUMAN_SIZE + CAR_SIZE:
            if not (ord('W') in keys_pressed or ord('w') in keys_pressed or
                    ord('A') in keys_pressed or ord('a') in keys_pressed or
                    ord('S') in keys_pressed or ord('s') in keys_pressed or
                    ord('D') in keys_pressed or ord('d') in keys_pressed):
                he[3] += dt
                if he[3] > 4:  # Increased time before touch damage
                    if not shield_active:
                        player_health -= 3  # Reduced touch damage since they can shoot
                    he[3] = 0
            else:
                he[3] = 0
        else:
            he[3] = 0

def update_turrets(dt):
    global turrets, player_health
    for t in turrets:
        dx = player_pos[0] - t[0]
        dz = player_pos[2] - t[2]
        dist = math.sqrt(dx*dx + dz*dz)
        t[3] = math.degrees(math.atan2(dx, dz))
        if dist < TURRET_FIRE_RANGE and t[4] <= 0:
            fire_enemy_bullet(t[0], t[1]+TURRET_SIZE/2, t[2], t[3], speed=1200, damage=3)
            t[4] = 4.0
        if t[4] > 0:
            t[4] -= dt

def update_mine_bots(dt):
    global mine_bots, player_health
    for mb in mine_bots[:]:
        dx = player_pos[0] - mb[0]
        dz = player_pos[2] - mb[2]
        dist = math.sqrt(dx*dx + dz*dz)
        if dist > 1:
            angle = math.atan2(dx, dz)
            speed = 18
            mb[0] += math.sin(angle) * speed * dt
            mb[2] += math.cos(angle) * speed * dt
        if dist < MINE_SIZE + CAR_SIZE:
            player_health -= 30
            print(f"Mine explosion! Player health: {player_health}")
            mine_bots.remove(mb)
            spawn_mine_bot()

# --- PLAYER BULLET LOGIC (FIXED - with enemy hit detection) ---
def update_bullets(delta_time):
    global bullets, enemy_cars, human_enemies, turrets, mine_bots, score
    updated_bullets = []
    for bullet in bullets:
        # Move bullet
        bullet[0] += bullet[3] * delta_time
        bullet[1] += bullet[4] * delta_time
        bullet[2] += bullet[5] * delta_time
        
        hit = False
        
        # Check enemy car hit
        for ec in enemy_cars:
            dx = ec[0] - bullet[0]
            dz = ec[2] - bullet[2]
            dist = math.sqrt(dx*dx + dz*dz)
            if dist < ENEMY_CAR_SIZE/2:
                ec[4] -= 1
                print(f"Enemy car hit! Health: {ec[4]}")
                if ec[4] <= 0:
                    print("Enemy car destroyed! Respawning...")
                    ec[0] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
                    ec[2] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
                    ec[4] = 2
                    score += 10  # +10 points for car
                hit = True
                break
        
        # Check human enemy hit
        if not hit:
            for he in human_enemies:
                dx = he[0] - bullet[0]
                dz = he[2] - bullet[2]
                dist = math.sqrt(dx*dx + dz*dz)
                if dist < HUMAN_SIZE/2:
                    print("Human enemy hit! Respawning...")
                    he[0] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
                    he[2] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
                    score += 15  # +15 points for human
                    hit = True
                    break
        
        # Check turret hit
        if not hit:
            for t in turrets:
                dx = t[0] - bullet[0]
                dz = t[2] - bullet[2]
                dist = math.sqrt(dx*dx + dz*dz)
                if dist < TURRET_SIZE/2:
                    t[5] -= 1
                    print(f"Turret hit! Health: {t[5]}")
                    if t[5] <= 0:
                        print("Turret destroyed! Respawning...")
                        t[0] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
                        t[2] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
                        t[5] = 3
                        score += 20  # +20 points for turret
                    hit = True
                    break
        
        # Check mine bot hit
        if not hit: # means true 
            for mb in mine_bots:
                dx = mb[0] - bullet[0]
                dz = mb[2] - bullet[2]
                dist = math.sqrt(dx*dx + dz*dz)
                if dist < MINE_SIZE:
                    print("Mine bot destroyed! Respawning...")
                    mb[0] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
                    mb[2] = random.uniform(-GRID_SIZE+100, GRID_SIZE-100)
                    score += 25  # +25 points for minebot
                    hit = True
                    break
        
        if not hit and abs(bullet[0]) < GRID_SIZE and abs(bullet[2]) < GRID_SIZE:
            updated_bullets.append(bullet)
    
    bullets = updated_bullets
#---------------------------------------------------------------------------------1

def spawn_mountains():
    """Spawn 2 mountains at random locations"""
    global mountains
    mountains = []
    for _ in range(3):
        # Ensure mountains don't spawn too close to player start (0,0,0)
        while True:
            x = random.uniform(-GRID_SIZE + 300, GRID_SIZE - 300)
            z = random.uniform(-GRID_SIZE + 300, GRID_SIZE - 300)
            # Don't spawn too close to center
            if abs(x) > 200 or abs(z) > 200:
                break
        
        height = random.uniform(150, 300)
        width = random.uniform(180, 250)
        mountains.append([x, 0, z, height, width])

def spawn_trees():
    """Spawn 3 trees at random locations"""
    global trees
    trees = []
    for _ in range(3):
        # Ensure trees don't spawn too close to player start or mountains
        attempts = 0
        while attempts < 50:  # Prevent infinite loop
            x = random.uniform(-GRID_SIZE + 200, GRID_SIZE - 200)
            z = random.uniform(-GRID_SIZE + 200, GRID_SIZE - 200)
            
            # Don't spawn too close to center
            if abs(x) < 150 and abs(z) < 150:
                attempts += 1
                continue
                
            # Don't spawn too close to mountains
            too_close = False
            for mountain in mountains:
                mx, _, mz, _, mwidth = mountain
                dist = math.sqrt((x - mx)**2 + (z - mz)**2)
                if dist < mwidth/2 + TREE_SIZE:
                    too_close = True
                    break
            
            if not too_close:
                break
            attempts += 1
        
        trunk_height = random.uniform(40, 80)
        crown_size = random.uniform(60, 100)
        trees.append([x, 0, z, trunk_height, crown_size])

def check_mountain_collision(new_x, new_z):
    """Check if position collides with any mountain"""
    for mountain in mountains:
        mx, _, mz, _, mwidth = mountain
        dx = new_x - mx
        dz = new_z - mz
        dist = math.sqrt(dx*dx + dz*dz)
        if dist < mwidth/2 + CAR_SIZE:
            return True
    return False

def check_tree_collision(new_x, new_z):
    """Check if position collides with any tree"""
    for tree in trees:
        tx, _, tz, _, crown_size = tree
        dx = new_x - tx
        dz = new_z - tz
        dist = math.sqrt(dx*dx + dz*dz)
        if dist < crown_size/2 + CAR_SIZE:
            return True
    return False


def draw_mountain(x, y, z, height, base_radius):
    glPushMatrix()
    glTranslatef(x, y, z)
    quad = gluNewQuadric()

    # Main cone
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.5, 0.4, 0.3)
    gluCylinder(quad, base_radius, 0.1, height, 32, 8)
    glPopMatrix()

    # Snow cap (cone at peak)
    glPushMatrix()
    glTranslatef(0, 150, 0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(1.0, 1.0, 1.0)
    gluCylinder(quad, base_radius * 0.25, 0.0, base_radius * 0.5, 24, 4)
    glPopMatrix()

    glPopMatrix()


def draw_tree(x, y, z, trunk_height, crown_size):
    """Draw a tree using cubes and a sphere"""
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Draw trunk (brown cylinder approximated with cube)
    glColor3f(0.4, 0.2, 0.1)  # Brown
    glPushMatrix()
    glTranslatef(0, trunk_height/2, 0)
    glScalef(8, trunk_height, 8)
    glutSolidCube(1)
    glPopMatrix()
    
    # Draw crown (green sphere)
    glColor3f(0.1, 0.6, 0.1)  # Dark green
    glPushMatrix()
    glTranslatef(0, trunk_height + crown_size/3, 0)
    quad = gluNewQuadric()
    gluSphere(quad,crown_size/2, 12, 12)
    glPopMatrix()
    
    # Add some branches (small brown cubes)
    glColor3f(0.3, 0.15, 0.05)
    for angle in [0, 90, 180, 270]:
        glPushMatrix()
        glRotatef(angle, 0, 1, 0)
        glTranslatef(crown_size/4, trunk_height * 0.8, 0)
        glScalef(crown_size/8, 3, 3)
        glutSolidCube(1)
        glPopMatrix()
    
    glPopMatrix()

# --- DRAWING FUNCTIONS ---
def draw_grid():
    glColor3f(0.3, 0.7, 0.9)
    glBegin(GL_LINES)
    for x in range(-GRID_SIZE, GRID_SIZE + GRID_STEP, GRID_STEP):
        glVertex3f(x, 0, -GRID_SIZE)
        glVertex3f(x, 0, GRID_SIZE)
    for z in range(-GRID_SIZE, GRID_SIZE + GRID_STEP, GRID_STEP):
        glVertex3f(-GRID_SIZE, 0, z)
        glVertex3f(GRID_SIZE, 0, z)
    glEnd()


def spawn_pit_holes(count=3):
    """Spawn multiple pit holes randomly across the grid."""
    global pit_holes
    pit_holes = []  # reset before spawning

    attempts = 0
    while len(pit_holes) < count and attempts < 500:  # allow many attempts
        x = random.uniform(-GRID_SIZE + 300, GRID_SIZE - 300)
        z = random.uniform(-GRID_SIZE + 300, GRID_SIZE - 300)

        # Not too close to player start (0,0)
        if abs(x) < 200 and abs(z) < 200:
            attempts += 1
            continue

        # Not too close to mountains
        too_close_to_mountain = False
        for mountain in mountains:
            mx, _, mz, _, mwidth = mountain
            if math.hypot(x - mx, z - mz) < mwidth/2 + PIT_RADIUS + 50:
                too_close_to_mountain = True
                break

        # Not too close to trees
        too_close_to_tree = False
        for tree in trees:
            tx, _, tz, _, crown_size = tree
            if math.hypot(x - tx, z - tz) < crown_size/2 + PIT_RADIUS + 30:
                too_close_to_tree = True
                break

        # Not too close to other pit holes
        too_close_to_other_pit = False
        for px, pz in pit_holes:
            if math.hypot(x - px, z - pz) < PIT_RADIUS * 3:
                too_close_to_other_pit = True
                break

        if not (too_close_to_mountain or too_close_to_tree or too_close_to_other_pit):
            pit_holes.append([x, z])
            print(f"Pit hole spawned at: ({int(x)}, {int(z)})")

        attempts += 1

    # Fallbacks if not enough pits placed
    while len(pit_holes) < count:
        pit_holes.append([500 + len(pit_holes) * 100, 500])
        print(f"Pit hole spawned at fallback position: {pit_holes[-1]}")

def draw_pit_holes():
    """Draw all pit holes as colorful, rainbow-rimmed cylinders."""
    quad = gluNewQuadric()
    for pit in pit_holes:
        x, z = pit
        y = 0.1  # slightly above ground

        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(-90, 1, 0, 0)  # lie the cylinder flat on the ground

        # --- Pit body: vertical rainbow gradient cylinder ---
        num_bands = 8
        band_height = 0.2 / num_bands
        for i in range(num_bands):
            t = i / (num_bands - 1)
            angle = t * 2 * math.pi
            r = 0.5 + 0.5 * math.sin(angle)
            g = 0.5 + 0.5 * math.sin(angle + 2 * math.pi / 3)
            b = 0.5 + 0.5 * math.sin(angle + 4 * math.pi / 3)
            glColor3f(r, g, b)
            glPushMatrix()
            glTranslatef(0, 0, i * band_height)
            gluCylinder(quad, PIT_RADIUS, PIT_RADIUS, band_height, 36, 1)
            glPopMatrix()

        # --- Pit bottom: fake rainbow "disk" using spheres ---
        rim_count = 24
        for i in range(rim_count):
            angle = 2 * math.pi * i / rim_count
            px = math.cos(angle) * (PIT_RADIUS * 0.85)
            py = math.sin(angle) * (PIT_RADIUS * 0.85)
            r = 0.5 + 0.5 * math.sin(angle)
            g = 0.5 + 0.5 * math.sin(angle + 2 * math.pi / 3)
            b = 0.5 + 0.5 * math.sin(angle + 4 * math.pi / 3)
            glPushMatrix()
            glTranslatef(px, py, 0.21)
            glColor3f(r, g, b)
            gluSphere(quad, PIT_RADIUS * 0.18, 10, 10)
            glPopMatrix()

        # --- Outer rim: large rainbow spheres ---
        for i in range(rim_count):
            angle = 2 * math.pi * i / rim_count
            px = math.cos(angle) * PIT_RADIUS
            py = math.sin(angle) * PIT_RADIUS
            r = 0.5 + 0.5 * math.sin(angle)
            g = 0.5 + 0.5 * math.sin(angle + 2 * math.pi / 3)
            b = 0.5 + 0.5 * math.sin(angle + 4 * math.pi / 3)
            glPushMatrix()
            glTranslatef(px, py, 0.22)
            glColor3f(r, g, b)
            gluSphere(quad, PIT_RADIUS * 0.13, 12, 12)
            glPopMatrix()

        # --- Inner rim: smaller rainbow spheres ---
        for i in range(rim_count):
            angle = 2 * math.pi * i / rim_count
            px = math.cos(angle) * (PIT_RADIUS * 0.7)
            py = math.sin(angle) * (PIT_RADIUS * 0.7)
            r = 0.5 + 0.5 * math.sin(angle + math.pi)
            g = 0.5 + 0.5 * math.sin(angle + 2 * math.pi / 3 + math.pi)
            b = 0.5 + 0.5 * math.sin(angle + 4 * math.pi / 3 + math.pi)
            glPushMatrix()
            glTranslatef(px, py, 0.22)
            glColor3f(r, g, b)
            gluSphere(quad, PIT_RADIUS * 0.08, 8, 8)
            glPopMatrix()

        glPopMatrix()


def check_pit_hole_fall():
    """Check if the car is over any pit hole (game over if so)."""
    global pit_holes
    
    for pit in pit_holes:
        dx = player_pos[0] - pit[0]
        dz = player_pos[2] - pit[1]
        dist = math.hypot(dx, dz)
        
        # Only check if car is on ground (not jumping) and within pit radius
        if dist < PIT_RADIUS and not is_jumping and player_pos[1] <= 5:
            print(f"FELL INTO PIT HOLE at ({int(pit[0])}, {int(pit[1])})!")
            gameover()  # Call gameover() instead of returning True
            return False
    return False

def draw_beautiful_walls():
    """Draw glowing see-through walls with energy lines visible from inside and outside."""
    frame_thickness = 8
    time_factor = time.time()
    glow = 0.3 + 0.2 * (1.0 + math.sin(time_factor * 2.0))  # 0.3–0.7
    line_spacing = 100
    offset = 0.5  # lines drawn slightly inside the wall

    # --- FRONT WALL FRAME ---
    glColor3f(0.0, glow, 1.0)  # Cyan glow
    glBegin(GL_QUADS)
    # Top frame
    glVertex3f(-GRID_SIZE, WALL_HEIGHT - frame_thickness, GRID_SIZE)
    glVertex3f(GRID_SIZE, WALL_HEIGHT - frame_thickness, GRID_SIZE)
    glVertex3f(GRID_SIZE, WALL_HEIGHT, GRID_SIZE)
    glVertex3f(-GRID_SIZE, WALL_HEIGHT, GRID_SIZE)
    # Left frame
    glVertex3f(-GRID_SIZE, 0, GRID_SIZE)
    glVertex3f(-GRID_SIZE + frame_thickness, 0, GRID_SIZE)
    glVertex3f(-GRID_SIZE + frame_thickness, WALL_HEIGHT, GRID_SIZE)
    glVertex3f(-GRID_SIZE, WALL_HEIGHT, GRID_SIZE)
    # Right frame
    glVertex3f(GRID_SIZE - frame_thickness, 0, GRID_SIZE)
    glVertex3f(GRID_SIZE, 0, GRID_SIZE)
    glVertex3f(GRID_SIZE, WALL_HEIGHT, GRID_SIZE)
    glVertex3f(GRID_SIZE - frame_thickness, WALL_HEIGHT, GRID_SIZE)
    # Bottom frame
    glVertex3f(-GRID_SIZE, 0, GRID_SIZE)
    glVertex3f(GRID_SIZE, 0, GRID_SIZE)
    glVertex3f(GRID_SIZE, frame_thickness, GRID_SIZE)
    glVertex3f(-GRID_SIZE, frame_thickness, GRID_SIZE)
    glEnd()

    # Front wall pastel panel
    glColor3f(0.6, 0.9, 1.0)  # light cyan
    glBegin(GL_QUADS)
    glVertex3f(-GRID_SIZE + frame_thickness, frame_thickness, GRID_SIZE)
    glVertex3f(GRID_SIZE - frame_thickness, frame_thickness, GRID_SIZE)
    glVertex3f(GRID_SIZE - frame_thickness, WALL_HEIGHT - frame_thickness, GRID_SIZE)
    glVertex3f(-GRID_SIZE + frame_thickness, WALL_HEIGHT - frame_thickness, GRID_SIZE)
    glEnd()

    # Front energy lines (slightly inside wall)
    glColor3f(1.0, 1.0, 1.0)
    for x in range(-GRID_SIZE + line_spacing, GRID_SIZE, line_spacing):
        glBegin(GL_LINES)
        glVertex3f(x, frame_thickness, GRID_SIZE - offset)
        glVertex3f(x, WALL_HEIGHT - frame_thickness, GRID_SIZE - offset)
        glEnd()
    for y in range(frame_thickness + line_spacing, WALL_HEIGHT - frame_thickness, line_spacing):
        glBegin(GL_LINES)
        glVertex3f(-GRID_SIZE + frame_thickness, y, GRID_SIZE - offset)
        glVertex3f(GRID_SIZE - frame_thickness, y, GRID_SIZE - offset)
        glEnd()

    # --- BACK WALL ---
    glColor3f(1.0, 0.6, 0.9)  # light magenta
    glBegin(GL_QUADS)
    glVertex3f(-GRID_SIZE + frame_thickness, frame_thickness, -GRID_SIZE)
    glVertex3f(GRID_SIZE - frame_thickness, frame_thickness, -GRID_SIZE)
    glVertex3f(GRID_SIZE - frame_thickness, WALL_HEIGHT - frame_thickness, -GRID_SIZE)
    glVertex3f(-GRID_SIZE + frame_thickness, WALL_HEIGHT - frame_thickness, -GRID_SIZE)
    glEnd()

    # Back energy lines
    glColor3f(1.0, 1.0, 1.0)
    for x in range(-GRID_SIZE + line_spacing, GRID_SIZE, line_spacing):
        glBegin(GL_LINES)
        glVertex3f(x, frame_thickness, -GRID_SIZE + offset)
        glVertex3f(x, WALL_HEIGHT - frame_thickness, -GRID_SIZE + offset)
        glEnd()
    for y in range(frame_thickness + line_spacing, WALL_HEIGHT - frame_thickness, line_spacing):
        glBegin(GL_LINES)
        glVertex3f(-GRID_SIZE + frame_thickness, y, -GRID_SIZE + offset)
        glVertex3f(GRID_SIZE - frame_thickness, y, -GRID_SIZE + offset)
        glEnd()

    # --- LEFT WALL ---
    glColor3f(0.9, 1.0, 0.6)  # yellow-green
    glBegin(GL_QUADS)
    glVertex3f(-GRID_SIZE, frame_thickness, -GRID_SIZE + frame_thickness)
    glVertex3f(-GRID_SIZE, frame_thickness, GRID_SIZE - frame_thickness)
    glVertex3f(-GRID_SIZE, WALL_HEIGHT - frame_thickness, GRID_SIZE - frame_thickness)
    glVertex3f(-GRID_SIZE, WALL_HEIGHT - frame_thickness, -GRID_SIZE + frame_thickness)
    glEnd()

    # Left energy lines
    glColor3f(1.0, 1.0, 1.0)
    for z in range(-GRID_SIZE + line_spacing, GRID_SIZE, line_spacing):
        glBegin(GL_LINES)
        glVertex3f(-GRID_SIZE + offset, frame_thickness, z)
        glVertex3f(-GRID_SIZE + offset, WALL_HEIGHT - frame_thickness, z)
        glEnd()
    for y in range(frame_thickness + line_spacing, WALL_HEIGHT - frame_thickness, line_spacing):
        glBegin(GL_LINES)
        glVertex3f(-GRID_SIZE + offset, y, -GRID_SIZE + frame_thickness)
        glVertex3f(-GRID_SIZE + offset, y, GRID_SIZE - frame_thickness)
        glEnd()

    # --- RIGHT WALL ---
    glColor3f(1.0, 0.9, 0.6)  # orange
    glBegin(GL_QUADS)
    glVertex3f(GRID_SIZE, frame_thickness, -GRID_SIZE + frame_thickness)
    glVertex3f(GRID_SIZE, frame_thickness, GRID_SIZE - frame_thickness)
    glVertex3f(GRID_SIZE, WALL_HEIGHT - frame_thickness, GRID_SIZE - frame_thickness)
    glVertex3f(GRID_SIZE, WALL_HEIGHT - frame_thickness, -GRID_SIZE + frame_thickness)
    glEnd()

    # Right energy lines
    glColor3f(1.0, 1.0, 1.0)
    for z in range(-GRID_SIZE + line_spacing, GRID_SIZE, line_spacing):
        glBegin(GL_LINES)
        glVertex3f(GRID_SIZE - offset, frame_thickness, z)
        glVertex3f(GRID_SIZE - offset, WALL_HEIGHT - frame_thickness, z)
        glEnd()
    for y in range(frame_thickness + line_spacing, WALL_HEIGHT - frame_thickness, line_spacing):
        glBegin(GL_LINES)
        glVertex3f(GRID_SIZE - offset, y, -GRID_SIZE + frame_thickness)
        glVertex3f(GRID_SIZE - offset, y, GRID_SIZE - frame_thickness)
        glEnd()

def draw_car():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_rotation, 0, 1, 0)
    glColor3f(0.9, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 15, 0)
    glScalef(60, 20, 120)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(0.05, 0.05, 0.05)
    glPushMatrix()
    glTranslatef(0, 25, 40)
    glScalef(50, 15, 40)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(0.0, 0.5, .5)
    glPushMatrix()
    glTranslatef(0, 35, -10)
    glScalef(45, 20, 60)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(1.0, 1.0, 0)
    for offset in [-12, 12]:
        glPushMatrix()
        glTranslatef(offset, 27, 0)
        glScalef(6, 6, 120)
        glutSolidCube(1)
        glPopMatrix()
    wheel_positions = [(-40, 8, 35), (30, 8, 35), (-40, 8, -35), (30, 8, -35)]
    for wheel_pos in wheel_positions:
        glPushMatrix()
        glTranslatef(*wheel_pos)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.05, 0.05, 0.05)
        gluCylinder(gluNewQuadric(), 12, 12, 10, 24, 1)
        glColor3f(0.9, 0.9, 0.9)
        glPushMatrix()
        glTranslatef(0, 0, 5)
        quad = gluNewQuadric()
        gluSphere(quad,6, 16, 16)
        glPopMatrix()
        glPopMatrix()
    glColor3f(0.5, 0.8, 1.0)
    glPushMatrix()
    glTranslatef(0, 40, 15)
    glScalef(40, 15, 3)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(1.0, 1.0, 0.2)
    for x in [-15, 15]:
        glPushMatrix()
        glTranslatef(x, 20, 60)
        quad = gluNewQuadric()
        gluSphere(quad,8, 12, 12)
        glPopMatrix()
    draw_gun()
    glPopMatrix()

def draw_gun():
    glPushMatrix()
    quad = gluNewQuadric()
    glTranslatef(0, 48, 0)
    glRotatef(gun_rotation, 0, 1, 0)
    glColor3f(0.0, 0.9, 1.0)
    glPushMatrix()
    gluCylinder(quad, 12, 12, 3, 24, 1)
    glPopMatrix()
    glColor3f(0.18, 0.18, 0.22)
    glPushMatrix()
    glTranslatef(0, 6, 0)
    glScalef(18, 8, 18)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(0.12, 0.12, 0.15)
    glPushMatrix()
    glTranslatef(0, 10, 20)
    glScalef(14, 10, 30)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 12, 30)
    glColor3f(1.0, 0.45, 0.0)
    quad = gluNewQuadric()
    gluCylinder(quad, 4.5, 4.5, 70, 16, 3)
    glTranslatef(0, 0, 70)
    glColor3f(0.0, 0.9, 1.0)
    gluCylinder(quad, 8.5, 8.5, 1.5, 12, 1)
    glColor3f(0.05, 0.05, 0.05)
    quad = gluNewQuadric()
    gluSphere(quad,5, 12, 12)
    glPopMatrix()
    glColor3f(1.0, 0.9, 0.0)
    glPushMatrix()
    glTranslatef(0, 17, 28)
    glScalef(4, 3, 8)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()
#---------------------------------------------------------draw with position
def draw_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.8, 0.0)
    quad = gluNewQuadric()
    gluSphere(quad,5, 10, 10)
    glPopMatrix()

def draw_bullet_collectible(x, y, z, rotation):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)
    glColor3f(0.0, 1.0, 0.0)
    quad = gluNewQuadric()
    gluSphere(quad,10, 12, 12)
    glColor3f(1.0, 1.0, 0.0)
    quad = gluNewQuadric()
    gluSphere(quad,5, 10, 10)
    glPopMatrix()

def fire_bullet():
    """Fire a bullet from the gun"""
    global bullets, bullet_count, camera_shake_timer, camera_shake_intensity
    if bullet_count <= 0:
        return
    total_rotation = player_rotation + gun_rotation
    angle_rad = math.radians(total_rotation)
    start_x = player_pos[0] + math.sin(angle_rad) * 50
    start_y = player_pos[1] + 55
    start_z = player_pos[2] + math.cos(angle_rad) * 50
    vel_x = math.sin(angle_rad) * BULLET_SPEED
    vel_y = 0
    vel_z = math.cos(angle_rad) * BULLET_SPEED
    bullets.append([start_x, start_y, start_z, vel_x, vel_y, vel_z])
    bullet_count -= 1
    if camera_mode == 'first_person':
        camera_shake_timer = 10
        camera_shake_intensity = 2.0
    print(f"Bullet fired! Remaining: {bullet_count}")

def draw_enemy_car(x, y, z, rotation):
    glPushMatrix()
    glTranslatef(x, y+ENEMY_CAR_SIZE/2, z)
    glRotatef(rotation, 0, 1, 0)
    glScalef(1, 1, 1)
    glColor3f(0.2, 0.8, 0.2)
    glPushMatrix()
    glScalef(ENEMY_CAR_SIZE, ENEMY_CAR_SIZE/2, ENEMY_CAR_SIZE*1.5)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(0.1, 0.3, 0.1)
    glPushMatrix()
    glTranslatef(0, ENEMY_CAR_SIZE/2, 0)
    glScalef(ENEMY_CAR_SIZE*0.7, ENEMY_CAR_SIZE/3, ENEMY_CAR_SIZE*0.7)
    glutSolidCube(1)
    glPopMatrix()
    for wx in [-ENEMY_CAR_SIZE/2+3, ENEMY_CAR_SIZE/2-3]:
        for wz in [-ENEMY_CAR_SIZE*0.6, ENEMY_CAR_SIZE*0.6]:
            glPushMatrix()
            glTranslatef(wx, -ENEMY_CAR_SIZE/4, wz)
            glColor3f(0.05, 0.05, 0.05)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 5, 5, 7, 10, 1)
            glPopMatrix()
    glPopMatrix()

def draw_human_enemy(x, y, z, rotation=0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)  # Rotate to face player
    
    # Head
    glColor3f(1, 0.8, 0.6)  # Skin color
    glPushMatrix()
    glTranslatef(0, HUMAN_SIZE - 5, 0)  # Position head at top
    quad = gluNewQuadric()
    gluSphere(quad,8, 12, 12)
    glPopMatrix()
    
    # Body (torso)
    glColor3f(0.2, 0.2, 0.8)  # Blue shirt
    glPushMatrix()
    glTranslatef(0, HUMAN_SIZE/2, 0)  # Center the body
    glScalef(12, HUMAN_SIZE/2, 8)  # Width, height, depth
    glutSolidCube(1)
    glPopMatrix()
    
    # Arms
    glColor3f(1, 0.8, 0.6)  # Skin color for arms
    for dx in [-12, 12]:  # Left and right arms
        glPushMatrix()
        glTranslatef(dx, HUMAN_SIZE * 0.7, 0)  # Position arms at shoulder level
        glScalef(3, 15, 3)  # Thin arms
        glutSolidCube(1)
        glPopMatrix()
    
    # Legs
    glColor3f(0.1, 0.1, 0.1)  # Dark pants
    for dx in [-5, 5]:  # Left and right legs
        glPushMatrix()
        glTranslatef(dx, HUMAN_SIZE/4, 0)  # Position legs properly
        glScalef(4, HUMAN_SIZE/2, 4)  # Leg dimensions
        glutSolidCube(1)
        glPopMatrix()
    
    # Weapon (rifle) - now points forward
    glColor3f(0.3, 0.3, 0.3)  # Dark gray weapon
    glPushMatrix()
    glTranslatef(8, HUMAN_SIZE * 0.6, 12)  # Hold weapon pointing forward
    glRotatef(90, 0, 1, 0)  # Point weapon forward
    glScalef(2, 2, 25)  # Long rifle
    glutSolidCube(1)
    glPopMatrix()
    
    # Muzzle flash effect (when firing)
    # This could be enhanced to show only during firing
    glColor3f(1.0, 0.8, 0.0)
    glPushMatrix()
    glTranslatef(8, HUMAN_SIZE * 0.6, 25)  # At weapon tip
    quad = gluNewQuadric()
    gluSphere(quad,2, 8, 8)
    glPopMatrix()
    
    glPopMatrix() 

def draw_turret(x, y, z, rotation):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glScalef(TURRET_SIZE, 7, TURRET_SIZE)
    glutSolidCube(1)
    glPopMatrix()
    glRotatef(rotation, 0, 1, 0)
    glColor3f(0.8, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, 14, TURRET_SIZE/2)
    gluCylinder(gluNewQuadric(), 4, 4, 18, 12, 1)
    glPopMatrix()
    glPopMatrix()

def draw_mine_bot(x, y, z):
    glPushMatrix()
    # Make the mine bot bigger (e.g., 1.7x original size)
    scale = 2
    mine_radius = (MINE_SIZE * scale) / 2

    glTranslatef(x, y + mine_radius, z)
    glColor3f(0.7, 0.7, 0.7)
    quad = gluNewQuadric()
    gluSphere(quad, mine_radius, 16, 16)  # Bigger sphere

    # Draw black ring around the equator
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)  # Align cylinder horizontally
    # Slightly larger than sphere, very thin
    gluCylinder(quad, mine_radius * 1.08, mine_radius * 1.08, 4, 32, 1)
    glPopMatrix()

    # Draw spikes (cubes), also scaled up
    glColor3f(0.2, 0.2, 0.2)
    for angle in range(0, 360, 60):
        glPushMatrix()
        glRotatef(angle, 0, 1, 0)
        glTranslatef(mine_radius, 0, 0)
        glScalef(1.2, 1.2, 9.5)  # Slightly bigger and longer spikes
        glutSolidCube(1)
        glPopMatrix()
    glPopMatrix()


def update_collectibles(delta_time):
    """Update bullet collectibles: float up/down and rotate"""
    global bullet_collectibles, bullet_count
    for collectible in bullet_collectibles[:]:
        x, y, z, float_dir, float_speed, rotation = collectible
        y += float_dir * float_speed * delta_time
        if y > 25:
            float_dir = -1
        elif y < 5:
            float_dir = 1
        rotation += 90 * delta_time
        collectible[1] = y
        collectible[3] = float_dir
        collectible[5] = rotation
        dx = player_pos[0] - x
        dz = player_pos[2] - z
        distance = math.sqrt(dx*dx + dz*dz)
        if distance < 30:
            bullet_collectibles.remove(collectible)
            bullet_count += 10
            print(f"Bullet collected! Total: {bullet_count}")

# Update the handle_movement function to include collision detection
def handle_movement(delta_time):
    """Handle player car movement - UPDATED to respect first person cheat mode"""
    global player_pos, player_rotation, car_speed, is_jumping, jump_timer, jump_start_y
    global gun_rotation, boost_active

    # Handle jumping
    if is_jumping:
        jump_timer += delta_time * 60
        if jump_timer < JUMP_DURATION // 2:
            player_pos[1] = jump_start_y + (jump_timer / (JUMP_DURATION // 2)) * JUMP_HEIGHT
        elif jump_timer < JUMP_DURATION:
            remaining = jump_timer - JUMP_DURATION // 2
            player_pos[1] = jump_start_y + JUMP_HEIGHT - (remaining / (JUMP_DURATION // 2)) * JUMP_HEIGHT
        else:
            player_pos[1] = jump_start_y
            is_jumping = False
            jump_timer = 0

    # Use boost_active flag
    if boost_active:
        car_speed = BOOST_SPEED
    else:
        car_speed = NORMAL_SPEED

    # Skip manual movement if first person cheat mode is controlling movement
    if fp_movement_override:
        return

    # Forward/Backward movement with collision detection
    angle_rad = math.radians(player_rotation)
    if ord('W') in keys_pressed or ord('w') in keys_pressed:
        new_x = player_pos[0] + math.sin(angle_rad) * car_speed * delta_time
        new_z = player_pos[2] + math.cos(angle_rad) * car_speed * delta_time
        # Check boundaries and obstacle collisions
        if (abs(new_x) < GRID_SIZE - CAR_SIZE and abs(new_z) < GRID_SIZE - CAR_SIZE and
            not check_mountain_collision(new_x, new_z) and not check_tree_collision(new_x, new_z)):
            player_pos[0] = new_x
            player_pos[2] = new_z
    if ord('S') in keys_pressed or ord('s') in keys_pressed:
        new_x = player_pos[0] - math.sin(angle_rad) * car_speed * delta_time
        new_z = player_pos[2] - math.cos(angle_rad) * car_speed * delta_time
        # Check boundaries and obstacle collisions
        if (abs(new_x) < GRID_SIZE - CAR_SIZE and abs(new_z) < GRID_SIZE - CAR_SIZE and
            not check_mountain_collision(new_x, new_z) and not check_tree_collision(new_x, new_z)):
            player_pos[0] = new_x
            player_pos[2] = new_z

    # Rotation - don't allow manual rotation if first person cheat mode is controlling it
    if not (first_person_cheat_mode and camera_mode == 'first_person' and fp_cheat_target):
        if ord('A') in keys_pressed or ord('a') in keys_pressed:
            player_rotation -= ROTATION_SPEED * delta_time
        if ord('D') in keys_pressed or ord('d') in keys_pressed:
            player_rotation += ROTATION_SPEED * delta_time

    # Gun rotation (only in third person mode)
    if camera_mode != 'first_person':
        if ord('K') in keys_pressed or ord('k') in keys_pressed:
            gun_rotation -= GUN_ROTATION_SPEED * delta_time
        if ord('L') in keys_pressed or ord('l') in keys_pressed:
            gun_rotation += GUN_ROTATION_SPEED * delta_time

def setup_camera():
    """Setup camera based on current mode - UPDATED for better first person"""
    global camera_shake_timer, camera_shake_intensity
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(65.0 / camera_zoom, 1.25, 0.1, 4000)  # Slightly wider FOV for first person
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    shake_x = shake_y = 0
    if camera_shake_timer > 0:
        shake_x = random.uniform(-camera_shake_intensity, camera_shake_intensity)
        shake_y = random.uniform(-camera_shake_intensity, camera_shake_intensity)
        camera_shake_timer -= 1
        camera_shake_intensity *= 0.9
    
    if camera_mode == 'third_person':
        angle_rad = math.radians(camera_angle)
        cam_x = player_pos[0] + math.sin(angle_rad) * camera_distance
        cam_z = player_pos[2] + math.cos(angle_rad) * camera_distance
        cam_y = camera_height
        gluLookAt(cam_x + shake_x, cam_y + shake_y, cam_z,
                  player_pos[0], player_pos[1] + 30, player_pos[2],
                  0, 1, 0)
    elif camera_mode == 'first_person':
        # Position camera at driver's seat height and position
        total_rotation = player_rotation
        angle_rad = math.radians(total_rotation)
        
        # Camera positioned at realistic driver's seat location
        cam_x = player_pos[0] + math.sin(angle_rad) * 5  # Slightly forward in car
        cam_y = player_pos[1] + 50  # Driver eye level (higher for better view)
        cam_z = player_pos[2] + math.cos(angle_rad) * 5
        
        # Look direction includes gun rotation for aiming
        look_angle_rad = math.radians(total_rotation + gun_rotation)
        look_x = cam_x + math.sin(look_angle_rad) * 100
        look_y = cam_y + 0  # Level looking
        look_z = cam_z + math.cos(look_angle_rad) * 100
        
        gluLookAt(cam_x + shake_x, cam_y + shake_y, cam_z,
                  look_x, look_y, look_z,
                  0, 1, 0)
    elif camera_mode == 'top_down':
        gluLookAt(player_pos[0] + shake_x, 1000 + shake_y, player_pos[2],
                  player_pos[0], 0, player_pos[2],
                  0, 0, 1)


def draw_first_person_overlay():
    """Draw realistic first-person view from inside the car with prominent red hood"""
    if camera_mode != 'first_person':
        return
    
    # Save current matrices
    glPushMatrix()
    glLoadIdentity()
    
    # === CAR INTERIOR FRAME - WINDSHIELD FRAME ===
    glColor3f(0.15, 0.15, 0.15)  # Dark car interior frame
    glBegin(GL_QUADS)
    # Left windshield pillar (A-pillar)
    glVertex3f(-100, -100, -50)  # Bottom left
    glVertex3f(-85, -100, -50)   # Bottom right of pillar
    glVertex3f(-85, 100, -50)    # Top right of pillar
    glVertex3f(-100, 100, -50)   # Top left
    
    # Right windshield pillar (A-pillar)
    glVertex3f(85, -100, -50)    # Bottom left of pillar
    glVertex3f(100, -100, -50)   # Bottom right
    glVertex3f(100, 100, -50)    # Top right
    glVertex3f(85, 100, -50)     # Top left of pillar
    
    # Dashboard top edge (visible at bottom of windshield)
    glVertex3f(-85, -25, -50)
    glVertex3f(85, -25, -50)
    glVertex3f(85, -15, -50)
    glVertex3f(-85, -15, -50)
    glEnd()
    
    # === PROMINENT RED CAR HOOD (Bottom 40% of screen) ===
    # Main hood surface - much larger and more prominent
    glColor3f(0.9, 0.1, 0.1)  # Bright red car color
    glBegin(GL_QUADS)
    # Large hood surface taking up bottom portion of screen
    glVertex3f(-85, -100, -48)  # Bottom left (at screen edge)
    glVertex3f(85, -100, -48)   # Bottom right (at screen edge)
    glVertex3f(60, -25, -48)    # Top right (perspective narrowing)
    glVertex3f(-60, -25, -48)   # Top left (perspective narrowing)
    glEnd()
    
    # Hood depth/thickness - make it look 3D
    glColor3f(0.7, 0.08, 0.08)  # Darker red for hood edges
    glBegin(GL_QUADS)
    # Left hood edge
    glVertex3f(-85, -100, -48)
    glVertex3f(-60, -25, -48)
    glVertex3f(-60, -25, -45)
    glVertex3f(-85, -100, -45)
    
    # Right hood edge
    glVertex3f(60, -25, -48)
    glVertex3f(85, -100, -48)
    glVertex3f(85, -100, -45)
    glVertex3f(60, -25, -45)
    
    # Front hood edge (closest to windshield)
    glVertex3f(-60, -25, -48)
    glVertex3f(60, -25, -48)
    glVertex3f(60, -25, -45)
    glVertex3f(-60, -25, -45)
    glEnd()
    
    # === HOOD DETAILS ===
    # Hood ornament/logo
    glColor3f(0.9, 0.9, 0.9)  # Chrome/silver hood ornament
    glPushMatrix()
    glTranslatef(0, -60, -47)  # Center of hood
    glScalef(6, 12, 3)
    glutSolidCube(1)
    glPopMatrix()
    
    # Hood air vents/scoops
    glColor3f(0.3, 0.3, 0.3)  # Dark vents
    for x_offset in [-25, 25]:
        for y_offset in [-80, -70, -60]:
            glPushMatrix()
            glTranslatef(x_offset, y_offset, -47)
            glScalef(12, 4, 2)
            glutSolidCube(1)
            glPopMatrix()
    
    # Hood panel lines (realistic car design)
    glColor3f(0.6, 0.06, 0.06)  # Slightly darker red for panel lines
    glBegin(GL_QUADS)
    # Left panel line
    glVertex3f(-30, -95, -47.5)
    glVertex3f(-28, -95, -47.5)
    glVertex3f(-22, -30, -47.5)
    glVertex3f(-24, -30, -47.5)
    
    # Right panel line
    glVertex3f(28, -95, -47.5)
    glVertex3f(30, -95, -47.5)
    glVertex3f(24, -30, -47.5)
    glVertex3f(22, -30, -47.5)
    
    # Center panel line
    glVertex3f(-1, -95, -47.5)
    glVertex3f(1, -95, -47.5)
    glVertex3f(1, -30, -47.5)
    glVertex3f(-1, -30, -47.5)
    glEnd()
    
    # === CAR INTERIOR DASHBOARD (visible at top of hood) ===
    glColor3f(0.2, 0.2, 0.2)  # Dark dashboard plastic
    glBegin(GL_QUADS)
    # Main dashboard surface
    glVertex3f(-60, -25, -47)
    glVertex3f(60, -25, -47)
    glVertex3f(50, -10, -47)
    glVertex3f(-50, -10, -47)
    glEnd()
    
    # Dashboard instrument cluster housing
    glColor3f(0.1, 0.1, 0.1)  # Black instrument cluster
    glBegin(GL_QUADS)
    glVertex3f(-40, -20, -46.5)
    glVertex3f(40, -20, -46.5)
    glVertex3f(35, -12, -46.5)
    glVertex3f(-35, -12, -46.5)
    glEnd()
    
    # Speedometer and tachometer (circular gauges)
    glColor3f(0.9, 0.9, 0.9)  # White gauge faces
    # Left gauge (speedometer)
    glPushMatrix()
    glTranslatef(-20, -16, -46)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 1, 16, 1)
    glPopMatrix()
    
    # Right gauge (tachometer)
    glPushMatrix()
    glTranslatef(20, -16, -46)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 1, 16, 1)
    glPopMatrix()
    
    # === STEERING WHEEL (partial view at bottom) ===
    glColor3f(0.1, 0.1, 0.1)  # Black steering wheel
    # Only show top part of steering wheel
    for angle in range(30, 150, 5):  # Only top arc
        angle_rad = math.radians(angle)
        next_angle_rad = math.radians(angle + 5)
        
        glBegin(GL_QUADS)
        # Inner rim
        x1, y1 = math.cos(angle_rad) * 18, math.sin(angle_rad) * 18 - 35
        x2, y2 = math.cos(next_angle_rad) * 18, math.sin(next_angle_rad) * 18 - 35
        # Outer rim
        x3, y3 = math.cos(next_angle_rad) * 22, math.sin(next_angle_rad) * 22 - 35
        x4, y4 = math.cos(angle_rad) * 22, math.sin(angle_rad) * 22 - 35
        
        glVertex3f(x1, y1, -46)
        glVertex3f(x2, y2, -46)
        glVertex3f(x3, y3, -46)
        glVertex3f(x4, y4, -46)
        glEnd()
    
    
    # === CROSSHAIR/AIMING RETICLE ===
    glColor3f(0, 1, 0)  # Green crosshair
    glBegin(GL_LINES)
    # Horizontal crosshair
    glVertex3f(-10, 5, -40)  # Slightly above center for realistic aiming
    glVertex3f(10, 5, -40)
    # Vertical crosshair
    glVertex3f(0, -5, -40)
    glVertex3f(0, 15, -40)
    glEnd()
    
   
    
    # Center dot
    glColor3f(1, 0, 0)  # Red center dot
    glPushMatrix()
    glTranslatef(0, 5, -40)
    quad = gluNewQuadric()
    gluSphere(quad,1.5, 8, 8)
    glPopMatrix()
    
    # === SIDE MIRRORS (small parts visible) ===
    glColor3f(0.15, 0.15, 0.15)  # Dark mirror housing
    # Left mirror (just edge visible)
    glPushMatrix()
    glTranslatef(-90, 20, -48)
    glScalef(6, 8, 4)
    glutSolidCube(1)
    glPopMatrix()
    
    # Right mirror (just edge visible)
    glPushMatrix()
    glTranslatef(90, 20, -48)
    glScalef(6, 8, 4)
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()  # Restore matrix


def gameover():
    global game_over, game_over_spin_speed, game_over_message_timer
    game_over = True
    game_over_spin_speed = 360  # Start spinning at 360 degrees per second
    game_over_message_timer = 0
    print("GAME OVER!")

def draw_game_over_message():
    """Draw the game over message in the center of the screen"""
    if not game_over:
        return
        
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    
    # Pulsing effect for game over text
    pulse = 0.5 + 0.5 * (1.0 + math.sin(game_over_message_timer * 4.0))
    glColor3f(1.0, pulse * 0.5, pulse * 0.5)  # Pulsing red
    
    # GAME OVER text (large, centered)
    game_over_text = "GAME OVER"
    text_width = len(game_over_text) * 18  # Approximate width for HELVETICA_18
    glRasterPos2f(500 - text_width // 2, 450)
    for char in game_over_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    # Score display
    glColor3f(1.0, 1.0, 1.0)  # White
    score_text = f"FINAL SCORE: {score}"
    score_width = len(score_text) * 10
    glRasterPos2f(500 - score_width // 2, 400)
    for char in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    
    # Restart instruction (blinking effect)
    if int(game_over_message_timer * 2) % 2:  # Blink every 0.5 seconds
        glColor3f(0.8, 0.8, 1.0)  # Light blue
        restart_text = "Press R to Restart"
        restart_width = len(restart_text) * 9
        glRasterPos2f(500 - restart_width // 2, 350)
        for char in restart_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def draw_shield():
    if not shield_active:
        return

    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1] + 30, player_pos[2])
    glRotatef(shield_rotation, 1, 1, 1)  # rotate the shield

    quad = gluNewQuadric()
    glColor3f(0.2, 0.6, 1.0)  # Blue shield color

    # --- Longitude spheres (like vertical lines) ---
    slices = 17
    stacks = 100
    for i in range(slices):
        angle = 2 * math.pi * i / slices
        for j in range(stacks + 1):
            theta = -math.pi/2 + math.pi * j / stacks
            x = SHIELD_RADIUS * math.cos(theta) * math.cos(angle)
            y = SHIELD_RADIUS * math.sin(theta)
            z = SHIELD_RADIUS * math.cos(theta) * math.sin(angle)
            glPushMatrix()
            glTranslatef(x, y, z)
            gluSphere(quad, 0.5, 8, 8)  # small sphere
            glPopMatrix()

    # --- Latitude spheres (like horizontal rings) ---
    latitudes = [-60, -30, 0, 30, 60]  # degrees
    for lat in latitudes:
        t = math.radians(lat)
        r = SHIELD_RADIUS * math.cos(t)
        y = SHIELD_RADIUS * math.sin(t)
        for i in range(slices):
            angle = 2 * math.pi * i / slices
            x = r * math.cos(angle)
            z = r * math.sin(angle)
            glPushMatrix()
            glTranslatef(x, y, z)
            gluSphere(quad, 0.5, 8, 8)
            glPopMatrix()

    glPopMatrix()



def draw_hud():
    """Draw HUD information"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 900)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Score (white, at the top)
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 790)
    score_text = f"Score: {score}"
    for char in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Bullets count (white)
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 770)
    bullet_text = f"Bullets: {bullet_count}"
    for char in bullet_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Health with color coding
    if player_health > 50:
        glColor3f(0, 1, 0)  # Green
    elif player_health > 25:
        glColor3f(1, 1, 0)  # Yellow
    else:
        glColor3f(1, 0, 0)  # Red
    glRasterPos2f(10, 740)
    health_text = f"Health: {player_health}"
    for char in health_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    # Timer display (top right)
    glColor3f(1, 1, 1)
    glRasterPos2f(800, 770)
    timer_text = f"Time Left: {int(game_timer)}s"
    for char in timer_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Camera mode (white)
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 720)
    mode_text = f"Camera: {camera_mode.replace('_', ' ').title()}"
    for char in mode_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    # Position (white)
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 700)
    pos_text = f"Position: ({int(player_pos[0])}, {int(player_pos[2])})"
    for char in pos_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    # Bullet collectibles (white)
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 680)
    collectible_text = f"Collectibles: {len(bullet_collectibles)}"
    for char in collectible_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    # Health collectibles (white)
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 660)
    health_collectible_text = f"Health Pickups: {len(health_collectibles)}"
    for char in health_collectible_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    # Enemy count (white)
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 640)
    enemy_text = f"Enemies: Cars({len(enemy_cars)}) Humans({len(human_enemies)}) Turrets({len(turrets)}) Mines({len(mine_bots)})"
    for char in enemy_text:
        glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(char))

    # Pit hole warning with distance-based color coding
    if pit_holes:
        closest_distance = float('inf')
        closest_pit = None
        for pit in pit_holes:
            dx = player_pos[0] - pit[0]
            dz = player_pos[2] - pit[1]
            distance = math.hypot(dx, dz)
            if distance < closest_distance:
                closest_distance = distance
                closest_pit = pit
        if closest_pit:
            if closest_distance < 100:
                glColor3f(1, 0.2, 0.2)  # Red warning - DANGER!
                warning_text = f"!!! PIT HOLE NEARBY! Distance: {int(closest_distance)} !!!"
            elif closest_distance < 300:
                glColor3f(1, 1, 0.2)  # Yellow warning - CAUTION
                warning_text = f"CAUTION: Pit Hole Distance: {int(closest_distance)}"
            else:
                glColor3f(0.2, 1, 0.2)  # Green - SAFE
                warning_text = f"Nearest Pit Distance: {int(closest_distance)} (Safe)"
            glRasterPos2f(10, 620)
            for char in warning_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    if shield_active:
        glColor3f(0.2, 0.6, 1.0)
        glRasterPos2f(400, 760)
        shield_text = "SHIELD ACTIVE"
        for char in shield_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    # Cheat mode status
    if cheat_mode:
        glColor3f(1, 0.2, 0.2)  # Red for cheat mode
        cheat_text = "CHEAT MODE: ON"
    else:
        glColor3f(0.7, 0.7, 0.7)  # Gray when off
        cheat_text = "CHEAT MODE: OFF"
    glRasterPos2f(10, 590)
    for char in cheat_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    # First person cheat mode status
    if first_person_cheat_mode and camera_mode == 'first_person':
        glColor3f(0.2, 1, 0.2)  # Green for active FP cheat mode
        fp_cheat_text = "FP CHEAT MODE: ON"
    elif camera_mode == 'first_person':
        glColor3f(1, 1, 0.2)  # Yellow when available
        fp_cheat_text = "FP CHEAT MODE: OFF (Press V)"
    else:
        glColor3f(0.7, 0.7, 0.7)  # Gray when not available
        fp_cheat_text = "FP CHEAT MODE: N/A"
    glRasterPos2f(10, 570)
    for char in fp_cheat_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    # Controls (white)
    glColor3f(1, 1, 1)
    controls = [
        "WASD: Move car",
        "KL: Rotate gun (3rd person only)",
        "J: Jump",
        "Space: Fire",
        "Shift+W: Toggle Boost",
        "C: Toggle Cheat Mode",
        "V: Toggle FP Cheat Mode (1st person only)",
        "Right click: Change camera",
        "F: Top-down view",
        "+/-: Zoom (1st person)",
        "Arrows: Camera control",
        "R: Reset"
    ]
    y_pos = 200
    for control in controls:
        glRasterPos2f(10, y_pos)
        for char in control:
            glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(char))
        y_pos -= 15

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_camera()
    draw_grid()
    draw_beautiful_walls()
    draw_pit_holes()
    # Draw mountains and trees
    for mountain in mountains:
        draw_mountain(mountain[0], mountain[1], mountain[2], mountain[3], mountain[4])
    for tree in trees:
        draw_tree(tree[0], tree[1], tree[2], tree[3], tree[4])
    
    if camera_mode != 'first_person':
        draw_car()
        draw_shield()
    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1], bullet[2])
    for collectible in bullet_collectibles:
        draw_bullet_collectible(collectible[0], collectible[1], collectible[2], collectible[5])
    for collectible in health_collectibles:
        draw_health_collectible(collectible[0], collectible[1], collectible[2], collectible[5])
    for pickup in time_pickups:
        draw_time_pickup(pickup[0], pickup[1], pickup[2], pickup[5])
    for ec in enemy_cars:
        draw_enemy_car(ec[0], ec[1], ec[2], ec[3])
    for he in human_enemies:
        draw_human_enemy(he[0], he[1], he[2], he[5])  # Now includes rotation
    for t in turrets:
        draw_turret(t[0], t[1], t[2], t[3])
    for mb in mine_bots:
        draw_mine_bot(mb[0], mb[1], mb[2])
    for eb in enemy_bullets:
        draw_enemy_bullet(eb[0], eb[1], eb[2])
    
    draw_first_person_overlay()
    draw_hud()
    draw_game_over_message()
    glutSwapBuffers()



# def display():
#     glClear(GL_COLOR_BUFFER_BIT)  # No GL_DEPTH_BUFFER_BIT!
#     glLoadIdentity()
#     setup_camera()

#     # Calculate camera position
#     if camera_mode == 'third_person':
#         angle_rad = math.radians(camera_angle)
#         cam_x = player_pos[0] + math.sin(angle_rad) * camera_distance
#         cam_z = player_pos[2] + math.cos(angle_rad) * camera_distance
#         cam_y = camera_height
#     elif camera_mode == 'first_person':
#         total_rotation = player_rotation
#         angle_rad = math.radians(total_rotation)
#         cam_x = player_pos[0] + math.sin(angle_rad) * 5
#         cam_y = player_pos[1] + 50
#         cam_z = player_pos[2] + math.cos(angle_rad) * 5
#     else:
#         cam_x, cam_y, cam_z = player_pos[0], 1000, player_pos[2]

#     # Collect all drawable 3D objects
#     drawables = []

#     # Add grid (usually drawn first as background)
#     drawables.append((0, 0, 0, draw_grid))

#     # Add beautiful walls
#     drawables.append((0, 0, 0, draw_beautiful_walls))

#     # Add pit holes
#     for pit in pit_holes:
#         drawables.append((pit[0], 0, pit[1], draw_pit_holes))

#     # Add mountains
#     for mountain in mountains:
#         drawables.append((mountain[0], mountain[1], mountain[2], draw_mountain, *mountain))

#     # Add trees
#     for tree in trees:
#         drawables.append((tree[0], tree[1], tree[2], draw_tree, *tree))

#     # Add player car if not in first person mode
#     if camera_mode != 'first_person':
#         drawables.append((player_pos[0], player_pos[1], player_pos[2], draw_car))

#     # Add shield
#     if camera_mode != 'first_person':
#         drawables.append((player_pos[0], player_pos[1], player_pos[2], draw_shield))

#     # Add bullets
#     for bullet in bullets:
#         drawables.append((bullet[0], bullet[1], bullet[2], draw_bullet, bullet[0], bullet[1], bullet[2]))

#     # Add bullet collectibles
#     for collectible in bullet_collectibles:
#         drawables.append((collectible[0], collectible[1], collectible[2], draw_bullet_collectible, collectible[0], collectible[1], collectible[2], collectible[5]))

#     # Add health collectibles
#     for collectible in health_collectibles:
#         drawables.append((collectible[0], collectible[1], collectible[2], draw_health_collectible, collectible[0], collectible[1], collectible[2], collectible[5]))

#     # Add time pickups
#     for pickup in time_pickups:
#         drawables.append((pickup[0], pickup[1], pickup[2], draw_time_pickup, pickup[0], pickup[1], pickup[2], pickup[5]))

#     # Add enemy cars
#     for ec in enemy_cars:
#         drawables.append((ec[0], ec[1], ec[2], draw_enemy_car, ec[0], ec[1], ec[2], ec[3]))

#     # Add human enemies
#     for he in human_enemies:
#         drawables.append((he[0], he[1], he[2], draw_human_enemy, he[0], he[1], he[2], he[5]))

#     # Add turrets
#     for t in turrets:
#         drawables.append((t[0], t[1], t[2], draw_turret, t[0], t[1], t[2], t[3]))

#     # Add mine bots
#     for mb in mine_bots:
#         drawables.append((mb[0], mb[1], mb[2], draw_mine_bot, mb[0], mb[1], mb[2]))

#     # Add enemy bullets
#     for eb in enemy_bullets:
#         drawables.append((eb[0], eb[1], eb[2], draw_enemy_bullet, eb[0], eb[1], eb[2]))

#     # Sort from farthest to nearest based on distance to camera
#     drawables.sort(key=lambda obj: -((obj[0] - cam_x) ** 2 + (obj[1] - cam_y) ** 2 + (obj[2] - cam_z) ** 2))

#     # Draw all objects in sorted order (back to front)
#     for obj in drawables:
#         if len(obj) > 4:
#             # Object has additional arguments
#             obj[3](*obj[4:])
#         else:
#             # Object has no additional arguments
#             obj[3]()

#     # Draw overlays (these should be drawn last, on top of everything)
#     draw_first_person_overlay()
#     draw_hud()
#     draw_game_over_message()
    
#     glutSwapBuffers()


def idle():
    global last_time, player_health, game_timer, game_over
    global game_over_spin_speed, game_over_message_timer, player_rotation
    global level_up
    global shield_active, bullet_count
    global shield_rotation

    if not level_up and score > 50:
        level_up = True
        shield_active = True
        print("LEVEL UP! Shield activated, infinite bullets!")

    # Infinite bullets when shield is active
    if shield_active:
        bullet_count = 9999
    if not level_up and score > 50:
        level_up = True
        print("LEVEL UP! Shield activated, infinite bullets!")

    current_time = time.time()
    if last_time == 0:
        last_time = current_time
    delta_time = current_time - last_time
    last_time = current_time
    if delta_time > 0.1:
        delta_time = 0.1

    # Handle game over state
    if game_over:
        # Make car spin wildly
        player_rotation += game_over_spin_speed * delta_time
        game_over_message_timer += delta_time
        # Increase spin speed over time for more dramatic effect
        game_over_spin_speed = min(game_over_spin_speed + 50 * delta_time, 720)
        glutPostRedisplay()
        return  # Don't update anything else when game over

    # Timer update
    game_timer -= delta_time
    if game_timer <= 0:
        gameover()
        return
    
    # Check for pit hole fall FIRST (before other updates)
    if check_pit_hole_fall():
        print("  FELL INTO THE PIT HOLE! GAME OVER! ")
        gameover()
        return
    
    # Check for game over from health
    if player_health <= 0:
        print("GAME OVER! Health depleted! Resetting...")
        gameover()
        return
    
    update_cheat_mode(delta_time)
    update_first_person_cheat_mode(delta_time)
    handle_movement(delta_time)
    update_bullets(delta_time)
    update_collectibles(delta_time)
    update_health_collectibles(delta_time)

     # Update shield rotation if active
    if shield_active:
        shield_rotation += 30 * delta_time  # 30° per second
        if shield_rotation > 360:
            shield_rotation -= 360

    
    if len(bullet_collectibles) < 8:
        for _ in range(5):
            x = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
            z = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
            bullet_collectibles.append([x, 15, z, 1, 10, 0])
    if len(health_collectibles) < 5:  # When below 5, respawn some
        respawn_count = 12 - len(health_collectibles)  # Respawn to get back to 12 total
        for _ in range(respawn_count):
            x = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
            z = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
            health_collectibles.append([x, 15, z, 1, 10, 0])
    
    update_enemy_cars(delta_time)
    update_human_enemies(delta_time)
    update_turrets(delta_time)
    update_mine_bots(delta_time)
    update_enemy_bullets(delta_time)
    update_time_pickups(delta_time)
    glutPostRedisplay()


def keyboard(key, x, y):
    """Handle keyboard input"""
    global camera_mode, is_jumping, jump_start_y, camera_zoom, gun_rotation
    global shift_down, w_down, boost_active, boost_toggle_ready, cheat_mode
    global cheat_target, auto_fire_cooldown, cheat_move_override
    global first_person_cheat_mode, fp_cheat_target, fp_auto_fire_cooldown, fp_movement_override


    keys_pressed.add(ord(key))

    # Toggle first person cheat mode (only works in first person view)
    if key == b'v' or key == b'V':
        if camera_mode == 'first_person':
            first_person_cheat_mode = not first_person_cheat_mode
            print(f"First Person Cheat Mode: {'ON' if first_person_cheat_mode else 'OFF'}")
            if not first_person_cheat_mode:
                # Reset first person cheat mode states
                fp_cheat_target = None
                fp_auto_fire_cooldown = 0
                fp_movement_override = False
        else:
            print("First Person Cheat Mode only works in first person camera view!")
        glutPostRedisplay()
        return

    # Toggle cheat mode
    if key == b'c' or key == b'C':
        cheat_mode = not cheat_mode
        print(f"Cheat mode: {'ON' if cheat_mode else 'OFF'}")
        if not cheat_mode:
            # Reset any cheat mode states
            cheat_target = None
            auto_fire_cooldown = 0
            cheat_move_override = False
        glutPostRedisplay()
        return

    # Track if W or Shift is pressed for boost toggle
    if key == b'w' or key == b'W':
        w_down = True
    if key == b'\x10':  # Shift key (not always reliable, see below)
        shift_down = True

    # --- BOOST TOGGLE LOGIC ---
    if shift_down and w_down and boost_toggle_ready:
        boost_active = not boost_active
        boost_toggle_ready = False
        print(f"Boost toggled: {'ON' if boost_active else 'OFF'}")

    if key == b'r' or key == b'R':
        reset_game()
    elif key == b'j' or key == b'J':
        if not is_jumping:
            is_jumping = True
            jump_timer = 0
            jump_start_y = player_pos[1]
    elif key == b' ':  # Space
        fire_bullet()
    elif key == b'f' or key == b'F':
        camera_mode = 'top_down' if camera_mode != 'top_down' else 'third_person'
    elif key == b'g' or key == b'G':
        gun_rotation = 0
        print("Gun rotation reset to center position")
    elif key == b'+' or key == b'=':
        if camera_mode == 'first_person':
            camera_zoom = min(camera_zoom + 0.1, 3.0)
    elif key == b'-':
        if camera_mode == 'first_person':
            camera_zoom = max(camera_zoom - 0.1, 0.5)

    glutPostRedisplay()

def keyboard_up(key, x, y):
    """Handle key release"""
    global shift_down, w_down, boost_toggle_ready
    keys_pressed.discard(ord(key))
    if key == b'w' or key == b'W':
        w_down = False
        boost_toggle_ready = True
    if key == b'\x10':
        shift_down = False
        boost_toggle_ready = True

def special_keys(key, x, y):
    """Handle special key input"""
    global camera_angle, camera_height
    if key == GLUT_KEY_LEFT:
        camera_angle -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle += 5
    elif key == GLUT_KEY_UP:
        if camera_mode == 'third_person':
            camera_height = min(camera_height + 20, 1200)
    elif key == GLUT_KEY_DOWN:
        if camera_mode == 'third_person':
            camera_height = max(camera_height - 20, 100)
    glutPostRedisplay()

def special_keys_up(key, x, y):
    """Handle special key release"""
    pass

def mouse(button, state, x, y):
    global camera_mode, first_person_cheat_mode, fp_cheat_target, fp_auto_fire_cooldown, fp_movement_override, cheat_mode, cheat_target, auto_fire_cooldown, cheat_move_override

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == 'third_person':
            camera_mode = 'first_person'
            # Disable third person cheat mode when switching to first person
            if cheat_mode:
                cheat_mode = False
                cheat_target = None
                auto_fire_cooldown = 0
                cheat_move_override = False
                print("Cheat Mode disabled (switched to first person)")
        elif camera_mode == 'first_person':
            camera_mode = 'third_person'
            # Disable first person cheat mode when switching away
            if first_person_cheat_mode:
                first_person_cheat_mode = False
                fp_cheat_target = None
                fp_auto_fire_cooldown = 0
                fp_movement_override = False
                print("First Person Cheat Mode disabled (switched to third person)")
    glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Enhanced Car Shooter - Beautiful Transparent Arena")
    glEnable(GL_DEPTH_TEST)
    # glClearColor(0.05, 0.05, 0.15, 1.0)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)
    glutSpecialUpFunc(special_keys_up)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)
    reset_game()
    print("Enhanced Car Shooter Game Started!")
    print(f"Arena size: {GRID_SIZE}x{GRID_SIZE}")
    print("Features: Beautiful transparent walls with energy effects")
    print("Use WASD to move, Space to shoot, Right-click to change camera mode")
    print("Enemy collision detection is now working properly!")
    glutMainLoop()

if __name__ == "__main__":
    main()