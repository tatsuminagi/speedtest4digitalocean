#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import shutil
import time
import requests
import multiprocessing
import subprocess
import platform
from datetime import datetime, timedelta
from AnalyseResult import DisplayResults

MaxTime = 120           # maximum download testing time (secs)
secondDiff = 3600       # interval length between test runs (secs)
noPings = 20            # No. of pings for each test server
noRuns = 20             # Note that runs between 2:30-6:60 will be skipped, so noRuns
                        # defines runs for a whole day (24 - 4 = 20)
plotWhenCompletd = True # if you want to display the results when the runs complete
if secondDiff == 0:
    noRuns = 99999999
###################################################################################
# All tests in each turn should be able to complete in secondDiff (secs), 
# otherwise there would be no waiting intervals between test runs.
# For example, secondDiff=3600 defines the difference of the begining time of 
# the current run and the next. There are currently 12 test servers, so each run
# would take (MaxTime * 12) plus (20 ping times * 12) and this should be within
# secondDiff.
# Alternatively, you can set secondDiff to 0, so the next run would start right after
# the previous finishes.
###################################################################################

# global variable
runCount = 0

    
def ReadURLs(filename):
    urls = []
    with open(filename, 'r') as f:
        for line in f:
            urls.append(line.strip())
    return urls

# core code for testing download speed
def downloadFile(url, queue, directory='.') :
    start = time.time()
    queue.put(0)

    dlTotal = 0    
    localFilename = url.split('/')[-1]
    retryCount = 0
    while retryCount < 3:
        try:
            s = requests.Session()
            s.mount(url, requests.adapters.HTTPAdapter(max_retries=5))
            r = s.get(url, stream=True, timeout=5)
        except Exception as e:
            if repr(e).split('(')[0] == 'HTTPError':
                print('HTTP Error, please check your server.lst')
                return
            else:
                retryCount += 1
                print("Connection broken, retry times: {}".format(retryCount))
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
                        if not queue.empty():
                            _ = queue.get()
                        queue.put(currentSpeed)
            break
        except requests.exceptions.ConnectionError:
            os.remove(directory + '/' + localFilename)
            retryCount += 1
            print("\nConnection broken, retry times: {}".format(retryCount))
    if retryCount > 3:
        print("Max retry times reached, download failed")
        return
        
    print("")
    print("Download completed, elapsed time: {}".format(time.time() - start))
    return
    
def PingTest(url, noPings):
    call = ['ping', '-c', str(noPings), url]
    s = subprocess.Popen(' '.join(call), shell=True, stdout=subprocess.PIPE)
    out = ''
    returncode = s.poll()
    while True:
        line = s.stdout.readline()
        if line == '':
            break
        out += line
        line = line.strip()
        print line
    
    print('_' * 80)
    
    out = out.split()
    loss = out[ out.index('packet')-1 ]
    # check if all ping lost
    if loss == '100%':
        return None, noPings
    if platform.system() == 'Linux':
        avg = float( out[ out.index('min/avg/max/mdev')+2 ].split('/')[1] )
    else:
        avg = float( out[ out.index('min/avg/max/stddev')+2 ].split('/')[1] )
    loss = int( round(float(loss[:-1]) / 100 * noPings) )
    return avg, loss

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
        if p.is_alive():
            print("")
            print("Maximum of {0} seconds exceeded.".format(MaxTime))
            # Terminate process
            p.terminate()
            p.join()
            
        print("\tcleaning up...")
        try:
            os.remove(directory + '/' + localFilename)
        except:
            pass
        
    resultFilename  = "result_download.txt"
    resultFilename2 = "result_ping.txt"
    with open(resultFilename, 'a') as f:
        f.write("=" * 60)
        f.write("\n")
        f.write("Tested at {0}\n".format(run_at.strftime('%H:%M:%S on %d %b %Y')))
        for key in sorted(result.keys()):
            f.write("{0}: {1:.3f}\n".format(key, result[key]))
        f.write("\n")
        
    print("")
    print("=" * 80)
    print("")
    print("Ping test")
    print("_" * 80)
    
   
    with open(resultFilename2, 'a') as f:
        f.write("=" * 60)
        f.write("\n")
        f.write("Tested at {0}\n".format(run_at.strftime('%H:%M:%S on %d %b %Y')))
        for url in urls:
            serverName = url[17:21]
            urlPing = url[7:].split('/')[0]
            avg, loss = PingTest(urlPing, noPings)
            if avg == None:
                avg = -1
            f.write("{0}: avg={1:>7.3f}, loss={2:>2}/{3}\n".format(serverName, avg, loss, noPings))
        f.write("\n")
        
    return
        
def CountDown(secondsLeft, run_at):
    t0 = time.time()
    print("=" * 80)
    while secondsLeft - (time.time() - t0) >= 1:
        m, s = divmod(int(secondsLeft - (time.time() - t0)), 60)
        if m == 0:
            print("\r{0} sec left until the next run...{1:<10}".format(s, " ")),
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
            break
    return

def RunAtEveryHour(lastTime, secondDiff=3600):
    # start the first run immediately
    global runCount
    if runCount == 0:
        now = datetime.now()
        runCount += 1
        main(now)
        RunAtEveryHour(now, secondDiff=secondDiff)
    else:
        run_at = lastTime + timedelta(seconds=secondDiff)
        if run_at < datetime.now():
            run_at = datetime.now()
            
        while True:
            # no need to test at sleeping hours... (2:30am-6:30am)
            if run_at.hour in {3, 4, 5} or \
               (run_at.hour == 2 and run_at.minute >= 30) or\
               (run_at.hour == 6 and run_at.minute < 30):
                if secondDiff == 0:
                    run_at = run_at.replace(hour = 6, minute = 30, second = 0, microsecond = 0)
                    break
                else:
                    run_at += timedelta(seconds=secondDiff)
            else:
                break
            
        delay = (run_at - datetime.now()).total_seconds()
        
        if runCount < noRuns:
            runCount += 1
            CountDown(delay, run_at)
            RunAtEveryHour(run_at, secondDiff=secondDiff)
        else: 
            return
    
if __name__ == '__main__':
    RunAtEveryHour(0, secondDiff=secondDiff)
    if plotWhenCompletd:
        DisplayResults()