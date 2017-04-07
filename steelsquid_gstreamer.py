#!/usr/bin/python -OO


'''
Wrapper for gstreamer command line interface
'''


import sys
import threading
import time
import steelsquid_utils
import thread
import os

# IP-number were to send the video stream
video_ip = ""
video_port = "6602"
    
# IP-number were to send the audio stream
audio_ip = ""
audio_port = "6602"

# Width/height for the stream
width = "800"
height = "480"

# Width for the stream
fps = "20"

# Bitrate for the stream
bitrate = "800000"

# , tcp_video
tcp_video = False

# has this unit the mic and camera
is_camera_mic = False

# Enable
enable_video = False
enable_audio = False
enable_hud = False

# Save to disk
save_to_disk = False

# interuppt thread
interrupt = threading.Event()

# Running
running = True

# Save to this location
save_function = None

# low_light
low_light_v = ""
low_light_bool = False

# Running
low_bandwidth_mode = False


def setup_camera_mic(video_ip, video_port, audio_ip, audio_port, width, height, fps, bitrate, tcp_video, low_light):
    '''
    Stream raspberry pi camera to host using TCP
    Also record with mic and stream using UDP
    ''' 
    global is_camera_mic 
    is_camera_mic = True 
    globals()['video_ip'] = video_ip
    globals()['video_port'] = str(video_port)
    globals()['audio_ip'] = audio_ip
    globals()['audio_port'] = str(audio_port)
    globals()['width'] = str(width)
    globals()['height'] = str(height)
    globals()['fps'] = str(fps)
    globals()['bitrate'] = str(bitrate)
    globals()['tcp_video'] = tcp_video
    _low_light(low_light)
    steelsquid_utils.execute_system_command(["modprobe", "bcm2835-v4l2", "gst_v4l2src_is_broken=1"])
    thread.start_new_thread(_video_cam_thread, ())
    thread.start_new_thread(_audio_mic_thread, ())


def setup_display_speaker(video_ip, video_port, audio_ip, audio_port, width, height, fps, save_function, tcp_video, low_light):
    '''
    Listen for stream from host and display on screen
    Also listen for audio stream and play in speaker
    save_function = function that should return the directory to save to () if save is enabled or use HUD
    ''' 
    global is_camera_mic
    is_camera_mic = False
    globals()['video_ip'] = video_ip
    globals()['video_port'] = str(video_port)
    globals()['audio_ip'] = audio_ip
    globals()['audio_port'] = str(audio_port)
    globals()['width'] = str(width)
    globals()['height'] = str(height)
    globals()['fps'] = str(fps)
    globals()['save_function'] = save_function
    globals()['tcp_video'] = tcp_video
    _low_light(low_light)
    thread.start_new_thread(_video_display_thread, ())
    thread.start_new_thread(_audio_speaker_thread, ())
    thread.start_new_thread(_hud_thread, ())


def save(enable):
    '''
    Save to disk...will enable audio/video and hud...
    ''' 
    globals()['low_bandwidth_mode'] = False
    globals()['save_to_disk'] = enable
    globals()['enable_video'] = enable
    globals()['enable_audio'] = enable
    globals()['enable_hud'] = enable
    kill_all()


def video(enable):
    '''
    Enable the video stream or listen for stream
    ''' 
    globals()['low_bandwidth_mode'] = False
    globals()['enable_video'] = enable
    kill_video()


def video_bitrate(new_bitrate):
    '''
    Change the bitrate of the video stream
    ''' 
    globals()['low_bandwidth_mode'] = False
    globals()['bitrate'] = new_bitrate
    kill_video()


def video_tcp(enable):
    '''
    Change the bitrate of the video stream
    ''' 
    globals()['low_bandwidth_mode'] = False
    globals()['tcp_video'] = enable
    kill_video()
    
    
def low_light(enable):
    '''
    Use low light camera
    ''' 
    globals()['low_bandwidth_mode'] = False
    _low_light(enable)
    kill_video()
    
    
def _low_light(enable):
    '''
    Use low light camera
    ''' 
    globals()['low_light_bool'] = enable
    if enable:
        globals()['low_light_v'] = "image_stabilization=1,auto_exposure=0,auto_exposure_bias=24,iso_sensitivity=4,scene_mode=9,brightness=60,saturation=10"
    else:
        globals()['low_light_v'] = "image_stabilization=1,auto_exposure=0,auto_exposure_bias=12,iso_sensitivity=0,scene_mode=0,brightness=50,saturation=0"
        
        
def audio(enable):
    '''
    Enable the audio stream or listen for stream
    ''' 
    globals()['low_bandwidth_mode'] = False
    globals()['enable_audio'] = enable
    kill_audio()
    
    
def hud(enable):
    '''
    Enable the HUD (Save HUD video to disk)
    ''' 
    globals()['enable_hud'] = enable
    kill_hud()


def low_bandwidth():  
    '''
    Set low bandwidth mode 
    ''' 
    globals()['low_bandwidth_mode'] = True
    kill_video()
    kill_audio()
    

def close():
    '''
    CLose all threads
    ''' 
    global running
    running = False
    kill_video()
    kill_audio()
    kill_hud()


def kill_all():
    '''
    Kill all
    ''' 
    kill_video()
    kill_audio()
    kill_hud()
        

def kill_video():
    '''
    Kill gstreamer video
    ''' 
    if is_camera_mic:                                   
        steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e v4l2src"])
    elif save_to_disk:
        steelsquid_utils.execute_system_command_blind(["pkill", "-SIGINT", "-f", "gst-launch-1.0 -e tcpserversrc host=0.0.0.0 port="+video_port])
        steelsquid_utils.execute_system_command_blind(["pkill", "-SIGINT", "-f", "gst-launch-1.0 -e udpsrc port="+video_port])
    else:
        steelsquid_utils.execute_system_command_blind(["pkill", "-SIGINT", "-f", "gst-launch-1.0 -e tcpserversrc host=0.0.0.0 port="+video_port])
        steelsquid_utils.execute_system_command_blind(["pkill", "-SIGINT", "-f", "gst-launch-1.0 -e udpsrc port="+video_port])
    interrupt.set()


def kill_audio():
    '''
    Kill gstreamer audio
    ''' 
    if is_camera_mic:
        steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e alsasrc"])
    elif save_to_disk:
        steelsquid_utils.execute_system_command_blind(["pkill", "-SIGINT", "-f", "gst-launch-1.0 -e udpsrc port="+audio_port])
    else:
        steelsquid_utils.execute_system_command_blind(["pkill", "-SIGINT", "-f", "gst-launch-1.0 -e udpsrc port="+audio_port])
    interrupt.set()


def kill_hud():
    '''
    Kill gstreamer hud 
    ''' 
    if not is_camera_mic:
        steelsquid_utils.execute_system_command_blind(["pkill", "-SIGINT", "-f", "gst-launch-1.0 -e ximagesrc"])        
        interrupt.set()


def _video_cam_thread():
    '''
    Thread
    ''' 
    while running:
        try:
            if enable_video:
                kill_video()
                if low_bandwidth_mode:
                    if tcp_video:
                        steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "v4l2src", "extra-controls=\"c,vertical_flip=1,horizontal_flip=1," + low_light_v + "\"", "device=/dev/video0", "!", "video/x-raw,width="+width+",height="+height+",framerate=" + "5" + "/1", "!", "clockoverlay", "xpad=0", "ypad=0", "!", "omxh264enc", "target-bitrate="+"100000", "control-rate=3", "!", "tcpclientsink", "host="+video_ip, "port="+video_port])
                    else:
                        steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "v4l2src", "extra-controls=\"c,vertical_flip=1,horizontal_flip=1," + low_light_v + "\"", "device=/dev/video0", "!", "video/x-raw,width="+width+",height="+height+",framerate=" + "5" + "/1", "!", "clockoverlay", "xpad=0", "ypad=0", "!", "omxh264enc", "target-bitrate="+"100000", "control-rate=3", "!", "rtph264pay", "pt=96", "config-interval=1", "!", "udpsink", "sync=false", "host="+video_ip, "port="+video_port])
                else:
                    if tcp_video:
                        steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "v4l2src", "extra-controls=\"c,vertical_flip=1,horizontal_flip=1," + low_light_v + "\"", "device=/dev/video0", "!", "video/x-raw,width="+width+",height="+height+",framerate=" + fps + "/1", "!", "clockoverlay", "xpad=0", "ypad=0", "!", "omxh264enc", "target-bitrate="+bitrate, "control-rate=3", "!", "tcpclientsink", "host="+video_ip, "port="+video_port])
                    else:
                        steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "v4l2src", "extra-controls=\"c,vertical_flip=1,horizontal_flip=1," + low_light_v + "\"", "device=/dev/video0", "!", "video/x-raw,width="+width+",height="+height+",framerate=" + fps + "/1", "!", "clockoverlay", "xpad=0", "ypad=0", "!", "omxh264enc", "target-bitrate="+bitrate, "control-rate=3", "!", "rtph264pay", "pt=96", "config-interval=1", "!", "udpsink", "sync=false", "host="+video_ip, "port="+video_port])
            else:
                interrupt.wait(1)
                interrupt.clear()
        except:
            pass


def _video_display_thread():
    '''
    Thread
    ''' 
    while running:
        try:
            if enable_video: 
                kill_video()
                if save_to_disk:
                    f = get_file("video.mp4")
                    if tcp_video:
                        steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "tcpserversrc", "host=0.0.0.0", "port="+video_port, "!", "tee", "name=t", "!", "h264parse", "!", "omxh264dec", "!", "autovideosink", "text-overlay=false", "sync=false", "t.", "!", "queue", "!", "video/x-h264,width="+width+",height="+height+",framerate=" + fps + "/1,profile=constrained-baseline", "!", "h264parse", "disable-passthrough=true", "!", "queue", "!", "mp4mux", "!", "filesink", "location="+f]) 
                    else:
                        steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "udpsrc", "port="+video_port, "caps=application/x-rtp,media=video,clock-rate=90000,encoding-name=H264", "!", "rtpjitterbuffer", "!", "rtph264depay", "!", "video/x-h264,width="+width+",height="+height+",framerate="+fps+"/1", "!", "tee", "name=t", "!", "h264parse", "!", "omxh264dec", "!", "autovideosink", "text-overlay=false", "sync=false", "t.", "!", "queue", "!", "video/x-h264,width="+width+",height="+height+",framerate=" + fps + "/1,profile=constrained-baseline", "!", "h264parse", "disable-passthrough=true", "!", "queue", "!", "mp4mux", "!", "filesink", "location="+f]) 
                else:
                    if tcp_video:
                        steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "tcpserversrc", "host=0.0.0.0", "port="+video_port, "!", "h264parse", "!", "omxh264dec", "!", "autovideosink", "text-overlay=false", "sync=false"]) 
                    else:
                        steelsquid_utils.execute_system_command(["gst-launch-1.0", "-e", "udpsrc", "port="+video_port, "caps=application/x-rtp,media=video,clock-rate=90000,encoding-name=H264", "!", "rtpjitterbuffer", "!", "rtph264depay", "!", "video/x-h264,width="+width+",height="+height+",framerate="+fps+"/1", "!", "h264parse", "!", "omxh264dec", "!", "autovideosink", "text-overlay=false", "sync=false"]) 
            else:
                interrupt.wait(1)
                interrupt.clear()
        except:
            steelsquid_utils.shout()


def _audio_mic_thread():
    '''
    Thread
    ''' 
    while running:
        try:
            if enable_audio:
                kill_audio()
                if low_bandwidth_mode:
                    interrupt.wait(1)
                    interrupt.clear()
                else:
                    steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "alsasrc", "latency-time=1", "device=sysdefault:CARD=1", "!", "audioconvert", "!", "audio/x-raw,channels=1,depth=16,width=16,rate=22000",  "!", "rtpL16pay", "!", "udpsink", "host="+audio_ip, "port="+audio_port])
                    #steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "alsasrc", "latency-time=1", "device=sysdefault:CARD=1", "!", "mulawenc", "!", "rtppcmupay", "!", "udpsink", "host="+audio_ip, "port="+audio_port])
            else:
                interrupt.wait(1)
                interrupt.clear()
        except:
            pass  
            

def _audio_speaker_thread():
    '''
    Thread
    ''' 
    while running:
        try:
            if enable_audio:
                if save_to_disk:
                    f = get_file("audio.wav")
                    steelsquid_utils.execute_system_command_blind(["nice", "-n", "8", "gst-launch-1.0", "-e", "udpsrc", "port="+audio_port, "!", "application/x-rtp,media=audio,clock-rate=22000,width=16,height=16,encoding-name=L16,encoding-params=1,channels=1,channel-positions=1,payload=96", "!", "rtpjitterbuffer", "!", "rtpL16depay", "!", "audioconvert", "!", "tee", "name=myt", "!", "queue", "!", "alsasink", "sync=false", "myt.", "!", "queue", "!", "audiorate", "!", "audioconvert", "!", "audioresample", "!", "wavenc", "!", "filesink", "location="+f]) 
                    #steelsquid_utils.execute_system_command_blind(["nice", "-n", "8", "gst-launch-1.0", "-e", "udpsrc", "port="+audio_port, "caps=application/x-rtp", "!", "rtpjitterbuffer", "!", "rtppcmudepay", "!", "mulawdec", "!", "tee", "name=myt", "!", "queue", "!", "alsasink", "sync=false", "myt.", "!", "queue", "!", "audiorate", "!", "audioconvert", "!", "audioresample", "!", "wavenc", "!", "filesink", "location="+f]) 
                    time.sleep(1)
                else:
                    kill_audio()
                    steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "udpsrc", "port="+audio_port, "!", "application/x-rtp,media=audio,clock-rate=22000,width=16,height=16,encoding-name=L16,encoding-params=1,channels=1,channel-positions=1,payload=96", "!", "rtpjitterbuffer", "!", "rtpL16depay", "!", "audioconvert", "!", "alsasink", "sync=false"]) 
                    #steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "udpsrc", "port="+audio_port, "caps=application/x-rtp", "!", "rtpjitterbuffer", "!", "rtppcmudepay", "!", "mulawdec", "!", "alsasink", "sync=false"]) 
            else:
                interrupt.wait(1)
                interrupt.clear()
        except:
            pass


def _hud_thread():
    '''
    Thread
    ''' 
    while running:
        try:
            if enable_hud:
                kill_hud()
                f = get_file("hud.avi")
                #steelsquid_utils.execute_system_command_blind(["nice", "-n", "10", "avconv", "-f", "x11grab", "-r", "2", "-s", width+"x"+height, "-i", ":0.0", "-vcodec", "libx264", "-threads", "1", f])
                steelsquid_utils.execute_system_command_blind(["gst-launch-1.0", "-e", "ximagesrc", "display-name=:0", "use-damage=0", "!", "video/x-raw,framerate=2/1", "!", "videoconvert", "!", "omxh264enc", "!", "video/x-h264,profile=high", "!", "avimux", "!", "filesink", "location="+f])
            else:
                interrupt.wait(1)
                interrupt.clear()
        except:
            pass



def get_file(file_name):
    '''
    Get save file
    ''' 
    d = save_function()
    d = os.path.join(d, steelsquid_utils.get_date())
    t = os.path.join(d, steelsquid_utils.get_time(delemitter="")+"_"+file_name)
    try:
        os.mkdir(d);
    except:
        pass
    return t

