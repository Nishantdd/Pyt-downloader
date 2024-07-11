import customtkinter
from pytube import YouTube
from pytube import exceptions as tubexceptions
from threading import Thread
from PIL import Image, ImageTk
import requests
from io import BytesIO
from os import path, rename, system, remove
from shutil import move

# Get the path to the downloads directory 
home_dir = path.expanduser("~") 
downloads_dir = path.join(home_dir, "Downloads")

def checks(ytObject):
    try:

        f_var = int(fps_var.get().split(' ')[0])
        r_var = resolution_var.get().split(' ')[0]
        c_var = container_var.get()
        p_var = prog_var.get()
        filters = ytObject.streams.filter(res = r_var, fps = f_var, type = 'video', subtype = c_var, progressive = p_var)
        if(len(filters)!=0):
            download.configure(state='normal', fg_color = 'green')
        else:
            finishLabel.configure(text='Either Resolution/FPS not available', text_color = ('#BDB82D', 'yellow'))
    except tubexceptions.AgeRestrictedError:
        finishLabel.configure(text = 'The video is Age-Restricted', text_color = 'red')

def get_thumbnail(ytObject):
    title.configure(text=ytObject.title)
    img = Image.open(BytesIO(requests.get(ytObject.thumbnail_url).content))
    thumbnail.configure(app, image=customtkinter.CTkImage(img, size = (320,180)))

def video_download_progressive(ytObject, f_var, r_var, c_var, p_var):
    download.configure(fg_color = '#144870') #Darkening Downlaod button while the download's in process
    
    video = ytObject.streams.filter(res = r_var, fps = f_var, type = 'video', subtype = c_var, progressive = p_var).first()

    try : 
        finishLabel.configure(text="Downloading...", text_color='white') #Putting Downloading... text to provide update and change title to video's title
        video.download(downloads_dir)
        finishLabel.configure(text=f"Video saved in {downloads_dir}", text_color='green')
    except:
        finishLabel.configure(text='Error - Please Fetch first', text_color = 'red')
        exit(0)
    finally :
        download.configure(fg_color = '#2E86C1')

def video_download_not_progressive(ytObject, f_var, r_var, c_var, p_var):

    download.configure(fg_color = '#144870') #Darkening Downlaod button while the download's in process

    video = ytObject.streams.filter(res = r_var, fps = f_var, type = 'video', subtype = c_var, progressive = p_var).first()
    audio = ytObject.streams.filter(only_audio = True, custom_filter_functions=[lambda s: (s.abr == '192kbps') or (s.abr == '160kbps')],mime_type=f"audio/{c_var}").first()

    try : 
        finishLabel.configure(text="Downloading...", text_color='white') #Putting Downloading... text to provide update and change title to video's title
        title_ext = str(title._text)+'.'+str(c_var)
        # print(title_ext)
        video.download(); rename(title_ext,f'video.{c_var}')
        audio.download(); rename(title_ext,f'audio.{c_var}')
        if(c_var=='webm'):
            system(f'ffmpeg -i video.webm -i audio.webm -c copy -f webm output.webm')
        else:
            system(f'ffmpeg -i video.mp4 -i audio.mp4 -c copy output.mp4')
        remove(f"video.{c_var}")
        remove(f"audio.{c_var}")
        rename(f'output.{c_var}',title_ext)
        move(f'{title._text}.{c_var}',f'{downloads_dir}\{title_ext}')
        finishLabel.configure(text=f"Video saved in {downloads_dir}", text_color='green')
    except Exception as e:
        print(e)
        exit(0)
    finally :
        download.configure(fg_color = '#2E86C1')

def Fetch_Video():
    download.configure(state = 'disabled', fg_color = '#2E86C1')
    finishLabel.configure(text = '')
    try:
        ytlink = link.get()
        ytObject = YouTube(ytlink)
        # ytObject = YouTube(ytlink, use_oauth=True, allow_oauth_cache=True) -> To fix Age-Restriction by logging in

        #Getting Image from URL and displaying it in right format
        Thread(target = get_thumbnail, args=(ytObject,)).start()

        #Checking if the set of Resolution and FPS is available
        check = Thread(target = checks, args = (ytObject,))
        check.start()
        
    except Exception as e:
        finishLabel.configure(text="Youtube link invalid!", text_color = 'red')

def StartDownload():
    try:
        ytlink = link.get()
        ytObject = YouTube(ytlink)
        f_var = int(fps_var.get().split(' ')[0])
        r_var = resolution_var.get().split(' ')[0]
        c_var = container_var.get()
        p_var = prog_var.get()

        #Creating a new thread to download video simultaneously
        if(p_var == True):
            Thread(target=video_download_progressive ,args=(ytObject, f_var, r_var, c_var, p_var)).start()
        else:
            Thread(target=video_download_not_progressive ,args=(ytObject, f_var, r_var, c_var, p_var)).start()

    except Exception as e:
        finishLabel.configure(text=str(e), text_color = 'red')




#System settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

#Frame
app = customtkinter.CTk()
app.geometry("620x480")
app.title("Youtube Downloader")

#Fonts
prsans = customtkinter.CTkFont(family='Product Sans', size = 20)
prsans_small = customtkinter.CTkFont(family='Product Sans', size = 15)
cascode = customtkinter.CTkFont(family='Cascadia Code PL Bold', size = 18)
cascode_small = customtkinter.CTkFont(family='Cascadia Code PL', size = 14)


#Title
title = customtkinter.CTkLabel(app, text = "Insert the YouTube url :", font=cascode)
title.pack(padx = 10, pady = 20)


#Link Input
url_var = customtkinter.StringVar()
try:
    clip = app.clipboard_get()
    if(clip.find('youtu') != -1):
        url_var = customtkinter.StringVar(value=clip)   
except:
    pass

link = customtkinter.CTkEntry(app, width = 530, height = 45, textvariable=url_var, font=prsans_small)
link.pack()

#Finished Downloading or Error
finishLabel = customtkinter.CTkLabel(app, text="",font=cascode_small)
finishLabel.pack()

#Fetch Button
fetch = customtkinter.CTkButton(app, text="Fetch", command=Fetch_Video, font=cascode)
fetch.pack(padx=10,pady=5)

#Technicals ComboBox
resolution_var = customtkinter.StringVar(value="240p : 426x240")
fps_var = customtkinter.StringVar(value = '30 FPS')
container_var = customtkinter.StringVar(value="mp4")
resolutions = ['240p : 426x240','360p : 640x360','480p : 854x480','720p : 1280x720','1080p : 1920x1080','1440p : 2560x1440','2160p : 3840x2160']

Res_label = customtkinter.CTkLabel(app, text="Select Technicals :",font=prsans)
resbox = customtkinter.CTkComboBox(app,values=resolutions, variable=resolution_var, font=prsans_small, dropdown_font=prsans_small, state='readonly', width=142)
fpsbox = customtkinter.CTkComboBox(app,values=['24 FPS','25 FPS','30 FPS','60 FPS'], variable=fps_var, font=prsans_small, dropdown_font=prsans_small, state='readonly')
conbox = customtkinter.CTkComboBox(app, values = ['mp4','webm'], variable=container_var,font = prsans_small, dropdown_font=prsans_small)

Res_label.pack(padx = 45,pady = (30,10),anchor='w')
resbox.pack(padx=45,pady = (0,5), anchor='w')
fpsbox.pack(padx = 45,pady = (0,5),anchor='w')
conbox.pack(padx = 45, anchor = 'w')

#Progressive Checkbox
prog_var = customtkinter.StringVar(value = 'True')
prog_var = customtkinter.BooleanVar(value = False)
progbox = customtkinter.CTkCheckBox(app, text="Progressive", variable=prog_var, onvalue=True, offvalue=False, font=prsans_small)
progbox.pack(padx = 45, pady = (10,10),anchor = 'w')


#Download Button
download = customtkinter.CTkButton(app, text="Download", command=StartDownload, font=cascode, height=30, state='disabled')
download.pack(padx=45, pady=(25,0), anchor='w')

#Thumbnail
thumbnail = customtkinter.CTkLabel(app, text='')
thumbnail.place(x=235,y=245)

if __name__ == '__main__':
    app.minsize(620,480)
    app.maxsize(620,480)
    app.attributes('-topmost',True)
    app.mainloop()
