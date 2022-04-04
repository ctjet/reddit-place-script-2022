import pathlib
import time
import matplotlib.pyplot as plt

imageW = 3555
imageH = 2000
processW = imageW-imageH

def renderFrame(date, goodEnoughCount):


def process():
    csvPath = str(pathlib.Path(__file__).parent.resolve())+"/frames.csv"
    f = open(csvPath,'r')
    lines = f.readlines()
    f.close()

    goodCount = []
    defectsCounts = [[],[],[]]

    for line in lines:
        if line == None:
            break  

        line = line.replace("\n","")
        
        fields = line.split(",")
        frameNum = fields[0]
        frameEpoch = float(fields[1])
        allMogusCount = int(fields[2])
        filter1Count = int(fields[5])
        filter2Count = int(fields[6])
        filter3Count = int(fields[7])
        filter4Count = int(fields[8])
        defects0Count = int(fields[9])
        defects1Count = int(fields[10])
        defects2Count = int(fields[11])
        goodEnoughCount = int(fields[13])
        goodCount.append(goodEnoughCount)
        defectsCounts[0].append(defects0Count)
        defectsCounts[1].append(defects1Count)
        defectsCounts[2].append(defects2Count)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frameEpoch)))



def main():
    process()

if __name__ == "__main__":
    main()
