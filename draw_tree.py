TREE_SIZE = 80
trees = []
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


def spawn_trees():
    """Spawn 3 trees at random locations"""
    global trees
    trees = []
    for _ in range(3):
        
        attempts = 0
        while attempts < 50:  # Prevent infinite loop
            x = random.uniform(-GRID_SIZE + 200, GRID_SIZE - 200)
            z = random.uniform(-GRID_SIZE + 200, GRID_SIZE - 200)
            
        trunk_height = random.uniform(40, 80)
        crown_size = random.uniform(60, 100)
        trees.append([x, 0, z, trunk_height, crown_size])
