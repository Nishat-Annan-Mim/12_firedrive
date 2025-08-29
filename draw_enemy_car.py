GRID_SIZE = 1500
enemy_cars = []  # [x, y, z, rotation, health, fire_cooldown, touch_timer]
ENEMY_CAR_SIZE = 50 # Increased for visibility

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
            ec[6] += dt
            if ec[6] > 5:
                if not shield_active:
                   player_health -= 2
                ec[6] = 0
        else:
            ec[6] = 0
