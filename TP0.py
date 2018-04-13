#import module_manager
#module_manager.review()
import pyaudio
from tkinter import *
import numpy
import pygame
import os
import wave
#import soundanalyse


def init(data):
    data.mode="splashScreen"
    data.file="triangles-download (3).png"
    data.background=PhotoImage(file=data.file)





def mousePressed(event, data):
    if (data.mode == "splashScreen"): splashScreenMousePressed(event, data)
    elif (data.mode=="songSelection"): songSelectionMousePressed(event, data)
    elif (data.mode=="settings"): settingsMousePressed(event, data)
    elif (data.mode == "playGame"):   playGameMousePressed(event, data)
    elif (data.mode=="gameOver"):   gameOverMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "splashScreen"): splashScreenKeyPressed(event, data)
    elif (data.mode=="songSelection"): songSelectionKeyPressed(event, data)
    elif (data.mode=="settings"): settingsKeyPressed(event, data)
    elif (data.mode == "playGame"):   playGameKeyPressed(event, data)
    elif (data.mode=="gameOver"):   gameOverKeyPressed(event, data) 

def timerFired(data):
    if (data.mode == "splashScreen"): splashScreenTimerFired(data)
    elif (data.mode=="songSelection"): songSelectionTimerFired(data)
    elif (data.mode=="settings"): settingsTimerFired(data)
    elif (data.mode == "playGame"):   playGameTimerFired(data)
    elif (data.mode=="gameOver"):   gameOverTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "splashScreen"): splashScreenRedrawAll(canvas, data)
    elif (data.mode=="songSelection"): songSelectionRedrawAll(canvas, data)
    elif(data.mode=="settings"): settingsRedrawAll(canvas, data)
    elif (data.mode == "playGame"):   playGameRedrawAll(canvas, data)
    elif (data.mode=="gameOver"):   gameOverRedrawAll(canvas, data)

def splashScreenMousePressed(event, data):
    pass

def splashScreenKeyPressed(event, data): pass

def splashScreenRedrawAll(canvas, data):
    #backgroundLabel.image=data.background
    #data.backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)
    canvas.create_image(data.width/2, data.height/2, \
        anchor="center", image=data.background)
    canvas.create_rectangle(data.width/2-400, data.height/2-300, \
        data.width/2+400, data.height/2, fill="white", \
        stipple='gray50', outline='')
    canvas.create_text(data.width/2, data.height/2-150, \
        text="Osu!", font=("Century Gothic", int(100)), fill="gray40")
    canvas.create_rectangle(data.width/2-300, data.height/2+20, \
    data.width/2+300, data.height/2+100, fill="white", \
    stipple='gray50', outline='')
    canvas.create_text(data.width/2, data.height/2+60, \
    text="Play", font=("Century Gothic", int(30)), fill="gray40")
    canvas.create_rectangle(data.width/2-300, data.height/2+120, \
    data.width/2+300, data.height/2+200, fill="white", \
    stipple='gray50', outline='')
    canvas.create_text(data.width/2, data.height/2+160, text="Help"\
    , font=("Century Gothic", int(30)), fill="gray40")
    canvas.create_rectangle(data.width/2-300, data.height/2+220, \
    data.width/2+300, data.height/2+300, fill="white", \
    stipple='gray50', outline='')
    canvas.create_text(data.width/2, data.height/2+260, text="Settings",\
     font=("Century Gothic", int(30)), fill="gray40")

def splashScreenTimerFired(data): pass

# chunk = 1024
# wf = wave.open('Mike-Perry-The-Ocean-ft-Shy-Martin.wav', 'rb')
# p = pyaudio.PyAudio()

# stream = p.open(
#     format = p.get_format_from_width(wf.getsampwidth()),
#     channels = wf.getnchannels(),
#     rate = wf.getframerate(),
#     output = True)
# data = wf.readframes(chunk)

# while data != '':
#     stream.write(data)
#     data = wf.readframes(chunk)

# stream.close()
# p.terminate()

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
    #data.width = width
    #data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    init(data)
    data.width = root.winfo_screenwidth()
    data.height = root.winfo_screenheight()
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    # set up events
    #root.overrideredirect(True)
    root.attributes("-fullscreen", True)
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1400, 900)

#audio lecture
#pyaudio demo

#Code modified from https://people.csail.mit.edu/hubert/pyaudio/

###########################################################################
######################### Playing a WAV file ##############################
###########################################################################


"""PyAudio Example: Play a WAVE file."""

# import pyaudio
# import wave
# from array import array
# from struct import pack

# def play(file):
#     CHUNK = 1024 #measured in bytes

#     wf = wave.open(file, 'rb')

#     p = pyaudio.PyAudio()

#     stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                     channels=wf.getnchannels(),
#                     rate=wf.getframerate(),
#                     output=True)

#     data = wf.readframes(CHUNK)

#     while len(data) > 0:
#         stream.write(data)
#         data = wf.readframes(CHUNK)

#     stream.stop_stream()
#     stream.close()

#     p.terminate()

# ###########################################################################
# ######################### Recording a WAV file ############################
# ###########################################################################
# def record(outputFile):
#     CHUNK = 1024 #measured in bytes
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 2 #stereo
#     RATE = 44100 #common sampling frequency
#     RECORD_SECONDS = 5 #change this record for longer or shorter!

#     p = pyaudio.PyAudio()

#     stream = p.open(format=FORMAT,
#                     channels=CHANNELS,
#                     rate=RATE,
#                     input=True,
#                     frames_per_buffer=CHUNK)

#     print("* recording")

#     frames = []

#     for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#         data = stream.read(CHUNK)
#         frames.append(data)

#     print("* done recording")

#     stream.stop_stream()
#     stream.close()
#     p.terminate()

#     wf = wave.open(outputFile, 'wb')
#     wf.setnchannels(CHANNELS)
#     wf.setsampwidth(p.get_sample_size(FORMAT))
#     wf.setframerate(RATE)
#     wf.writeframes(b''.join(frames))
#     wf.close()

