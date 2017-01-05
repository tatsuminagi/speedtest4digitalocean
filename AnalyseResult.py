#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline

def ReadPingResults(filename):
    pingRes = {}
    with open(filename, 'r') as f:
        for line in f:
            if line[0:4] == '====' or line == '\n':
                continue
            elif line[0:6] == 'Tested':
                tempLine = line.split()
                hour = int(tempLine[2].split(':')[0])
            else:
                server = line[0:4]
                tempLine = line[6:].strip().split(', ')
                avg = float( tempLine[0].split('=')[1] ) # ms
                
                lossFrac = tempLine[1].split('=')[1].strip()
                lossFrac = lossFrac.split('/')
                loss = float(lossFrac[0]) / float(lossFrac[1]) * 100.0 # percentage
                
                if pingRes.has_key(server):
                    pingRes[server][hour, 0] = avg
                    pingRes[server][hour, 1] = loss
                else:
                    pingRes[server] = np.zeros((24, 2))
                    pingRes[server][hour, 0] = avg
                    pingRes[server][hour, 1] = loss
    return pingRes

def ReadDownloadResults(filename):
    downloadRes = {}
    hourList = []
    with open(filename, 'r') as f:
        for line in f:
            if line[0:4] == '====' or line == '\n':
                continue
            elif line[0:6] == 'Tested':
                tempLine = line.split()
                hour = int(tempLine[2].split(':')[0])
                hourList.append(hour)
            else:
                server = line[0:4]
                tempLine = line[6:].strip()
                speed = float(tempLine) # KB/s
                
                if downloadRes.has_key(server):
                    downloadRes[server][hour, 0] = speed
                else:
                    downloadRes[server] = np.zeros((24, 1))
                    downloadRes[server][hour, 0] = speed
    return downloadRes, np.array(hourList)

if __name__ == '__main__':
    pingRes = ReadPingResults('result_ping2.txt')
    downloadRes, hourList = ReadDownloadResults('result_download2.txt')
    
    hourList_ = np.zeros((hourList.shape), dtype=np.int)
    hourListInd = np.zeros((hourList.shape), dtype=np.int)
    for i in range(2, hourList.shape[0]):
        if abs(hourList[-i] - hourList[-i+1]) != 1 and hourList[-i] != 23:
            hourList_[0:i-1] = hourList[-i+1:]
            hourListInd = range(hourList.shape[0]-i+1, hourList.shape[0])
            hourList_[i-1:] = hourList[:-i+1]
            hourListInd += range(0, hourList.shape[0]-i+1)
    hourListInd = np.array(hourListInd)
    
    keys = ['nyc1', 'nyc2', 'nyc3', 'ams2', 'ams3', 'sfo1', 'sfo2', 
            'sgp1', 'lon1', 'fra1', 'tor1', 'blr1']
    
    for key in keys:
        speed = np.mean(downloadRes[key][hourList])
        speedStd = np.std(downloadRes[key][hourList])
        pingTime, pingLoss = np.mean(pingRes[key][hourList, :], axis=0)
        pingTimeStd, pingLossStd = np.std(pingRes[key][hourList, :], axis=0)
        print("_" * 80)
        print("{0}".format(key))
        print("\tspeed: {0:.3f} KB/s ({1:.3f})".format(speed, speedStd))
        print("\tping:  {0:.3f} ms   ({1:.3f})".format(pingTime, pingTimeStd))
        print("\tloss:  {0:.3f} %    ({1:.3f})".format(pingLoss, pingLossStd))
        
    nb_smooth1 = 200 * (np.argmax(hourList_)+1) / hourList_.shape[0]
    x_smooth1 = np.linspace(hourList_[0], hourList_.max(), nb_smooth1)
    x_smooth2 = np.linspace(hourList_.min(), hourList_[-1], 200-nb_smooth1)    
    x_smooth = np.concatenate((x_smooth1, x_smooth2))
    
    x_smooth = np.linspace(0, hourList_.shape[0], 200)
    
    plt.figure(0)    
    for key in keys:
        y_smooth = spline(np.arange(hourList_.shape[0]), downloadRes[key][hourListInd], x_smooth)
        plt.plot(x_smooth, y_smooth, linewidth=2, label='{0}'.format(key))
    
    plt.xlabel("Hour in one day")  
    plt.ylabel("Download Speed (KB/s)")      
    plt.legend()
    
    plt.figure(1)    
    for key in keys:
        #y_smooth = spline(np.arange(hourList_.shape[0]), downloadRes[key][hourList_], x_smooth)
        plt.plot(hourListInd, downloadRes[key][hourListInd], linewidth=2, label='{0}'.format(key))
    
    plt.xlabel("Hour in one day")  
    plt.ylabel("Download Speed (KB/s)")      
    plt.legend()
    
    plt.show()
    
    #plt.figure(1)    
    #for key in keys:
        #y_smooth = spline(np.arange(24), pingRes[key][:, 0], x_smooth)
        #plt.plot(x_smooth, y_smooth, linewidth=2, label='{0}'.format(key))
    
    #plt.xlabel("Hour in one day")  
    #plt.ylabel("Avg ping respond time (ms)")      
    #plt.legend()
    
    #plt.figure(2)    
    #for key in keys:
        #y_smooth = spline(np.arange(24), pingRes[key][:, 1], x_smooth)
        #plt.plot(x_smooth, y_smooth, linewidth=2, label='{0}'.format(key))
    
    #plt.xlabel("Hour in one day")  
    #plt.ylabel("Pack loss percentage")      
    #plt.legend()
    