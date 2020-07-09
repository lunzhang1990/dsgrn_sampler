import random
from math import log
from math import floor
import numpy as np
from time import time
import sys
import json
from bisect import bisect_left

precision = 1000
timeInterval = 0.5*60*60 # half day

def getVLogic(logic):
    """Value logic"""
    vLogic = list(map(lambda x:int(x), logic.split('_')))
    return vLogic

def getLLogic(vLogic):
    """Log logic"""
    lLogic = list(map(lambda x: int(log(x,2)), vLogic))
    return lLogic

def rSample(vLogic, no):
    """The input is value logic"""
    lLogic = getLLogic(vLogic)
    samples = []
    for _ in range(no):
        temp = []
        for j in range(len(lLogic)):
            fsample =[sorted(random.sample(range(1,precision),2)) for _ in range(lLogic[j])]
            temp+=fsample
        samples.append(temp)
    return samples

def indexMask(vLogic):
    """Generate map i-> bit mask of i for value logic"""
    no = np.prod(vLogic)
    l = int(log(no,2))
    pattern = '{0:0'+str(l)+'b}'
    ret = []
    for i in range(no):
        mask = pattern.format(i)
        vMask = [int(i) for i in mask]
        currMask = []
        lLogic = getLLogic(vLogic)
        currPos = 0
        for i in range(len(lLogic)):
            temp = vMask[currPos:currPos+lLogic[i]]
            currMask.append(temp)
            currPos += lLogic[i]
        ret.append(currMask)
    return ret

def evalMask(sample, masks):
    """Given masks evaluate the sample sequence of switching polynomials"""
    ret = []
    for i in range(len(masks)):
        currVal = 1
        currPos = 0
        for j in range(len(masks[i])):
            tempSum = 0
            for k in range(len(masks[i][j])):
                if masks[i][j][k] == 0:
                    tempSum += sample[currPos][0]
                else:
                    tempSum += sample[currPos][1]
                currPos +=1
            currVal*=tempSum
        ret.append(currVal)
    return ret 

def reachTime(startTime,timeLimit):
    if time() - startTime > timeLimit:
        return True
    else:
        return False
    
def saveResult(logicName, fileNumber, res):
    fileName = logicName +'_'+str(fileNumber)
    with open(fileName,'w') as file:
        json.dump(res,file)
    
    return


            

def runSampleSPolynomials(logic):
    """Sample the swithcing polynomials without thetas"""
    roundLimit = 1000000
    
    res = dict()
    count = 1
    vLogic = getVLogic(logic)
    masks = indexMask(vLogic)
    start = time()

    while True:
        print(count)
        samples = rSample(vLogic,roundLimit)
        for i in range(len(samples)):
            tempVals = evalMask(samples[i],masks)
            if len(np.unique(tempVals)) != len(tempVals):
                continue
            tempOrd = str(np.argsort(tempVals))
            
            if tempOrd not in res:
                res[tempOrd] = 1
            else:
                res[tempOrd] +=1

        if reachTime(start, count*timeInterval):
            saveResult(str(vLogic), count, res)
            count+=1
            
def genThetas(noThetas,degree):
    """Generated Thetas, return thetas from the smallest to the biggest"""
    thetas = sorted(random.sample(range(1,precision**degree),noThetas))
    return thetas


def binSort(x):
    prev = 0
    for i in range(len(x)):
        if x[i] < 0:
            x[prev:i] = sorted(x[prev:i])
            prev = i+1
            
    l = len(x)
    x[prev:l] = sorted(x[prev:l])
    return x
            
    
            
def runSampleWithThetas(logic,noThetas):
    """Sample the swithcing polynomials without thetas"""
    roundLimit = 1000000
    res = dict()
    count = 1
    vLogic = getVLogic(logic)
    masks = indexMask(vLogic)
    start = time()
    degree = len(vLogic)
    

    while True:
        
        samples = rSample(vLogic,roundLimit)
        for i in range(len(samples)):
            tempVals = evalMask(samples[i],masks)
            thetas = genThetas(noThetas,degree)
            if len(np.unique(tempVals+thetas)) != (len(tempVals)+len(thetas)):
                continue
            
            tempOrd = np.argsort(tempVals+thetas)
            for i in range(len(tempOrd)):
                if tempOrd[i] >= len(tempVals):
                    tempOrd[i] -= len(tempOrd)
                
            tempOrd = str(binSort(tempOrd))
            
            #print(tempord)
            if tempOrd not in res:
                res[tempOrd] = 1
            else:
                res[tempOrd] +=1

        if reachTime(start, count*timeInterval):
            print(count)
            saveResult(str(vLogic), count, res)
            count+=1
            
        print(len(res))

def generateRegionForNode(logic, samples, thetas):
    
    vLogic = getVLogic(logic)
    masks = indexMask(vLogic)
    
    tempVals = evalMask(samples,masks)
    
    if len(np.unique(tempVals)) != len(tempVals):
            return False
    
    rthetas = thetas.copy()[::-1]
    tempOrd = np.argsort(tempVals+rthetas)
    for i in range(len(tempOrd)):
        if tempOrd[i] >= len(tempVals):
            tempOrd[i] -= len(tempOrd)
    tempOrd = str(list(binSort(tempOrd)))
    return eval(tempOrd)

def generateRegionForNetwork(logics,sampleList,thetaList):
    ret = []
    for i in range(len(logics)):
        logic, samples, thetas = logics[i], sampleList[i], thetaList[i]
        factor = generateRegionForNode(logic, samples, thetas)
        ret.append(factor)
    return ret