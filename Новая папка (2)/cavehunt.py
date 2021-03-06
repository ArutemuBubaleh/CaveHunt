import random, sys, time, math, pygame
from pygame.locals import *

FPS = 30
WINWIDTH = 640
WINHEIGHT = 480
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

GRASSCOLOR = (113, 114, 113)
WHITE = (0, 0, 0)
RED = (255, 0, 0)

CAMERASLACK = 3
MOVERATE = 6
BOUNCERATE = 15
BOUNCEHEIGHT = 10
STARTSIZE = 40
MAXSIZE = 100
INVULNTIME = 2
GAMEOVERTIME = 4
MAXHEALTH = 5
MAXSPEED = 20
screen = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
NUMGRASS = 80
NUMSQUIRRELS = 50
SQUIRRELMINSPEED = 6
SQUIRRELMAXSPEED = 12
DIRCHANGEFREQ = 2
waiting = False
LEFT = 'left'
RIGHT = 'right'
UP = 'up'
DOWN = 'down'
background = pygame.image.load('screen.png').convert()
background_rect = background.get_rect()
SCORE = 0

GRASSIMAGES = []
font_name = pygame.font.match_font('papyrus')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def start_screen():
    global waiting
    screen.blit(background, background_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_CAPSLOCK:
                    waiting = False


def changedificulty(event):
    global MAXHEALTH, STARTSIZE, NUMSQUIRRELS, SQUIRRELMINSPEED, SQUIRRELMAXSPEED, DIRCHANGEFREQ, waiting
    if event.type == QUIT:
        terminate()

    elif event.type == KEYUP:

        if event.key == pygame.K_Y:
            MAXHEALTH = 5
            STARTSIZE = 40
            NUMSQUIRRELS = 50
            SQUIRRELMINSPEED = 6
            SQUIRRELMAXSPEED = 12
            DIRCHANGEFREQ = 2
        if event.key == pygame.K_U:
            MAXHEALTH = 3
            STARTSIZE = 30
            NUMSQUIRRELS = 60
            SQUIRRELMINSPEED = 9
            SQUIRRELMAXSPEED = 15
            DIRCHANGEFREQ = 5
        if event.key == pygame.K_I:
            MAXHEALTH = 1
            STARTSIZE = 20
            NUMSQUIRRELS = 70
            SQUIRRELMINSPEED = 12
            SQUIRRELMAXSPEED = 18
            DIRCHANGEFREQ = 10


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_SQUIR_IMG, R_SQUIR_IMG, GRASSIMAGES, SUP, SDOWN, SRIGHT, SLEFT, \
        BATIMG, waiting, SCORE

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('gameicon.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Cave Hunt')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    SDOWN = pygame.image.load('flopup.png')
    SLEFT = pygame.image.load('flopleft.png')
    SUP = pygame.image.load('flopdown.png')
    SRIGHT = pygame.image.load('flopright.png')
    BATIMG = pygame.image.load('squirrel.png')
    start_screen()
    if waiting == True:
        changedificulty(event)

    for i in range(1, 5):
        GRASSIMAGES.append(pygame.image.load('grass%s.png' % i))

    while True:
        runGame()


def get_frame(frame_set):
    frame = 0
    frame += 1
    if frame > (len(frame_set) - 1):
        frame = 0
    return frame_set[frame]


def clip(clipped_rect):
    global SHEET
    if type(clipped_rect) is dict:
        SHEET.set_clip(pygame.Rect(get_frame(clipped_rect)))
    else:
        SHEET.set_clip(pygame.Rect(clipped_rect))

    return clipped_rect


def runGame():
    global SCORE
    drawScoreMeter()
    invulnerableMode = False
    invulnerableStartTime = 0
    gameOverMode = False
    gameOverStartTime = 0
    winMode = False

    gameOverSurf = BASICFONT.render('YOU ARE DEAD', True, RED)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('You Win', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('Press "r" to restart', True, WHITE)

    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    camerax = 0
    cameray = 0

    grassObjs = []
    squirrelObjs = []
    playerObj = {'surface': pygame.transform.scale(SDOWN, (STARTSIZE, STARTSIZE)),
                 'facing': DOWN,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce': 0,
                 'speed': MOVERATE,
                 'health': MAXHEALTH}

    moveLeft = False
    moveRight = False
    moveUp = False
    moveDown = False

    for i in range(10):
        grassObjs.append(makeNewGrass(camerax, cameray))
        grassObjs[i]['x'] = random.randint(0, WINWIDTH)
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT)

    while True:
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME:
            invulnerableMode = False

        for sObj in squirrelObjs:
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0

            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = RandomVelocity()
                sObj['movey'] = RandomVelocity()
                if sObj['movex'] > 0:
                    sObj['surface'] = pygame.transform.scale(BATIMG, (sObj['width'], sObj['height']))
                else:
                    sObj['surface'] = pygame.transform.scale(BATIMG, (sObj['width'], sObj['height']))

        for i in range(len(grassObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(squirrelObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, squirrelObjs[i]):
                del squirrelObjs[i]

        while len(grassObjs) < NUMGRASS:
            grassObjs.append(makeNewGrass(camerax, cameray))
        while len(squirrelObjs) < NUMSQUIRRELS:
            squirrelObjs.append(makeNewBat(camerax, cameray))

        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2)
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2)
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        DISPLAYSURF.fill(GRASSCOLOR)

        for gObj in grassObjs:
            gRect = pygame.Rect((gObj['x'] - camerax,
                                 gObj['y'] - cameray,
                                 gObj['width'],
                                 gObj['height']))
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect)

        for sObj in squirrelObjs:
            sObj['rect'] = pygame.Rect((sObj['x'] - camerax,
                                        sObj['y'] - cameray - Bounce(sObj['bounce'], sObj['bouncerate'],
                                                                     sObj['bounceheight']), sObj['width'],
                                        sObj['height']))
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])

        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect((playerObj['x'] - camerax,
                                             playerObj['y'] - cameray - Bounce(playerObj['bounce'], BOUNCERATE,
                                                                               BOUNCEHEIGHT),
                                             playerObj['size'],
                                             playerObj['size']))
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])

        drawHealthMeter(playerObj['health'])
        drawScoreMeter()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:

                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                    playerObj['surface'] = pygame.transform.scale(SUP,
                                                                  (playerObj['size'], playerObj['size']))
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                    playerObj['surface'] = pygame.transform.scale(SDOWN,
                                                                  (playerObj['size'], playerObj['size']))

                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    playerObj['surface'] = pygame.transform.scale(SLEFT,
                                                                  (playerObj['size'], playerObj['size']))

                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    playerObj['surface'] = pygame.transform.scale(SRIGHT,
                                                                  (playerObj['size'], playerObj['size']))

                elif winMode and event.key == K_r:
                    return

            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not gameOverMode:
            if moveLeft:
                playerObj['x'] -= playerObj['speed']
            if moveRight:
                playerObj['x'] += playerObj['speed']
            if moveUp:
                playerObj['y'] -= playerObj['speed']
            if moveDown:
                playerObj['y'] += playerObj['speed']

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0

            for i in range(len(squirrelObjs) - 1, -1, -1):
                sqObj = squirrelObjs[i]
                if 'rect' in sqObj and playerObj['rect'].colliderect(sqObj['rect']):

                    if sqObj['width'] * sqObj['height'] <= playerObj['size'] ** 2:
                        SCORE += 100

                        del squirrelObjs[i]

                        if playerObj['facing'] == LEFT:
                            playerObj['surface'] = pygame.transform.scale(SLEFT,
                                                                          (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(SRIGHT,
                                                                          (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == UP:
                            playerObj['surface'] = pygame.transform.scale(SUP,
                                                                          (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == DOWN:
                            playerObj['surface'] = pygame.transform.scale(SDOWN,
                                                                          (playerObj['size'], playerObj['size']))

                        if playerObj['size'] < MAXSIZE:
                            playerObj['size'] += int((sqObj['width'] * sqObj['height']) ** 0.06)

                        if playerObj['speed'] < MAXSPEED:
                            playerObj['speed'] += 1


                    elif not invulnerableMode:
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            gameOverMode = True
                            gameOverStartTime = time.time()
        else:
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return

        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawHealthMeter(currentHealth):
    for i in range(currentHealth):
        pygame.draw.rect(DISPLAYSURF, RED, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH):
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def drawScoreMeter():
    global SCORE
    draw_text(screen, str(SCORE), 30, 620, 0)


def terminate():
    pygame.quit()
    sys.exit()


def Bounce(currentBounce, bounceRate, bounceHeight):
    return int(math.sin((math.pi / float(bounceRate)) * currentBounce) * bounceHeight)


def RandomVelocity():
    speed = random.randint(SQUIRRELMINSPEED, SQUIRRELMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewBat(camerax, cameray):
    sq = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    sq['width'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['x'], sq['y'] = getRandomOffCameraPos(camerax, cameray, sq['width'], sq['height'])
    sq['movex'] = RandomVelocity()
    sq['movey'] = RandomVelocity()
    if sq['movex'] < 0:
        sq['surface'] = pygame.transform.scale(BATIMG, (sq['width'], sq['height']))
    else:
        sq['surface'] = pygame.transform.scale(BATIMG, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10, 18)
    sq['bounceheight'] = random.randint(10, 50)
    return sq


def makeNewGrass(camerax, cameray):
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width'] = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect((gr['x'], gr['y'], gr['width'], gr['height']))
    return gr


def isOutsideActiveArea(camerax, cameray, obj):
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()
