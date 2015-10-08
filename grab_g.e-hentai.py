#!/usr/bin/env python
 
import logging
import optparse
import os
import platform
import Queue
import random
import re
import subprocess
import sys
import threading
import time
import types
import urllib2
 
VERSION = '1.2.1'
EXIT_FLAG = False
PROG_FLAG = False
OUTPUT_FOLDER = ''
TOTAL = '0'
failed = []
 
 
class WorkerThread(threading.Thread):
  def __init__(self, tid, workQueue, counter):
    threading.Thread.__init__(self)
    self.tid = tid
    self.queue = workQueue
    self.counter = counter
    self.daemon = True
 
  def run(self):
    prefix = '[T%s] '%self.tid
    logging.debug(prefix+"Starting new a theread T%s" % self.tid)
    headers = {"User-Agent":"Mozilla/4.0 (compatible; MSIE 5.5;Windows NT)"}
    while not EXIT_FLAG:
      if not self.queue.empty():
        pageurl = self.queue.get()
        logging.debug(prefix+'Retrieving image in %s' % pageurl)
        try:
          resp = urllib2.urlopen(pageurl)
          cookie = resp.headers.get('Set-Cookie')
          html = resp.read()
 
          p = re.compile('<img id="img" src="(http://[a-zA-Z0-9\-\.]+:?\d*/[a-zA-Z0-9\-\./=_]+\.(jpg|png))" style=')
          m = p.search(html)
          if m:
            img = m.group(1)
            logging.debug(prefix+'Downloading ' + img)
            req = urllib2.Request(img)
            req.add_header('cookie', cookie)
           
            resp = urllib2.urlopen(req)
 
            if 'image/gif' == resp.headers.get('Content-Type'):
              logging.error(prefix+'Internal server error. Will retry later...')
              failed.append(pageurl)
            else:
              filename = img.split('/')[-1]
              p = re.compile('<span>(\d+)</span> / <span>(\d+)</span>')
              m = p.search(html)
              if m and TOTAL!='0': filename = m.group(1).zfill(len(TOTAL)) + os.path.splitext(filename)[-1]
 
              f = open("%s/%s"%(OUTPUT_FOLDER, filename),'wb')
              f.write(resp.read())
              f.close()
              logging.debug(prefix+'Image saved at %s'%("%s/%s"%(OUTPUT_FOLDER, filename)))
              counter.increase()
          else:
            logging.error('Cannot find the image URL. Will try it later...')
            failed.append(pageurl)
        except Exception as ex:
          logging.error(prefix+'There was an error: %s. Will retry this page later...' % ex)
          failed.append(pageurl)
      time.sleep(1)
    logging.debug(prefix+"Exiting thread T%s" % self.tid)
 
class ProgressThread(threading.Thread):
  def __init__(self, counter):
    threading.Thread.__init__(self)
    self.counter = counter
    self.daemon = True
 
  def run(self):
    r = int(TOTAL)
    columns = 80
    if 'Windows' == platform.system():
      con = os.popen('mode con', 'r').read()
      match = re.compile('Columns:\s+(\d+)').search(con)
      if match: columns = int(match.group(1)) - 1
    else:
      rows, columns = os.popen('stty size', 'r').read().split()
      columns = int(columns) - 1
    d = 'Downloading ['
    c = 'Completed   ['
    percent = ''
    bar = ''
 
    i = self.counter.count()
    while not PROG_FLAG and i < r:
      i = self.counter.count()
      percent = ' %d/%d] %d%%' % (i, r, round(i*100/r))
      bar_size = columns -len(d) - len(percent)
      bar = ('#'*int(bar_size*round(i*100/r)/100)).ljust(bar_size, '.')
      sys.stdout.write('\r%s%s%s' % (d, bar, percent))
      sys.stdout.flush()
      time.sleep(0.2)
    sys.stdout.write('\r%s%s%s' % (c, bar, percent))
    print('')
 
def send_request(url):
  resp = urllib2.urlopen(url)
  return resp.read()
 
def parse_arguements(argv):
  return options, args
 
class Counter:
  def __init__(self, start=0, increment=1):
    self.start = start
    self.counter = start
    self.increment = increment
    self.lock = threading.RLock()
   
  def increase(self):
    self.lock.acquire()
    self.counter += self.increment
    self.lock.release()
 
  def count(self):
    return self.counter
 
  def reset(self):
    self.lock.acquire()
    self.counter = self.start
    self.lock.release()
 
 
if __name__=='__main__':
  logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-6s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=__file__+'.log',
                    filemode='w')
  logging.debug('Start __main__')
 
  usage = "Usage: %s [Options] url1 [url2] [url#]]\nVersion: %s" % (os.path.basename(sys.argv[0]), VERSION)
  parser = optparse.OptionParser(usage=usage)
  parser.add_option("-l", "--list", dest="list",
                    help="Import an url list file and ignore the urls in the command line")
  parser.add_option("-o", "--output", dest="output",
                    help="Specify the folder to save files. If multiple urls are given, -o will be ignore")
  parser.add_option("-r", "--retry", type="int", dest="retry",
                    help="Times to internally retry to download failed images (default=5)", default=5)
  parser.add_option("-t", "--thread", type="int", dest="threads",
                    help="Specify maximum thread number (default=5)", default=5)
  parser.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="Enable verbose mode")
 
  options, args = parser.parse_args(sys.argv)
  if not options.list and len(args) <= 1:
    parser.print_help()
    exit(1)
 
  threads = []
  workQueue = Queue.Queue()
  urls = []
  counter = Counter()
 
 
  if options.verbose:
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)-6s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
 
  if options.list:
    with open(options.list) as f: urls = f.readlines()
  else: urls = args[1:]
 
  if len(urls) > 1: options.output = None
 
  for url in urls:
    del failed[:]
    del threads[:]
    lastpage = 0
    logging.debug('Parsing %s'+url)
    resp = send_request(url)
 
    OUTPUT_FOLDER = options.output
    gallery = ''
    if not options.output:
      p = re.compile('<h1 id=".+">(.+)</h1><h1')
      m = p.search(resp)
      if m:
        gallery = m.group(1)
        OUTPUT_FOLDER = m.group(1)
    logging.info('Output folder: ' + OUTPUT_FOLDER)
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
 
    p = re.compile('<p class="gpc">Showing \d+ - \d+ of (\d+) images</p>')
    m = p.search(resp)
    if m:
      TOTAL = m.group(1)
      logging.info('Total images: ' + TOTAL)
 
    p = re.compile(url.strip('/')+'/\?p=(\d+)')
    found = p.findall(resp)
    if found:
      for f in found:
        if int(f) > lastpage: lastpage = int(f)
    logging.info('Total pages: %d' % lastpage)
 
    print('\nGallery Name: %s' % gallery)
    print(' Output path: %s' % os.path.abspath(OUTPUT_FOLDER))
    print(' Total pages: %d' % (lastpage+1))
    print('Total images: %s' % TOTAL)

    EXIT_FLAG = False
    for i in range(0, options.threads):
      t = WorkerThread(i, workQueue, counter)
      t.start()
      threads.append(t)
 
    if not options.verbose:
      PROG_FLAG = False
      t_progress = ProgressThread(counter)
      t_progress.start()
 
    i = 0
    while True:
      p = re.compile('http://g\.e-hentai\.org/s/[\d\w]+/[\d\w]+-\d+')
      found = p.findall(resp)
      if found:
        for f in found: workQueue.put(f)
      while not workQueue.empty():
        time.sleep(1)
        pass
 
      i = i + 1
      if i > lastpage: break
      nexturl = url+'?p=%s'%i
      resp = send_request(nexturl)
      logging.debug('Parsing %s'%nexturl)
    EXIT_FLAG = True
    for t in threads: t.join()
     
    retry = options.retry
    while len(failed) > 0 and retry > 0:
      logging.info("Failed page count: %s" % str(len(failed)))
      logging.info('Retry after 10 seconds...(attempt: %s)'%str(retry))
      time.sleep(10)
      del threads[:]
      EXIT_FLAG = False
      max_thread = options.threads
      if options.threads > len(failed):
        max_thread = len(failed)
      for i in range(0, max_thread):
        t = WorkerThread(i, workQueue, counter)
        t.start()
        threads.append(t)
      while len(failed) > 0:
        workQueue.put(failed.pop(0))
      while not workQueue.empty():
        time.sleep(1)
        pass
      retry = retry - 1
       
      EXIT_FLAG = True
      for t in threads: t.join()
       
      if not options.verbose:
        PROG_FLAG = True
        t_progress.join()
 
    counter.reset()

    if len(failed) > 0:
      print('There were still %s pages failed to be retrieved.' % str(len(failed)))
      txt = os.path.join(OUTPUT_FOLDER,'failures.txt')
      print('The failed pages are listed in "%s"' % os.path.abspath(txt))
      f = open(txt, 'w')
      for r in failed: f.write(r + '\n')
      f.close()
 
    logging.debug('Exit __main__')