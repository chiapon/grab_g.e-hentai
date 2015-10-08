# grab_g.e-hentai
A light-weight python script to grab galleris from g.e-hentai.org
+ Running with Python version 2.7 and supporting the platform of Windows, Linux, and Mac
+ Light-weight script written by using build-in python modules
+ Multi-threaded
+ Various of commandline options
+ Batch downloading for multiple galleries

###Usage
For help, just run the script without arguements in the console.
```text
chiapon$ python grab_g.e-hentai.py
Usage: grab_g.e-hentai.py [Options] url1 [url2] [url#]]
Version: 1.2

Options:
  -h, --help            show this help message and exit
  -l LIST, --list=LIST  Import an url list file and ignore the urls in the
                        command line
  -o OUTPUT, --output=OUTPUT
                        Specify the folder to save files. If multiple urls are
                        given, -o will be ignore
  -r RETRY, --retry=RETRY
                        Times to internally retry to download failed images
                        (default=5)
  -t THREADS, --thread=THREADS
                        Specify maximum thread number (default=5)
  -v, --verbose         Enable verbose mode
  ```
  
####Download one gallery
```text
chiapon$ python grab_g.e-hentai.py http://g.e-hentai.org/g/854706/b9e6411ce3/

Gallery Name: THE COCKROACH - EPISODE 1
 Output path: /Users/chiapon/Documents/THE COCKROACH - EPISODE 1
 Total pages: 1
Total images: 31
Downloading [############################################................... 22/31] 70%
```

####Download multile galleries
```text
alexcp-lins-mbp:temp Alex_Lin$ python grab_g.e-hentai.py http://g.e-hentai.org/g/854725/b07d8cc37f/ http://g.e-hentai.org/g/854726/3477d20a85/

Gallery Name: THE COCKROACH - EPISODE 2
 Output path: /Users/chiapon/Documents/THE COCKROACH - EPISODE 2
 Total pages: 1
Total images: 36
Completed   [############################################################## 36/36] 100%

Gallery Name: THE COCKROACH - EPISODE 3
 Output path: /Users/chiapon/Documents/THE COCKROACH - EPISODE 3
 Total pages: 1
Total images: 37
Downloading [#######################........................................ 14/37] 37%
```

You can speicfy a text file (ex., urllist.txt) in which saves gallery urls in lines to batch download the galleries.
```text
chiapon$ cat urllist.txt
http://g.e-hentai.org/g/854706/b9e6411ce3/
http://g.e-hentai.org/g/854725/b07d8cc37f/

chiapon$ python grab_g.e-hentai.py -l urllist.txt
```
####Failures
When some pictures were failed to be downloaded due to some reasons (ex., internal server error), the failed pages will be listed in a file under the output folder.
```text
chiapon$ python grab_g.e-hentai.py http://g.e-hentai.org/g/829865/94f7529ecf/

Gallery Name: Tales of Pleasure - 2014-2015 (3D)
 Output path: /Users/chiapon/Documents/Tales of Pleasure - 2014-2015 (3D)
 Total pages: 11
Total images: 421
Completed   [############################################################. 419/421] 99%
There were still 2 pages failed to be retrieved.
The failed pages are listed in "/Users/chiapon/Documents/Tales of Pleasure - 2014-2015 (3D)/failures.txt"
```



