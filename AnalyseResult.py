#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline

def ReadPingResults(filename):
    pingTimeRes = {}
    pingLossRes = {}
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
                
                if pingTimeRes.has_key(server):
                    pingTime = np.array([avg,  hour])
                    pingTimeRes[server] = np.vstack((pingTimeRes[server], pingTime))
                    pingLoss = np.array([avg,  hour])
                    pingLossRes[server] = np.vstack((pingLossRes[server], pingLoss))
                else:
                    pingTimeRes[server] = np.array([avg,  hour])
                    pingLossRes[server] = np.array([loss, hour])
    #for key in pingTimeRes.iterkeys():
        #pingTimeRes[key] = np.array(pingTimeRes)
        #pingLossRes[key] = np.array(pingLossRes)
    return pingTimeRes, pingLossRes

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
                    download = np.array([speed, hour])
                    downloadRes[server] = np.vstack((downloadRes[server], download))
                else:
                    downloadRes[server] = np.array([speed, hour])
    #for key in downloadRes.iterkeys():
        #downloadRes[key] = np.array(downloadRes)
    return downloadRes, np.array(hourList)

if __name__ == '__main__':
    pingTimeRes, pingLossRes = ReadPingResults('result_ping.txt')
    downloadRes, hourList = ReadDownloadResults('result_download.txt')
    
    #hourList_ = np.zeros((hourList.shape), dtype=np.int)
    #hourListInd = np.zeros((hourList.shape), dtype=np.int)
    #for i in range(2, hourList.shape[0]):
        #if abs(hourList[-i] - hourList[-i+1]) != 1 and hourList[-i] != 23:
            #hourList_[0:i-1] = hourList[-i+1:]
            #hourListInd = range(hourList.shape[0]-i+1, hourList.shape[0])
            #hourList_[i-1:] = hourList[:-i+1]
            #hourListInd += range(0, hourList.shape[0]-i+1)
    #hourListInd = np.array(hourListInd)
    
    keys = ['nyc1', 'nyc2', 'nyc3', 'ams2', 'ams3', 'sfo1', 'sfo2', 
            'sgp1', 'lon1', 'fra1', 'tor1', 'blr1']
    
    for key in keys:
        speed = np.mean(downloadRes[key][:, 0])
        speedStd = np.std(downloadRes[key][:, 0])
        pingTime = np.mean(pingTimeRes[key][:, 0])
        pingTimeStd = np.std(pingTimeRes[key][:, 0])
        pingLoss = np.mean(pingLossRes[key][:, 0])
        pingLossStd = np.std(pingLossRes[key][:, 0])
        print("_" * 80)
        print("{0}".format(key))
        print("\tspeed: {0:.3f} KB/s ({1:.3f})".format(speed, speedStd))
        print("\tping:  {0:.3f} ms   ({1:.3f})".format(pingTime, pingTimeStd))
        print("\tloss:  {0:.3f} %    ({1:.3f})".format(pingLoss, pingLossStd))
        
    #nb_smooth1 = 200 * (np.argmax(hourList_)+1) / hourList_.shape[0]
    #x_smooth1 = np.linspace(hourList_[0], hourList_.max(), nb_smooth1)
    #x_smooth2 = np.linspace(hourList_.min(), hourList_[-1], 200-nb_smooth1)    
    #x_smooth = np.concatenate((x_smooth1, x_smooth2))
    
    #x_smooth = np.linspace(0, hourList_.shape[0], 200)
    
    fig = plt.figure()
    ax = plt.subplot(211)
    data = []
    xtickList = []
    for key in keys:
        data.append( downloadRes[key][:, 0] )
        xtickList.append(key)
    box = plt.boxplot(data,patch_artist=True)

    colors = ['lavender', 'goldenrod', 'steelblue', 'lightgreen', 'pink', 'seashell',
              'cyan', 'lightblue', 'lightcoral', 'lightyellow', 'pink', 'moccasin']
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    plt.xticks(range(1, len(xtickList)+1), xtickList)
    plt.xlabel("Servers", fontsize=14)  
    plt.ylabel("Download Speed (KB/s)", fontsize=14)
    ax.set_title("Download Speed", fontsize=18)
    
    ax = plt.subplot(223)
    data = []
    xtickList = []
    for key in keys:
        data.append( pingTimeRes[key][:, 0] )
        xtickList.append(key)
    box = plt.boxplot(data,patch_artist=True)

    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    plt.xticks(range(1, len(xtickList)+1), xtickList)
    plt.xlabel("Servers", fontsize=14)  
    plt.ylabel("Ping time (ms)", fontsize=14)
    ax.set_title("Ping Time", fontsize=18)
        
    ax = plt.subplot(224)
    data = []
    xtickList = []
    for key in keys:
        data.append( pingLossRes[key][:, 0] )
        xtickList.append(key)
    box = plt.boxplot(data,patch_artist=True)

    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    plt.xticks(range(1, len(xtickList)+1), xtickList)
    plt.xlabel("Servers", fontsize=14)  
    plt.ylabel("Ping loss (%)", fontsize=14)
    ax.set_title("Ping Loss", fontsize=18)
        
    fig.tight_layout()
    
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
    