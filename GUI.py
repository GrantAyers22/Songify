import os
import tkinter as tk
import urllib.request
from tkinter import *
from PIL import Image, ImageTk
from pygame import mixer
from pytube import YouTube
from tkscrolledframe import ScrolledFrame
from youtube_search import YoutubeSearch
import ffmpy
from mutagen.mp3 import MP3


class CreateMusic:
    def __init__(self, f, t, a):
        self.folder = f
        self.title = t
        self.artist = a
        self.watch_link = ''
        self.youtube_link = "youtube.com"
        self.directory_name = self.folder + "\\" + self.title

    def search(self):
        # Returns the first 10 results
        results = YoutubeSearch(self.title + " by " + self.artist, max_results=10).to_dict()

        # Grabs the first result
        first_result = str(results.pop(0))

        # Sets youtube_link to the full youtube link
        remove_title = first_result[first_result.find(',') + 11: len(first_result)]
        self.watch_link = remove_title[0:remove_title.find('\'')]
        self.youtube_link += self.watch_link

    def getYoutubeLink(self):
        return self.youtube_link

    def download_video(self):
        return YouTube(str(self.youtube_link))

    def download_thumbnail(self):
        videoID = self.watch_link[self.watch_link.find('v')+2:len(self.watch_link)]
        return 'http://img.youtube.com/vi/%s/0.jpg' % videoID

    def CreateSong(self):
        # Making the file path for the new song
        if not os.path.isdir(self.directory_name):
            os.mkdir(self.directory_name)

        # Downloading song
        link = self.download_video()
        song = link.streams.filter(only_audio=True).first()
        created_file = song.download(output_path=self.directory_name)
        song_name = self.directory_name + "\\music.mp3"

        # Creating renamed file
        if not os.path.isfile(song_name):
            ff = ffmpy.FFmpeg(inputs={created_file: None}, outputs={song_name: None})
            ff.run()

        # Adding art
        url = self.download_thumbnail()
        urllib.request.urlretrieve(url, self.directory_name + "\\art.jpg")

        # Finding length of song
        audio = MP3(self.directory_name + "\\music.mp3")

        # Writing information to file
        file_writer = open(self.directory_name + "\\config.txt", "w")
        file_writer.write(self.title + "\n")
        file_writer.write(self.artist + "\n")
        file_writer.write(str(audio.info.length) + "\n")
        file_writer.close()

        # Deleting extra file
        os.remove(created_file)


class MusicInterpreter:
    def __init__(self, l, n):
        self.link = l
        self.name = n
        self.folder = self.link + "\\" + self.name
        self.song_file_path = self.folder + "\\music.mp3"

        # Creating mixer
        self.mix_tool = mixer
        self.mix_tool.init()

    def getLink(self):
        return str(self.link)

    def getName(self):
        return str(self.name)

    def play_music(self):
        self.mix_tool.music.load(self.song_file_path)
        self.mix_tool.music.play()

    def pause_music(self):
        if self.mix_tool.music.get_busy:
            self.mix_tool.music.pause()

    def resume(self):
        self.mix_tool.music.unpause()

    def getPic(self):
        return self.folder + "\\art.jpg"

    def setVolume(self, volume):
        v = float(volume)
        self.mix_tool.music.set_volume((v / 100))


class PushButton:
    def __init__(self, file_path, w, h, screen):
        full_size_image = Image.open(file_path).resize((w, h), Image.ANTIALIAS)
        self.Icon = ImageTk.PhotoImage(full_size_image)
        self.width = w
        self.height = h
        self.Window = screen

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_button(self):
        return tk.Button(self.Window, image=self.Icon, borderwidth=0)


class MusicIcon:
    def __init__(self, w, f, mi, pic, isd):
        self.window = w
        self.frame = f
        self.music = mi
        self.image = pic
        self.icon_size = isd

    def get_music(self):
        return self.music

    def get_button(self):
        return Button(self.frame,
                      width=self.icon_size,
                      height=self.icon_size,
                      borderwidth=0,
                      relief="groove",
                      anchor="center",
                      justify="center",
                      image=self.image,
                      command=lambda: [self.music.play_music(), self.window.playToPause(),
                                       self.window.setMusicPlaying(self.music.getLink, self.music.getName)])


class Window:
    def __init__(self):
        # --------------------------- Creating Default 600x600 window in grey -----------------------------------------
        # Setting the dimension of the window
        self.width = 600
        self.height = 600
        self.size_dimension = str(self.width) + "x" + str(self.height)

        # Creating a window
        self.root = tk.Tk()

        # Giving the window a title
        self.root.title("SONGIFY")

        # Assigning the window size
        self.root.geometry(self.size_dimension)

        # Making the color
        self.root.configure(background='#43464b')

        # Creating the folder variable
        self.folder = 'D:\\SongPlayer\\songs'

        # Creates blank music variable
        self.music_playing = MusicInterpreter(self.folder, 'Darude Sandstorm')

        # ---------------------------- Creating a Scrolling Frame within window ---------------------------------------
        self.put_songs()
        # --------------------------------- Creating the search bar and adding functionality ---------------------------
        # Creating text box
        text_box_width = int(self.width*2/75)
        self.search_box = tk.Entry(self.root, width=text_box_width)
        self.search_box.place(x=self.width/120, y=self.height/15)

        # Creating search button
        self.search_button = Button(self.root, width=10, height=1, text="Search", command=self.add_song)
        self.search_button.place(x=self.width / 40, y=self.height / 9)

        # --------------------------------- Creating the music control buttons -----------------------------------------
        # Creating a pause button
        pause_image_reference = "D:\\SongPlayer\\imgrsc\\pause.png"
        pause_button = PushButton(pause_image_reference, 50, 50, self.root)
        self.pause = pause_button.get_button()
        self.pause.configure(command=lambda: [self.pauseToPlay(), self.music_playing.pause_music()])
        self.pause_button_x = (self.width / 2) - (pause_button.get_width() / 2)
        self.pause_button_y = (self.height - pause_button.height)

        # Creating a play button
        play_image_reference = "D:\\SongPlayer\\imgrsc\\play.jpg"
        play_button = PushButton(play_image_reference, 50, 50, self.root)
        self.play = play_button.get_button()
        self.play.configure(command=lambda: [self.playToPause(), self.music_playing.resume()])
        self.play_button_x = (self.width / 2) - (play_button.get_width() / 2)
        self.play_button_y = (self.height - play_button.get_height())

        # Creating rewind button
        rewind_image_reference = "D:\\SongPlayer\\imgrsc\\rewind.png"
        rewind_button = PushButton(rewind_image_reference, 50, 50, self.root)
        self.rewind = rewind_button.get_button()
        self.rewind_button_x = (self.width / 2) - (3 / 2 * rewind_button.get_width())
        self.rewind_button_y = (self.height - rewind_button.get_height())

        # Creating fast forward button
        fastforward_image_reference = "D:\\SongPlayer\\imgrsc\\fastforward.png"
        fastforward_button = PushButton(fastforward_image_reference, 50, 50, self.root)
        self.fastforward = fastforward_button.get_button()
        self.fastforward_button_x = (self.width / 2) + (1 / 2 * fastforward_button.get_width())
        self.fastforward_button_y = (self.height - fastforward_button.get_height())

        # Creating the volume button
        volume_width = self.width / 5
        volume_height = self.height / 12
        self.volume = tk.Scale(self.root,
                               from_=1,
                               to=100,
                               borderwidth=0,
                               orient=tk.HORIZONTAL,
                               background='#43464b',
                               bd=0,
                               activebackground='#43464b',
                               fg='#FFFFFF',
                               highlightbackground='#43464b',
                               highlightcolor='#43464b',
                               length=volume_width,
                               width=volume_height / 2,
                               showvalue=0,
                               troughcolor='#FFFFFF')
        self.volume.set(50)
        self.volume.config(command=self.printVolume)
        volume_x = (self.width - volume_width)
        volume_y = (self.height - volume_height)

        # Placing buttons
        self.rewind.place(x=self.rewind_button_x, y=self.rewind_button_y)
        self.play.place(x=self.play_button_x, y=self.play_button_y)
        self.fastforward.place(x=self.fastforward_button_x, y=self.fastforward_button_y)
        self.volume.place(x=volume_x, y=volume_y)

        # Making the window not resizable
        self.root.resizable(0, 0)

        # Running the window
        self.root.mainloop()

    # -------------------------------------- Helping Functions --------------------------------------------------------
    # Creating pause button functionality
    def pauseToPlay(self):
        self.pause.place_forget()
        self.play.place(x=self.play_button_x, y=self.play_button_y)

    def playToPause(self):
        self.play.place_forget()
        self.pause.place(x=self.pause_button_x, y=self.pause_button_y)

    def printVolume(self, vol):
        self.music_playing.setVolume(int(vol))

    def setMusicPlaying(self, l, n):
        self.music_playing = MusicInterpreter(str(l), str(n))

    def add_song(self):
        song_search = self.search_box.get()
        title = song_search[0: song_search.find(',')]
        artist = song_search[song_search.find(',')+2: len(song_search)]
        add_music = CreateMusic(self.folder, title, artist)
        add_music.search()
        add_music.CreateSong()
        self.put_songs()
        self.root.update()

    def put_songs(self):
        # Set height and width of scroll frame
        sf_width = 7 / 10 * self.width
        sf_height = 4 / 5 * self.height

        # Create scrolled frame and place it
        sf = ScrolledFrame(self.root, width=sf_width, height=sf_height)
        sf.place(x=(1 / 5 * self.width), y=(1 / 15 * self.height))

        # Bind the arrow keys and scroll wheel
        sf.bind_arrow_keys(self.root)
        sf.bind_scroll_wheel(self.root)

        # Create a frame within the ScrolledFrame
        inner_frame = sf.display_widget(Frame)

        # Getting the number of songs and creating the appropriate number of rows and columns
        number_of_songs = len(os.listdir(self.folder))
        num_cols = 4
        row_temp = float(number_of_songs / num_cols)
        if not row_temp.is_integer():
            num_rows = int(row_temp) + 1
        else:
            num_rows = int(row_temp)

        # Creating a list of all the songs
        songs = list()
        
        song_folders = os.listdir('D:\\SongPlayer\\songs\\')
        for folder in song_folders:
            songs.append(MusicInterpreter(self.folder, folder))

        # Creating a list of pics
        pics = list()
        pic_counter = 0

        # Determining the size of the icon
        icon_size_dimension = int(sf_width / num_cols)
        music_counter = 0

        # Looping through the songs and creating a button for each song
        for row in range(num_rows):
            for column in range(num_cols):
                # This if statement determines if there are more songs to make
                if music_counter < number_of_songs:
                    music = songs[music_counter]
                    mir = Image.open(music.getPic()).resize((icon_size_dimension, icon_size_dimension), Image.ANTIALIAS)
                    pics.append(ImageTk.PhotoImage(mir))
                    # Creates the music button
                    MI = MusicIcon(self, inner_frame, music, pics[pic_counter], icon_size_dimension)
                    w = MI.get_button()
                    music_counter += 1
                    pic_counter += 1

                # putting it in grid layout
                w.grid(row=row,
                       column=column,
                       padx=0,
                       pady=0)


app = Window()

'''
add_music = CreateMusic('D:\\SongPlayer\\songs', 'Rock Star', 'DaBaby')
add_music.search()
add_music.CreateSong()
'''
