import module_manager
module_manager.review()
import pyaudio
from tkinter import *
import numpy
import pygame
import os
import wave
import aubio
import random
import librosa

import sys
from aubio import source, onset

def getOnsets(filename):
    win_s = 1024               # fft size
    hop_s = win_s // 2          # hop size

    filename=filename
    samplerate=0

    if len(sys.argv) < 2:
        print("Usage: %s <'Mike-Perry-The-Ocean-ft-Shy-Martin.wav'> [0]" % sys.argv[0])
        #sys.exit(1)
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
            #print("%f" % o.get_last_s())
            onsets.append(o.get_last())
        total_frames += read
        if read < hop_s: break
    return onsets


def init(data):
    data.mode="splashScreen"
    data.file="triangles-download (3).png"
    data.background=PhotoImage(file=data.file)
    data.songName="Mike-Perry-The-Ocean-ft-Shy-Martin.wav"
    data.onsets=getOnsets(data.songName)
    data.beatCircles=BeatCircles(data)
    data.timerCalls=0
    data.backgroundSong="WHITE-ALBUM-off-Vocals.wav"
    playSong(data.backgroundSong)

def mousePressed(event, data):
    if (data.mode == "splashScreen"): splashScreenMousePressed(event, data)
    elif (data.mode=="songSelection"): songSelectionMousePressed(event, data)
    elif (data.mode=="help"): helpMousePressed(event, data)
    elif (data.mode=="settings"): settingsMousePressed(event, data)
    elif (data.mode == "playGame"):   playGameMousePressed(event, data)
    elif (data.mode=="gameOver"):   gameOverMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "splashScreen"): splashScreenKeyPressed(event, data)
    elif (data.mode=="songSelection"): songSelectionKeyPressed(event, data)
    elif (data.mode=="help"): helpKeyPressed(event, data)
    elif (data.mode=="settings"): settingsKeyPressed(event, data)
    elif (data.mode == "playGame"):   playGameKeyPressed(event, data)
    elif (data.mode=="gameOver"):   gameOverKeyPressed(event, data) 

def timerFired(data):
    if (data.mode == "splashScreen"): splashScreenTimerFired(data)
    elif (data.mode=="songSelection"): songSelectionTimerFired(data)
    elif (data.mode=="help"): helpTimerFired(data)
    elif (data.mode=="settings"): settingsTimerFired(data)
    elif (data.mode == "playGame"):   playGameTimerFired(data)
    elif (data.mode=="gameOver"):   gameOverTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "splashScreen"): splashScreenRedrawAll(canvas, data)
    elif (data.mode=="songSelection"): songSelectionRedrawAll(canvas, data)
    elif (data.mode=="help"): helpRedrawAll(canvas, data)
    elif(data.mode=="settings"): settingsRedrawAll(canvas, data)
    elif (data.mode == "playGame"):   playGameRedrawAll(canvas, data)
    elif (data.mode=="gameOver"):   gameOverRedrawAll(canvas, data)

def splashScreenMousePressed(event, data):
    if data.width/2-300<=event.x<=data.width/2+300 and \
    data.height/2-60<=event.y<=data.height/2+20:
        data.mode="songSelection"
    if data.width/2-300<=event.x<=data.width/2+300 and \
    data.height/2+40<=event.y<=data.height/2+120:
        data.mode="help"
    if data.width/2-300<=event.x<=data.width/2+300 and \
    data.height/2+140<=event.y<=data.height/2+220:
        data.mode="settings"
    if data.width/2-300<=event.x<=data.width/2+300 and \
    data.height/2+240<=event.y<=data.height/2+320:
        pygame.quit()
        sys.exit()


def splashScreenKeyPressed(event, data): pass

def splashScreenRedrawAll(canvas, data):
    canvas.create_image(data.width/2, data.height/2, \
        anchor="center", image=data.background)
    canvas.create_rectangle(data.width/2-400, data.height/2-300, \
        data.width/2+400, data.height/2-100, fill="white", \
        stipple='gray50', outline='')
    canvas.create_text(data.width/2, data.height/2-200, \
        text="Osu!", font=("Century Gothic", int(100)), fill="gray40")
    canvas.create_rectangle(data.width/2-300, data.height/2-60, \
    data.width/2+300, data.height/2+20, fill="white", \
    stipple='gray50', outline='')
    canvas.create_text(data.width/2, data.height/2-20, \
    text="Play", font=("Century Gothic", int(30)), fill="gray40")
    canvas.create_rectangle(data.width/2-300, data.height/2+40, \
    data.width/2+300, data.height/2+120, fill="white", \
    stipple='gray50', outline='')
    canvas.create_text(data.width/2, data.height/2+80, text="Help"\
    , font=("Century Gothic", int(30)), fill="gray40")
    canvas.create_rectangle(data.width/2-300, data.height/2+140, \
    data.width/2+300, data.height/2+220, fill="white", \
    stipple='gray50', outline='')
    canvas.create_text(data.width/2, data.height/2+180, text="Settings",\
     font=("Century Gothic", int(30)), fill="gray40")
    canvas.create_rectangle(data.width/2-300, data.height/2+240, data.width/2+300,\
    data.height/2+320, fill="white", outline='', stipple="gray50")
    canvas.create_text(data.width/2, data.height/2+280, text="Exit",\
     font=("Century Gothic", int(30)), fill="gray40")

def splashScreenTimerFired(data): pass

def helpKeyPressed(event, data): pass

def helpMousePressed(event, data):
    if data.width/2-600<=event.x<=200 and data.height/2-300<=event.y<=150:
        data.mode="splashScreen"

def helpRedrawAll(canvas, data):
    canvas.create_image(data.width/2, data.height/2, \
    anchor="center", image=data.background)
    canvas.create_rectangle(data.width/2-400, data.height/2-300, \
    data.width/2+400, data.height/2+300, fill="white", stipple="gray50", \
    outline='')
    canvas.create_text(data.width/2, data.height/2-200, \
        text="Choose a song and level from the menu.", fill="gray40",\
        font=("Century Gothic", int(29)))
    canvas.create_text(data.width/2-10, data.height/2-100, \
    text=" Click the beats in time with the music to", fill="gray40",\
    font=("Century Gothic", int(29)))
    canvas.create_text(data.width/2-30, data.height/2, \
    text="keep a combo streak. If you miss too", fill="gray40",\
    font=("Century Gothic", int(29)))
    canvas.create_text(data.width/2-10, data.height/2+100, \
    text="many, the health bar will drain and the", fill="gray40",\
    font=("Century Gothic", int(29)))
    canvas.create_text(data.width/2, data.height/2+200, \
    text="game will be over. Good luck, have fun!", fill="gray40",\
    font=("Century Gothic", int(29)))
    canvas.create_rectangle(data.width/2-600, data.height/2-300, \
    200, 150, fill="white", stipple="gray50", outline='')
    canvas.create_text(((data.width/2-600)+200)/2, \
    ((data.height/2-300)+150)/2, text="Back", \
    font=("Century Gothic", int(30)), fill="gray40") 

def helpTimerFired(data): pass

def songSelectionRedrawAll(canvas, data): pass

def songSelectionKeyPressed(event, data): pass

def songSelectionMousePressed(event, data): pass

def songSelectionTimerFired(data): pass

def playGameRedrawAll(canvas, data):
    data.beatCircles.draw(canvas)

def playGameTimerFired(data): pass
    #pass
    #playSong()
    #data.timerCalls+=1
    #print(data.timerCalls)
    #print(timeit.timeit())





class BeatCircles(object):
    def __init__(self, data):
        #self.width=data.width
        #self.height=data.height
        #self.x=random.randint(0, self.width)
        #self.y=random.randint(0, self.height)
        self.x=100
        self.y=100
        self.radius=100
        self.onsets=data.onsets

    def draw(self, canvas):
        #print(pygame.mixer.music.get_pos()/1000)
        #for i in range(len(self.onsets)):
        if pygame.mixer.music.get_pos()/1000 in self.onsets:
             #print("entered")
             c.create_oval(self.x-self.radius, self.y-self.radius, \
             self.x+self.radius, self.y+self.radius, fill="blue")


def playSong(filename):
    pygame.mixer.pre_init(48000,-16,1, 1024)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(loops=0, start=0)

def exitGame(root):
    pygame.quit()
    root.destroy()

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.timerDelay = 100 # milliseconds
    root = Tk()
    init(data)
    data.width = root.winfo_screenwidth()
    data.height = root.winfo_screenheight()
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    # set up events
    root.attributes("-fullscreen", True)
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    root.bind("<Escape>", lambda event: exitGame(root))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1400, 900)
