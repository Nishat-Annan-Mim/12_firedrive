# Enhanced Car Shooter with Beautiful Transparent Walls (Boost Toggle Fixed)
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Game constants - INCREASED GRID SIZE
GRID_SIZE = 1500  # Increased from 1000 to 1500
GRID_STEP = 50
CAR_SIZE = 30
BULLET_SPEED = 1200 
MAX_BULLETS = 50
JUMP_HEIGHT = 80
JUMP_DURATION = 30
WALL_HEIGHT = 150  # Increased wall height for better visibility
# Movement + rotation speeds (units/second, degrees/second)
NORMAL_SPEED = 200
BOOST_SPEED = 400
ROTATION_SPEED = 90
GUN_ROTATION_SPEED = 60

# Camera variables
camera_mode = 'third_person'  # 'third_person', 'first_person', 'top_down'
camera_angle = 0
camera_height = 600  # Increased height for better grid view
camera_distance = 500  # Increased distance for better overview
camera_zoom = 1.0
camera_shake_timer = 0
camera_shake_intensity = 0

# Player car variables
player_pos = [0, 0, 0]  # x, y, z
player_rotation = 0  # car rotation
gun_rotation = 0  # gun rotation relative to car
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
boost_toggle_ready = True  # Prevents repeated toggling while holding

def reset_game():
    """Reset game to initial state"""
    global player_pos, player_rotation, gun_rotation, bullets, bullet_count
    global camera_mode, camera_angle, camera_height, camera_zoom, is_jumping, jump_timer
    global boost_active, shift_down, w_down, boost_toggle_ready, keys_pressed

    player_pos = [0, 0, 0]
    player_rotation = 0
    gun_rotation = 0
    bullets = []
    bullet_count = MAX_BULLETS

    # Reset camera to third person
    camera_mode = 'third_person'
    camera_angle = 0
    camera_height = 600  # Higher camera for better grid view
    camera_zoom = 1.0
    is_jumping = False
    jump_timer = 0

    # --- RESET BOOST STATE ---
    boost_active = False
    shift_down = False
    w_down = False
    boost_toggle_ready = True
    keys_pressed.clear()  # Clear all movement keys so car stands still

    # Generate some bullet collectibles
    generate_bullet_collectibles()

    print(f"Game Reset! Bullet Count: {bullet_count}")

def generate_bullet_collectibles():
    """Generate bullet collectibles on the grid"""
    global bullet_collectibles
    bullet_collectibles = []

    for _ in range(15):  # More collectibles for bigger area
        x = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
        z = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
        # Format: [x, y, z, float_dir, float_speed, rotation]
        bullet_collectibles.append([x, 15, z, 1, 10, 0])

def draw_grid():
    """Draw the game grid with transparent effect"""
    glColor3f(0.3, 0.7, 0.9)
    glBegin(GL_LINES)
    for x in range(-GRID_SIZE, GRID_SIZE + GRID_STEP, GRID_STEP):
        glVertex3f(x, 0, -GRID_SIZE)
        glVertex3f(x, 0, GRID_SIZE)
    for z in range(-GRID_SIZE, GRID_SIZE + GRID_STEP, GRID_STEP):
        glVertex3f(-GRID_SIZE, 0, z)
        glVertex3f(GRID_SIZE, 0, z)
    glEnd()

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
    """Draw a colorful sports car with upright wheels"""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_rotation, 0, 1, 0)
    # --- Car Body (Bright Red) ---
    glColor3f(0.9, 0.1, 0.1)  # Red
    glPushMatrix()
    glTranslatef(0, 15, 0)
    glScalef(60, 20, 120)
    glutSolidCube(1)
    glPopMatrix()
    # --- Hood (Glossy Black) ---
    glColor3f(0.05, 0.05, 0.05)
    glPushMatrix()
    glTranslatef(0, 25, 40)
    glScalef(50, 15, 40)
    glutSolidCube(1)
    glPopMatrix()
    # --- Roof (Silver Metallic) ---
    glColor3f(0.0, 0.5, .5)
    glPushMatrix()
    glTranslatef(0, 35, -10)
    glScalef(45, 20, 60)
    glutSolidCube(1)
    glPopMatrix()
    # --- Racing Stripes (Yellow) ---
    glColor3f(1.0, 1.0, 0)
    for offset in [-12, 12]:
        glPushMatrix()
        glTranslatef(offset, 27, 0)
        glScalef(6, 6, 120)
        glutSolidCube(1)
        glPopMatrix()
    # --- Wheels (Proper orientation, parallel with car body) ---
    wheel_positions = [(-40, 8, 35), (30, 8, 35), (-40, 8, -35), (30, 8, -35)]
    for wheel_pos in wheel_positions:
        glPushMatrix()
        glTranslatef(*wheel_pos)
        glRotatef(90, 0, 1, 0)  # Rotate around Y so cylinder is upright
        glColor3f(0.05, 0.05, 0.05)  # Black tire
        gluCylinder(gluNewQuadric(), 12, 12, 10, 24, 1)
        # Wheel hub
        glColor3f(0.9, 0.9, 0.9)
        glPushMatrix()
        glTranslatef(0, 0, 5)  # center hub along cylinder
        glutSolidSphere(6, 16, 16)
        glPopMatrix()
        glPopMatrix()
    # --- Windshield (Sky Blue Glass) ---
    glColor3f(0.5, 0.8, 1.0)
    glPushMatrix()
    glTranslatef(0, 40, 15)
    glScalef(40, 15, 3)
    glutSolidCube(1)
    glPopMatrix()
    # --- Headlights (Bright Yellow) ---
    glColor3f(1.0, 1.0, 0.2)
    for x in [-15, 15]:
        glPushMatrix()
        glTranslatef(x, 20, 60)
        glutSolidSphere(8, 12, 12)
        glPopMatrix()
    # --- Gun ---
    draw_gun()
    glPopMatrix()

def draw_gun():
    """Bright, aligned turret gun mounted on car roof (+Z = forward)."""
    glPushMatrix()
    glTranslatef(0, 48, 0)                 # just above the roof
    glRotatef(gun_rotation, 0, 1, 0)       # yaw relative to car
    # --- Turret ring (bright cyan) ---
    glColor3f(0.0, 0.9, 1.0)
    glPushMatrix()
    glutSolidTorus(3, 12, 16, 24)
    glPopMatrix()
    # --- Turret mount block (dark) ---
    glColor3f(0.18, 0.18, 0.22)
    glPushMatrix()
    glTranslatef(0, 6, 0)
    glScalef(18, 8, 18)
    glutSolidCube(1)
    glPopMatrix()
    # --- Barrel housing (dark rectangular shroud) ---
    glColor3f(0.12, 0.12, 0.15)
    glPushMatrix()
    glTranslatef(0, 10, 20)
    glScalef(14, 10, 30)
    glutSolidCube(1)
    glPopMatrix()
    # --- Main barrel (bright orange), points along +Z ---
    glPushMatrix()
    glTranslatef(0, 12, 30)
    glColor3f(1.0, 0.45, 0.0)
    quad = gluNewQuadric()
    gluCylinder(quad, 4.5, 4.5, 70, 16, 1)
    # Muzzle ring (bright cyan) + cap
    glTranslatef(0, 0, 70)
    glColor3f(0.0, 0.9, 1.0)
    glutSolidTorus(1.5, 5.5, 12, 18)
    glColor3f(0.05, 0.05, 0.05)
    glutSolidSphere(5, 12, 12)
    glPopMatrix()
    # --- Simple top sight (yellow) ---
    glColor3f(1.0, 0.9, 0.0)
    glPushMatrix()
    glTranslatef(0, 17, 28)
    glScalef(4, 3, 8)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

def draw_bullet(x, y, z):
    """Draw a bullet as a solid sphere"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.8, 0.0)  # Golden bullet
    glutSolidSphere(3, 8, 8)
    glPopMatrix()

def draw_bullet_collectible(x, y, z, rotation):
    """Draw a bullet collectible with floating and spinning effect"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)
    glColor3f(0.0, 1.0, 0.0)
    glutSolidSphere(8, 10, 10)
    glColor3f(1.0, 1.0, 0.0)
    glutSolidSphere(4, 8, 8)
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

def update_bullets(delta_time):
    """Move bullets forward and clean up old ones"""
    global bullets
    updated_bullets = []
    for bullet in bullets:
        bullet[0] += bullet[3] * delta_time
        bullet[1] += bullet[4] * delta_time
        bullet[2] += bullet[5] * delta_time
        if abs(bullet[0]) < GRID_SIZE and abs(bullet[2]) < GRID_SIZE:
            updated_bullets.append(bullet)
    bullets = updated_bullets

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

def handle_movement(delta_time):
    """Handle player car movement (frame-rate independent)"""
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

    # --- BOOST LOGIC: Use boost_active flag ---
    if boost_active:
        car_speed = BOOST_SPEED
    else:
        car_speed = NORMAL_SPEED

    # Forward/Backward movement
    angle_rad = math.radians(player_rotation)
    if ord('W') in keys_pressed or ord('w') in keys_pressed:
        new_x = player_pos[0] + math.sin(angle_rad) * car_speed * delta_time
        new_z = player_pos[2] + math.cos(angle_rad) * car_speed * delta_time
        if abs(new_x) < GRID_SIZE - CAR_SIZE and abs(new_z) < GRID_SIZE - CAR_SIZE:
            player_pos[0] = new_x
            player_pos[2] = new_z
    if ord('S') in keys_pressed or ord('s') in keys_pressed:
        new_x = player_pos[0] - math.sin(angle_rad) * car_speed * delta_time
        new_z = player_pos[2] - math.cos(angle_rad) * car_speed * delta_time
        if abs(new_x) < GRID_SIZE - CAR_SIZE and abs(new_z) < GRID_SIZE - CAR_SIZE:
            player_pos[0] = new_x
            player_pos[2] = new_z

    # Rotation
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
    """Setup camera based on current mode"""
    global camera_shake_timer, camera_shake_intensity
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0 / camera_zoom, 1.25, 0.1, 4000)
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
        total_rotation = player_rotation + gun_rotation
        angle_rad = math.radians(total_rotation)
        cam_x = player_pos[0]
        cam_y = player_pos[1] + 55
        cam_z = player_pos[2]
        look_x = cam_x + math.sin(angle_rad) * 100
        look_y = cam_y
        look_z = cam_z + math.cos(angle_rad) * 100
        gluLookAt(cam_x + shake_x, cam_y + shake_y, cam_z,
                  look_x, look_y, look_z,
                  0, 1, 0)
    elif camera_mode == 'top_down':
        gluLookAt(player_pos[0] + shake_x, 1000 + shake_y, player_pos[2],
                  player_pos[0], 0, player_pos[2],
                  0, 0, 1)

def draw_first_person_overlay():
    """Draw gun overlay for first person mode"""
    if camera_mode != 'first_person':
        return
    glPushMatrix()
    glTranslatef(10, -30, -40)
    glRotatef(gun_rotation - player_rotation, 0, 1, 0)
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 6, 60, 12, 1)
    glPopMatrix()
    glPopMatrix()

def draw_hud():
    """Draw HUD information"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 770)
    bullet_text = f"Bullets: {bullet_count}"
    for char in bullet_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glRasterPos2f(10, 750)
    mode_text = f"Camera: {camera_mode.replace('_', ' ').title()}"
    for char in mode_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    glRasterPos2f(10, 730)
    pos_text = f"Position: ({int(player_pos[0])}, {int(player_pos[2])})"
    for char in pos_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    glRasterPos2f(10, 710)
    collectible_text = f"Collectibles: {len(bullet_collectibles)}"
    for char in collectible_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    glRasterPos2f(10, 690)
    grid_text = f"Grid Size: {GRID_SIZE}x{GRID_SIZE}"
    for char in grid_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    controls = [
        "WASD: Move car",
        "KL: Rotate gun (3rd person only)",
        "J: Jump",
        "Space: Fire",
        "Shift+W: Toggle Boost",
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
    """Main display function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_camera()
    draw_grid()
    draw_beautiful_walls()
    if camera_mode != 'first_person':
        draw_car()
    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1], bullet[2])
    for collectible in bullet_collectibles:
        draw_bullet_collectible(collectible[0], collectible[1], collectible[2], collectible[5])
    draw_first_person_overlay()
    draw_hud()
    glutSwapBuffers()

def keyboard(key, x, y):
    """Handle keyboard input"""
    global camera_mode, is_jumping, jump_start_y, camera_zoom, gun_rotation
    global shift_down, w_down, boost_active, boost_toggle_ready

    keys_pressed.add(ord(key))

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
    """Handle mouse input"""
    global camera_mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == 'third_person':
            camera_mode = 'first_person'
        elif camera_mode == 'first_person':
            camera_mode = 'third_person'
    glutPostRedisplay()

def idle():
    """Idle function for continuous updates"""
    global last_time
    current_time = time.time()
    if last_time == 0:
        last_time = current_time
    delta_time = current_time - last_time
    last_time = current_time
    if delta_time > 0.1:
        delta_time = 0.1
    handle_movement(delta_time)
    update_bullets(delta_time)
    update_collectibles(delta_time)
    if len(bullet_collectibles) < 8:
        for _ in range(5):
            x = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
            z = random.uniform(-GRID_SIZE + 100, GRID_SIZE - 100)
            bullet_collectibles.append([x, 15, z, 1, 10, 0])
    glutPostRedisplay()

def main():
    """Main function"""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Enhanced Car Shooter - Beautiful Transparent Arena")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.15, 1.0)
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
    glutMainLoop()

if __name__ == "__main__":
    main()
