#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

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
                    pingLoss = np.array([loss,  hour])
                    pingLossRes[server] = np.vstack((pingLossRes[server], pingLoss))
                else:
                    pingTimeRes[server] = np.array([avg,  hour])
                    pingLossRes[server] = np.array([loss, hour])
    
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
    
    return downloadRes, np.array(hourList)

def DisplayResults():
    pingTimeRes, pingLossRes = ReadPingResults('result_ping.txt')
    downloadRes, hourList = ReadDownloadResults('result_download.txt')
    
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
    
    fig = plt.figure()
    # define box colors
    colors = ['lavender', 'goldenrod', 'steelblue', 'lightgreen', 'pink', 'seashell',
              'cyan', 'lightblue', 'lightcoral', 'lightyellow', 'pink', 'moccasin']
    ax = plt.subplot(211)
    data = []
    xtickList = []
    for key in keys:
        data.append( downloadRes[key][:, 0] )
        xtickList.append(key)
    box = plt.boxplot(data,patch_artist=True)
    
    # plot boxplot for download speed
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    plt.xticks(range(1, len(xtickList)+1), xtickList)
    plt.xlabel("Servers", fontsize=14)  
    plt.ylabel("Download Speed (KB/s)", fontsize=14)
    ax.set_title("Download Speed", fontsize=18)
    
    # plot boxplot for ping response time
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
    
    # plot boxplot for ping loss percentage
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

if __name__ == '__main__':
    DisplayResults()
    