import module_manager
module_manager.review()
import pyaudio
import numpy
import pygame
import os
import aubio
import random
from collections import deque
import time
import math
import pygame.gfxdraw
import wave

import sys
from aubio import source, onset


#adapted from the aubio demo code
def getOnsets(filename):
    win_s = 1024*8 # fft size
    hop_s = win_s // 2           # hop size
    samplerate=0
    sys.argv.append(filename)
    sys.argv.append(samplerate)
    if len( sys.argv ) > 2: samplerate = int(sys.argv[2])
    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate
    o = onset("default", win_s, hop_s, samplerate)
    # list of onsets, in samples
    onsets = []
    # total number of frames read
    total_frames = 0
    while True:
        samples, read = s()
        if o(samples):
            onsets.append(o.get_last_s())
        total_frames += read
        if read < hop_s: break
    return onsets

class Button1(pygame.sprite.Sprite):
    def __init__(self, path, x, y, width, height):
    	super(Button1, self).__init__()
    	(self.x, self.y) = (x, y)
    	(self.width, self.height) = (width, height)
    	self.image = pygame.image.load(path)
    	self.image = self.image.convert_alpha()
    	self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

class BeatCircle(pygame.sprite.Sprite):
	white=(255, 255, 255)
	def __init__(self, x, y, color, number):
		super(BeatCircle, self).__init__()
		self.x=x
		self.y=y
		self.color=color
		self.number=number
		self.radius=50
		self.border=4
		self.clock=0.1
		self.outerRadius=self.radius*4
		self.ring=self.outerRadius
		self.outerWidth=3
		self.shrinkSize=(self.outerRadius//60)-(self.radius//60)
		self.rect=pygame.Rect(self.x - self.outerRadius, self.y - self.outerRadius,
                                2 * self.outerRadius, 2 * self.outerRadius)
		self.image=pygame.Surface((2 * self.outerRadius, 2 * self.outerRadius),
                                    pygame.SRCALPHA|pygame.HWSURFACE)
		self.outline=4
		self.fontSize=50
		self.missTime=0.2
		self.missClock=None
		self.draw()

	def shrinkRing(self, sec):
		self.clock+=sec
		if self.missClock!=None: #calculating 
			self.missClock-=sec #when ring should disappear
			if self.missClock<=0:
				self.kill()
		if self.ring>self.radius:
			self.ring-=self.shrinkSize
		self.draw()

	def draw(self): #draws the beats
		self.image.fill((255,255, 255,0))
		pygame.draw.circle(self.image, BeatCircle.white, (self.outerRadius, self.outerRadius), self.ring, self.outerWidth)
		radius=2*self.radius
		outline=2*self.outline
		newWindow=pygame.Surface((2*radius, 2*radius), pygame.SRCALPHA|pygame.HWSURFACE)
		pygame.draw.circle(newWindow, BeatCircle.white, (radius, radius), radius)
		pygame.draw.circle(newWindow, self.color, (radius, radius), radius-outline)
		width=radius
		height=radius
		newWindow=pygame.transform.smoothscale(newWindow, (width, height))
		start=self.outerRadius-self.radius
		self.image.blit(newWindow, (start, start))
		self.drawText() #draws the numbers
		if self.missClock!=None: #beats fade for smoother gameplay
			#pygame example https://stackoverflow.com/questions/15177568/pygame-surface-fade-in-out
			a=max(int((self.missClock/self.missTime)*255), 0)
			a=max(a, 0)
			fillSpace=(start, start, width, height)
			self.image.fill((255,255,255, a), fillSpace, pygame.BLEND_RGBA_MIN)

	def drawText(self): #draws number on beats
		font=pygame.font.SysFont("Arial", self.fontSize)
		text=font.render(str(self.number), 1, BeatCircle.white)
		position=text.get_rect()
		position.centerx=self.image.get_rect().centerx
		position.centery=self.image.get_rect().centery
		self.image.blit(text, position)

	def getPosition(self):
		return self.x, self.y

	def draining(self): #calculates when beats should disappear
		self.missClock=self.missTime


class MouseLocation(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(MouseLocation, self).__init__()
		self.radius=1
		self.x=x
		self.y=y
		self.rect=pygame.Rect(self.x-self.radius, self.y-self.radius, 2*self.radius, 2*self.radius)

class FadingText(pygame.sprite.Sprite):
	white=(255, 255, 255)
	font="Tahoma"
	def __init__(self, window, text, size, x, y, anchor="nw", color=white, font=font):
		super(FadingText, self).__init__()
		self.x=x
		self.y=y
		self.text=text
		self.anchor=anchor
		self.color=color
		self.window=window
		self.time=0
		self.font=pygame.font.SysFont(font, size)
		self.width, self.height=self.font.size(self.text)
		self.initPosition()
		self.rect=pygame.Rect(self.areaX, self.areaY, self.width, self.height)
		self.image=pygame.Surface((self.width, self.height), pygame.HWSURFACE)
		self.missTime=0.2
		self.missClock=None
		self.draw()
		self.window.blit(self.image, (self.areaX, self.areaY))

	def initPosition(self):
		if self.anchor=="nw":
			self.areaX=self.x
			self.areaY=self.y
		if self.anchor=="ne":
			self.areaX=self.x-self.width
			self.areaY=self.y
		if self.anchor=="sw":
			self.areaX=self.x
			self.areaY=self.y-self.height
		if self.anchor=="se":
			self.areaX=self.x-self.width
			self.areaY=self.y-self.height
		if self.anchor=="center":
			self.areaX=self.x-self.width//2
			self.areaY=self.y-self.height//2

	def draw(self):
		text=self.font.render(self.text, 1, self.color)
		self.image.blit(text, (0,0))
		if self.missClock!=None: #text fades out smoother
			a=int((self.missClock/self.missTime)*255)
			a=max(a, 0)
			self.image.set_alpha(a)

	def update(self, sec=0):
		self.time+=sec
		if self.missClock!=None:
			self.missClock-=sec
			if self.missClock<=0:
				self.kill() #calculates when to kill text
		self.draw()
		self.window.blit(self.image, (self.areaX, self.areaY))

	def draining(self):
		self.missClock=self.missTime

class PermText(FadingText):
	white=(255,255,255,0)
	bg=(255,182,193)
	font="Tahoma"
	def __init__(self, window, text, size, x, y, anchor="nw"):
		super().__init__(window, text, size, x, y, anchor)

	def draw(self):
		super().draw()
		text=self.font.render(self.text, 1, PermText.white, PermText.bg)
		self.image.blit(text, (0,0))



class BlitzBeatGame(object):
	def __init__(self, width=1400, height=900, fps=60, title="Blitz Beat"):
		self.width=width
		self.height=height
		self.fps=fps
		self.title=title
		self.modes()
		self.makeBeats()
		self.tracking()
		self.PLAYBACK_END=pygame.USEREVENT+1
		self.startDelay=-1.45
		self.timePassed=self.startDelay
		self.endDelay=2.0
		self.countdown=None
		pygame.mixer.pre_init(48000,-16,1, 1024)
		pygame.mixer.init()
		pygame.init()
		pygame.font.init()


	def tracking(self):
		self.combostreak=0
		self.maxComboStreak=0
		self.score=0
		self.prevAdd=0
		self.hits=pygame.sprite.Group()
		self.hitKill=0.5 #when to make the hit marks disappear

	def modes(self):
		self.inGame=True
		self.splashScreen=True
		self.songSelect=False
		self.helpScreen=False
		self.playGame=False
		self.scoreBoard=False
		self.isPaused=False

	def makeSplashScreen(self):
		backgroundPicture="triangles-download (3).png"
		self.backgroundPicture=pygame.image.load(backgroundPicture)
		self.backgroundPicture=pygame.transform.scale(self.backgroundPicture,(1600,900))
		self.backgroundPicture.convert()
		self.splashScreenButtons=pygame.sprite.Group()
		self.makeSplashScreenButtons()

	def makePauseScreen(self):
		self.pauseScreenButtons=pygame.sprite.Group()
		continueX, continueY=(self.width/2-175, 300)
		continueWidth, continueHeight=(901, 122)
		continueFile="ContinueButton.png"
		self.continueButton=Button1(continueFile, continueX, continueY, continueWidth, continueHeight)
		retryX, retryY=(self.width/2-175, 500)
		retryWidth, retryHeight = 901, 120
		retryFile="RetryButton.png"
		self.retryButton=Button1(retryFile, retryX, retryY, retryWidth, retryHeight)
		backX, backY=self.width/2-175, 700
		backWidth, backHeight=901, 123
		backFile="LongBackButton.png"
		self.longBackButton=Button1(backFile, backX, backY, backWidth, backHeight)
		self.continueButton.add(self.pauseScreenButtons)
		self.retryButton.add(self.pauseScreenButtons)
		self.longBackButton.add(self.pauseScreenButtons)



	def makeSplashScreenButtons(self):
		(titleX, titleY)=(510, 200)
		(titleWidth, titleHeight)=(0, 0)
		titleFile="Title Name.png"
		title=Button1(titleFile, titleX, titleY, titleWidth, titleHeight)
		playButtonX, playButtonY=self.width/2-60, self.height/2-10
		playWidth, playHeight=675, 91 
		playFile="PlayButton.png"
		self.playButton=Button1(playFile, playButtonX, playButtonY, playWidth, playHeight)
		helpX, helpY=self.width/2-60, self.height/2+100
		helpWidth, helpHeight=675, 91
		helpFile="HelpButton.png"
		self.helpButton=Button1(helpFile, helpX, helpY, helpWidth, helpHeight)
		settingsX, settingsY=self.width/2-60, self.height/2+210
		settingsWidth, settingsHeight=677, 92
		settingsFile="SettingsButton.png"
		self.settings=Button1(settingsFile, settingsX, settingsY, settingsWidth, settingsHeight)
		exitX, exitY=self.width/2-60, self.height/2+320
		exitWidth, exitHeight=677, 92
		exitFile="ExitButton.png"
		self.exitButton=Button1(exitFile, exitX, exitY, exitWidth, exitHeight)
		title.add(self.splashScreenButtons)
		self.playButton.add(self.splashScreenButtons)
		self.helpButton.add(self.splashScreenButtons)
		self.settings.add(self.splashScreenButtons)
		self.exitButton.add(self.splashScreenButtons) 

	def backgroundMusic(self):
		backgroundMusicPath="WHITE-ALBUM-off-Vocals.wav"
		pygame.mixer.music.load(backgroundMusicPath)
		pygame.mixer.music.play(loops=-1)

	def makeBeats(self):
		self.radius=50
		self.beats=pygame.sprite.Group()
		self.beatQueue=deque()
		self.colors=[(126, 178, 245), (255, 192, 203), (220, 162, 249), (114, 230, 199)]
		self.beatColor=(0, 0, 0)
		self.chooseColor()
		self.oldX=None
		self.oldY=None
		self.maxDistance=200
		self.minDistance=100
		self.startingNum=1
		self.endingNum=4
		self.beatScoring()
		self.startingScore()

	def chooseColor(self):
		newColor=random.choice(self.colors)
		while newColor==self.beatColor:
			newColor=random.choice(self.colors)
		self.beatColor=newColor

	#how osu scores 
	def startingScore(self):
		self.scoreOK=50
		self.scoreGood=100
		self.scorePerfect=300
		self.miss=0
		self.missCount=0
		self.OKCount=0
		self.goodCount=0
		self.perfectCount=0

	#based on how osu calculates timing from osu.ppy
	#https://osu.ppy.sh/help/wiki/Guides/How_to_Time_Songs
	def beatScoring(self): #calculating hit scores
		self.comingUp=1.0
		self.winWidth=0.06
		self.perfect=self.comingUp-self.winWidth
		self.goodLate=self.comingUp+self.winWidth
		self.OKLate=self.goodLate+self.winWidth
		self.missLate=self.OKLate+self.winWidth
		self.beatKill=self.missLate
		self.goodEarly=self.perfect-self.winWidth
		self.OKEarly=self.goodEarly-self.winWidth
		self.missEarly=self.OKEarly-self.winWidth

	#creates combo and score on playGame mode
	def createComboScore(self):
		score=str(self.score)
		scoreX, scoreY=350, 200
		scoreSize=50
		printScoreText=FadingText(self.screen, score, scoreSize, scoreX, scoreY, "nw")
		combo=str(self.combostreak)+"x"
		comboX, comboY=350, 900
		comboSize=80
		printComboText=FadingText(self.screen, combo, comboSize, comboX, comboY, "sw")	

	def startSong(self, path):
		self.path=path
		start=time.time()
		self.onsets=getOnsets(self.path)
		self.nextBeat=self.onsets.pop(0)
		pygame.mixer.music.load(self.path)
		end=time.time()
		offsetTime=abs(end-start)
		self.timePassed-=offsetTime

	def makeHelpScreen(self):
		self.helpButtons=pygame.sprite.Group()
		helpX=550
		helpY=200
		helpWidth=904
		helpHeight=673
		helpFile="Instructions.png"
		helpScreen=Button1(helpFile, helpX, helpY, helpWidth, helpHeight)
		backX=350
		backY=200
		backWidth=182
		backHeight=102
		backFile="BackButton.png"
		self.backButton=Button1(backFile, backX, backY, backWidth, backHeight)
		helpScreen.add(self.helpButtons)
		self.backButton.add(self.helpButtons)

	#makes the scoreBoard screen
	def makeScoreBoard(self):
		self.scoreButtons=pygame.sprite.Group()
		backX, backY=350, 750
		backWidth, backHeight= 182, 102
		backFile="BackButton.png"
		self.backInScore=Button1(backFile, backX, backY, backWidth, backHeight)
		self.backInScore.add(self.scoreButtons)

	#creates score and combo on scoreboard
	def createScoreText(self):
		width, height=self.screen.get_size()
		score="Score: "+str(self.score)
		scoreX, scoreY=400, 290
		scoreSize=70
		finalScoreText=PermText(self.screen, score, scoreSize, scoreX, scoreY)
		combo="Combo: "+str(self.maxComboStreak)+"x"
		comboX, comboY=400, 200
		comboSize=70
		comboText=PermText(self.screen, combo, comboSize, comboX, comboY)
		self.createTimedScore()

	
	#creates number of perfects, goods, oks, and misses on scoreboard
	def createTimedScore(self):
		numPerfects="Perfect: "+str(self.perfectCount)
		numPerfX, numPerfY=620, 445
		textSize=50
		numPerfText=PermText(self.screen, numPerfects, textSize, numPerfX, numPerfY)
		numGoods="Good: "+str(self.goodCount)
		numGoodX, numGoodY=1190, 445
		numGoodText=PermText(self.screen, numGoods, textSize, numGoodX, numGoodY)
		numOKs="OK: "+str(self.OKCount)
		numOKX, numOKY=620, 540
		numOKText=PermText(self.screen, numOKs, textSize, numOKX, numOKY)
		numMisses="Miss: "+str(self.missCount)
		numMissX, numMissY=1190, 540
		numMissText=PermText(self.screen, numMisses, textSize, numMissX, numMissY)


	def runGame(self):
		gameClock=pygame.time.Clock()
		self.screen=pygame.display.set_mode((0,0), pygame.FULLSCREEN)
		pygame.display.set_caption(self.title)
		self.makeSplashScreen()
		self.makeHelpScreen()
		self.makePauseScreen()
		while self.inGame:
			self.gameLoop(gameClock)
		pygame.font.quit()
		pygame.mixer.quit()
		pygame.quit()

	def gameLoop(self, clock):
		if not pygame.mixer.music.get_busy():
			self.backgroundMusic()
		while self.splashScreen:
			self.splashScreenLoop(clock)
		while self.helpScreen:
			self.helpScreenLoop(clock)
		if self.playGame:
			pygame.mixer.music.play()
			pygame.mixer.music.set_endevent(self.PLAYBACK_END)
		while self.playGame:
			self.playGameLoop(clock)
		while self.scoreBoard:
			self.scoreBoardLoop(clock)
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				self.inGame=False
		self.gameLoopUpdate()

	def splashScreenLoop(self, clock):
		clock.tick(self.fps)
		self.screen.blit(self.backgroundPicture, (0,0))
		self.splashScreenButtons.draw(self.screen)
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				self.inGame=False
				self.splashScreen=False
			if event.type == pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					pygame.quit()
			if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
				self.mousePressed()

	def helpScreenLoop(self, clock):
		clock.tick(self.fps)
		self.screen.blit(self.backgroundPicture, (0,0))
		self.helpButtons.draw(self.screen)
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				self.inGame=False
				self.helpScreen=False
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.helpScreen=False
					self.splashScreen=True
			if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
				self.mousePressed()

	def pauseScreenLoop(self, clock):
		clock.tick(self.fps)
		self.screen.blit(self.backgroundPicture, (0, 0))
		self.pauseScreenButtons.draw(self.screen)
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				self.inGame=False
				self.isPaused=False
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.splashScreen=True
			if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
				self.mousePressed()

	def scoreBoardLoop(self, clock):
		clock.tick(self.fps)
		if not pygame.mixer.music.get_busy():
			self.backgroundMusic()
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				self.inGame=False
				self.scoreBoard=False
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					self.scoreBoard=False
					self.splashScreen=True
					self.resetGame()
			if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
				self.mousePressed()
		self.screen.fill((255,182,193))
		self.scoreButtons.draw(self.screen)
		self.createScoreText()
		pygame.display.flip()



	def updateNumber(self):
		self.startingNum+=1
		if self.startingNum>self.endingNum:
			self.startingNum=1
			self.chooseColor()


	def addBeat(self): #keeps beat on screen and have some pattern
		if self.oldX==None and self.oldY==None:
			self.oldX=random.randint(350, 1200)
			self.oldY=random.randint(400, 600)
		if self.oldX<800:
			xDirection=1
		elif self.oldX>1200:
			xDirection=-1
		else:
			xDirection=random.choice([-1,1])
		if self.oldY<400:
			yDirection=1
		elif self.oldY>600:
			yDirection=-1
		else:
			yDirection=random.choice([-1,1])
		dx=random.randint(self.minDistance, self.maxDistance)*xDirection
		dy=random.randint(self.minDistance, self.maxDistance)*yDirection
		x, y =self.oldX+dx, self.oldY+dy
		self.oldX, self.oldY= x, y
		beat=BeatCircle(x, y,self.beatColor, self.startingNum)
		beat.add(self.beats)
		self.beatQueue.append(beat)
		self.updateNumber()

	def mistake(self, beat):
		missColor=(255, 0, 0)
		text="x"
		size=70
		x,y=beat.getPosition()
		if self.combostreak>self.maxComboStreak:
			self.maxComboStreak=self.combostreak
		self.combostreak=0
		missText=FadingText(self.screen, text, size, x, y, "center", missColor)
		missText.add(self.hits)
		self.missCount+=1


	def gameTimerFired(self, time, sec):
		if time+self.comingUp>=self.nextBeat:
			if len(self.onsets)>0:
				self.addBeat()
				self.nextBeat=self.onsets.pop(0)
		for beat in self.beats:
			beat.shrinkRing(sec)
			if beat.missClock==None and beat.clock>=self.beatKill:
				beat.draining()
				self.beatQueue.remove(beat)
				self.mistake(beat)
		for hit in self.hits:
			hit.update(sec)
			if hit.missClock==None and hit.time>=self.hitKill:
				hit.draining()

	def playGameLoop(self, clock):
		sec=clock.tick_busy_loop(self.fps)/1000
		if not self.isPaused:
			pygame.mixer.music.unpause()
			self.timePassed+=sec
			self.gameTimerFired(self.timePassed, sec)
		for event in pygame.event.get():
			self.doAction(event)
		if self.isPaused:
			pygame.mixer.music.pause()
		while self.isPaused:
			self.pauseScreenLoop(clock)
		if self.countdown!=None:
			self.countdown-=sec
			if self.countdown<=0:
				self.playGame=False
				self.scoreBoard=True

		self.playGameLoopUpdate()

	def gameLoopUpdate(self):
		self.screen.fill((0,0,0))
		pygame.display.flip()

	def addScore(self, time, beat):
		self.add=0
		if time>=self.missLate:
			return True
		elif time>=self.OKLate:
			self.add=self.scoreOK
		elif time>=self.goodLate:
			self.add=self.scoreGood
		elif time>=self.perfect:
			self.add=self.scorePerfect
		elif time>=self.goodEarly:
			self.add=self.scoreGood
		elif time>=self.OKEarly:
			self.add=self.scoreOK
		elif time>=self.missEarly:
			return True
		else:
			return None
		
		self.keepScore()
		
		return False


	def keepScore(self):
		multiplier=1+self.combostreak/25
		self.score=int(self.score+(self.add*multiplier))
		self.prevAdd=self.add
		if self.add==self.scoreOK:
			self.OKCount+=1
		if self.add==self.scoreGood:
			self.goodCount+=1
		if self.add==self.scorePerfect:
			self.perfectCount+=1

	
	def addHit(self, beat):
		colorPerfect=(125, 200, 255)
		colorGood=(88, 255, 88)
		colorOK=(255, 226, 125)
		x, y = beat.getPosition()
		text=str(self.prevAdd)
		if self.prevAdd==self.scorePerfect:
			color=colorPerfect
		elif self.prevAdd==self.scoreGood:
			color=colorGood
		elif self.prevAdd==self.scoreOK:
			color=colorOK
		else: return
		size=50
		hitText=FadingText(self.screen, text, size, x, y, "center", color)
		hitText.add(self.hits)



	def playGameLoopUpdate(self):
		if not self.isPaused:
			black=(0, 0, 0)
			self.screen.fill(black)
			self.createComboScore()
			self.hits.draw(self.screen) 
			self.beats.draw(self.screen) 
			if self.countdown!=None: #makes the game fade out
				displayFade=pygame.Surface((self.width, self.height)) #?
				displayFade.fill((0,0,0))
				a=int((1-self.countdown/self.endDelay)*255)
				a=max(a,0)
				displayFade.set_alpha(a)
				self.screen.blit(displayFade, (0,0))
		if self.isPaused:
			self.screen.blit(self.backgroundPicture, (0,0))

		pygame.display.flip()

	def beatHit(self):
		if len(self.beatQueue)==0:
			return
		x,y=pygame.mouse.get_pos()
		click=MouseLocation(x,y)
		beat=self.beatQueue[0] #only hit the oldest beat
		if pygame.sprite.collide_circle(beat,click):
			miss=self.addScore(beat.clock, beat)
			if miss==None:
				return
			elif miss:
				self.mistake(beat)
			else:
				self.combostreak+=1
			beat.draining()
			self.beatQueue.popleft()
			self.addHit(beat)

	def doAction(self, event):
		if event.type==pygame.QUIT:
			self.inGame=False
			self.playGame=False
		elif event.type==pygame.KEYDOWN:
			if event.key==pygame.K_ESCAPE:
				self.isPaused=not self.isPaused
			if self.isPaused:
				if event.key==pygame.K_r:
					self.resetGame()
					self.splashScreen=True
					return
		if not self.isPaused:
			if event.type==pygame.MOUSEBUTTONDOWN:
				self.beatHit()
			if event.type==self.PLAYBACK_END:
				if self.combostreak>self.maxComboStreak:
					self.maxComboStreak=self.combostreak
				self.makeScoreBoard()
				self.countdown=self.endDelay

	def mousePressed(self):
		x, y=pygame.mouse.get_pos()
		click=MouseLocation(x,y)
		if self.splashScreen:
			self.checkSplashScreenCollision(click)
		if self.helpScreen:
			self.checkHelpScreenCollision(click)
		if self.scoreBoard:
			self.checkScoreBoardCollision(click)
		if self.isPaused:
			self.checkPauseScreenCollision(click)

	def checkSplashScreenCollision(self, click):
		if pygame.sprite.collide_rect(self.playButton, click):
			self.startGame()
			self.splashScreen=False
			self.playGame=True
		if pygame.sprite.collide_rect(self.helpButton, click):
			self.helpScreen=True
			self.splashScreen=False
		if pygame.sprite.collide_rect(self.settings, click):
			pass
		if pygame.sprite.collide_rect(self.exitButton, click):
			pygame.quit()

	def checkHelpScreenCollision(self, click):
		if pygame.sprite.collide_rect(self.backButton, click):
			self.helpScreen=False
			self.splashScreen=True

	def checkScoreBoardCollision(self, click):
		if pygame.sprite.collide_rect(self.backInScore, click):
			self.scoreBoard=False
			self.playGame=False
			self.resetGame()
			self.splashScreen=True

	def checkPauseScreenCollision(self, click):
		if pygame.sprite.collide_rect(self.continueButton, click):
			self.isPaused=not self.isPaused
		if pygame.sprite.collide_rect(self.retryButton, click):
			pass
		if pygame.sprite.collide_rect(self.longBackButton, click):
			self.isPaused=False
			self.playGame=False
			self.splashScreen=True
			self.resetGame()

	def startGame(self):
		self.screen.blit(self.backgroundPicture, (1280, 1024))
		pygame.display.flip()
		try:
			self.startSong("060o0-fqkan.wav")
		except:
			self.error=True
			return
		pygame.mixer.music.stop()
		self.splashScreen=False
		self.playGame=True

	def resetGame(self):
		pygame.mixer.music.stop()
		self.error=False
		self.countdown=None
		self.playGame=False
		self.isPaused=False
		self.combostreak=0
		self.maxComboStreak=0
		self.score=0
		self.prevAdd=0
		self.hits=pygame.sprite.Group()
		self.timePassed=self.startDelay
		self.beats=pygame.sprite.Group()
		self.beatQueue=deque()
		self.startingNum=1
		self.startingScore()
		pygame.mixer.music.set_endevent()	

game=BlitzBeatGame()
game.runGame()