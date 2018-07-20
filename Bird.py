from itertools import cycle
import random
import sys
import time
import numpy as np

import pygame
from pygame.locals import *
from multiprocessing import Process, Value
import NeuralNetwork as nn


class FlappyBird():

    def __init__(self, index, brain=nn.NeuralNetwork(4, 5, 2), FPS=30, SCREENWIDTH=288, SCREENHEIGHT=512, PIPEGAPSIZE=100):
        self.brain = brain
        self.FPS = FPS
        self.index = index
        self.fitness = 0
        self.finalGameOver = Value('d', 0)
        self.finalScore = Value("d", 0)
        self.nextPipeBottomY = Value('d', 0)
        self.nextPipeTopY = Value('d', 0)
        self.playerY = Value('d', 0)
        self.nextPipeDistance = Value('d', 0)
        self.SCREENWIDTH = SCREENWIDTH
        self.SCREENHEIGHT = SCREENHEIGHT
        # amount by which base can maximum shift to left
        self.PIPEGAPSIZE = PIPEGAPSIZE  # gap between upper and lower part of pipe
        self.BASEY = SCREENHEIGHT * 0.79
        # image, sound and hitmask  dicts
        self.IMAGES, self.SOUNDS, self.HITMASKS = {}, {}, {}
        # list of all possible players (tuple of 3 positions of flap)
        self.PLAYERS_LIST = (
            # red bird
            (
                'assets/sprites/redbird-upflap.png',
                'assets/sprites/redbird-midflap.png',
                'assets/sprites/redbird-downflap.png',
            ),
            # blue bird
            (
                # amount by which base can maximum shift to left
                'assets/sprites/bluebird-upflap.png',
                'assets/sprites/bluebird-midflap.png',
                'assets/sprites/bluebird-downflap.png',
            ),
            # yellow bird
            (
                'assets/sprites/yellowbird-upflap.png',
                'assets/sprites/yellowbird-midflap.png',
                'assets/sprites/yellowbird-downflap.png',
            ),
        )

        # list of backgrounds
        self.BACKGROUNDS_LIST = (
            'assets/sprites/background-day.png',
            'assets/sprites/background-night.png',
        )

        # list of pipes
        self.PIPES_LIST = (
            'assets/sprites/pipe-green.png',
            'assets/sprites/pipe-red.png',
        )

        try:
            xrange
        except NameError:
            self.xrange = range

    def init(self):
        self.process = Process(target=self.main, args=(self.finalGameOver, self.finalScore, self.nextPipeDistance, self.nextPipeTopY, self.nextPipeBottomY, self.playerY))
        self.process.start()

    def main(self, gameStatus, finalScore, nextPipeDistance, nextPipeTop, nextPipeBottom, playerY):
        global SCREEN, FPSCLOCK
        time.sleep(0.5)
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((self.SCREENWIDTH, self.SCREENHEIGHT))
        pygame.display.set_caption('Flappy Bird')

        # numbers sprites for score display
        self.IMAGES['numbers'] = (
            pygame.image.load('assets/sprites/0.png').convert_alpha(),
            pygame.image.load('assets/sprites/1.png').convert_alpha(),
            pygame.image.load('assets/sprites/2.png').convert_alpha(),
            pygame.image.load('assets/sprites/3.png').convert_alpha(),
            pygame.image.load('assets/sprites/4.png').convert_alpha(),
            pygame.image.load('assets/sprites/5.png').convert_alpha(),
            pygame.image.load('assets/sprites/6.png').convert_alpha(),
            pygame.image.load('assets/sprites/7.png').convert_alpha(),
            pygame.image.load('assets/sprites/8.png').convert_alpha(),
            pygame.image.load('assets/sprites/9.png').convert_alpha()
        )

        # game over sprite
        self.IMAGES['gameover'] = pygame.image.load(
            'assets/sprites/gameover.png').convert_alpha()
        # message sprite for welcome screen
        self.IMAGES['message'] = pygame.image.load(
            'assets/sprites/message.png').convert_alpha()
        # base (ground) sprite
        self.IMAGES['base'] = pygame.image.load(
            'assets/sprites/base.png').convert_alpha()
        # select random background sprites
        randBg = random.randint(0, len(self.BACKGROUNDS_LIST) - 1)
        self.IMAGES['background'] = pygame.image.load(
            self.BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(self.PLAYERS_LIST) - 1)
        self.IMAGES['player'] = (
            pygame.image.load(
                self.PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(
                self.PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(
                self.PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(self.PIPES_LIST) - 1)
        self.IMAGES['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        self.HITMASKS['pipe'] = (
            self.getHitmask(self.IMAGES['pipe'][0]),
            self.getHitmask(self.IMAGES['pipe'][1]),
        )

        # hitmask for player
        self.HITMASKS['player'] = (
            self.getHitmask(self.IMAGES['player'][0]),
            self.getHitmask(self.IMAGES['player'][1]),
            self.getHitmask(self.IMAGES['player'][2]),
        )
        self.playerIndex = 0
        self.playerIndexGen = cycle([0, 1, 2, 1])
        # iterator used to change playerIndex after every 5th iteration
        self.loopIter = 0

        self.playerx = int(self.SCREENWIDTH * 0.2)
        self.playery = int(
            (self.SCREENHEIGHT - self.IMAGES['player'][0].get_height()) / 2)

        self.messagex = int(
            (self.SCREENWIDTH - self.IMAGES['message'].get_width()) / 2)
        self.messagey = int(self.SCREENHEIGHT * 0.12)

        self.basex = 0
        # amount by which base can maximum shift to left
        self.baseShift = self.IMAGES['base'].get_width(
        ) - self.IMAGES['background'].get_width()

        # player shm for up-down motion on welcome screen
        self.playerShmVals = {'val': 0, 'dir': 1}
        movementInfo = {
            'playery': self.playery,
            'basex': self.basex,
            'playerIndexGen': self.playerIndexGen,
        }
        crashInfo = self.mainGame(movementInfo, nextPipeDistance, nextPipeTop, nextPipeBottom, playerY)
        finalScore.value = self.finalScore.value + crashInfo['score'] * 10
        gameStatus.value = 1.0
        # print(gameStatus.value)
        # FlappyBird.gameOver = True
        # FlappyBird.score = crashInfo['score']
        # self.showGameOverScreen(crashInfo)
    
    def showGameOverScreen(self, crashInfo):
        """crashes the player down ans shows gameover image"""
        self.score = crashInfo['score']
        self.gameOver = True
        playerx = self.SCREENWIDTH * 0.2
        playery = crashInfo['y']
        playerHeight = self.IMAGES['player'][0].get_height()
        playerVelY = crashInfo['playerVelY']
        playerAccY = 2
        playerRot = crashInfo['playerRot']
        playerVelRot = 7

        basex = crashInfo['basex']

        upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

        # play hit and die sounds
        # SOUNDS['hit'].play()
        # if not crashInfo['groundCrash']:
        # SOUNDS['die'].play()

        # while True:
        #     for event in pygame.event.get():
        #         if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
        #             pygame.quit()
        #             sys.exit()
        #         if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
        #             if playery + playerHeight >= self.BASEY - 1:
        #                 return

        #     # player y shift
        #     if playery + playerHeight < self.BASEY - 1:
        #         playery += min(playerVelY, self.BASEY - playery - playerHeight)

        #     # player velocity change
        #     if playerVelY < 15:
        #         playerVelY += playerAccY

        #     # rotate only when it's a pipe crash
        #     if not crashInfo['groundCrash']:
        #         if playerRot > -90:
        #             playerRot -= playerVelRot

        #     # draw sprites
        #     SCREEN.blit(self.IMAGES['background'], (0, 0))

        #     for uPipe, lPipe in zip(upperPipes, lowerPipes):
        #         SCREEN.blit(self.IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
        #         SCREEN.blit(self.IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        #     SCREEN.blit(self.IMAGES['base'], (basex, self.BASEY))
        #     self.showScore(self.score)

        #     playerSurface = pygame.transform.rotate(
        #         self.IMAGES['player'][1], playerRot)
        #     SCREEN.blit(playerSurface, (playerx, playery))

        #     FPSCLOCK.tick(self.FPS)
        #     pygame.display.update()

    def mutate(self, rate):
        self.brain.hiddenBias = self.normalRandom(self.brain.hiddenBias, rate)
        self.brain.inputHiddenWeights = self.normalRandom(self.brain.inputHiddenWeights, rate)
        self.brain.hiddenOutputWeights = self.normalRandom(self.brain.hiddenOutputWeights, rate)
        self.brain.outputBias = self.normalRandom(self.brain.outputBias, rate)
        print(self.brain.inputHiddenWeights)
        return self.brain
        
    def normalRandom(self, weights, rate):
        for i in range(len(weights)):
            if np.random.rand() < rate:
                print("prev", weights[i])
                weights[i] += np.random.normal(0, 0.1, 1)[0]
                print("new", weights[i])
                
        return weights

    def getGameState(self):
        return {'playerY': self.playerY.value,
                'nextPipeDistance': self.nextPipeDistance.value,
                'nextPipeTopY': self.nextPipeBottomY.value - self.PIPEGAPSIZE,
                'nextPipeBottomY': self.nextPipeBottomY.value}

    def getScore(self):
        return self.finalScore.value

    def mainGame(self, movementInfo, nextPipeDist, nextPipeTop, nextPipeBottom, playerY):
        self.score = playerIndex = loopIter = 0
        playerIndexGen = movementInfo['playerIndexGen']
        playerx, playery = int(self.SCREENWIDTH * 0.2), movementInfo['playery']

        basex = movementInfo['basex']
        baseShift = self.IMAGES['base'].get_width(
        ) - self.IMAGES['background'].get_width()

        # get 2 new pipes to add to upperPipes lowerPipes list
        newPipe1 = self.getRandomPipe()
        newPipe2 = self.getRandomPipe()

        # list of upper pipes
        upperPipes = [
            {'x': self.SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
            {'x': self.SCREENWIDTH + 200 +
                (self.SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
        ]

        # list of lowerpipe
        lowerPipes = [
            {'x': self.SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
            {'x': self.SCREENWIDTH + 200 +
                (self.SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
        ]

        pipeVelX = -4

        # player velocity, max velocity, downward accleration, accleration on flap
        playerVelY = -9   # player's velocity along Y, default same as playerFlapped
        playerMaxVelY = 10   # max vel along Y, max descend speed
        playerMinVelY = -8   # min vel along Y, max ascend speed
        playerAccY = 1   # players downward accleration
        playerRot = 45   # player's rotation
        playerVelRot = 3   # angular speed
        playerRotThr = 20   # rotation threshold
        playerFlapAcc = -9   # players speed on flapping
        playerFlapped = False  # True when player flaps
        
        while True:
            playerY.value = playery
            if upperPipes[0]['x'] - 88 < 0:
                nextPipeDist.value = upperPipes[1]['x'] - 88
                nextPipeTop.value = newPipe2[2]['gapY'] - self.PIPEGAPSIZE / 2
                nextPipeBottom.value = lowerPipes[1]['y']
                # print(upperPipes[1]['x'] - 88)
            else:
                nextPipeDist.value = upperPipes[0]['x'] - 88
                nextPipeTop.value = newPipe1[2]['gapY'] - self.PIPEGAPSIZE / 2
                nextPipeBottom.value = lowerPipes[0]['y']
            gameStatus = [playery, nextPipeDist.value, nextPipeTop.value, nextPipeBottom.value]
            
            prediction = self.brain.predict(gameStatus)
            if playery < 0:
                return {'score': 0}
            
            if prediction[0] > prediction[1]:
                if playery > -2 * self.IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
            self.finalScore.value += 1
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                # if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                #     if playery > -2 * self.IMAGES['player'][0].get_height():
                #         print("flapping")
                #         playerVelY = playerFlapAcc
                #         playerFlapped = True
                # if prediction[0] > prediction[1]:
                #     if playery > -2 * self.IMAGES['player'][0].get_height():
                #         print("flapping")
                #         playerVelY = playerFlapAcc
                #         playerFlapped = True

            # check for crash here            
            crashTest = self.checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                                        upperPipes, lowerPipes)
            if crashTest[0]:
                self.gameOver = True
                return {
                    'y': playery,
                    'groundCrash': crashTest[1],
                    'basex': basex,
                    'upperPipes': upperPipes,
                    'lowerPipes': lowerPipes,
                    'score': self.score,
                    'playerVelY': playerVelY,
                    'playerRot': playerRot
                }

            # check for score
            playerMidPos = playerx + self.IMAGES['player'][0].get_width() / 2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + self.IMAGES['pipe'][0].get_width() / 2
                if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                    self.score += 1
                    # SOUNDS['point'].play()

            # playerIndex basex change
            if (loopIter + 1) % 3 == 0:
                playerIndex = next(playerIndexGen)
            loopIter = (loopIter + 1) % 30
            basex = -((-basex + 100) % baseShift)

            # rotate the player
            if playerRot > -90:
                playerRot -= playerVelRot

            # player's movement
            if playerVelY < playerMaxVelY and not playerFlapped:
                playerVelY += playerAccY
            if playerFlapped:
                playerFlapped = False

                # more rotation to cover the threshold (calculated in visible rotation)
                playerRot = 45

            playerHeight = self.IMAGES['player'][playerIndex].get_height()
            playery += min(playerVelY, self.BASEY - playery - playerHeight)

            # move pipes to left
            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                uPipe['x'] += pipeVelX
                lPipe['x'] += pipeVelX

            # add new pipe when first pipe is about to touch left of screen
            if 0 < upperPipes[0]['x'] < 5:
                newPipe = self.getRandomPipe()
                upperPipes.append(newPipe[0])
                lowerPipes.append(newPipe[1])

            # remove first pipe if its out of the screen
            if upperPipes[0]['x'] < -self.IMAGES['pipe'][0].get_width():
                upperPipes.pop(0)
                lowerPipes.pop(0)

            # draw sprites
            SCREEN.blit(self.IMAGES['background'], (0, 0))

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(self.IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(self.IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

            SCREEN.blit(self.IMAGES['base'], (basex, self.BASEY))
            # print score so player overlaps the score
            self.showScore(self.score)

            # Player rotation has a threshold
            visibleRot = playerRotThr
            if playerRot <= playerRotThr:
                visibleRot = playerRot

            playerSurface = pygame.transform.rotate(
                self.IMAGES['player'][playerIndex], visibleRot)
            SCREEN.blit(playerSurface, (playerx, playery))

            pygame.display.update()
            FPSCLOCK.tick(self.FPS)

    

    def playerShm(self, playerShm):
        """oscillates the value of playerShm['val'] between 8 and -8"""
        if abs(playerShm['val']) == 8:
            playerShm['dir'] *= -1

        if playerShm['dir'] == 1:
            playerShm['val'] += 1
        else:
            playerShm['val'] -= 1

    def getRandomPipe(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gapY = random.randrange(0, int(self.BASEY * 0.6 - self.PIPEGAPSIZE))
        gapY += int(self.BASEY * 0.2)
        pipeHeight = self.IMAGES['pipe'][0].get_height()
        pipeX = self.SCREENWIDTH + 10

        return [
            {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
            {'x': pipeX, 'y': gapY + self.PIPEGAPSIZE},  # lower pipe
            {'gapY': gapY, "pipeHeight": pipeHeight},
        ]

    def showScore(self, score):
        """displays score in center of screen"""
        scoreDigits = [int(x) for x in list(str(self.score))]
        totalWidth = 0  # total width of all numbers to be printed

        for digit in scoreDigits:
            totalWidth += self.IMAGES['numbers'][digit].get_width()

        Xoffset = (self.SCREENWIDTH - totalWidth) / 2

        for digit in scoreDigits:
            SCREEN.blit(self.IMAGES['numbers'][digit],
                        (Xoffset, self.SCREENHEIGHT * 0.1))
            Xoffset += self.IMAGES['numbers'][digit].get_width()

    def checkCrash(self, player, upperPipes, lowerPipes):
        """returns True if player collders with base or pipes."""
        pi = player['index']
        player['w'] = self.IMAGES['player'][0].get_width()
        player['h'] = self.IMAGES['player'][0].get_height()

        # if player crashes into ground
        if player['y'] + player['h'] >= self.BASEY - 1:
            return [True, True]
        else:

            playerRect = pygame.Rect(player['x'], player['y'],
                                     player['w'], player['h'])
            pipeW = self.IMAGES['pipe'][0].get_width()
            pipeH = self.IMAGES['pipe'][0].get_height()

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                # upper and lower pipe rects
                uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
                lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

                # player and upper/lower pipe hitmasks
                pHitMask = self.HITMASKS['player'][pi]
                uHitmask = self.HITMASKS['pipe'][0]
                lHitmask = self.HITMASKS['pipe'][1]

                # if bird collided with upipe or lpipe
                uCollide = self.pixelCollision(
                    playerRect, uPipeRect, pHitMask, uHitmask)
                lCollide = self.pixelCollision(
                    playerRect, lPipeRect, pHitMask, lHitmask)

                if uCollide or lCollide:
                    return [True, False]

        return [False, False]

    def pixelCollision(self, rect1, rect2, hitmask1, hitmask2):
        """Checks if two objects collide and not just their rects"""
        rect = rect1.clip(rect2)

        if rect.width == 0 or rect.height == 0:
            return False

        x1, y1 = rect.x - rect1.x, rect.y - rect1.y
        x2, y2 = rect.x - rect2.x, rect.y - rect2.y

        for x in self.xrange(rect.width):
            for y in self.xrange(rect.height):
                if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                    return True
        return False

    def getHitmask(self, image):
        """returns a hitmask using an image's alpha."""
        mask = []
        for x in self.xrange(image.get_width()):
            mask.append([])
            for y in self.xrange(image.get_height()):
                mask[x].append(bool(image.get_at((x, y))[3]))
        return mask
