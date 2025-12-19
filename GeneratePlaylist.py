import os, sys, re
from os import path
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.aac import AAC
from mutagen.wavpack import WavPack
from mutagen.oggvorbis import OggVorbis
from mutagen.aiff import AIFF
from mutagen.mp4 import MP4

class playlist(object):
    def __init__(self,directory=None,exclude=[],formatOrder=None,relative=False):
        #check if directory is none or emptystring, if it is
        #open file dialog
        if directory == None or "":
            from tkinter import filedialog
            directory = filedialog.askdirectory()
        self.directory = directory.replace('/',path.sep)
        self.formatOrder = formatOrder
        self.exclude = exclude
        self.music = []
        self.savepath = path.join(self.directory,'playlist.m3u')
        self.relative = relative
    def findmusic(self):
        if self.formatOrder != None:
            for frmt in self.formatOrder:
                if frmt[0] != '.':
                    self.formatOrder[self.formatOrder.index(frmt)]='.'+frmt
                self.formatOrder[self.formatOrder.index(frmt)]=frmt.lower()
        for (dirpath, dirnames, filenames) in os.walk(self.directory):
            if any([i.lower() in dirpath.lower() for i in self.exclude]):
                #i.lower() in self.exclude for i in dirpath):
                continue
            for file in filenames:
                musicobj = MusicObject(file,dirpath,self.formatOrder)
                try:
                    musicobj.getOptimalFormat()
                    if not musicobj in self.music:
                        self.music.append(musicobj)
                except IOError:
                    continue
        return self.music
    def print(self):
        for song in self.music:
            print(song.file)
        
    def save(self):
        if path.exists(self.savepath):
            os.remove(self.savepath)
        playlistFile = open(self.savepath,'w')
        playlistFile.write('#EXTM3U\n')
        for musicobj in self.music:
            try:
                playlistFile.write('#EXTINF:'
                                   +str(int(round(musicobj.audio.info.length)))
                                   +','
                                   +musicobj.title
                                   +'\n')
                playlistFile.write(str(musicobj.optimalFormat)+'\n')
            except Exception as e:
                print(e)
                print(musicobj.optimalFormat)
                continue
        playlistFile.close()
        
class MusicObject(object):
    def __init__(self,file,directory,formatOrder):
        #MusicObject object (say that 10 times fast)
        #self.name = filesplit[0].lower()
        self.parentDirectory = path.split(directory)[1].lower()
        self.file = file
        self.directory = directory
        self.formatOrder = formatOrder
        self.audioFormat = {'.mp3' : MP3,
                            '.aac' : AAC,
                            '.wav' : WavPack,
                            '.mp4' : MP4,
                            '.m4a' : MP4,
                            '.flac': FLAC,
                            '.aiff': AIFF,
                            '.ogg' : OggVorbis
                            }
        #self.audio =
    def __eq__(self, other): #I should add self.title to speed this up
        try:
            return (self.optimalFormat == other.optimalFormat
                    or
                    self.file == other.file
                    or
                    (self.title
                     ==
                     other.title
                     )
                    )
        except:
            return (self.optimalFormat == other.optimalFormat
                    or
                    self.file == other.file
                    )
    def __ne__(self, other):
        return (self.optimalFormat != other.optimalFormat
                or
                self.file != other.file
                or
                (self.title
                 !=
                 other.title
                 )
                )
    def __len__(self):
        return len(self.file)
    def getOptimalFormat(self):
        self.optimalFormat = MusicPaths(self.file,self.directory,self.formatOrder).getOptimalFormat()
        filesplit = path.split(self.optimalFormat)
        self.file = filesplit[1]
        self.directory = filesplit[0]
        try:
            self.audio = self.audioFormat[
                path.splitext(self.optimalFormat)[1]
                ](self.optimalFormat)
            self.title = self.audio.get('title',path.splitext(self.file))[0]
            return self.optimalFormat
        except:
            print("Error in file: ")
            print(self.file)
            self.optimalFormat = MusicPaths(self.file,self.directory,self.formatOrder).getOptimalFormat(path.splitext(self.file)[1].replace('.',''))
            filesplit = path.split(self.optimalFormat)
            self.file = filesplit[1]
            self.directory = filesplit[0]
        try:
            self.audio = self.audioFormat[
                path.splitext(self.optimalFormat)[1]
                ](self.optimalFormat)
            self.title = self.audio.get('title',path.splitext(self.file))[0]
            return self.optimalFormat
        except:
            print("Skipping File, Error irrecoverable")
            None#continue
class MusicPaths(object):
    def __init__(self, file,directory,formatOrder):
        noext = path.join(directory,file)
        noext = path.splitext(noext)[0]
        self.original = file
        self.directory = directory
        self.formatOrder = formatOrder
        #Pre-initialize the strings
        self.mp3 = noext + '.mp3'
        self.aac = noext + '.aac'
        self.wav = noext + '.wav'
        self.mp4 = noext + '.mp4'
        self.m4a = noext + '.m4a'
        self.flac = noext + '.flac'
        self.aiff = noext + '.aiff'
        self.vorbis = noext + '.ogg'
        self.audioFormat = {'.mp3'  : self.mp3,
                            '.aac'  : self.aac,
                            '.wav'  : self.wav,
                            '.mp4'  : self.mp4,
                            '.m4a'  : self.m4a,
                            '.flac' : self.flac,
                            '.aiff' : self.aiff,
                            '.ogg'  : self.vorbis}
        
    def getOptimalFormat(self, __skip__ = []):
        #Sometimes there's multiple versions...
        #E.G. [a.mp3, a(1).mp3, a.flac]
        #we don't want to end up w/ [a.flac, a(1).mp3], so make sure that doesn't happen
        rgx = re.search('\\s?[(][0-9]+[)]', self.original)
        if __skip__ != []:
            skip = (i.lower()for i in __skip__)
        if rgx != None:
            noncopyPath = path.join(self.directory,(self.original).replace(rgx.group(0),''))
            noncopyPath = noncopyPath
            if path.exists(noncopyPath):
                self = MusicPaths(self.original,self.directory,self.formatOrder)
        if self.formatOrder != None:
            for frmt in self.formatOrder:
                if path.exists(self.audioFormat[frmt]) and frmt not in __skip__:
                    return self.audioFormat[frmt]
        else:
            if path.exists(self.flac) and "flac" not in __skip__:
                return self.flac
            elif path.exists(self.aiff) and "aiff" not in __skip__:
                return self.aiff
            elif path.exists(self.wav) and "wav" not in __skip__:
                return self.wav
            elif path.exists(self.vorbis) and "vorbis" not in __skip__:
                return self.vorbis
            elif path.exists(self.mp3) and "mp3" not in __skip__:
                return self.mp3
            elif path.exists(self.aac) and "aac" not in __skip__:
                return self.aac
            elif path.exists(self.mp4) and "mp4" not in __skip__:
                return self.mp4
            elif path.exists(self.m4a) and "m4a" not in __skip__:
                return self.mp4
            else:
                raise IOError
#path.join(f[0]+'/',f[2][1])


#from GeneratePlaylist import playlist
'''





from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

from os import walk

f = []
for (dirpath, dirnames, filenames) in walk(mypath):
    f.extend(filenames)
    break
'''
 
