enemy_bullets = []  # [x, y, z, vx, vy, vz, damage]

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