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
    with open(filename, 'r') as f:
        for line in f:
            if line[0:4] == '====' or line == '\n':
                continue
            elif line[0:6] == 'Tested':
                tempLine = line.split()
                hour = int(tempLine[2].split(':')[0])
            else:
                server = line[0:4]
                tempLine = line[6:].strip()
                speed = float(tempLine) # KB/s
                
                if downloadRes.has_key(server):
                    downloadRes[server][hour, 0] = speed
                else:
                    downloadRes[server] = np.zeros((24, 1))
                    downloadRes[server][hour, 0] = speed
    return downloadRes

if __name__ == '__main__':
    pingRes = ReadPingResults('result_ping.txt')
    downloadRes = ReadDownloadResults('result_download.txt')
    keys = ['nyc1', 'nyc2', 'nyc3', 'ams2', 'ams3', 'sfo1', 'sfo2', 
            'sgp1', 'lon1', 'fra1', 'tor1', 'blr1']
    
    x_smooth = np.linspace(0, 23, 200)
    
    plt.figure(0)    
    for key in keys:
        y_smooth = spline(np.arange(24), downloadRes[key], x_smooth)
        plt.plot(x_smooth, y_smooth, linewidth=2, label='{0}'.format(key))
    
    plt.xlabel("Hour in one day")  
    plt.ylabel("Download Speed (KB/s)")      
    plt.legend()
    
    
    plt.figure(1)    
    for key in keys:
        y_smooth = spline(np.arange(24), pingRes[key][:, 0], x_smooth)
        plt.plot(x_smooth, y_smooth, linewidth=2, label='{0}'.format(key))
    
    plt.xlabel("Hour in one day")  
    plt.ylabel("Avg ping respond time (ms)")      
    plt.legend()
    
    plt.figure(2)    
    for key in keys:
        y_smooth = spline(np.arange(24), pingRes[key][:, 1], x_smooth)
        plt.plot(x_smooth, y_smooth, linewidth=2, label='{0}'.format(key))
    
    plt.xlabel("Hour in one day")  
    plt.ylabel("Pack loss percentage")      
    plt.legend()
    
    plt.show()