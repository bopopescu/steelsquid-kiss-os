#!/usr/bin/python -OO


'''
Simple python interface for the omxplayer

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import threading
import steelsquid_utils
import os


def play(play_this, use_playlist=0):
    '''
    Play file
    '''    
    global play_thread
    try:
        play_thread.stop()
    except:
        pass
    steelsquid_utils.execute_system_command_blind(['sudo', 'steelsquid', 'omxplayer-kill'])
        
    play_thread = PlayThread(str(play_this), use_playlist)
    play_thread.start()


def stop():
    '''
    Stop play
    '''    
    global play_thread
    try:
        play_thread.stop()
    except:
        pass


def pause_toggle():
    '''
    Toggle pause
    '''    
    global play_thread
    try:
        play_thread.child.send(" ")
    except:
        pass


def audio_previous():
    '''
    Previous Audio
    '''    
    global play_thread
    try:
        play_thread.child.send("j")
    except:
        pass


def audio_next():
    '''
    Next Audio
    '''    
    global play_thread
    try:
        play_thread.child.send("k")
    except:
        pass


def sub_previous():
    '''
    Previous Subtitle stream
    '''    
    global play_thread
    try:
        play_thread.child.send("n")
    except:
        pass


def sub_next():
    '''
    Next Subtitle stream
    '''    
    global play_thread
    try:
        play_thread.child.send("m")
    except:
        pass


def sub_toggle():
    '''
    Toggle Subtitle stream
    '''    
    global play_thread
    try:
        play_thread.child.send("s")
    except:
        pass


def volume_decrease():
    '''
    Decrease Volume
    '''    
    global play_thread
    try:
        play_thread.child.send("-")
    except:
        pass


def volume_increase():
    '''
    Increase Volume
    '''    
    global play_thread
    try:
        play_thread.child.send("+")
    except:
        pass


def backward_short():
    '''
    Short backward
    '''    
    global play_thread
    try:
        play_thread.child.send("\027[D")
    except:
        pass


def forward_short():
    '''
    Short forward
    '''    
    global play_thread
    try:
        play_thread.child.send("\027[C")
    except:
        pass


def backward_long():
    '''
    Short backward
    '''    
    global play_thread
    try:
        play_thread.child.send("\x1B[B")
    except:
        pass


def forward_long():
    '''
    Short forward
    '''    
    global play_thread
    try:
        play_thread.child.send("\x1B[A")
    except:
        pass


def playlist_play(play_this):
    '''
    Play from playlist
    '''    
    play(play_this, 2)


def playlist_previous():
    '''
    Play prev from playlist
    '''    
    try:
        play_thread.previous()
    except:
        pass


def playlist_next():
    '''
    Play next from playlist
    '''    
    try:
        play_thread.next()
    except:
        pass
        
        
def playlist_list():
    '''
    Get playlist
    '''    
    return steelsquid_utils.get_list("playlist")


def playlist_clear():
    '''
    Clear playlist
    '''    
    steelsquid_utils.del_list("playlist")
        

def playlist_add(post):
    '''
    Add to playlist
    '''    
    steelsquid_utils.del_values_from_list("playlist", post)
    steelsquid_utils.add_to_list("playlist", post)


def playlist_remove(number):
    '''
    Remove from playlist
    '''    
    steelsquid_utils.del_from_list("playlist", int(number))


def playing():
    '''
    What is playing (None= nothing)
    '''    
    global play_thread
    try:
        if play_thread.isAlive():
            return play_thread.the_file
    except:
        pass
    return None


class PlayThread(threading.Thread):
    '''
    Thread that play the omx.
    '''

    __slots__ = ['child', 'the_file', 'use_playlist']
    
    def __init__(self, the_file, use_playlist):
        self.the_file = the_file
        self.child = None
        self.use_playlist = use_playlist
        threading.Thread.__init__(self)

    def run(self):
        '''
        Thread main method
        '''
        import pexpect
        import sys
        while self.the_file:
            cmd = "sudo nice --10 omxplayer -o both -b '%s'" % (self.the_file)
            try:
                self.child=pexpect.spawn(cmd)
                self.child.expect(pexpect.EOF, timeout=None)
                self.child.close()
            except Exception as ee:
                try:
                    child.close()
                except:
                    pass
            if self.use_playlist == 1:
                the_next = None
                try:
                    plist = steelsquid_utils.get_list("playlist")
                    found = False
                    for p in reversed(plist):
                        if p == self.the_file:
                            found = True;
                        elif found:
                            the_next = p;
                            break
                except:
                    pass
                if the_next == None:
                    self.the_file = None
                else:
                    self.use_playlist = 2
                    self.the_file = the_next
            elif self.use_playlist == 2:
                the_next = None
                try:
                    plist = steelsquid_utils.get_list("playlist")
                    found = False
                    for p in plist:
                        if p == self.the_file:
                            found = True;
                        elif found:
                            the_next = p;
                            break
                except:
                    pass
                if the_next == None:
                    self.the_file = None
                else:
                    self.the_file = the_next
            else:
                self.the_file = None
            

    def stop(self):
        '''
        Stop the thread
        '''
        self.use_playlist = 0
        try:
            self.child.send("q")
        except:
            pass
        try:
            self.join(0.5)
        except:
            pass
        steelsquid_utils.execute_system_command_blind(['sudo', 'steelsquid', 'omxplayer-kill'])


    def next(self):
        '''
        Stop the thread
        '''
        self.use_playlist = 2
        try:
            self.child.send("q")
        except:
            pass
        try:
            self.join(0.5)
        except:
            pass
        steelsquid_utils.execute_system_command_blind(['sudo', 'steelsquid', 'omxplayer-kill'])



    def previous(self):
        '''
        Stop the thread
        '''
        self.use_playlist = 1
        try:
            self.child.send("q")
        except:
            pass
        try:
            self.join(0.5)
        except:
            pass
        steelsquid_utils.execute_system_command_blind(['sudo', 'steelsquid', 'omxplayer-kill'])



