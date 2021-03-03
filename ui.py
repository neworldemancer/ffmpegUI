import numpy as np
#from matplotlib.pyplot import cm
#from matplotlib import pyplot as plt
#from scipy import optimize as opt
import os
#import PIL
import pickle
import glob
import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter import *
import tkinter.ttk as ttk
import subprocess


cfg_name = 'ffmpeg-gui.cfg'

def del_cfg():
    os.remove(cfg_name)

def load_cfg():
    """
    loads cfg file or creates new dict
    Returns: cfg disctionary
    """

    if os.path.exists(cfg_name):
        try:
            with open(cfg_name, 'rb') as f:
                cfg = pickle.load(f)
                assert(isinstance(cfg, dict))
                return cfg
        except:
            del_cfg()
            print('config corrupt')
    
    ffmpeg_path = filedialog.askopenfilename(filetypes=[('Program', '.exe')],
                                             initialdir='d:/',
                                             title='Please locate ffmpeg binary'
                                            )
    cfg = {'ffmpeg_path': ffmpeg_path}
    return cfg

def save_cfg(cfg):
    with open(cfg_name, 'wb') as f:
        pickle.dump(cfg, f)

def get_in_file():
    path = filedialog.askopenfilename(filetypes=[('Video', '.avi .mp4 .mov'), ('Audio', '.wav .mp3 .ogg .mpa'), ('Unknown video/audio', '*.*')],
                                      title='Select input file'
                                     )
    return path


def get_out_file(in_file, audio=False, audiohr=False):
    o_path = os.path.dirname(in_file)
    i_file = os.path.basename(in_file)
    i_name = i_file.split('.')[0]
    
    ext = '.' + ('wav' if audiohr else ('mp3' if audio else 'mp4'))
    o_file = i_name + ext
    
    path = filedialog.asksaveasfilename(initialdir=o_path,
                                    title='Select output file',
                                    filetypes=[('Audio', ext) if (audio or audiohr) else ('Video', ext) ],
                                    initialfile=o_file
                                   )
    if path[-len(ext):] != ext and len(path):
        path += ext
    return path

def select_speed(speed):
    """
    Returns acceptable speed 
    """
    if speed not in [
        'ultrafast',
        'superfast',
        'veryfast',
        'faster',
        'fast',
        'medium',
        'slow',
        'slower',
        'veryslow',
    ]:
        speed = 'veryslow'
    return speed

def quote_spaced(s):
    if ' ' in s:
        s = f'"{s}"'
    return s

def convert_video(in_path, out_path, bitrate='2000k', overwrite=False, speed='veryslow', flip_LR=False, flip_UD=False, to_time=None):

    args = []
    prg = cfg['ffmpeg_path']
    args.append(prg)
    
    #fr = ' -framerate %d' % framerate
    inp = f' -i "{in_path}"'
    args.append('-i')
    args.append(in_path)
    
    speed = select_speed(speed)
    flip_str = ('hflip,' if flip_LR else '') + ('vflip,' if flip_UD else '')
    to_str = '' if to_time is None else f'-t {to_time}'
    
    pars = f' -c:v libx264 -pix_fmt yuv420p -vf "{flip_str}scale=trunc(iw/2)*2:trunc(ih/2)*2" -preset {speed} -b:v {bitrate} {to_str}'
    args.extend([v.strip('" ') for v in pars.split()])
    
    if os.path.exists(out_path):
        if overwrite:
            os.remove(out_path)
        else:
            raise FileExistsError(f'{out_path} already exists')
            
    #cmd = prg + fr + inp + pars + ' ' + out_path
    cmd = prg + inp + pars + ' ' + f'"{out_path}"'
    args.append(out_path)
    print(cmd, args)
    #os.system(cmd)
    res = subprocess.call(args)
    #subprocess.Popen([cmd], shell = True)
    #subprocess.Popen(args, shell = True)
    return res==0

def convert_audio(in_path, out_path, bitrate='256k', overwrite=False, speed='veryslow'):
    # "d:\Program Files\ffmpeg\bin\ffmpeg" -i %in% -c:a libmp3lame -ac 2 -q:a 1 -b:a {bitrate} %in%.mp3
    args = []
    prg = cfg['ffmpeg_path']
    args.append(prg)
    
    #fr = ' -framerate %d' % framerate
    inp = f' -i "{in_path}"'
    args.append('-i')
    args.append(in_path)
    
    is_wav = '.wav' in out_path
    
    speed = select_speed(speed)
    codec = 'pcm_f32le' if is_wav else 'libmp3lame'
    
    
    pars = f' -c:a {codec} -ac 2 -q:a 1'
    
    args.append('-c:a')
    args.append(f'{codec}')
    args.append('-ac')
    args.append('2')
    args.append('-q:a')
    args.append('1')
    
    br = f' -b:a {bitrate}'
    
    
    if os.path.exists(out_path):
        if overwrite:
            os.remove(out_path)
        else:
            raise FileExistsError(f'{out_path} already exists')
            
    #cmd = prg + fr + inp + pars + br + ' ' + out_path
    cmd = prg + inp + pars + br + ' ' + f'"{out_path}"'
    args.append(out_path)
    print(cmd, args)
    #os.system(cmd)
    res = subprocess.call(args)
    #print('res=', res)
    #subprocess.Popen([cmd], shell = True)
    #subprocess.Popen(args, shell = True)
    return res==0
    
def run_ui():
    window = Tk()

    window.title("FFMPEG UI")

    fnt1 = ("Arial", 11)

    window.geometry('530x300')


    # def clicked():
    #     lbl.configure(text=f"Button was clicked !! {selected.get()}")
        

    # btn = Button(window, text="Click Me", font=fnt1, command=clicked)
    # btn.grid(column=1, row=1)

    # txt = Entry(window,width=10)
    # txt.grid(column=0, row=1)

    out_type = IntVar()
    rbv = Radiobutton(window,width=10, text="mp4", font=fnt1, value=0, variable=out_type)
    rbv.grid(column=0, row=0)

    rbv = Radiobutton(window,width=10, text="mp3", font=fnt1, value=1, variable=out_type)
    rbv.grid(column=1, row=0)

    rbv = Radiobutton(window,width=10, text="wav", font=fnt1, value=2, variable=out_type)
    rbv.grid(column=2, row=0)

    lbl = Label(window, text="overwrite", font=fnt1)
    lbl.grid(column=0, row=1)
    overwrite = BooleanVar()
    overwrite.set(True)
    chb = Checkbutton(window,width=10, font=fnt1, var=overwrite)
    chb.grid(column=1, row=1)

    lbl = Label(window, text="speed", font=fnt1)
    lbl.grid(column=0, row=2)

    speed_combo = ttk.Combobox(window)
    speed_combo['values']= [
            'ultrafast',
            'superfast',
            'veryfast',
            'faster',
            'fast',
            'medium',
            'slow',
            'slower',
            'veryslow'
        ]
    speed_combo.current(5) #set the selected item
    speed_combo.grid(column=1, row=2)

    lbl = Label(window, text="bitrate", font=fnt1)
    lbl.grid(column=0, row=3)
    bitrate = tk.StringVar()
    txt_bitrate = Entry(window,width=10, font=fnt1, textvariable=bitrate )
    txt_bitrate.grid(column=1, row=3)
    bitrate.set('720k')
    
    rotate_type = IntVar()
    rbv = Radiobutton(window,width=10, text="straight", font=fnt1, value=0, variable=rotate_type)
    rbv.grid(column=0, row=4)

    rbv = Radiobutton(window,width=10, text="flip LR", font=fnt1, value=1, variable=rotate_type)
    rbv.grid(column=1, row=4)

    rbv = Radiobutton(window,width=10, text="flop UD", font=fnt1, value=2, variable=rotate_type)
    rbv.grid(column=2, row=4)

    rbv = Radiobutton(window,width=10, text="rotate 180", font=fnt1, value=3, variable=rotate_type)
    rbv.grid(column=3, row=4)
    
    
    lbl = Label(window, text="test run 1min", font=fnt1)
    lbl.grid(column=0, row=5)
    testrun = BooleanVar()
    testrun.set(False)
    chb = Checkbutton(window,width=10, font=fnt1, var=testrun)
    chb.grid(column=1, row=5)


    log = Label(window, text="", font=fnt1)
    log.grid(column=0, row=8, columnspan=3, rowspan=3)
    
    

    def go():
        aud = out_type.get() == 1
        audhr = out_type.get() == 2
        
        i = get_in_file()
        if i == '':
            return
        o = get_out_file(i, audio=aud, audiohr=audhr)
        if o == '':
            return
        
        
        speed_val = speed_combo.get()
        bitrate_val = bitrate.get()
        
        
        #out = f"i={i} \no={o} \naud={aud} audhr={audhr}, bitrate={bitrate_val}, speed={speed_val}"
        out = f"i={i} \no={o}"
        
        log.configure(text=out)
        if aud or audhr:
            res = convert_audio(i, o, overwrite=overwrite, speed=speed_val, bitrate=bitrate_val)
        else:
            rt = rotate_type.get()
            flip_LR = rt in [1,3]
            flip_UD = rt in [2,3]
            tr = testrun.get()
            res = convert_video(i, o, overwrite=overwrite, speed=speed_val, bitrate=bitrate_val, flip_LR=flip_LR, flip_UD=flip_UD, to_time=60 if tr else None)
        
        out += f'\nres={res}'
        log.configure(text=out)
        
    btn = Button(window, text="Go", font=fnt1, command=go)
    btn.grid(column=3, row=7)

    window.mainloop()
    
if __name__=='__main__':
    cfg = load_cfg()
    save_cfg(cfg)
    run_ui()