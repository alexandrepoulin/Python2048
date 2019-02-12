import pygame
import random

import time

GAME_SIZE           = 500
TILE_SIZE           = 105
TILE_SPACING        = 16
GAME_CORNER_RADIUS  = 5
TILE_CORNER_RADIUS  = 2
MOVEMENT_TIME       = 100
SCORE_HEIGHT        = 100
SCORE_WIDTH         = 202

pygame.font.init()
fontPath = "fonts/clearsans-1.00/TTF/ClearSans-Bold.ttf"
fontSizeBig = 48
fontSizeMedBig = 44
fontSizeMedSmall = 40
fontSizeSmall = 38
fontBig = pygame.font.Font(fontPath, fontSizeBig)
fontMedBig = pygame.font.Font(fontPath, fontSizeMedBig)
fontMedSmall = pygame.font.Font(fontPath, fontSizeMedSmall)
fontSmall = pygame.font.Font(fontPath, fontSizeSmall)

fontText = pygame.font.Font(fontPath, 20)

white = (255,255,255)
black = (0,0,0)

colGrid = (187,173,160)
colEmpty = (205,193,180)
col2 = (238,228,218)
col4 = (237,224,200)
col8 = (242,177,121)
col16 = (245,149,99)
col32 = (246,124,95)
col64 = (246,94,59)
col128 = (237,207,114)
col256 = (237,204,97)
col512 = (237,200,80)
col1024 = (237,197,63)
col2048 = (237,194,46)
colLarge = (60,58,50)
tileColors = [colEmpty,col2,col4,col8,col16,col32,col64,col128,col256,col512,col1024,col2048,colLarge]

def drawRoundRec(surf, pos, size, rad, c):
    x, y = int(pos[0]),int(pos[1])
    w, h = int(size[0]),int(size[1])
    r = int(rad)
    pygame.draw.circle(surf, c, (x+r,y+r), r)
    pygame.draw.circle(surf, c, (x+w-r,y+r), r)
    pygame.draw.circle(surf, c, (x+r,y+h-r), r)
    pygame.draw.circle(surf, c, (x+w-r,y+h-r), r)
    surf.fill(c,rect=[x+r,y,w-2*r,h])
    surf.fill(c,rect=[x,y+r,w,h-2*r])

def convIndToPos(ind):
        return ((ind[0]+1)*TILE_SPACING+ind[0]*TILE_SIZE,(ind[1]+1)*TILE_SPACING+ind[1]*TILE_SIZE)

class Tile:

    def __init__(self, pot, pos, scaleInd):
        self.pot = pot
        self.hasMerged = False
        self.pos = pos
        self.dest = pos
        self.speed = (0,0)
        self.scales = [x/10 for x in range(1,11)] + [x/10 for x in range(11,16)] +[x/10 for x in range(15,9,-1)]
        self.scaleInd = scaleInd
        
    def changePOT(self,newPOT):
        self.pot = newPOT

    def changePos(self, pos):
        self.pos = self.dest
        self.dest = pos
        self.speed = (int((self.dest[0]-self.pos[0])/MOVEMENT_TIME),int((self.dest[1]-self.pos[1])/MOVEMENT_TIME))

    def drawTile(self, surf):
        col = tileColors[self.pot] if self.pot <=12 else tileColors[-1]
        labelText = "" if self.pot == 0 else str(2**self.pot)

        fontSizeUsed = fontSizeBig
        fontToUse = fontBig
        if  self.pot>=7 and self.pot <=9:
            fontSizeUsed = fontSizeMedBig
            fontToUse = fontMedBig
        elif self.pot >=10 and self.pot <=11:
            fontSizeUsed = fontSizeMedSmall
            fontToUse = fontMedSmall
        elif self.pot >11:
            fontSizeUsed = fontSizeSmall
            fontToUse = fontSmall

        if self.dest != self.pos:
            tempPos = (self.pos[0] + self.speed[0],self.pos[1] + self.speed[1])
            oldDist = (self.dest[0] - self.pos[0],self.dest[1] - self.pos[1])
            newDist = (self.dest[0] - tempPos[0],self.dest[1] - tempPos[1])
            if oldDist[0]*newDist[0] >= 0 and  oldDist[1]*newDist[1] >= 0:
                self.pos = tempPos
            else:
                self.pos = self.dest
                self.speed = (0,0)                   

        label = fontToUse.render(labelText, 1, black if self.pot <=2 else white)
        labelSize = label.get_size()
        labelPos = (self.pos[0]+((TILE_SIZE-labelSize[0])>>1), self.pos[1]+((TILE_SIZE-labelSize[1])>>1))

        s = self.scales[self.scaleInd]
        if self.scaleInd > 9:
            self.scaleInd -= 1
        if self.scaleInd < 9:
            self.scaleInd += 1

        scaledPos = (self.pos[0] + (1-s)*TILE_SIZE/2, self.pos[1] + (1-s)*TILE_SIZE/2)
        
        drawRoundRec(surf,scaledPos,(s*TILE_SIZE,s*TILE_SIZE),s*TILE_CORNER_RADIUS,col)
        surf.blit(label, labelPos)
        


class Grid:

    def __init__(self):
        ##this keeps track of all the powers of two
        self.gameGrid = [[0 for x in range(4)] for y in range(4)]
        ##these are the static blank tiles that never move
        self.gameStaticTiles  = [[Tile(0,convIndToPos((x,y)),9) for x in range(4)] for y in range(4)]
        ##these are the tiles which will move
        self.gameTiles  = dict()
        self.addNum = False
        self.ready = True

        self.currentBestTile = 1
        self.currentScore = 0

        self.lastBestTile = 1
        self.lastBestScore = 0

        self.bestTileEver = 1
        self.bestScoreEver = 0
        

    def isReady(self):
        return self.ready
        
    def setXYpot(self,pos,val):
        self.gameGrid[pos[0]][pos[1]] = val
        
    def getXY(self,pos):
        return self.gameGrid[pos[0]][pos[1]]

    def getEmptyPositions(self):
        emptySlots = []
        for y in range(4):
            for x in range(4):
                if self.getXY((x,y)) == 0:
                    emptySlots.append((x,y))
        return emptySlots

    def hasEmptyPositions(self):
        for y in range(4):
            for x in range(4):
                if self.getXY((x,y)) == 0:
                    return True
        return False

    def newNumber(self):
        value = 1 if random.random() < 0.9 else 2
        emptyPos= self.getEmptyPositions()
        randPos = emptyPos.pop(random.randrange(len(emptyPos)))
        self.gameTiles[randPos] = [Tile(value,((randPos[0]+1)*TILE_SPACING+randPos[0]*TILE_SIZE,(randPos[1]+1)*TILE_SPACING+randPos[1]*TILE_SIZE),0)]
        self.setXYpot(randPos, value)
        self.ready = False
        if value > self.currentBestTile:
            self.currentBestTile = value
        

    def newGame(self):
        for y in range(4):
            for x in range(4):
                self.setXYpot((x,y),0)
        self.gameTiles  = dict()

        self.lastBestTileEver = self.currentBestTile
        self.lastBestScore = self.currentScore
        self.currentBestTile = 1
        self.currentScore = 0
        
        self.newNumber()
        self.newNumber()
        

    def canMoveLeft(self):
        for y in range(4):
            minX = 0
            for xRef in range(1,4):
                xRefPOT = self.getXY((xRef,y))
                if xRefPOT == 0:
                    continue
                for xCheck in range(minX, xRef):
                    ti = self.getXY((xCheck,y))
                    if ti == 0 or ti == xRefPOT:
                        return True
                    else:
                        minX+=1
        return False

    def canMoveRight(self):
        for y in range(4):
            maxX = 3
            for xRef in range(2,-1,-1):
                xRefPOT = self.getXY((xRef,y))
                if xRefPOT == 0:
                    continue
                for xCheck in range(maxX, xRef,-1):
                    ti = self.getXY((xCheck,y))
                    if ti == 0 or ti == xRefPOT:
                        return True
                    else:
                        maxX-=1
        return False
    
    def canMoveUp(self):
        for x in range(4):
            minY = 0
            for yRef in range(1,4):
                yRefPOT = self.getXY((x,yRef))
                if yRefPOT == 0:
                    continue
                for yCheck in range(minY, yRef):
                    ti = self.getXY((x,yCheck))
                    if ti == 0 or ti == yRefPOT:
                        return True
                    else:
                        minY+=1
        return False
    
    def canMoveDown(self):
        for x in range(4):
            maxY = 3
            for yRef in range(2,-1,-1):
                yRefPOT = self.getXY((x,yRef))
                if yRefPOT == 0:
                    continue
                for yCheck in range(maxY, yRef,-1):
                    ti = self.getXY((x,yCheck))
                    if ti == 0 or ti == yRefPOT:
                        return True
                    else:
                        maxY-=1
        return False

    def isGameOver(self):
        return not (self.canMoveLeft() or self.canMoveRight() or self.canMoveUp() or self.canMoveDown())

    def moveLeft(self):
        if not self.canMoveLeft():
            return -1
        for y in range(4):
            minX = 0
            for xRef in range(1,4):
                xRefPOT = self.getXY((xRef,y))
                if xRefPOT == 0:
                    continue
                for xCheck in range(minX, xRef):
                    ti = self.getXY((xCheck,y))
                    if ti == 0:
                        self.gameTiles[(xRef,y)][0].changePos(convIndToPos((xCheck,y)))
                        self.gameTiles[(xCheck,y)]  = [self.gameTiles[(xRef,y)][0]]
                        del self.gameTiles[(xRef,y)]
                        self.setXYpot((xCheck,y),xRefPOT)
                        self.setXYpot((xRef,y),0)
                        break
                    elif ti == xRefPOT:
                        self.gameTiles[(xRef,y)][0].changePos(convIndToPos((xCheck,y)))
                        self.gameTiles[(xCheck,y)].append(self.gameTiles[(xRef,y)][0])
                        del self.gameTiles[(xRef,y)]
                        self.setXYpot((xCheck,y),xRefPOT+1)
                        self.setXYpot((xRef,y),0)
                        minX+=1
                        break
                    else:
                        minX+=1
        return 1

    def moveRight(self):
        if not self.canMoveRight():
            return -1
        for y in range(4):
            maxX = 3
            for xRef in range(2,-1,-1):
                xRefPOT = self.getXY((xRef,y))
                if xRefPOT == 0:
                    continue
                for xCheck in range(maxX, xRef,-1):
                    ti = self.getXY((xCheck,y))
                    if ti == 0:
                        self.gameTiles[(xRef,y)][0].changePos(convIndToPos((xCheck,y)))
                        self.gameTiles[(xCheck,y)]  = [self.gameTiles[(xRef,y)][0]]
                        del self.gameTiles[(xRef,y)]
                        self.setXYpot((xCheck,y),xRefPOT)
                        self.setXYpot((xRef,y),0)
                        break
                    elif ti == xRefPOT:
                        self.gameTiles[(xRef,y)][0].changePos(convIndToPos((xCheck,y)))
                        self.gameTiles[(xCheck,y)].append(self.gameTiles[(xRef,y)][0])
                        del self.gameTiles[(xRef,y)]
                        self.setXYpot((xCheck,y),xRefPOT+1)
                        self.setXYpot((xRef,y),0)
                        maxX-=1
                        break
                    else:
                        maxX-=1
        return 1
    
    def moveUp(self):
        if not self.canMoveUp():
            return -1
        for x in range(4):
            minY = 0
            for yRef in range(1,4):
                yRefPOT = self.getXY((x,yRef))
                if yRefPOT == 0:
                    continue
                for yCheck in range(minY, yRef):
                    ti = self.getXY((x,yCheck))
                    if ti == 0:
                        self.gameTiles[(x,yRef)][0].changePos(convIndToPos((x,yCheck)))
                        self.gameTiles[(x,yCheck)]  = [self.gameTiles[(x,yRef)][0]]
                        del self.gameTiles[(x,yRef)]
                        self.setXYpot((x,yCheck),yRefPOT)
                        self.setXYpot((x,yRef),0)
                        break
                    elif ti == yRefPOT:
                        self.gameTiles[(x,yRef)][0].changePos(convIndToPos((x,yCheck)))
                        self.gameTiles[(x,yCheck)].append(self.gameTiles[(x,yRef)][0])
                        del self.gameTiles[(x,yRef)]
                        self.setXYpot((x,yCheck),yRefPOT+1)
                        self.setXYpot((x,yRef),0)
                        minY+=1
                        break
                    else:
                        minY+=1
        return 1
    
    def moveDown(self):
        if not self.canMoveDown():
            return -1
        for x in range(4):
            maxY = 3
            for yRef in range(2,-1,-1):
                yRefPOT = self.getXY((x,yRef))
                if yRefPOT == 0:
                    continue
                for yCheck in range(maxY, yRef,-1):
                    ti = self.getXY((x,yCheck))
                    if ti == 0:
                        self.gameTiles[(x,yRef)][0].changePos(convIndToPos((x,yCheck)))
                        self.gameTiles[(x,yCheck)]  = [self.gameTiles[(x,yRef)][0]]
                        del self.gameTiles[(x,yRef)]
                        self.setXYpot((x,yCheck),yRefPOT)
                        self.setXYpot((x,yRef),0)
                        break
                    elif ti == yRefPOT:
                        self.gameTiles[(x,yRef)][0].changePos(convIndToPos((x,yCheck)))
                        self.gameTiles[(x,yCheck)].append(self.gameTiles[(x,yRef)][0])
                        del self.gameTiles[(x,yRef)]
                        self.setXYpot((x,yCheck),yRefPOT+1)
                        self.setXYpot((x,yRef),0)
                        maxY-=1
                        break
                    else:
                        maxY-=1
        return 1

    def handleMove(self, move):
        movementResult = 0
        if move == 0:
            movementResult = self.moveLeft()
        elif move == 1:
            movementResult = self.moveRight()
        elif move == 2:
            movementResult = self.moveUp()
        elif move == 3:
            movementResult = self.moveDown()
        if movementResult ==-1:
            return
        self.addNum = True   


    def drawGrid(self, surf, pos):
        drawRoundRec(surf, pos, (GAME_SIZE,GAME_SIZE), GAME_CORNER_RADIUS, colGrid)
        for y in range(4):
            for x in range(4):
                self.gameStaticTiles[y][x].drawTile(surf)
                
        doneMoving = True

        doneAnimating = True
        for k, v in self.gameTiles.items():
            if len(v) > 1:
                doneAnimating = False
                break
            if v[0].pos != convIndToPos(k) or v[0].scaleInd !=9:
                doneAnimating=False
                break
        self.ready = doneAnimating
        
        for k, v in self.gameTiles.items():
            if len(v) == 1:
                v[0].drawTile(surf)
                if v[0].pos != convIndToPos(k):
                    doneMoving = False
            elif v[0].pos == v[1].pos:
                self.gameTiles[k] = [Tile(v[0].pot+1,convIndToPos(k),20)]
                if v[0].pot+1 > self.currentBestTile:
                    self.currentBestTile = v[0].pot+1
                self.currentScore += 2**(v[0].pot+1)
                
            else:
                v[0].drawTile(surf)
                v[1].drawTile(surf)
                doneMoving = False
        if doneMoving and self.addNum:
            self.newNumber()
            self.addNum = False

        if self.currentScore > self.bestScoreEver:
            self.bestScoreEver = self.currentScore
        if self.currentBestTile > self.bestTileEver:
            self.bestTileEver = self.currentBestTile


        labelCSL = fontText.render("Current Score", 1, col4)
        labelCSV = fontMedSmall.render(str(self.currentScore), 1, white)

        labelCTL = fontText.render("Current Best Tile", 1, col4)
        labelCTV = fontMedSmall.render(str(2**self.currentBestTile), 1, white)

        labelLSL = fontText.render("Last Game Score", 1, col4)
        labelLSV = fontMedSmall.render(str(self.lastBestScore), 1, white)

        labelLTL = fontText.render("Last Game Best Tile", 1, col4)
        labelLTV = fontMedSmall.render(str(2**self.lastBestTile), 1, white)

        labelBSL = fontText.render("Best Score Ever", 1, col4)
        labelBSV = fontMedSmall.render(str(self.bestScoreEver), 1, white)

        labelBTL = fontText.render("Best Tile Ever", 1, col4)
        labelBTV = fontMedSmall.render(str(2**self.bestTileEver), 1, white)

        
        labelSizeCSL = labelCSL.get_size()
        labelSizeCSV = labelCSV.get_size()

        labelSizeCTL = labelCTL.get_size()
        labelSizeCTV = labelCTV.get_size()

        labelSizeLSL = labelLSL.get_size()
        labelSizeLSV = labelLSV.get_size()

        labelSizeLTL = labelLTL.get_size()
        labelSizeLTV = labelLTV.get_size()

        labelSizeBSL = labelBSL.get_size()
        labelSizeBSV = labelBSV.get_size()

        labelSizeBTL = labelBTL.get_size()
        labelSizeBTV = labelBTV.get_size()

        posCSL =  (500+32 +((SCORE_WIDTH-labelSizeCSL[0])>>1), 50+20)
        posCSV =  (500+32 +((SCORE_WIDTH-labelSizeCSV[0])>>1), 150-labelSizeCSV[1])

        posCTL =  (500+2*32+202 +((SCORE_WIDTH-labelSizeCTL[0])>>1), 50+20)
        posCTV =  (500+2*32+202 +((SCORE_WIDTH-labelSizeCTV[0])>>1), 150-labelSizeCTV[1])

        posLSL =  (500+32 +((SCORE_WIDTH-labelSizeLSL[0])>>1), 2*50+100+20)
        posLSV =  (500+32 +((SCORE_WIDTH-labelSizeLSV[0])>>1), 2*50+2*100-labelSizeLSV[1])

        posLTL =  (500+2*32+202 +((SCORE_WIDTH-labelSizeLTL[0])>>1), 2*50+100+20)
        posLTV =  (500+2*32+202 +((SCORE_WIDTH-labelSizeLTV[0])>>1), 2*50+2*100-labelSizeLTV[1])

        posBSL =  (500+32 +((SCORE_WIDTH-labelSizeBSL[0])>>1), 3*50+2*100+20)
        posBSV =  (500+32 +((SCORE_WIDTH-labelSizeBSV[0])>>1), 3*50+3*100-labelSizeBSV[1])

        posBTL =  (500+2*32+202 +((SCORE_WIDTH-labelSizeBTL[0])>>1), 3*50+2*100+20)
        posBTV =  (500+2*32+202 +((SCORE_WIDTH-labelSizeBTV[0])>>1), 3*50+3*100-labelSizeBTV[1])


        recCS = (500+32,50)
        recCT = (500+2*32+202,50)
        recLS = (500+32,2*50+100)
        recLT = (500+2*32+202,2*50+100)
        recBS = (500+32,3*50+2*100)
        recBT = (500+2*32+202,3*50+2*100)

        
        drawRoundRec(surf,recCS,(SCORE_WIDTH,SCORE_HEIGHT),TILE_CORNER_RADIUS,colGrid)
        drawRoundRec(surf,recCT,(SCORE_WIDTH,SCORE_HEIGHT),TILE_CORNER_RADIUS,colGrid)
        drawRoundRec(surf,recLS,(SCORE_WIDTH,SCORE_HEIGHT),TILE_CORNER_RADIUS,colGrid)
        drawRoundRec(surf,recLT,(SCORE_WIDTH,SCORE_HEIGHT),TILE_CORNER_RADIUS,colGrid)
        drawRoundRec(surf,recBS,(SCORE_WIDTH,SCORE_HEIGHT),TILE_CORNER_RADIUS,colGrid)
        drawRoundRec(surf,recBT,(SCORE_WIDTH,SCORE_HEIGHT),TILE_CORNER_RADIUS,colGrid)

        surf.blit(labelCSL, posCSL)
        surf.blit(labelCSV, posCSV)

        surf.blit(labelCTL, posCTL)
        surf.blit(labelCTV, posCTV)

        surf.blit(labelLSL, posLSL)
        surf.blit(labelLSV, posLSV)

        surf.blit(labelLTL, posLTL)
        surf.blit(labelLTV, posLTV)

        surf.blit(labelBSL, posBSL)
        surf.blit(labelBSV, posBSV)

        surf.blit(labelBTL, posBTL)
        surf.blit(labelBTV, posBTV)
        
        
    def randomMove(self):
        moveName = ["Left", "Right", "Up", "Down"]
        possibleMoves = []
        if self.canMoveLeft():
            possibleMoves.append(0)
        if self.canMoveRight():
            possibleMoves.append(1)
        if self.canMoveUp():
            possibleMoves.append(2)
        if self.canMoveDown():
            possibleMoves.append(3)

        if len(possibleMoves) == 0:
            return
        
        move = random.choice(possibleMoves)
        self.handleMove(move)
        
        
                     
                                        
        
        

    
