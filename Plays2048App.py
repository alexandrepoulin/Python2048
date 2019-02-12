import pygame
import gameModel
import time

KEYVALUES = {276:0, 275:1, 274:3, 273:2} ## left, right, down, up

class Play2048:

    def __init__(self):
        x = pygame.init()
        if x!=(6,0):
            print("Error initializing pygame")
            pygame.quit()
            quit()

        self.colBack = (250,248,239)
        
        self.gameDisplay = pygame.display.set_mode((1000,500))
        pygame.display.set_caption("Chat Plays 2048")
        
        self.game = gameModel.Grid()
        self.game.newGame()
 
        self.value = -1
        self.lastMoveTime = 0
        self.gameExit = False

    def mainLoop(self):
        while not self.gameExit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameExit = True
                elif event.type == pygame.KEYDOWN and self.game.isReady() and event.key in [276, 275, 274, 273]:
                    self.value = KEYVALUES[event.key]

            self.gameDisplay.fill(self.colBack)
            currentTime = time.time()
            if currentTime - self.lastMoveTime > 0.1 and self.value >= 0 and self.game.isReady():
                self.lastMoveTime=currentTime
                self.game.handleMove(self.value)
                self.value=-1
            if self.game.isGameOver():
                self.game.newGame()

            self.game.drawGrid(self.gameDisplay,(0,0))
            pygame.display.update()
        pygame.quit()


if __name__== "__main__":  
    app = Play2048()
    app.mainLoop()
    quit()
    

