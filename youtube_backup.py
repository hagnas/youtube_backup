# -*- coding: utf-8 -*-

"""
    Script that backs up all the Youtube-videos in a users favorites-list


    Requires youtube-dl to be installed. Use homebrew or follow instruction here: 
    http://bitbucket.org/rg3/youtube-dl/wiki/Home

    Please edit the "Settings"-section below before running the script.

    See http://www.github.com/hagnas/youtube_backup for more information and the latest version.

    -------

    Copyright (c) 2010, Henry Hagnäs <henry@hagnas.com>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * Neither the name of Henry Hagnäs nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

__author__ = "Henry Hagnäs <henry@hagnas.com>"
__copyright__ = "Henry Hagnäs"
__license__ = "BSD"

from xml.etree import cElementTree as ET
import urllib2
import os
import re
import copy
import shlex, subprocess

# Settings

# Edit User and download-directory info. Directory will NOT be automatically created.
USER = 'hagnas'
DIR = '/Users/hagge/Files/Online Data Backups/youtube/'
YT_DL = '/usr/local/bin/youtube-dl'
YT_OPT = '--quiet --ignore-errors --continue --max-quality=22 -a .favorites -o "%(stitle)s--%(id)s.%(ext)s"'
# quality 22 = 720p

def get_urls(startindex):
    """ Fetches the next 10 video-URL's from startindex of USER's favourites

     modified from example found here: http://stackoverflow.com/questions/1452144/simple-scraping-of-youtube-xml-to-get-a-python-list-of-videos
    """

    results = []
    data = urllib2.urlopen('http://gdata.youtube.com/feeds/api/users/{user}/favorites?max-results=10&start-index={startindex}'.format(user=USER, startindex=startindex))
    tree = ET.parse(data)
    ns = '{http://www.w3.org/2005/Atom}'
    for entry in tree.findall(ns + 'entry'):
        for link in entry.findall(ns + 'link'):
            if link.get('rel') == 'alternate':
                results.append(link.get('href'))

    return results

def get_all_urls():

    results = []
    result = ['dummy']
    startindex = 1
    while len(result)>0:
        result = get_urls(startindex)
        results = results + result
        startindex = startindex + 10

    return results

def get_video_ids():
    """ cleans up url_list and returns a list with only the Youtube-video id's"""

    url_list = get_all_urls()
    
    re_videoid = re.compile('watch\?v=(?P<videoid>.*?)&')
    
    videolist = {}

    for i in url_list:
        t = re_videoid.search(i)
        videolist[t.group('videoid')] = i
        
    return videolist

def check_for_existing():
    """ Checks the download-folder for existing videos with same id and removes from videolist """

    videolist = get_video_ids()

    filelist = os.listdir(DIR)


    for video in copy.deepcopy(videolist):
        for files in filelist:
            if re.search(video,files):
                del videolist[video]
    
    return videolist

def write_fav_file():
    """ writes a plain text-file called 'favorites' into DIR. One line per youtube-URL. 
        This is the format youtube-dl wants for batch-downloads.
        
        Returns the count on how many new videos have been written to the download-queue.
    """

    videolist = check_for_existing()

    try:
        os.chdir(DIR)
    except(OSError):
        print 'Could not open directory!'
        quit()

    stream = open('.favorites', 'w')
    
    for i in videolist:
        stream.write(videolist[i] + '\n')

    stream.close()

    return len(videolist)

def download_files():
    """ Uses subprocess to trigger a download using youtube-dl of the list created earlier. """
    

    os.chdir(DIR)
    args = shlex.split(YT_DL + ' ' + YT_OPT)

    p = subprocess.Popen(args)

    

def main():
    
    if write_fav_file()>0:
        download_files()
    

if __name__ == '__main__':
    main()
