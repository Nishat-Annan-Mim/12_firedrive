GRID_SIZE = 1500
MAX_TIME_PICKUPS = 5
time_pickups = []  # [x, y, z, float_dir, float_speed, rotation]
TIME_PICKUP_AMOUNT = 20  # seconds added per pickup

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
