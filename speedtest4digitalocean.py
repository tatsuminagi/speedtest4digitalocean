#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import shutil
import time
import requests
import multiprocessing
from datetime import datetime, timedelta
#from threading import Timer

MaxTime = 120  # maximum download time, NO BIGGER THAN 120 SECS!!!
hourRecorder = set()
secondDiff = 3600

# core code for testing download speed
def downloadFile(url, queue, directory='.') :
    start = time.time()
    queue.put(0)

    dlTotal = 0    
    localFilename = url.split('/')[-1]
    retryCount = 0
    while retryCount <= 3:
        while True:
            try:
                s = requests.Session()
                s.mount(url, requests.adapters.HTTPAdapter(max_retries=5))
                r = s.get(url, stream=True, timeout=10)
                break
            except Exception as e:
                if repr(e).split('(')[0] == 'HTTPError':
                    print('HTTP Error, please check your server.lst')
                    return
                continue
        total_length = int(r.headers.get('content-length'))
        try:
            dl = 0
            with open(directory + '/' + localFilename, 'wb') as f:
                if total_length is None: # no content length header
                    f.write(r.content)
                else:
                    for chunk in r.iter_content(1024):
                        dlTotal += len(chunk)
                        dl += len(chunk)
                        f.write(chunk)
                        done = int(50 * dl / total_length)
                        currentSpeed = dlTotal/(time.time() - start)/1024
                        print("\r[{0}{1}] {2:.2f} KB/s".format('='*done,
                                                               ' '*(50-done),
                                                               currentSpeed)),
                        sys.stdout.flush()
                        # update current speed                
                        if queue.qsize():
                            _ = queue.get()
                        queue.put(currentSpeed)
            break
        except requests.exceptions.ConnectionError:
            os.remove(directory + '/' + localFilename)
            retryCount += 1
            print("\nConnection broken, retry times: {}".format(retryCount))
    if retryCount > 3:
        print("Max retry times reached, download failed")
        
    print("")
    print("Download completed, elapsed time: {}".format(time.time() - start))
    
def ReadURLs(filename):
    urls = []
    with open(filename, 'r') as f:
        for line in f:
            urls.append(line.strip())
    return urls

def main(run_at):
    urls = ReadURLs('servers.lst')
    result = {}
    for url in urls:
        serverName = url[17:21]
        localFilename = url.split('/')[-1]
        directory = '.'
        # Start downloadFile as a process
        q = multiprocessing.Queue()
        print("_" * 80)
        print("Testing {}\n".format(serverName))
        p = multiprocessing.Process(target=downloadFile, name="Download", args=(url, q))
        p.start()
    
        # Wait a maximum of X seconds for downloading
        p.join(MaxTime)
        result[serverName] = q.get()    
        print("")
        if p.is_alive():
            print("Maximum of {0} seconds exceeded.".format(MaxTime))
            # Terminate process
            p.terminate()
            p.join()
            
        print("\tcleaning up...")
        try:
            os.remove(directory + '/' + localFilename)
        except:
            pass
        resultFilename = "result.txt".format(
                                             time.strftime('%Y_%m_%d_%H_%M',time.localtime(time.time()))
                                            )
    with open(resultFilename, 'a') as f:
        f.write("=" * 60)
        f.write("\n")
        f.write("Tested at {0}\n".format(run_at.strftime('%H:%M:%S on %d %b %Y')))
        for key in sorted(result.keys()):
            f.write("{0}: {1}\n".format(key, result[key]))
        f.write("\n")
        
def CountDown(secondsLeft, run_at):
    t0 = time.time()
    print("=" * 80)
    while secondsLeft - (time.time() - t0) >= 1:
        m, s = divmod(int(secondsLeft - (time.time() - t0)), 60)
        if m == 0:
            print("\r{0} sec left until the next run...".format(s)),
        else:
            print("\r{0} min {1} sec left until the next run...".format(m, s)),
        sys.stdout.flush()
        time.sleep(1)
    print("")
    print("=" * 80)
    print("\n")
    while True:
        if secondsLeft - (time.time() - t0) <= 0:
            main(run_at)

def RunAtEveryHour(lastTime, secondDiff):
    # start the first run immediately
    if not hourRecorder:
        now = datetime.now()        
        hourRecorder.add(now.hour)
        main(now)
        RunAtEveryHour(now, secondDiff=secondDiff)
    else:
        y = lastTime + timedelta(seconds=secondDiff)
        run_at = y.replace(day=y.day, hour=y.hour, minute=y.minute, second=y.second, microsecond=y.microsecond)    
        while True:
            # no need to test at sleeping hours... (2:30am-7:00am)
            if run_at.hour in {3, 4, 5, 6, 7} or \
               (run_at.hour == 2 and run_at.minute >= 30):
                run_at += timedelta(seconds=secondDiff)
            else:
                break
            
        delay = (run_at - datetime.now()).total_seconds()
        
        #t = Timer(delay, CountDown, [delay, run_at])
        
        #t.start()
        #while True:
            #if not t.isAlive():
                #if run_at.hour not in hourRecorder:
                    #hourRecorder.add(run_at.hour)
                    #RunAtEveryHour(now, secondDiff=secondDiff)
                #else:
                    #t.cancel()
                    #return
        if run_at.hour not in hourRecorder:
            hourRecorder.add(run_at.hour)
            CountDown(delay, run_at)
            RunAtEveryHour(run_at, secondDiff=secondDiff)
        else: 
            return
    
if __name__ == '__main__':
    RunAtEveryHour(0, secondDiff=secondDiff)
