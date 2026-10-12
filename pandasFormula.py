from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

# -----------------------------
# Global var class
# -----------------------------

class globalVar:
    def __init__(self):
        self.initState()
        self.initWindLines()
        self.quadric = gluNewQuadric()

    def initState(self):
        # panda
        self.panPos = [2500, 0, -10]
        self.panAng = 0
        self.panSpeed = 100
        self.panRotAmt = 10
        self.panNRG = 101
        self.currGrid = None
        self.bamEaten = 0
        
        # jumping vars
        self.iniJumpVel = 1500
        self.jumpAng = 45
        self.jumpStartT = None
        self.jumpStartPos = None
        self.jumpG = 1500
        self.jumpCol = False

        # climbing vars
        self.tree2Climb = None

        # Camera
        self.camPos = (2500, 400, 100)

        # Game
        self.totScore = 0
        self.gameState = "running"  # running, over
        self.gameStTime = time.time()
        self.gameRunTime = 0
        self.nrgSpent = 0
        self.gameScore = 0

        # World
        self.groundL = 30000
        self.groundW = 5000
        self.prevT = time.time() 

        # flags
        self.isJumping = False
        self.isClimbing = False

        # tree
        self.treeV = [] 

        # 6 grids of 5000x5000
        for grid in range(5):
            self.treeV.append({"normal": [], "bamboo": []})
            gridZstart = - grid * 6000
            gridZend = - (grid + 1) * 6000

            if grid == 4:
                normalTreeAmt = 5
                bamTreeAmt = 30
            else:
                normalTreeAmt = random.randint(20, 30)
                bamTreeAmt = random.randint(1, 2)

            for i in range(normalTreeAmt):
                treeX = random.uniform(50, self.groundW - 50)
                treeZ = random.uniform(gridZend + 50, gridZstart - 50)
                self.treeV[grid]["normal"].append([treeX, 0, treeZ, False])

            for j in range(bamTreeAmt):
                treeX = random.uniform(50, self.groundW - 50)
                treeZ = random.uniform(gridZend + 50, gridZstart - 50)
                self.treeV[grid]["bamboo"].append([treeX, 0, treeZ, False])

        # rain
        self.rdrops = []
        self.rcount = 950
        self.rainActive = True


        for i in range(0,self.rcount,1):
            self.rdrops.append([
                random.randint(0, self.groundW),
                random.randint(1200, 1600),
                random.randint(-self.groundL, 0)
            ])



        # stone
        self.stonePos = None
        self.stoneCollected = False
        self.showCollectText = False
        self.stoneResetTime = None      # when stone was collected
        self.stone_rstdelay = 4         # seconds before respawn

        self.lastStoneSpawn = time.time()
        self.stoneintrval = 4


        # wind
        self.windStartTime = None
        self.windActive = False
        self.windDir = 1          # 1 = right, -1 = left
        self.windStrength = 45
        self.lastWindSpawn = time.time()
        self.windintrvl = 10
        self.windLines = []
        self.wlinecount = 260
        self.windDuration = 3


        # wall
        self.wallH = 280
        self.wallT = 150
        self.wallZ = random.uniform(-20000, -5000)

        # final dest
        self.cx = 2500
        self.cy = 3
        self.cz = random.randint(-29900, -28800)
        self.showFinalText = False

    def reset(self):
        self.initState()

    def initWindLines(self):
        self.windLines = []

        i = 0
        while i < self.wlinecount:
            self.windLines.append([
                random.randint(0, self.groundW),
                random.randint(40, 500),
                random.randint(-self.groundL + 2500,
                            -self.groundL + 4000)
            ])
            i += 1



gVar = globalVar()

# -----------------------------
# all the helper functions here
# -----------------------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glDisable(GL_DEPTH_TEST)
    glColor3f(0,0,0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST) 

def colliCheck(pandaPos, objPos, objRad, objH):
    pX, pY, pZ = pandaPos

    dX = pX - objPos[0]
    dZ = pZ - objPos[2]
    hDist = (dX*dX + dZ*dZ)**0.5

    if hDist < (30 + objRad) and pY < objH:
        return True

    return False


def rotApt(x, y, z, wrt, ang):
    theta = math.radians(ang) 
    xT = x - wrt[0]
    zT = z - wrt[2]
    xR = xT * math.cos(theta) - zT * math.sin(theta)
    zR = xT * math.sin(theta) + zT * math.cos(theta)
    x = xR + wrt[0]
    z = zR + wrt[2]
    return (x, y, z)

def getDelT():
    currT = time.time()
    delT = currT - gVar.prevT
    gVar.prevT = currT
    return delT

def sphereDraw(r, g, b, v, rad):
    glPushMatrix()
    glColor3f(r, g, b)
    glTranslatef(v[0], v[1], v[2])
    gluSphere(gVar.quadric, rad, 16, 16)  # params are: quadric, radius, slices, stacks
    glPopMatrix()


def cylinderDraw(r, g, b, v, bRad, tRad, h, rotAng):
    glPushMatrix()  
    glColor3f(r, g, b)
    glTranslatef(v[0], v[1], v[2])
    glRotatef(rotAng, 1, 0, 0)
    gluCylinder(gVar.quadric, bRad, tRad, h, 16, 16)  # Take cube sz as  param
    glPopMatrix()

def cylinderDraw(r, g, b, v, bRad, tRad, h, rotAng):
    glPushMatrix()  
    glColor3f(r, g, b)
    glTranslatef(v[0], v[1], v[2])
    glRotatef(rotAng, 1, 0, 0) 
    gluCylinder(gluNewQuadric(), bRad, tRad, h, 10, 10)  # parameters are: quadric, base radius, top radius, height, slices, stacks
    glPopMatrix()


# -----------------------------
# Camera Setup
# -----------------------------

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if gVar.gameState == "running" or gVar.gameState == "complete":
        if gVar.isClimbing:
            gluPerspective(80, 1.25, 0.1, 8000)  
        else:
            gluPerspective(60, 1.25, 0.1, 8000)  
    else:
        gluPerspective(120, 1.25, 0.1, 8000)  
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    pX, pY, pZ = gVar.panPos

    if gVar.gameState == "running" or gVar.gameState == "complete":
        # def camera config
        cDist = 400          
        cH = 220        
        lookAtY = 190     

        # for climbing
        if gVar.isClimbing:
            cDist = 220          
            cH = 100           
            lookAtY = pY + 200
    else:
        cDist = 900          
        cH = 400        
        lookAtY = 0  

    cX, cY, cZ = pX, pY + cH, pZ + cDist
    cX, cY, cZ = rotApt(cX, cY, cZ, (pX, pY, pZ), gVar.panAng) # for dynamic movement of camera

    gVar.camPos = (cX, cY, cZ)

    gluLookAt(cX, cY, cZ, 
              pX, lookAtY, pZ, 
              0, 1, 0)  # Up vector (z-axis)



# -----------------------------
# scene
# -----------------------------
def sceneDraw():
    gridLen = 500  
    cols = gVar.groundW // gridLen  

    glBegin(GL_QUADS)
    colorToggle = False
    for col in range(cols):
        if colorToggle:
            glColor3f(0.15, 0.35, 0.1)  # darker green
        else:
            glColor3f(0.25, 0.45, 0.15)

        glVertex3f(col * gridLen, 0, 0)
        glVertex3f((col+1) * gridLen, 0, 0)
        glVertex3f((col+1) * gridLen, 0, -gVar.groundL)
        glVertex3f(col * gridLen, 0, -gVar.groundL)

        colorToggle = not colorToggle  
    glEnd()


    # Underground
    glColor3f(0.36, 0.25, 0.20)

    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, -gVar.groundL)
    glVertex3f(0, -500, -gVar.groundL)
    glVertex3f(0, -500, 0)

    glVertex3f(gVar.groundW, 0, 0)
    glVertex3f(gVar.groundW, 0, -gVar.groundL)
    glVertex3f(gVar.groundW, -500, -gVar.groundL)
    glVertex3f(gVar.groundW, -500, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(gVar.groundW, 0, 0)
    glVertex3f(gVar.groundW, -500, 0)
    glVertex3f(0, -500, 0)

    glVertex3f(0, 0, -gVar.groundL)
    glVertex3f(gVar.groundW, 0, -gVar.groundL)
    glVertex3f(gVar.groundW, -500, -gVar.groundL)
    glVertex3f(0, -500, -gVar.groundL)
    glEnd()




def bgDraw():
    glDisable(GL_DEPTH_TEST)

    # to 2D 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # bg Color
    glBegin(GL_QUADS)
    glColor3f(0.63, 0.81, 0.98) # top
    glVertex2f(0, 800)
    glVertex2f(1000, 800)
    glColor3f(0.07, 0.11, 0.21) # bottom
    glVertex2f(1000, 0)
    glVertex2f(0, 0)
    glEnd()

    # back
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)



def drawNormalTree(t):
    x, y, z, isEaten = t
    glPushMatrix()
    glTranslatef(x, y, z)

    cylinderDraw(0.55, 0.27, 0.07, (0, 0, 0), 40, 20, 1000, -90)

    glTranslatef(0, 800, 0)
    glColor3f(0.1, 0.3, 0.1)
    glBegin(GL_TRIANGLES)
    for a in range(0, 360, 20):
        t1 = math.radians(a)
        t2 = math.radians(a + 20)
        glVertex3f(0, 600, 0)
        glVertex3f(math.cos(t1) * 300, 0, math.sin(t1) * 300)
        glVertex3f(math.cos(t2) * 300, 0, math.sin(t2) * 300)
    glEnd()

    glPopMatrix()



def drawBambooTree(t):
    x, y, z = t[0], t[1], t[2]
    isEaten = t[3]
    glPushMatrix()
    glTranslatef(x, y, z)

    segH = 150          # h of a seg
    segCnt = 12       # num of seg
    rad = 20    

    # drawing a seg
    for i in range(segCnt):
        cylinderDraw(0.1, 0.3, 0.1,  # Dark bam color
                     (0, i * segH, 0),
                     rad, rad - 5,
                     segH, -90)
        sphereDraw(0.05, 0.2, 0.05,
                   (0, i * segH, 0),
                   15)

    if not isEaten:
        leafBaseY = (segCnt - 3) * segH  # leaves st here
        leafSpacing = 50                   
        leafL = 200
        leafW = 20
        leafH = 65

        leafLvl = [0.5, 1.2, 2.0, 2.5, 3.0, 4.0]
    
        glColor3f(0, 0.3, 0)  # Dark green leaves

        for i in range(len(leafLvl)):
            l = leafLvl[i] 
            ang = math.radians(i * 60 + 45)

            # leaf base
            baseX = math.cos(ang) * rad
            baseZ = math.sin(ang) * rad
            baseY = leafBaseY + l * leafSpacing

            # leaf tip
            tipX = baseX + math.cos(ang) * leafL
            tipZ = baseZ + math.sin(ang) * leafL
            tipY = baseY + leafH

            # baseV
            leftBaseX = baseX - math.sin(ang) * leafW
            leftBaseZ = baseZ + math.cos(ang) * leafW
            rightBaseX = baseX + math.sin(ang) * leafW
            rightBaseZ = baseZ - math.cos(ang) * leafW

            glBegin(GL_TRIANGLES)
            glVertex3f(leftBaseX, baseY, leftBaseZ)
            glVertex3f(rightBaseX, baseY, rightBaseZ)
            glVertex3f(tipX, tipY, tipZ)
            glEnd()

    glPopMatrix()



def treeDraw():
    pZ = gVar.panPos[2] 
    
    for i in range(5):
        if -6000 * (i + 1) <= pZ < -6000 * i:
            gVar.currGrid = i
            break

    for grid in [gVar.currGrid - 1, gVar.currGrid, gVar.currGrid + 1]:
        if 0 <= grid <= 4:
            for t in gVar.treeV[grid]["normal"]:
                drawNormalTree(t)
            for t in gVar.treeV[grid]["bamboo"]:
                drawBambooTree(t)


def drawWall():
    glPushMatrix()
    glColor3f(0.55, 0.15, 0.10)
    glTranslatef(gVar.groundW/2, gVar.wallH/2, gVar.wallZ)
    glScalef(gVar.groundW, gVar.wallH, gVar.wallT)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_the_rains():
    if gVar.rainActive==False:
        return

    glColor3f(0.6, 0.6, 1.0)
    glBegin(GL_LINES)

    for d in gVar.rdrops:
        glVertex3f(*d)
        glVertex3f(d[0], d[1]-40, d[2])
        deltatime=getDelT()
        speed=750
        d[1]-=speed*deltatime

        if d[1] < 0:
            d[1] = random.randint(1200,1600)
            d[0] = random.randint(0, gVar.groundW)
            d[2] = random.randint(-gVar.groundL, 0)

    glEnd()


# wind
def wgenerate():

  if gVar.rainActive==False:

     currTime = time.time()
     # start wind after interval
     if  gVar.windActive==False and currTime - gVar.lastWindSpawn > gVar.windintrvl:
        gVar.windActive = True
        gVar.windDir = random.choice([-1, 1])
        gVar.windStartTime = currTime
        gVar.lastWindSpawn = currTime
        gVar.initWindLines()
     # stop wind after duration
     if gVar.windActive==True and currTime - gVar.windStartTime > gVar.windDuration:
        gVar.windActive = False

  else:
       gVar.windActive = False
       return


def apply_thewind():
    if  gVar.windActive==False or gVar.rainActive==True:
        return

    pX, pY, pZ = gVar.panPos
    theta = math.radians(gVar.panAng)

    frwdX = math.sin(theta)
    frwdZ = -math.cos(theta)

    pX -= frwdX * gVar.windDir * gVar.windStrength * 0.03
    pZ -= frwdZ * gVar.windDir * gVar.windStrength * 0.03

    gVar.panPos = (pX, pY, pZ)



def drawWind():
    if  gVar.windActive==False or gVar.rainActive==True:
        return

    glColor3f(1, 1, 1)
    glBegin(GL_LINES)

    for w in gVar.windLines:
        glVertex3f(w[0], w[1], w[2])
        glVertex3f(w[0], w[1], w[2] + gVar.windDir * 220)

    glEnd()

def update_wlines():
    if  gVar.windActive==False or gVar.rainActive==True:
        return

    px,py,pz= gVar.panPos
    currT = time.time()
    deltatime2 = currT - gVar.prevT
    speed=9900
    for w in gVar.windLines:
        w[2] *= gVar.windDir *speed*deltatime2 # move toward +Z

        if w[2] > pz+30:
            w[0] = random.randint(0, gVar.groundW)
            w[2] = random.randint(-gVar.groundL+4500,10)


def drawPandaDied(pos, ang):
    pX, pY, pZ = pos
    glPushMatrix()
    glTranslatef(pX, 0, pZ)
    glRotatef(90, 1, 0, 0)
    glRotatef(180 - ang, 0, 1, 0)

    # Body
    sphereDraw(0, 0, 0, (0, 50, 0), 50)
    sphereDraw(1, 1, 1, (0, 50, 0), 45)

    # Head
    sphereDraw(1, 1, 1, (0, 125, 0), 30)
    sphereDraw(0, 0, 0, (-10, 130, 25), 5)
    sphereDraw(0, 0, 0, (10, 130, 25), 5)
    sphereDraw(0, 0, 0, (-20, 150, 0), 10)
    sphereDraw(0, 0, 0, (20, 150, 0), 10)

    # Legs
    cylinderDraw(0, 0, 0, (-25, 15, -20), 10, 10, 30, 90)
    cylinderDraw(0, 0, 0, (25, 15, -20), 10, 10, 30, 90)

    # Arms
    cylinderDraw(0, 0, 0, (-40, 55, 0), 8, 8, 35, 90)
    cylinderDraw(0, 0, 0, (40, 55, 0), 8, 8, 35, 90)
    glPopMatrix()

def drawing_finaldestination():

   if gVar.gameState=="running" and gVar.showCollectText == False:
      cylinderDraw(1, 0, 0, (gVar.cx,gVar.cy, gVar.cz), 120, 120, 465, -90)
   else:
        return

def finaldest_distance():

     if gVar.gameState == "complete":
        gVar.showFinalText = False
        return
     gVar.showFinalText = False
     playerx,playery,playerz=gVar.panPos
     fx,fy,fz=gVar.cx, gVar.cy, gVar.cz
     finaldist=((playerx-fx)**2+(playerz-fz)**2)**0.5

     if finaldist<220:
         gVar.showFinalText = True
     else:
         gVar.showFinalText = False

def showScreen():
    """
    Display function to render the game scene using gVar class.
    - Clears the screen and sets up the camera.
    - Draws world and pan.
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size


    
    bgDraw()
    setupCamera()  
    sceneDraw()
    treeDraw()

    if gVar.gameState == "running" or gVar.gameState == "complete":
        if not gVar.isClimbing:
            drawWalkingPanda(gVar.panPos, gVar.panAng)
        elif gVar.tree2Climb:
            drawClimbingPanda(gVar.tree2Climb, gVar.panAng)
    else:
        drawPandaDied(gVar.panPos, gVar.panAng)
   
    draw_the_rains()
    drawWind()
    drawStone()
    drawWall()
    if gVar.gameState == "running":
        drawing_finaldestination()

    # display texts
    if gVar.showFinalText:
        draw_text(380, 450, "PRESS F TO FINISH")
    
    if gVar.gameState == "complete":
        draw_text(300, 710,f"CONGRATULATIONS! YOUR GAME HAS COMPLETED")
        draw_text(400, 680,f"YOUR SCORE IS {int(gVar.gameScore)}")
        draw_text(400, 650, f"PRESS R TO RESTART")
        draw_text(400, 620, f"PRESS Q TO QUIT")
    
    if gVar.gameState == "over":
        draw_text(10, 770, f"GAME OVER!")
        draw_text(10, 710, f"PRESS R TO RESTART!")
        draw_text(10, 740, f"YOUR SCORE: {int(gVar.gameScore)}")

    if gVar.gameState == "running":
        draw_text(10, 770, f"Energy: {int(gVar.panNRG)}")
        draw_text(10, 740, f"Leaves Eaten: {gVar.bamEaten}")
    
    if gVar.gameState == "running" or gVar.gameState == "complete":
        if gVar.showCollectText==True:
            draw_text(420, 500, "PRESS S TO COLLECT RAIN STONE")

        if gVar.windActive==True:
            draw_text(420, 400, "OH! WIND AGAIN!")

        if gVar.tree2Climb:
            if not gVar.isClimbing:
                draw_text(100, 100, "PRESS C TO CLIMB")
            else:

                draw_text(100, 100, "PRESS C TO CLIMB OFF")
                if gVar.panPos[1] > 1300 and not gVar.tree2Climb[4]:
                    draw_text(100, 150, "PRESS E TO EAT LEAVES")
    glutSwapBuffers()
# -----------------------------
# drawing the panda
# ----------------------------
def drawWalkingPanda(pos, ang):
    pX, pY, pZ = pos
    glPushMatrix()
    glTranslatef(pX, pY, pZ)
    glRotatef(180 - ang, 0, 1, 0)

    # Body
    sphereDraw(0, 0, 0, (0, 50, 0), 50)
    sphereDraw(1, 1, 1, (0, 50, 0), 45)

    # Head
    sphereDraw(1, 1, 1, (0, 125, 0), 30)
    sphereDraw(0, 0, 0, (-10, 130, 25), 5)
    sphereDraw(0, 0, 0, (10, 130, 25), 5)
    sphereDraw(0, 0, 0, (-20, 150, 0), 10)
    sphereDraw(0, 0, 0, (20, 150, 0), 10)

    # Legs
    cylinderDraw(0, 0, 0, (-25, 15, -20), 10, 10, 30, 90)
    cylinderDraw(0, 0, 0, (25, 15, -20), 10, 10, 30, 90)

    # Arms
    cylinderDraw(0, 0, 0, (-40, 55, 0), 8, 8, 35, 90)
    cylinderDraw(0, 0, 0, (40, 55, 0), 8, 8, 35, 90)
    glPopMatrix()


def drawClimbingPanda(treeInfo, ang):
    tX, tY, tZ, treeType, isEaten, idx = treeInfo
    pY = gVar.panPos[1]
    glPushMatrix()
    glTranslatef(tX, pY + 50, tZ)
    glRotatef(180 - ang, 0, 1, 0)
    glRotatef(-30, 1, 0, 0)  

    # Body
    sphereDraw(0, 0, 0, (0, 50, 0), 50)
    sphereDraw(1, 1, 1, (0, 50, 0), 45)

    # Head 
    sphereDraw(1, 1, 1, (0, 130, 10), 30)
    sphereDraw(0, 0, 0, (-10, 135, 30), 5)
    sphereDraw(0, 0, 0, (10, 135, 30), 5)
    sphereDraw(0, 0, 0, (-20, 150, 0), 10)
    sphereDraw(0, 0, 0, (20, 150, 0), 10)

    # Legs 
    cylinderDraw(0, 0, 0, (-25, 5, -10), 10, 10, 25, 60)
    cylinderDraw(0, 0, 0, (25, 5, -10), 10, 10, 25, 60)

    # Arms
    cylinderDraw(0, 0, 0, (-40, 80, 15), 8, 8, 40, 70)
    cylinderDraw(0, 0, 0, (40, 80, 15), 8, 8, 40, 70)
    glPopMatrix()


def draw_the_rains():
    if gVar.rainActive==False:
        return

    glColor3f(0.6, 0.6, 1.0)
    glBegin(GL_LINES)

    for d in gVar.rdrops:
        glVertex3f(*d)
        glVertex3f(d[0], d[1]-40, d[2])
        deltatime=time.time()-gVar.prevT
        speed=750
        d[1]-=speed*deltatime

        if d[1] < 0:
            d[1] = random.randint(1200,1600)
            d[0] = random.randint(0, gVar.groundW)
            d[2] = random.randint(-gVar.groundL, 0)

    glEnd()

#stone
def stonesvisibility():

    px, py, pz = gVar.panPos
    theta = math.radians(gVar.panAng)

    frwrddX = math.sin(theta)
    frwrddZ = -math.cos(theta)

    dist = random.uniform(800, 1200)

    gVar.stonePos = [
        px + frwrddX * dist,
        10,
        pz + frwrddZ * dist
    ]


def drawStone():
    if gVar.stoneCollected==False and gVar.stonePos is not None:
      glPointSize(46)
      glColor3f(1, 0.5, 0)
      glBegin(GL_POINTS)
      glVertex3f(*gVar.stonePos)
      glEnd()

    else:
         return


def stones_distance():

    if gVar.stoneCollected ==False and gVar.stonePos is not None:

      px, py, pz = gVar.panPos
      sx, py, sz = gVar.stonePos

      dist = ((px - sx)**2 + (pz - sz)**2)**0.5
      if dist<160:
         gVar.showCollectText=True
      else:
         gVar.showCollectText=False

    else:
         return


# -----------------------------
# Keyboard
# -----------------------------
def keyboardListener(key, x, y):
    if gVar.gameState == "running":
        if key == b'f' and gVar.showFinalText==True:
            gVar.gameState= "complete"
    
    if key==b'r' and (gVar.gameState == "over" or gVar.gameState == "complete"):
        gVar.reset()

    if key==b'q' and gVar.gameState == "complete":
        glutLeaveMainLoop()
    

    pX, pY, pZ = gVar.panPos
    theta = math.radians(gVar.panAng)

    if (gVar.gameState == "running" or gVar.gameState == "complete"):
        # jumping
        if key==b' ' and not gVar.isJumping:
            gVar.isJumping = True
            gVar.jumpStartPos = (pX, pY, pZ)
            gVar.jumpStartT = time.time()

        # climbing
        if key == b'c' and gVar.tree2Climb:
            if gVar.isClimbing:
                if pY > 20:
                    return  
                gVar.isClimbing = False
                gVar.panPos = (pX, 0, pZ)
            else:
                gVar.isClimbing = True  

        # rain stone collecting
        if key == b's' and gVar.showCollectText==True:
            gVar.stoneCollected = True
            gVar.rainActive = False
            gVar.stoneResetTime = time.time()
            gVar.showCollectText=False

        # eat leaves
        if key == b'e' and gVar.isClimbing:
            if pY > 1300:
                tX, tY, tZ, treeType, isEaten, idx = gVar.tree2Climb

                if treeType == "bamboo":
                    gVar.treeV[gVar.currGrid]["bamboo"][idx][3] = True
                    gVar.tree2Climb[4] = True
                    if (gVar.gameState == "running"):
                        gVar.panNRG = 101
                        gVar.bamEaten += 1
    


def specialKeyListener(key, x, y):
    pX, pY, pZ = gVar.panPos
    theta = math.radians(gVar.panAng)
    if (gVar.gameState == "running" or gVar.gameState == "complete"):
        if not gVar.isClimbing:
            if key == GLUT_KEY_UP and not gVar.isJumping:
                pX += math.sin(theta) * gVar.panSpeed
                pZ -= math.cos(theta) * gVar.panSpeed
            if key == GLUT_KEY_DOWN and not gVar.isJumping:
                pX -= math.sin(theta) * gVar.panSpeed
                pZ += math.cos(theta) * gVar.panSpeed

            pX = max(10, min(gVar.groundW - 10, pX))
            pZ = max(-gVar.groundL + 10, min(-10, pZ))

            # if colliding while walking
            if ifWallCollided((pX, pY, pZ)):
                return
            for treeType in ["normal", "bamboo"]:
                for tX, tY, tZ, isEaten in gVar.treeV[gVar.currGrid][treeType]:
                    if colliCheck((pX, pY, pZ), (tX, tY, tZ), 30, 2225):   
                        return
            gVar.panPos = (pX, pY, pZ)
        else:
            if key == GLUT_KEY_UP:
                pY += 20
                if gVar.tree2Climb[3] == "normal":
                    pY = min(pY, 800)
                else:
                    pY = min(pY, 1350)
            if key == GLUT_KEY_DOWN:
                pY -= 20
                pY = max(0, pY)  
        
        if key == GLUT_KEY_LEFT:
            gVar.panAng = (gVar.panAng - gVar.panRotAmt) % 360
        if key == GLUT_KEY_RIGHT:
            gVar.panAng = (gVar.panAng + gVar.panRotAmt) % 360
        gVar.panPos = (pX, pY, pZ)



# -----------------------------
# sp movement (jumping & climbing)
# -----------------------------
def doJumpMotion():
    pX, pY, pZ = gVar.jumpStartPos
    theta = math.radians(gVar.panAng)
    jumpTheta = math.radians(gVar.jumpAng)

    elapsedT = time.time() - gVar.jumpStartT

    # forward dist
    if not gVar.jumpCol:
        fDist = gVar.iniJumpVel * math.cos(jumpTheta) * elapsedT
        # face pandas direction
        pX = pX + math.sin(theta) * fDist
        pZ = pZ - math.cos(theta) * fDist

    # up motion
    pY = pY + gVar.iniJumpVel * math.sin(jumpTheta) * elapsedT - 0.5 * gVar.jumpG * elapsedT * elapsedT

    if pY <= 0:
        pY = 0
        gVar.isJumping = False
        gVar.jumpCol = False

    pX = max(10, min(gVar.groundW - 10, pX))
    pZ = max(-gVar.groundL + 10, min(-10, pZ))

    # if colliding while jumping
    if not gVar.jumpCol:
        if pY < gVar.wallH:
            if (gVar.wallZ - (gVar.wallT/2) - 40) < pZ < (gVar.wallZ + (gVar.wallT/2) + 40):
                gVar.jumpCol = True

        for treeType in ("normal", "bamboo"):
            for tX, tY, tZ, isEaten in gVar.treeV[gVar.currGrid][treeType]:
                if colliCheck((pX, pY, pZ), (tX, tY, tZ), 20, 2225):
                    gVar.jumpCol = True
                    break
            if gVar.jumpCol:
                break
    gVar.panPos = (pX, pY, pZ)


def ok2Climb():
    pX, pY, pZ = gVar.panPos
    gVar.tree2Climb = None
    for treeType in ["normal", "bamboo"]:
        trees = gVar.treeV[gVar.currGrid][treeType]
        for i in range(len(trees)):
            tX, tY, tZ, isEaten = trees[i]
            if colliCheck((pX, pY, pZ), (tX, tY, tZ), 100, 2225):
                gVar.tree2Climb = [tX, tY, tZ, treeType, isEaten, i]
                return
     
def ifWallCollided(pandaPos):
    pX, pY, pZ = pandaPos

    # wall
    wX = gVar.groundW / 2
    wY = gVar.wallH / 2
    wZ = gVar.wallZ
    wW = gVar.groundW
    wH = gVar.wallH
    wT = gVar.wallT

    # panda
    pL = pX - 50 / 2
    pR = pX + 50 / 2
    pB = pY
    pT = pY + 60
    pF = pZ - 50 / 2
    pBk = pZ + 50 / 2

    wL = wX - wW / 2
    wR = wX + wW / 2
    wB = 0
    wT = wH
    wF = wZ - wT / 2
    wBk = wZ + wT / 2

    if pL < wR and pR > wL and pB < wT and pT > wB and pF < wBk and pBk > wF:
        return True
    return False


# Idle Function (updating each frame)
# -----------------------------
def idle():
    delT = getDelT()

    # energy calc
    if gVar.gameState == "running":
        calcNRG(delT)
        gVar.gameRunTime = time.time() - gVar.gameStTime


    # handling jump
    if gVar.isJumping and not gVar.isClimbing:
        doJumpMotion()

    # handling tree climbing
    ok2Climb()

    # rain and stone

    # spawn stone
    if gVar.stonePos is None and time.time() - gVar.lastStoneSpawn > gVar.stoneintrval:
        stonesvisibility()
        gVar.lastStoneSpawn = time.time()
        gVar.rainActive = True
        gVar.stoneCollected = False


    # reset after stone collected
    if gVar.stoneCollected and gVar.stoneResetTime is not None:
        if time.time() - gVar.stoneResetTime > gVar.stone_rstdelay:
            gVar.stonePos = None
            gVar.stoneCollected = False
            gVar.rainActive = True
            gVar.stoneResetTime = None
            gVar.lastStoneSpawn = time.time()

    wgenerate()
    apply_thewind()
    update_wlines()
    stones_distance()

    finaldest_distance()

    if gVar.gameState == "complete":
        efficiency = max(0, gVar.nrgSpent - gVar.gameRunTime) / gVar.nrgSpent * 100
        bamPt = gVar.bamEaten * 10
        gVar.gameScore = efficiency + bamPt

    glutPostRedisplay()

def calcNRG(delT):
    drain = 0

    if gVar.windActive or gVar.rainActive:
        drain += 1 * delT
    else:
        drain += 0.5 * delT

    if gVar.isJumping or gVar.isClimbing:
        drain += 1.5 * delT

    gVar.nrgSpent += drain
    gVar.panNRG -= drain
    gVar.panNRG = max(0, gVar.panNRG)
    
    if gVar.panNRG <= 0 and gVar.gameState == "running":
        gVar.gameState = "over"
        gVar.isClimbing = False
        gVar.isJumping = False
        efficiency = max(0, gVar.nrgSpent - gVar.gameRunTime) / gVar.nrgSpent * 100
        bamPt = gVar.bamEaten * 10
        gVar.gameScore = efficiency + bamPt
    




# -----------------------------
# Main
# -----------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000,800)
    glutInitWindowPosition(0,0)
    glutCreateWindow(b"panda's Formula")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__=="__main__":
    main()
