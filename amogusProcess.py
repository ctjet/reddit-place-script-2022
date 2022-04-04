import os
import os.path
import math
import subprocess

import requests
import json
import time
import threading
import sys
import random
from io import BytesIO
from http import HTTPStatus
from websocket import create_connection
from PIL import Image, UnidentifiedImageError, ImageEnhance
from loguru import logger
import click
from bs4 import BeautifulSoup
import pathlib

from stem import Signal, InvalidArguments, SocketError, ProtocolError
from stem.control import Controller

from src.mappings import ColorMapper


def process(path, currentFrame):
    imageExtension = "_{:06d}.png".format(int(currentFrame))
    storedFrame = currentFrame

    processStartTime = time.time()

    boardimg = Image.open(path)
    enhancer = ImageEnhance.Brightness(boardimg)
    darkImage = enhancer.enhance(0.25)
    darkImage2 = enhancer.enhance(0.25)

    pix = boardimg.convert("RGB").load()
    h, w = boardimg.size
    highlight = Image.new(mode="RGBA", size=(2000, 2000),color = (0, 0, 0,0))
    
    highlightZeroDefects = Image.new(mode="RGBA", size=(2000, 2000),color = (0, 0, 0,0))
    highlightOneDefect = Image.new(mode="RGBA", size=(2000, 2000),color = (0, 0, 0,0))
    highlightTwoDefect = Image.new(mode="RGBA", size=(2000, 2000),color = (0, 0, 0,0))
    highlightThreeDefect = Image.new(mode="RGBA", size=(2000, 2000),color = (0, 0, 0,0))


    highlightColorsTall = [(252, 3, 3,255),(252, 136, 3,255),(252, 240, 3,255),(3, 252, 11,255)]
    highlightColorsShort = [(3, 206, 252,255),(24, 3, 252,255),(148, 3, 252,255),(252, 3, 231,255)]

    # highlight = blank.load()

    files = os.listdir(str(pathlib.Path(__file__).parent.resolve()))

    # for item in files:
    #     if item.endswith(".png"):
    #         os.remove(os.path.join(str(pathlib.Path(__file__).parent.resolve()), item))
    # boardimg.save(str(pathlib.Path(__file__).parent.resolve())+"/snapshots/cur"+imageExtension,quality = 100)
    
    background = 0
    visor = 1
    mogus = 2
    backgroundOrMogus = 3
    mogus1 = [  (3,3,0,0,0),
                (3,0,2,2,2),
                (0,2,2,1,1),
                (0,2,2,2,2),
                (0,3,2,3,2),
                (3,0,2,0,2)]
    mogus3 = [  (3,3,0,0,0),
                (3,0,2,2,2),
                (0,2,2,1,1),
                (0,2,2,2,2),
                (3,0,2,0,2)]
    mogus2 = [  (3,0,0,0,3),
                (0,2,2,2,0),
                (0,1,1,2,2),
                (0,2,2,2,2),
                (0,2,3,2,3),
                (0,2,0,2,0)]
    mogus4 = [  (3,0,0,0,3),
                (0,2,2,2,0),
                (0,1,1,2,2),
                (0,2,2,2,2),
                (0,2,0,2,0)]
                
    
    filters = [mogus1, mogus2, mogus3, mogus4]
    filterNames = ["normal","normal reverse", "short", "short reverse"]

    highlightBlankColor = (0,0,0,0)

    def findMogus(filter, x, y, filterName, filterIndex): #returns 
        bgCount = 0
        bgDict = {}
        mogusCount = 0


        mogusDict = {}
        visorColor = (0,0,0)
        visorCount = 0
        mogusLeniency = 2
        bgLeniency = 1
        wasGreen = False

        for xOff in range(len(filter[0])):
            for yOff in range(len(filter)):
                xPos = x + xOff
                yPos = y + yOff
                if(xPos >=0 and xPos < w):
                    if(yPos >=0 and yPos < h):
                        color = pix[xPos,yPos]
                        #background
                        if(filter[yOff][xOff] == 0):
                            if highlight.getpixel((xPos,yPos)) == highlightBlankColor:
                                bgCount += 1
                                if color not in bgDict:
                                    bgDict[color] = 1
                                else:
                                    bgDict[color] = bgDict[color] + 1
                        #visor
                        elif(filter[yOff][xOff] == 1):
                            if visorCount == 0:
                                visorColor = color
                            else:
                                if color != visorColor:
                                    return tuple([False])
                            visorCount += 1
                        #mogus
                        elif(filter[yOff][xOff] == 2):
                            mogusCount += 1
                            if highlight.getpixel((xPos,yPos)) != highlightBlankColor:
                                return tuple([False])
                            if color not in mogusDict:
                                mogusDict[color] = 1
                            else:
                                mogusDict[color] = mogusDict[color] + 1
                        #dont worry about the 3s
        
        def getMaxColor(dict):
            maxColor = ()
            maxCount = 0
            for color,count in dict.items():
                if (count > maxCount):
                    maxColor = color
                    maxCount = count
            return (maxColor, maxCount)

        mogusColor, mogusColorCount = getMaxColor(mogusDict)
        defectCount = mogusCount - mogusColorCount
        bgDefectCount = 0
        if (mogusColorCount < mogusCount - mogusLeniency):
            return tuple([False])

        if (visorColor == mogusColor):
            return tuple([False])

        if mogusColor in bgDict:
            defectCount += bgDict[mogusColor]
            bgDefectCount = bgDict[mogusColor]
            if(bgDict[mogusColor] > bgLeniency):
                return tuple([False])
        
        for xOff in range(len(filter[0])):
            for yOff in range(len(filter)):
                xPos = x + xOff
                yPos = y + yOff
                if(xPos >=0 and xPos < w):
                    if(yPos >=0 and yPos < h):
                        color =  pix[xPos,yPos]
                        
                        if(filter[yOff][xOff] > 0 and not filter[yOff][xOff] == 3):
                            if bgDefectCount <2 and mogusCount - mogusColorCount < 2:
                                wasGreen = True
                                highlight.putpixel((xPos,yPos),(color[0], color[1],color[2], 255))
                            if defectCount < 4:
                                otherHighlight = highlightZeroDefects
                                if defectCount == 1:
                                    otherHighlight = highlightOneDefect
                                if defectCount == 2:
                                    otherHighlight = highlightTwoDefect
                                if defectCount == 3:
                                    otherHighlight = highlightThreeDefect
                                if filterIndex < 2:
                                    otherHighlight.putpixel((xPos,yPos),highlightColorsTall[defectCount])
                                else:
                                    otherHighlight.putpixel((xPos,yPos),highlightColorsShort[defectCount])
        # found, num defects, was tall, matched filter name, matched filter type,
        return (True, defectCount, filterIndex < 2, filterName, filterIndex, wasGreen)

    row = 0
    prevProgress = 0
    mogusCount = 0
    defectCount = [0,0,0,0,0]
    filterCount = [0,0,0,0]
    tallShort = [0,0]
    greenCount = 0

    prevTime = time.time()
    for i in range (len(filters)):
        for x in range(-1,w-len(mogus1[0])):
            progress = round(row*100 / (len(filters) * h))
            if math.floor(progress/10) != math.floor(prevProgress/10):
                prevProgress = progress
                print(progress, "% done, found", mogusCount, "mogi, this percent took seconds: ", time.time()-prevTime)
                prevTime = time.time()
            row += 1
            for y in range(-1,h-len(mogus1)):
                ret = findMogus(filters[i], x, y,filterNames[i], i)
                if len(ret) > 1:
                    defectCount[ret[1]] += 1
                    filterCount[ret[4]] += 1
                    if ret[5]:
                        greenCount += 1
                    if ret[2]:
                        tallShort[0] += 1
                    else:
                        tallShort[1] += 1
                    mogusCount += 1

    
    print("frame", storedFrame, "done, found ", mogusCount)
    file1 = open(str(pathlib.Path(__file__).parent.resolve())+"/frames.csv", "a")  # append mode
    file1.write(str(storedFrame) + "," +str(processStartTime) +  "," + str(mogusCount)+","+str(tallShort[0])+","+str(tallShort[1])+","+str(filterCount[0])+","+str(filterCount[1])+","+str(filterCount[2])+","+str(filterCount[3])+","+str(defectCount[0])+","+str(defectCount[1])+","+str(defectCount[2])+","+str(defectCount[3])+","+str(defectCount[4])+","+str(greenCount)+"\n")
    file1.close()

    highlightZeroDefects.save(str(pathlib.Path(__file__).parent.resolve())+"/nodefects/highlight"+imageExtension,quality = 100)
    highlightOneDefect.save(str(pathlib.Path(__file__).parent.resolve())+"/onedefect/highlight"+imageExtension,quality = 100)
    highlightTwoDefect.save(str(pathlib.Path(__file__).parent.resolve())+"/twodefect/highlight"+imageExtension,quality = 100)
    highlightThreeDefect.save(str(pathlib.Path(__file__).parent.resolve())+"/threedefect/highlight"+imageExtension,quality = 100)

    highlightZeroDefects.paste(highlightOneDefect, (0, 0), highlightOneDefect)
    highlightZeroDefects.paste(highlightTwoDefect, (0, 0), highlightTwoDefect)
    highlightZeroDefects.paste(highlightThreeDefect, (0, 0), highlightThreeDefect)
    highlightZeroDefects.save(str(pathlib.Path(__file__).parent.resolve())+"/combineddefect/highlight"+imageExtension,quality = 100)


    highlight.save(str(pathlib.Path(__file__).parent.resolve())+"/void/highlight"+imageExtension,quality = 100)
    darkImage.paste(highlight, (0, 0), highlight)
    darkImage.save(str(pathlib.Path(__file__).parent.resolve())+"/overlays/overlay"+imageExtension,quality = 100)

    for x in range(w):
        for y in range(h):
            if highlight.getpixel((x,y))[3]>0:
                highlight.putpixel((x,y),(0,255,0,255))

    darkImage.paste(highlight, (0, 0), highlight)
    darkImage.save(str(pathlib.Path(__file__).parent.resolve())+"/green/green"+imageExtension,quality = 100)

    darkImage2.paste(highlightZeroDefects, (0, 0), highlightZeroDefects)
    darkImage2.save(str(pathlib.Path(__file__).parent.resolve())+"/defectoverlays/overlay"+imageExtension,quality = 100)





@click.command()
@click.option(
    "-p",
    "--path",
    help="path of file to process",
)
@click.option(
    "-i",
    "--index",
    help="file number",
)
def main(path, index):

    process(path, index)

if __name__ == "__main__":
    main()
