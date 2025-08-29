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
