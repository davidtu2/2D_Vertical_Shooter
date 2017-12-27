"""
Space Pirate v3.5.py

Christopher Guerra   santaguerra@csu.fullerton.edu
Marc Jimenez         jimenezmw@csu.fullerton.edu
David Tu             david.tu2@csu.fullerton.edu

Implementation of a simple space-themed shooter game

Rules:
1. There are three types of attacks that correspond to different colors: Red, Green, and Yellow
2. There are three different types of enemies that correspond to those colors as well
3. The weakness of every enemy is the determined by the color of the enemy
4. Exploiting your enemies’ weaknesses will defeat them and is the key to victory
5. Every ship can only take one hit and that includes yours. Stay sharp and avoid your enemies’ maneuvers and their projectiles!
6. After 1 minute, you would have survived the battle and you be declared the winner 

Controls:
1 – 3 Keys: Switch to Green, Red, and Yellow Weapons, respectively
SPACEBAR: Shoot with the equipped weapon
LEFT: Move left
RIGHT: Move right
ESC: Exit the screen
"""
import os, pygame # os module ensures cross platform functionality
from pygame.locals import *
import random
import math
if not pygame.mixer: print ('Warning, sound disabled')
if not pygame.font: print ('Warning, fonts disabled')

#Game constants
main_dir = os.path.split(os.path.abspath(__file__))[0]
#Feel free to change the values for testing
ALIEN_ODDS     = 120   #Chances a new alien appears - starting value
BOMB_ODDS      = 200   #Chances a new bomb will drop
ALIEN_RELOAD   = 12    #Frames between new aliens
ALIEN_CHECK    = 0     #Checks how many are in the game
DYNAMIC_SPAWN  = 4     #For Dynamic Spawning

#Functions to create our resources
def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs

class dummysound: #This class will be used if pygame.mixer cannot be initialized
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return sound

#Classes for our game objects
class Player(pygame.sprite.Sprite): #Inherit the Sprite class
    speed = 5
    bounce = 24
    gun_offset = -11
    images = []
    score = 0
    weapon = 'Green Projectile' #Default weapon
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #Call the Sprite's constructor
        self.image = pygame.image.load(os.path.join('data', 'Player1.png')).convert_alpha()
        self.images = [self.image, pygame.transform.flip(self.image, 1, 0)]
        screen = pygame.display.get_surface()
        self.area = screen.get_rect() #Gets the area of the whole screen surface
        self.rect = self.image.get_rect(midbottom = self.area.midbottom) #Place the player in a initial position
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1 #Initially make the player go left

    def move(self, direction):
        if direction: self.facing = direction
        self.rect.move_ip(direction * self.speed, 0)
        self.rect = self.rect.clamp(self.area) #Keeps the player in the screen
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        self.rect.top = self.origtop - (self.rect.left//self.bounce%2)

    def gunPosition(self): #Used to determine the origin of the gun for projectile generation
        position = self.facing * self.gun_offset + self.rect.centerx
        return position, self.rect.top

#First Enemy: Goes Left to Right, drops a bomb at an internal interval. Can only be killed by Player's Green Weapon
class Enemy1(pygame.sprite.Sprite):
    gun_offset = 11
    shootCounter = 0
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'Enemy1.png')).convert_alpha()
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 1
        positionX= random.randint(0, 550)
        self.rect.topleft = positionX, 0
        
    def update(self):
        pos = self.rect.move(self.speed, 0) #Note that pos is a local variable
        if self.rect.left < self.area.left or self.rect.right > self.area.right: #Prevents the object from being stuck outside the Screen's Surface
            self.speed = -self.speed
            pos = self.rect.move(self.speed, 0)
        self.rect = pos
        self.shootCounter = self.shootCounter + 1
        
    def gunPosition(self):
        position = self.gun_offset + self.rect.centerx
        return position, self.rect.bottom

#Second Enemy: Goes up and down, crashes into player if both collide. Can only be killed by Player's Red Weapon
class Enemy2(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'Enemy2.png')).convert_alpha()
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 2
        positionX = random.randint(0, 550)
        self.rect.topleft = positionX, 0

    def update(self):
        pos = self.rect.move(0, self.speed)
        if self.rect.top < self.area.top or self.rect.bottom > self.area.bottom:
            self.speed = -self.speed
            pos = self.rect.move(0, self.speed)
        self.rect = pos

#Third Enemy: Goes in a diagonal patten, will always be above a certain section in the screen. Drops bombs. Can only be killed by Player's Yellow Weapon
class Enemy3(pygame.sprite.Sprite):
    shootCounter = 0
    gun_offset = 11
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'Enemy3.png')).convert_alpha()
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speedX = 2
        self.speedY = 2
        positionX= random.randint(0, 550)
        self.rect.topleft = positionX, 0

    def update(self):
        pos = self.rect.move(0, self.speedY)
        
        if (self.rect.bottom > self.area.bottom/3):
            pos = self.rect.move(self.speedX, self.speedY/2)
        if (self.rect.bottom > self.area.bottom-self.area.bottom/3):
            self.speedY = -self.speedY
            pos = self.rect.move(0,self.speedY)

        if self.rect.left < self.area.left or self.rect.right > self.area.right:
            self.speedX = -self.speedX
            pos = self.rect.move(self.speedX, 0)
        if self.rect.top < self.area.top or self.rect.bottom > self.area.bottom:
            self.speedY = -self.speedY
            pos = self.rect.move(0, self.speedY*2)
        self.rect = pos
        self.shootCounter = self.shootCounter + 1
        #print(self.shootCounter)

    def gunPosition(self):
        position = self.gun_offset + self.rect.centerx
        return position, self.rect.bottom

class Projectile(pygame.sprite.Sprite): #Superclass for projectiles
    speed = -11
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()

class GreenProjectile(Projectile): #Inherit from Projectile
    def __init__(self, position):
        Projectile.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'projectile1.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom = position)

class RedProjectile(Projectile):
    def __init__(self, position):
        Projectile.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'projectile2.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom = position)

class YellowProjectile(Projectile):
    def __init__(self, position):
        Projectile.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'projectile3.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom = position)

class EnemyProjectile(Projectile):
    def __init__(self, position):
        Projectile.__init__(self)
        self.speed = 1
        self.image = pygame.image.load(os.path.join('data', 'projectile4.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom = position)

class Explode(pygame.sprite.Sprite):
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('explosion1.gif')
        self.rect = self.image.get_rect(center = actor.rect.center)

    def update(self):
        self.kill()

def spawnRandomEnemy(enemiesType1, enemiesType2, enemiesType3, allsprites):
    global ALIEN_CHECK 
    spawnNumber = random.randint(1,3)
 
    if spawnNumber == 1:
        newenemy = Enemy1()
        enemiesType1.add(newenemy)
        allsprites.add(newenemy)
        ALIEN_CHECK = ALIEN_CHECK + 1
    elif spawnNumber == 2:
        newenemy = Enemy2()
        enemiesType2.add(newenemy)
        allsprites.add(newenemy)
        ALIEN_CHECK = ALIEN_CHECK + 1
    elif spawnNumber == 3:
        newenemy = Enemy3()
        enemiesType3.add(newenemy)
        allsprites.add(newenemy)
        ALIEN_CHECK = ALIEN_CHECK + 1
        #print('Added')

def spawnBomb(allsprites, enemy, projectilesEnemy):
    global BOMB_ODDS
    if (enemy.shootCounter >= BOMB_ODDS + random.randint(1,200)): 
    #if (enemy.shootCounter >= BOMB_ODDS + random.randint(1,30)): #debug ver
        #print('Shooting at: ', enemy.shootCounter)
        newShtE = EnemyProjectile(enemy.gunPosition())
        projectilesEnemy.add(newShtE)
        allsprites.add(newShtE)
        enemy.shootCounter = 0

def main():
    #Uses and modifies variables at the top
    global ALIEN_ODDS
    global ALIEN_CHECK
    global DYNAMIC_SPAWN
    #For spawning
    counter = 0
    counter2 = 0
    counter3 = 0
    #Controls the module the player is in
    running = True
    titleScreen = True
    gameOver = True
    #For the moving background
    y = 0
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = -480
    
    #Initialize everything
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Space Pirate')

    #Create the background
    background = pygame.image.load(os.path.join('data', 'background.png'))
    background_size = background.get_size()
    background_rect = background.get_rect()
    screen = pygame.display.set_mode(background_size)
    w,h = background_size
    x1 = 0
    y1 = -h

    #Display the background
    screen.blit(background, (0, 0))
    pygame.display.flip()

    #Prepare Game Objects
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 60000) #1 min in milliseconds
    boom_sound = load_sound('boom.wav')
    shoot_sound = load_sound('car_door.wav')
    if pygame.mixer: #Bg music. It won't play if pygame.mixer fails to initialize
        music = os.path.join(main_dir, 'data', 'bg_music.mp3')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)
    player1 = Player()
    weaponColor = pygame.image.load(os.path.join('data', 'weapon1.png')).convert_alpha()
    enemy1 = Enemy1()
    enemy2 = Enemy2()
    enemy3 = Enemy3()

    #Add objects to groups, to iterate later on
    playerBucket = pygame.sprite.Group(player1)
    enemiesType1 = pygame.sprite.Group(enemy1)
    enemiesType2 = pygame.sprite.Group(enemy2)
    enemiesType3 = pygame.sprite.Group(enemy3)
    projectilesGreen = pygame.sprite.Group() #Initially empty (for collisions)
    projectilesRed = pygame.sprite.Group()
    projectilesYellow = pygame.sprite.Group()
    projectilesEnemy = pygame.sprite.Group()
    allsprites = pygame.sprite.RenderPlain((player1, enemy1, enemy2)) #Add everyone to another group (in order to update all simultaneously)

    #Title Screen
    if pygame.font:
            font = pygame.font.Font(None, 36)
            start_text = font.render('Press ENTER to Start', 1, (255, 255, 255))
            start_textPosition = start_text.get_rect()
            start_textPosition.midtop = (screen.get_width()/2, screen.get_height() * 3/4)
    while titleScreen == True:
        #Handle all the input events
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                titleScreen = False
                running = False
        keystate = pygame.key.get_pressed()

        if keystate[K_RETURN]:
            titleScreen = False

        #Draw everything
        logo = pygame.image.load(os.path.join('data', 'logo.png')).convert_alpha()
        screen.blit(logo, (w/6, h/8))
        screen.blit(start_text, start_textPosition)
        
        pygame.display.flip()

    #Game Loop
    while running:
        clock.tick(60) #Makes game not run faster than 60fps

        #Handle player input
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) or event.type == pygame.USEREVENT:
                running = False
        keystate = pygame.key.get_pressed()
        direction = keystate[K_RIGHT] - keystate[K_LEFT]
        player1.move(direction)
        firing = keystate[K_SPACE]
        if keystate[K_1] or keystate[K_KP1]:
            player1.weapon = 'Green Projectile'
            weaponColor = pygame.image.load(os.path.join('data', 'weapon1.png')).convert_alpha()
        if keystate[K_2] or keystate[K_KP2]:
            player1.weapon = 'Red Projectile'
            weaponColor = pygame.image.load(os.path.join('data', 'weapon2.png')).convert_alpha()
        if keystate[K_3] or keystate[K_KP3]:
            player1.weapon = 'Yellow Projectile'
            weaponColor = pygame.image.load(os.path.join('data', 'weapon3.png')).convert_alpha()
        if not player1.reloading and firing: #Reloading prevents the player from spamming the fire button
            if player1.weapon == 'Green Projectile':
                greenProjectile = GreenProjectile(player1.gunPosition()) #Create a GREEN projectile from the position of the gun
                projectilesGreen.add(greenProjectile)
                allsprites.add(greenProjectile)
            elif player1.weapon == 'Red Projectile':
                redProjectile = RedProjectile(player1.gunPosition()) #Create a RED projectile from the position of the gun
                projectilesRed.add(redProjectile)
                allsprites.add(redProjectile)
            elif player1.weapon == 'Yellow Projectile':
                yellowProjectile = YellowProjectile(player1.gunPosition()) #Create a YELLOW projectile from the position of the gun
                projectilesYellow.add(yellowProjectile)
                allsprites.add(yellowProjectile)
            shoot_sound.play()
        player1.reloading = firing #Switch reloading back to 0

        allsprites.update()

        #Collisiion Detection
        for enemy in pygame.sprite.groupcollide(projectilesGreen, enemiesType1, 1, 1):
            explosion = Explode(enemy)
            allsprites.add(explosion)#Will make the explosion appear on the next draw()
            boom_sound.play()
            enemy.kill()
            #enemiesType1.remove()
            counter2 = 0
            ALIEN_CHECK = ALIEN_CHECK - 1
            player1.score += 1
            
        for enemy in pygame.sprite.groupcollide(projectilesRed, enemiesType2, 1, 1):
            explosion = Explode(enemy)
            allsprites.add(explosion)
            boom_sound.play()
            enemy.kill()
            player1.score += 1
            ALIEN_CHECK = ALIEN_CHECK - 1
                        
        for enemy in pygame.sprite.groupcollide(projectilesYellow, enemiesType3, 1, 1):
            explosion = Explode(enemy)
            allsprites.add(explosion)
            boom_sound.play()
            enemy.kill()
            player1.score += 1
            ALIEN_CHECK = ALIEN_CHECK - 1

        for enemy in pygame.sprite.groupcollide(playerBucket, enemiesType2, 1, 1):
            explosion = Explode(player1)
            allsprites.add(explosion)
            boom_sound.play()
            player1.kill()
            running = False

        for enemy in pygame.sprite.groupcollide(playerBucket, projectilesEnemy, 1, 1):
            explosion = Explode(player1)
            allsprites.add(explosion)
            boom_sound.play()
            player1.kill()
            running = False
        
        #First Spawn:
        counter = counter + 1
        if counter > ALIEN_ODDS :
            #print('ALIEN_CHECK BEFORE: ',ALIEN_CHECK)
            if ALIEN_CHECK < DYNAMIC_SPAWN:
                for i in range (random.randint(2,3)):
                    spawnRandomEnemy(enemiesType1, enemiesType2, enemiesType3, allsprites)
                    counter = 0
                    #print ('counter after: ' , counter)
                    #print('ALIEN_CHECK AFTER: ',ALIEN_CHECK)
                if ALIEN_ODDS == 120:
                    ALIEN_ODDS = 300
                    #print('Alien_odds at: ', ALIEN_ODDS)
                else:
                    ALIEN_ODDS = ALIEN_ODDS - random.randint(0, 30)
                    #print('Alien_odds at: ', ALIEN_ODDS)
            else:
                    spawnRandomEnemy(enemiesType1, enemiesType2, enemiesType3, allsprites)
                    counter = 0
                    ALIEN_ODDS = ALIEN_ODDS + random.randint(0, 50)
                    #print('Alien_odds at: ', ALIEN_ODDS)
                    #print ('counter after: ' , counter)
                    #print('ALIEN_CHECK AFTER: ',ALIEN_CHECK)

        for enemy in pygame.sprite.Group(enemiesType1):
            spawnBomb(allsprites, enemy, projectilesEnemy)

        for enemy in pygame.sprite.Group(enemiesType3):
            spawnBomb(allsprites, enemy, projectilesEnemy)

        #Draw the scene
        y1 += 10
        y += 10
        screen.blit(background,(0, y))
        screen.blit(background,(x1, y1))
        if y > h:
            y = -h
        if y1 > h:
            y1 = -h
        allsprites.draw(screen) #For this to work, we need to ensure that the game object's Rects stays updated
        if pygame.font: #Score label
            font = pygame.font.Font(None, 36)
            text = font.render('Score: ' + str(player1.score), 1, (255, 255, 255)) # Score count
            screen.blit(text, (50, 10)) #Make Score appear. 2nd parameter is the xy positions
        screen.blit(weaponColor, (10, 8)) #Weapon Type selected
        pygame.display.flip()

    text = font.render('GAME OVER', 1, (255, 255, 255))
    textPosition = text.get_rect()
    textPosition.midtop = (screen.get_width()/2, screen.get_height()/2)
    while gameOver:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                gameOver = False
        keystate = pygame.key.get_pressed()

        screen.blit(background, (0, 0))
        screen.blit(text, textPosition)
        pygame.display.flip()
        
    pygame.quit()

if __name__ == '__main__': main()
