MAX_MINE_BOTS = 4
mine_bots = []  # [x, y, z]
MINE_SIZE = 18  # Increased for visibility


def draw_mine_bot(x, y, z):
    glPushMatrix()
    glTranslatef(x, y+MINE_SIZE/2, z)
    glColor3f(0.7, 0.7, 0.7)
    quad = gluNewQuadric()
    gluSphere(quad,MINE_SIZE/2, 12, 12)
    glColor3f(0.2, 0.2, 0.2)
    for angle in range(0, 360, 60):
        glPushMatrix()
        glRotatef(angle, 0, 1, 0)
        glTranslatef(MINE_SIZE/2, 0, 0)
        glScalef(1, 1, 7)
        glutSolidCube(1)
        glPopMatrix()
    glPopMatrix()

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
