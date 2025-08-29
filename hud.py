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

