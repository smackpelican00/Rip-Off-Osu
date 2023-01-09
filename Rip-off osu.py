from cmu_112_graphics import *
from dataclasses import make_dataclass
import random
from pydub import * 
import simpleaudio as sa
import numpy as np
import time
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

Circle = make_dataclass('Circle', ['cx', 'cy', 'r', 'index', 'number'])
ApproachCircle = make_dataclass('ApproachCircle', ['cx', 'cy', 'r', 'index', 'dr']) 

################################
# Intro Screen
################################

def appStarted(app):
    app.mode = 'introScreen'
    colors(app)
    introScreenStart(app)
    
def introScreenStart(app):
    app.playableSongs, app.playableSongsDisplay = allPlayableSongs(app)
    app.shownSongIndex = 0
    app.timerDelay = 500 #Half a second flashing for Press Space Text Drawing
    app.showText = False
    app.bpm = songInfo(app, app.playableSongsDisplay[app.shownSongIndex])[0]
    app.difficulty = findDifficulty(app.bpm)
    app.survivalMode = False
    app.modeEasy = False
    app.modeMed = False
    app.modeHard = False
    app.adaptiveDifficulty = False
    

def colors(app):
    app.color1 = 'black'  #Line Colors
    app.color2 = 'white'  #Background Color
    app.color3 = 'white'  #Secondary Background Color

def introScreen_timerFired(app):
    if app.survivalMode == False:
        app.showText = not app.showText
    else:
        if ((app.modeEasy == False) and (app.modeMed == False) and 
            (app.modeHard == False)):
            app.showText = False
        else:
            app.showText = not app.showText

def findDifficulty(bpm):
    if bpm < 80:
        return 'Very Easy'
    if 80 <= bpm < 100:
        return 'Easy'
    if 100 <= bpm <= 120:
        return 'Medium'
    if 120 < bpm <= 140:
        return 'Medium Hard'
    if 140 < bpm <= 160:
        return 'Hard'
    if 160 < bpm:
        return 'Insane'

def introScreen_keyPressed(app, event):
    if app.survivalMode == False:
        if event.key == 'Space':
            app.mode = 'mainGame'
            startGame(app)
    else:
        if ((app.modeEasy == True) or (app.modeMed == True) or 
            (app.modeHard == True)):
            if event.key == 'Space':
                app.mode = 'mainGame'
                startGame(app)
    if event.key == 'Right':
        newIndex = app.shownSongIndex + 1
        if app.shownSongIndex < len(app.playableSongs)-1: #List Bound Check
            app.shownSongIndex = newIndex
    if event.key == 'Left':
        newIndex = app.shownSongIndex - 1
        if app.shownSongIndex > 0:  #List Bound Check
            app.shownSongIndex = newIndex
    app.bpm = songInfo(app, app.playableSongsDisplay[app.shownSongIndex])[0]
    app.difficulty = findDifficulty(app.bpm)
    
def introScreen_mousePressed(app, event):
    if (app.width/20 <= event.x <= app.width*4/10): 
        if (app.height*10/16 <= event.y <= app.height*12/16):
            app.survivalMode = not app.survivalMode
    if app.survivalMode == True:
        if (app.width/20 <= event.x <= app.width*3/20):
            if (app.height*12/16 <= event.y <= app.height*13/16):
                app.modeEasy = True
                app.modeMed = False
                app.modeHard = False
        if (app.width*3.5/20 <= event.x <= app.width*5.5/20):
            if (app.height*12.5/16 <= event.y <= app.height*13.5/16):
                app.modeEasy = False
                app.modeMed = True
                app.modeHard = False
        if (app.width*6/20 <= event.x <= app.width*8/20):
            if (app.height*12/16 <= event.y <= app.height*13/16):
                app.modeEasy = False
                app.modeMed = False
                app.modeHard = True
    if (app.width*11/20 <= event.x <= app.width*19/20):
        if (app.height*10/16 <= event.y <= app.height*12/16):
            app.adaptiveDifficulty = not app.adaptiveDifficulty
    if (app.width/10 <= event.x <= app.width*3/10):
        if (app.height*5/16 <= event.y <= app.height*7/16):
            skinsSet(app)
            app.mode = 'skinScreen'

def allPlayableSongs(app):
    resultForDisplay = []
    result = []
    for song in os.listdir('Songs'):
        if '.wav' in song:
            result.append(song)
            resultForDisplay.append(song[:len(song)-len('.wav')])
    return result, resultForDisplay

def introScreen_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, 
                            fill=f'{app.color2}')
    canvas.create_oval(app.width/8, app.height/24, 
                       app.width*7/8, app.height*7/24, width=5,
                       fill=f'{app.color3}', outline=f'{app.color1}')
    canvas.create_text(app.width/2, app.height/6, 
                       text='Rip-Off Osu!',
                       font='Arial 50 bold', fill=f'{app.color1}')
    canvas.create_oval(app.width/10, app.height*5/16, 
                       app.width*3/10, app.height*7/16, width=4,
                       fill=f'{app.color3}', outline=f'{app.color1}')
    canvas.create_text(app.width/5, app.height*6/16, 
                       text='Skins!',
                       font='Arial 25 bold', fill=f'{app.color1}')
    canvas.create_oval(app.width/20, app.height*10/16, 
                       app.width*8/20, app.height*12/16, width=4,
                       fill=f'{app.color3}', outline=f'{app.color1}')
    if app.survivalMode == True:
        canvas.create_text(app.width*4.5/20, app.height*11/16, 
                           text='Survival Mode: On', font='Arial 25 bold',
                           fill=f'{app.color1}')
        canvas.create_oval(app.width/20, app.height*12/16,
                           app.width*3/20, app.height*13/16, width=3,
                           fill=f'{app.color3}', outline=f'{app.color1}')
        if app.modeEasy == True:
            canvas.create_text(app.width*2/20, app.height*12.5/16, text='Easy',
                               font='Arial 15 bold', fill=f'{app.color1}')
        canvas.create_oval(app.width*3.5/20, app.height*12.5/16,
                           app.width*5.5/20, app.height*13.5/16, width=3,
                           fill=f'{app.color3}', outline=f'{app.color1}')
        if app.modeMed == True:
            canvas.create_text(app.width*4.5/20, app.height*13/16, text='Medium',
                               font='Arial 15 bold', fill=f'{app.color1}')
        canvas.create_oval(app.width*6/20, app.height*12/16,
                           app.width*8/20, app.height*13/16, width=3, 
                           fill=f'{app.color3}', outline=f'{app.color1}')
        if app.modeHard == True:
            canvas.create_text(app.width*7/20, app.height*12.5/16, text='Hard',
                               font='Arial 15 bold', fill=f'{app.color1}')
    else:
        canvas.create_text(app.width*4.5/20, app.height*11/16,
                           text='Survival Mode: Off', font='Arial 25 bold',
                           fill=f'{app.color1}')
    canvas.create_text(app.width/2, app.height/2, 
                       text=app.playableSongsDisplay[app.shownSongIndex],
                       font='Arial 30 bold', fill=f'{app.color1}')
    canvas.create_line(app.width/10, app.height*27/50, 
                       app.width*9/10, app.height*27/50,
                       width=3, fill=f'{app.color1}')
    canvas.create_text(app.width/2, app.height*29/50, 
                       text=f'{app.shownSongIndex+1}/{len(app.playableSongs)}',
                       font='Arial 20 bold', fill=f'{app.color1}')
    canvas.create_text(app.width*3/4, app.height*29/50,
                       text=f'{app.difficulty}',
                       font='Arial 25 bold', fill=f'{app.color1}')
    canvas.create_oval(app.width*11/20, app.height*10/16, 
                       app.width*19/20, app.height*12/16, width=4,
                       fill=f'{app.color3}', outline=f'{app.color1}')
    if app.adaptiveDifficulty == True:
        canvas.create_text(app.width*15/20, app.height*11/16, 
                        text='Adaptive Difficulty: On',
                        font='Arial 25 bold', fill=f'{app.color1}')
    else:
        canvas.create_text(app.width*15/20, app.height*11/16, 
                    text='Adaptive Difficulty: Off',
                    font='Arial 25 bold', fill=f'{app.color1}')
    if app.showText == True: 
        canvas.create_text(app.width/2, app.height*7/8, 
                        text='Press Space to Play!',
                        font='Arial 25 bold', fill=f'{app.color1}')

#################################
# Skin Screen
#################################

def skinsSet(app):
    app.default = True
    app.skin1 = False
    app.skin2 = False
    app.skin3= False

def skinScreen_keyPressed(app, event):
    if event.key == 'Space':
        app.mode = 'introScreen'

def skinScreen_mousePressed(app, event):
    if (app.width/10 <= event.x <= app.width*4.5/10):
        if (app.height*2/10 <= event.y <= app.width*3/10):
            app.default = True
            app.skin1 = False
            app.skin2 = False
            app.skin3 = False
    if (app.width*5.5/10 <= event.x <= app.width*9/10):
        if (app.height*2/10 <= event.y <= app.height*3/10):
            app.default = False
            app.skin1 = True
            app.skin2 = False
            app.skin3 = False 
    if (app.width/10 <= event.x <= app.width*4.5/10):
        if (app.height*4/10 <= event.y <= app.height*5/10):
            app.default = False
            app.skin1 = False
            app.skin2 = True
            app.skin3 = False
    if (app.width*5.5/10 <= event.x <= app.width*9/10):
        if (app.height*4/10 <= event.y <= app.height*5/10):
            app.default = False
            app.skin1 = False
            app.skin2 = False
            app.skin3 = True                                   
    changeskin(app)

##########################################
# Following function from 15-112 Notes
# https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
##########################################

def rgbString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

#######################################
# Colors used in skin obtained from:
# https://coolors.co/
#######################################

def changeskin(app):
    if app.default == True:
        app.color1 = 'black'  
        app.color2 = 'white'  
        app.color3 = 'white'
    if app.skin1 == True:
        app.color1 = rgbString(233, 128, 110) # Salmon
        app.color2 = rgbString(37, 77, 50) # British Racing Green
        app.color3 = rgbString(58, 125, 68) # Fern Green
    if app.skin2 == True:
        app.color1 = rgbString(243, 83, 97)# Sizzling Red
        app.color2 = rgbString(35, 22, 39) # Dark Purple
        app.color3 = rgbString(127, 183, 190) # Dark Sky Blue
    if app.skin3 == True:
        app.color1 = rgbString(72, 172, 240) # Blue Jeans
        app.color2 = rgbString(40, 61, 59) # Outer Space Crayola
        app.color3 = rgbString(195, 196, 158) # Sage

def skinScreen_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=f'{app.color2}')
    canvas.create_text(app.width/2, app.height/8, 
                       text='Skins!', font='Arial 25 bold',
                       fill=f'{app.color1}')
    canvas.create_rectangle(app.width/10, app.height*2/10, 
                            app.width*4.5/10, app.height*3/10, width=3, 
                            fill=f'{app.color3}', outline=f'{app.color1}')
    canvas.create_text(app.width*2.75/10, app.height*2.5/10, 
                       text='Default', font='Arial 25 bold', 
                       fill=f'{app.color1}')
    canvas.create_rectangle(app.width*5.5/10, app.height*2/10, 
                            app.width*9/10, app.height*3/10, width=3,
                            fill=f'{app.color3}', outline=f'{app.color1}')
    canvas.create_text(app.width*7.25/10, app.height*2.5/10, 
                       text='Skin 1', font='Arial 25 bold',
                       fill=f'{app.color1}')
    canvas.create_rectangle(app.width/10, app.height*4/10,
                            app.width*4.5/10, app.height*5/10, width=3,
                            fill=f'{app.color3}', outline=f'{app.color1}')
    canvas.create_text(app.width*2.75/10, app.height*4.5/10, 
                       text='Skin 2', font='Arial 25 bold',
                       fill=f'{app.color1}')
    canvas.create_rectangle(app.width*5.5/10, app.height*4/10,
                            app.width*9/10, app.height*5/10, width=3,
                            fill=f'{app.color3}', outline=f'{app.color1}')
    canvas.create_text(app.width*7.25/10, app.height*4.5/10, 
                       text='Skin 3', font='Arial 25 bold',
                       fill=f'{app.color1}')
    canvas.create_text(app.width/2, app.height*7/8, text='Press Space to return to Intro Screen',
                       font='Arial 25 bold', fill=f'{app.color1}')

################################
# Spotify API Stuff
# Some code commands (search and audio_features) come from Spotipy Documentation
# https://spotipy.readthedocs.io/en/2.18.0/#
################################

def songInfo(app, song):
    result = []
    for part in song.split(' - '):
        result.append(part)
    artist = result[0]
    songTitle = result[1]
    return findSongInfo(artist, songTitle)

def findSongInfo(artist, songTitle):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                     client_id='315f3aba89e64d849ed6a44b9d15ad20',
                     client_secret='3ca9bacb548c4df8b621be24ed1f63ee'))
    track_id = sp.search(q='artist:' + artist + ' track:' + songTitle, type='track') #searches for song
    trackId = track_id['tracks']['items'][0]['id']  # URI of the song
    trackInfo = sp.audio_features(tracks=[trackId]) #all info of the song in json
    tempo = trackInfo[0]['tempo']
    timeSignature = trackInfo[0]['time_signature']
    return tempo, timeSignature

################################
# Main Game
################################

def startGame(app):
    app.circles = []
    app.approachCircles = []
    app.radius = min(app.width, app.height)/10
    app.initialRadius = app.radius # to revert to in adaptive diff
    app.approachCircleRadius = app.radius * 3 
    app.song = app.playableSongs[app.shownSongIndex]
    app.sound = getSound(f'Songs/{app.song}')
    app.bpm, app.timeSignature = songInfo(app, app.playableSongsDisplay[app.shownSongIndex])
    app.timerDelay = 5
    app.timeStart = time.time()
    app.timePerCircle = millisecondsPerCircle(app) #how frequently circles should be created
    app.dr = velocityOfApproachCircle(app) # based on what app.radius is (mathematically)
    app.numCirclesCreated = 0 #use this with timeSignature to make numbers in circles
    app.paused = False
    app.sound_obj = playSound(app.sound) # this is so that the song can be paused
    initializeScoreInfo(app)

def initializeScoreInfo(app):
    app.score = 0
    app.streak = 0
    app.longestStreak = 0
    app.circlePerfectHits = 0
    app.circleCloseHits = 0
    app.circleMisses = 0
    if app.survivalMode == True:
        app.hp = 100
        app.death = False

def millisecondsPerCircle(app):
    beatsPerSecond = app.bpm/60
    secondsPerCircle = 1/beatsPerSecond
    return int(secondsPerCircle * 1000)

def velocityOfApproachCircle(app):
    distance = app.approachCircleRadius - app.radius
    time = app.timePerCircle / app.timerDelay #FPS kinda deal
    return distance/time

############################################
# The 3 following functions from the CMU 15-112 TA audio lecture
# written by Arjan Bedi
# also from: https://simpleaudio.readthedocs.io/en/latest/index.html
############################################

def getSound(AudioFile):  
    return AudioSegment.from_file(AudioFile)

def lengthSound(sound): 
    return sound.duration_seconds

def playSound(sound):
    rawAudioData = sound.raw_data
    np_array = np.frombuffer(rawAudioData, dtype=np.int16)
    wave_obj = sa.WaveObject(np_array, 2, 2, 44100)
    return wave_obj.play()
    #returns play_obj

def mouseInCircle(x, y, circle):
    return (((circle.cx - x)**2) + ((circle.cy - y)**2))**0.5 <= circle.r 

def createCircle(app):
    if len(app.circles) < 4: # just to control how many circles happen...
        numInCircle = (app.numCirclesCreated % app.timeSignature) + 1
        cx = random.uniform(0+app.radius, app.width-app.radius)
        cy = random.uniform(0+app.radius, app.height-app.radius)
        newCircle = Circle(cx=cx, cy=cy, r=app.radius, index=len(app.circles), number=numInCircle) 
        app.circles.append(newCircle)
        createApproachCircle(app, newCircle, cx, cy, app.radius)
        app.numCirclesCreated += 1

def createApproachCircle(app, circle, cx, cy, r):
    newApproachCircle = ApproachCircle(cx=cx, cy=cy, r=app.approachCircleRadius, 
                               index=len(app.approachCircles), dr=app.dr)
    app.approachCircles.append(newApproachCircle)

def mainGame_timerFired(app):
    if app.paused == False:
        timeElapsed = time.time() - app.timeStart
        if not app.sound_obj.is_playing(): #checks if song is not playing (from previously being paused)
            newSound = app.sound[timeElapsed*1000:] #plays song from paused moment
            app.sound_obj = playSound(newSound)
        if timeElapsed < lengthSound(app.sound):
            timeElapsed = timeElapsed * 1000 #make into milliseconds
            if 0 < timeElapsed % app.timePerCircle < 15: #time elapsed is close to when you want new circle
                createCircle(app)
            for circle in app.approachCircles:
                if checkCircleIllegal(app, circle):
                    removeCircle(app, circle)
                    changeScore(app, 'miss')
                if circle.r > 0:
                    circle.r -= circle.dr
        else:
            app.mode = 'scoreScreen'
    else:
        app.sound_obj.stop() 

def mainGame_keyPressed(app, event):
    if event.key == 'p':
        app.paused = not app.paused
    if event.key == 'f':
        app.mode = 'scoreScreen'
        app.sound_obj.stop()
    if event.key == 'r':
        app.mode = 'introScreen'
        app.sound_obj.stop()
        introScreenStart(app)

def mainGame_mousePressed(app, event):
    cx = event.x
    cy = event.y
    for circle in app.circles:
        if mouseInCircle(cx, cy, circle):
            checkRadiusDiff(app, circle)
            removeCircle(app, circle)
            break #so that if circles are stacked, only circle with smallest
                  #approach circle is clicked. 

def checkCircleIllegal(app, circle):
    approachCircle = app.approachCircles[circle.index]
    tgtCircle = app.circles[circle.index]
    radiusDiff = approachCircle.r / tgtCircle.r #use ratio to determine legality
    if radiusDiff <= 0.8:
        return True
    else:
        return False

def removeCircle(app, circle):
    indexOfRemovedCircle = circle.index
    app.circles.pop(indexOfRemovedCircle)
    app.approachCircles.pop(indexOfRemovedCircle)
    for circles in app.circles: 
        if circles.index > indexOfRemovedCircle:
            circles.index -= 1
    for circles in app.approachCircles:
        if circles.index > indexOfRemovedCircle:
            circles.index -= 1

def checkRadiusDiff(app, circle):
    approachCircle = app.approachCircles[circle.index]
    radiusDiff = approachCircle.r / circle.r #use ratio to determine score
    if 0.9 < radiusDiff < 1.1: 
        changeScore(app, 'perfectHit')
    elif 0.8 < radiusDiff < 1.4:
        changeScore(app, 'closeHit')
    else:
        changeScore(app, 'miss')

#################################
# Scoring System algorithm directly inspired from Original Osu! game. 
# https://osu.ppy.sh/wiki/en/Score#score
#################################

def changeScore(app, hitType): 
    if hitType == 'perfectHit':
        app.circlePerfectHits += 1
        app.streak += 1
        scoreAdd = 300
        app.score += scoreAdd + int((scoreAdd * app.streak)/25)
        if app.survivalMode == True:
            app.hp = changeHp(app, app.hp, hitType)
    elif hitType == 'closeHit':
        app.circleCloseHits += 1
        app.streak += 1
        scoreAdd = 100
        app.score += scoreAdd + int((scoreAdd * app.streak)/25)
        if app.survivalMode == True:
            app.hp = changeHp(app, app.hp, hitType)
    elif hitType == 'miss':
        app.circleMisses += 1
        if app.streak > app.longestStreak:
            app.longestStreak = app.streak
        app.streak = 0
        if app.survivalMode == True:
            app.hp = changeHp(app, app.hp, hitType)
            if app.hp == 0:
                app.death = True
                app.mode = 'scoreScreen'
                app.sound_obj.stop()
    if app.adaptiveDifficulty == True:
        app.radius = int(app.initialRadius*(0.95)**(app.streak//5)) #radius will get smaller as streak increases
        app.approachCircleRadius = app.radius*3
        
def changeHp(app, hp, hitType):
    if app.modeEasy == True:
        if hitType == 'perfectHit':
            hp += 10
        if hitType == 'closeHit':
            hp += 5
        if hitType == 'miss':
            hp -= 5
    elif app.modeMed == True:
        if hitType == 'perfectHit':
            hp += 6
        if hitType == 'closeHit':
            hp += 3
        if hitType == 'miss':
            hp -= 15
    elif app.modeHard == True:
        if hitType == 'perfectHit':
            hp += 4
        if hitType == 'closeHit':
            hp += 2
        if hitType == 'miss':
            hp -= 30
    if hp < 0: hp = 0
    if hp > 100: hp = 100
    return hp

def mainGame_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=f'{app.color2}')
    # reverse list so that circles that need to be clicked first are on top
    for circle in app.approachCircles[::-1]: 
        canvas.create_oval(circle.cx - circle.r, circle.cy - circle.r,
                           circle.cx + circle.r, circle.cy + circle.r, width=4, 
                           outline=f'{app.color1}')
    for circle in app.circles[::-1]:
        canvas.create_oval(circle.cx - circle.r, circle.cy - circle.r,
                           circle.cx + circle.r, circle.cy + circle.r, width=6, 
                           fill=f'{app.color3}', outline=f'{app.color1}')
        canvas.create_text(circle.cx, circle.cy, text=f'{circle.number}', 
                           font=f'Arial {int(app.radius/2)}',
                           fill=f'{app.color1}')
    if app.survivalMode == True:
        canvas.create_rectangle(app.width/25, app.height/30, 
                                app.width*8/25, app.height*2/30, width=2,
                                fill=f'{app.color2}', outline=f'{app.color1}')
        canvas.create_rectangle(app.width/25, app.height/30,
                                app.width/25 + (app.width*7/25)*(app.hp/100), #represents how much health graphically
                                app.height*2/30, width=2, fill=f'{app.color1}',
                                outline=f'{app.color1}')
    textSizeStreak = app.height//20
    textSizeScore = app.height//40
    canvas.create_text(app.width*2/30, app.height*19/20, text=f'x{app.streak}',
                       font=f'Arial {textSizeStreak}', fill=f'{app.color1}')
    canvas.create_text(app.width*3/4, app.height*1/20, text=f'Score: {app.score}',
                       font=f'Arial {textSizeScore}', fill=f'{app.color1}')

################################
# Score Screen
################################

def scoreScreen_keyPressed(app, event):
    if event.key == 'Space':
        app.mode = 'introScreen'
        introScreenStart(app)

def scoreScreen_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=f'{app.color2}')
    font = 'Arial 20 bold'
    canvas.create_text(app.width/4, app.height/8, 
                       text=f'Perfect Hits: {app.circlePerfectHits}', font=font,
                       fill=f'{app.color1}')
    canvas.create_text(app.width/4, app.height*2/8, 
                       text=f'Close Hits: {app.circleCloseHits}', font=font,
                       fill=f'{app.color1}')
    canvas.create_text(app.width/4, app.height*3/8, 
                       text=f'Misses: {app.circleMisses}', font=font,
                       fill=f'{app.color1}')
    canvas.create_text(app.width*3/4, app.height*3/8, 
                       text=f'Longest Streak: {app.longestStreak}', font=font,
                       fill=f'{app.color1}')
    canvas.create_text(app.width*3/4, app.height/8, text=f'Score: {app.score}', 
                       font=font, fill=f'{app.color1}')
    if app.survivalMode == True:
        if app.death == False:
            canvas.create_text(app.width/2, app.height*5/8, text='You Survived!',
                               font=font, fill=f'{app.color1}')
        else:
            canvas.create_text(app.width/2, app.height*5/8, text='You Died!', 
                               font=font, fill=f'{app.color1}')
    canvas.create_text(app.width/2, app.height*7/8, 
                       text='Press Space to return to return to main screen!',
                       font=font, fill=f'{app.color1}')

runApp(width=1000, height=1000)