import pathlib
import time
import matplotlib.pyplot as plt
from PIL import Image, UnidentifiedImageError, ImageEnhance, ImageFont,ImageDraw
import io

imageW = 3840
imageH = 2160
placeWidth = 2000
processW = imageW-imageH

def drawRows(x, y, spacing, msgs, im, fontSize = 60):
    fnt = ImageFont.truetype("arial.ttf", fontSize)
    d = ImageDraw.Draw(im)
    for i in range(len(msgs)):
        d.text((x, y+i*spacing), msgs[i], font=fnt, fill=(255, 255, 255, 255))

    return spacing * len(msgs)



def renderFrame(date, goodEnoughList, defectsLists, filtersLists, currentFrame):
    im = Image.new(mode="RGBA", size=(imageW-placeWidth, imageH),color = (0, 0, 0,0))
    fnt = ImageFont.truetype("arial.ttf", 60)
    d = ImageDraw.Draw(im)

    msgs = ["Current Time: " + str(date),
        "\"Good\" Mogus Count: "+ str(goodEnoughList[len(goodEnoughList)-1]),
        "Num Tall Facing Right: "+ str(filtersLists[0][len(filtersLists[0])-1]),
        "Num Tall Facing Left: "+ str(filtersLists[1][len(filtersLists[1])-1]),
        "Num Short Facing Right: "+ str(filtersLists[2][len(filtersLists[2])-1]),
        "Num Short Facing Left: "+ str(filtersLists[3][len(filtersLists[3])-1]),
        "Num 0 defects: " + str(defectsLists[0][len(defectsLists[0])-1]),
        "Num 1 defect: " + str(defectsLists[1][len(defectsLists[1])-1]),
        "Num 2 defects: " + str(defectsLists[2][len(defectsLists[2])-1]),
        "Num 3 defects: " + str(defectsLists[3][len(defectsLists[3])-1]),
        ]
    bottomY = drawRows(30,60,70,msgs,im)

    global plt


    plt.plot(range(len(goodEnoughList)),goodEnoughList)
    # naming the x axis
    plt.xlabel('Minutes')
    # naming the y axis
    plt.ylabel('"good" moguses')
    # giving a title to my graph
    plt.title('"good" mogus count over time')

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=130)

    pltIm = Image.open(img_buf)

    im.paste(pltIm, (30, bottomY))

    plt.clf()

    img_buf.close()

    plt.plot(range(len(defectsLists[0])),defectsLists[0], label = "0 Defects")
    plt.plot(range(len(defectsLists[1])),defectsLists[1], label = "1 Defect")
    plt.plot(range(len(defectsLists[2])),defectsLists[2], label = "2 Defects")
    plt.plot(range(len(defectsLists[3])),defectsLists[3], label = "3 Defects")

    # naming the x axis
    plt.xlabel('Minutes')
    # naming the y axis
    plt.ylabel('mogus count')
    # giving a title to my graph
    plt.title('mogus defect counts over time')
    plt.legend()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=130)

    pltIm = Image.open(img_buf)

    im.paste(pltIm, (30+900, bottomY))

    plt.clf()

    img_buf.close()

    plt.plot(range(len(filtersLists[0])),filtersLists[0], label = "Tall Face R")
    plt.plot(range(len(filtersLists[1])),filtersLists[1], label = "Tall Face L")
    plt.plot(range(len(filtersLists[2])),filtersLists[2], label = "Shrt Face R")
    plt.plot(range(len(filtersLists[3])),filtersLists[3], label = "Shrt Face L")

    # naming the x axis
    plt.xlabel('Minutes')
    # naming the y axis
    plt.ylabel('mogus count')
    # giving a title to my graph
    plt.title('mogus types over time')
    plt.legend()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=130)

    pltIm = Image.open(img_buf)

    im.paste(pltIm, (30, bottomY+700))

    plt.clf()

    img_buf.close()

    imageExtension = "_{:06d}.png".format(int(currentFrame))
    im.save(str(pathlib.Path(__file__).parent.resolve())+"/graphs/graph"+imageExtension,quality = 100)

    # im.show()


def process():

    csvPath = str(pathlib.Path(__file__).parent.resolve())+"/frames.csv"
    f = open(csvPath,'r')
    lines = f.readlines()
    f.close()

    goodCount = []
    defectsCounts = [[],[],[],[]]
    filtersCounts = [[],[],[],[]]

    for line in lines:
        if line == None:
            break  

        line = line.replace("\n","")
        
        fields = line.split(",")
         # frame, start epoch, all mogus count, tall, short, filter 1, filter 2, filter 3, filter 4, 0 defect, 1 defect, 2 defect, 3 defect, always 0, "good count"
        frameNum = int(fields[0])
        frameEpoch = float(fields[1])
        allMogusCount = int(fields[2])
        filter1Count = int(fields[5])
        filter2Count = int(fields[6])
        filter3Count = int(fields[7])
        filter4Count = int(fields[8])
        defects0Count = int(fields[9])
        defects1Count = int(fields[10])
        defects2Count = int(fields[11])
        defects3Count = int(fields[12])
        goodEnoughCount = int(fields[14])
        filtersCounts[0].append(filter1Count)
        filtersCounts[1].append(filter2Count)
        filtersCounts[2].append(filter3Count)
        filtersCounts[3].append(filter4Count)
        goodCount.append(goodEnoughCount)
        defectsCounts[0].append(defects0Count)
        defectsCounts[1].append(defects1Count)
        defectsCounts[2].append(defects2Count)
        defectsCounts[3].append(defects3Count)
        # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frameEpoch))+" CST")
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frameEpoch))+" CST"
        renderFrame(date, goodCount, defectsCounts, filtersCounts, frameNum)



def main():
    highlightColorsTall = [(252, 3, 3,255),(252, 136, 3,255),(252, 240, 3,255),(3, 252, 11,255)]
    highlightColorsShort = [(3, 206, 252,255),(24, 3, 252,255),(148, 3, 252,255),(252, 3, 231,255)]

    for c in highlightColorsShort:
        im = Image.new(mode="RGBA", size=(100,100),color = c)
        im.show()

    process()

if __name__ == "__main__":
    main()
