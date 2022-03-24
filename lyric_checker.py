from tkinter import * 
from tkinter import scrolledtext, filedialog, messagebox, ttk, font
from turtle import title
from ttkthemes import ThemedTk, ThemedStyle
import webbrowser
import lyricsgenius
import os
import sys
import requests
import string
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from PIL import ImageTk, Image
from configparser import ConfigParser
import threading # 1.3

# Local Files
import version_check # Checks current version
import excel_convert as ex # Allows to convert excel files to .csv files
import logger # Creates logs under lyricchecker.log
import cleaner # For the Spotify function.  Cleans up song names and extracts the URI from the URL


### THE SPLASH SCREEN
splash = Tk()
splash.geometry = "550x300"
splash.iconbitmap = "lyric checker.ico"
img = ImageTk.PhotoImage(Image.open("splash.jpg"))
splash_screen = Label(splash, image=img)
splash_screen.grid()
splash.overrideredirect(True)
splash.eval('tk::PlaceWindow . center') # Starts splash screen in the middle of the monitor.
splash.update_idletasks()


def splashfade():
    '''Adds a really nice fade out effect to the window.'''
    alpha = splash.attributes("-alpha")
    if alpha > 0:
        alpha -= .001
        splash.attributes("-alpha", alpha)
        splash.after(1, splashfade)
    else:
        splash.destroy()
        main_window()


# Read config file
parser = ConfigParser()
parser.read("config.ini")
saved_theme = parser.get('settings', 'theme')
saved_font = parser.get('settings', 'font')
saved_font_size = parser.get('settings', 'font_size')

def resource_path(relative_path):  # Idk, auto-py-to-exe told me to put this here
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

response = requests.get("http://www.bannedwordlist.com/lists/swearWords.txt")
BAD_WORDS = response.text.splitlines()

with open("remove.txt", "r") as remove:
    REMOVE = remove.read().splitlines()
    for word in REMOVE:
        BAD_WORDS.remove(word)
    remove.close()

with open("add.txt", "r") as add:
    ADD = add.read().splitlines()
    for word in ADD:
        BAD_WORDS.append(word)
    add.close()

token = "UL_un5hpVVp5dEkYXq2ovuoEjumaXfGo-mo_Cf8P0GxOgB7aOJoqnR5oSgxkZK6e" # Genius API token
CLIENT_ID = '1a29255fe7934b9b991cb401266da24f' # Spotify API ID
CLIENT_SECRET = '2bd6d203b27c4b45a1105533255e940f' # Spotify API Secret

numbers = string.digits
percent = IntVar
genius = lyricsgenius.Genius(token)

def about(event = None):
    '''
    Opens a small messagebox with some information
    '''
    messagebox.showinfo(title="About Lyric Checker", message="Version: 1.2\nCreated by Fredxp2003 on Github\n\nFor help, click the help menu option, or go to https://fredxp2003.github.io")

def help(event = None):
    '''
    Opens help website
    '''
    webbrowser.open('https://fredxp2003.github.io', new=2)

# Iterated through each word that would be flagged as explicit
# Change the first and last letter of each word to a '*'
# Output the changed word
# Thank you @SumitNalavade for this! 
def censor(word):
    try:
        for letters in word:
            if(word == " ass"):
                word = "a*s"
            elif(letters == word[0] or letters == word[-1]):
                pass
            else:
                word = word.replace(word[word.index(letters)], "*")
    except:
        pass
    finally:
        if word[0] == "n" and word[4] == "a":
            word = "n***a"
        elif word[0] == "n" and word[5] == "r":
            word = "n****r"
        output.insert(INSERT, f"CONTAINS: \"{word}\".\n\n")



def file_open(event = None):
    text_file = filedialog.askopenfile(title = "Select file", filetypes = (("Text files","*.txt"), ("All files", "*.*")))
    name = os.path.basename(text_file.name)
    logger.log(f"Opened {name}.")
    if text_file is None:
        return
    output.delete("1.0", END)
    stuff = text_file.read()
    output.insert(END, stuff)
    text_file.close()

def file_save(event = None):
    f = filedialog.asksaveasfile(title = "Select file",filetypes = (("Text files","*.txt"), ("All files", "*.*")),  initialfile = "lyrics.txt")

    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = str(output.get(1.0, END)) # starts from `1.0`, not `0.0`
    try:
        f.write(text2save)
        
    except Exception as e:
        messagebox.showerror(title="Failed to save", message="Was unable to save this file.")
        logger.log(f"Unable to save file.  Error: {e}", 2)
    f.close() # `()` was missing.
    logger.log("File saved.")

def group_check_thread(event = None):
    threading.Thread(target=group_check).start()

def group_check(event = None):
    bad_songs = []
    excel = False
    try:
        text_file = filedialog.askopenfile(title = "Select file", filetypes = (("Compatible files","*.txt *.csv *.xlsx *.rtf"), ('Text files', '*.txt'), ('Comma Separated Values files', '*.csv'), ('Excel files', '*.xlsx'), ('Rich Text File', '*.rtf'), ("All files", "*.*")))
    except Exception as e:
        messagebox.showerror(f"Unable to read file", f"Unable to read file.\n\nPlease make sure that the file is not currently open in a program such as Excel.")
        logger.log(f"Unable to save file.  Error: {e}", 2)


    name = os.path.basename(text_file.name)
    path = os.path.realpath(text_file.name)
    x = text_file.read()
    count = len(x.splitlines())
    print(x)
    progress['value'] = 0
    text_file.seek(0)

    if text_file is None:
        return
    logger.log(f"Opened {name}.")
    run = True
    output.delete("1.0", END)
    if ".xlsx" in name:
        text_file.close()
        ex.convert(path)
        text_file = open("converted.csv", "r")
        name = "converted.csv"
        excel = True
    while run is True:
        line = text_file.readline()
        print(line)
        clean = True
        if "\n" in line:
            run = True
            separator = "-"
            if ".csv" in name:
                separator = ","
            global title
            title, artist = line.split(separator)
            artist = artist.replace("\n", "")
            if artist == "":
                logger.log("Artist is blank", 3)
            print(f"{title} - {artist}")
            logger.log(f"Searching for {title} - {artist}")
            search = genius.search_song(title, artist)
            if search != None:
                lyrics = search.lyrics
                for word in BAD_WORDS:
                    if word in lyrics.lower():
                        if var.get() == 1:
                            censor(word)
                        else:
                            if word[0] == "n" and word[4] == "a":
                                word = "n***a"
                            elif word[0] == "n" and word[5] == "r":
                                word = "n****r"
                            output.insert(INSERT, f"CONTAINS: \"{word}\".\n\n")
                            #output.insert(INSERT, f"[{search.full_title}]\n\n")
                            #output.insert(INSERT, f"{lyrics}\n--------------------------------------\n")
                        clean = False
                        if f'{title} - {artist}' not in bad_songs:
                            bad_songs.append(f'{title} - {artist}')
                if clean == True:
                    #output.insert(INSERT, f"[{search.full_title}]  |  ")
                    output.insert(INSERT, "THIS SONG IS CLEAN!\n\n")
                    #output.insert(INSERT, f"{lyrics}\n--------------------------------------\n")
                output.insert(INSERT, f"[{search.full_title}]\n\n")
                output.insert(INSERT, f"{lyrics}\n--------------------------------------\n")
            else:
                output.insert(INSERT, f"No results found for {title} - {artist}\n--------------------------------------\n")
            
            progress['value'] += 100/count
            window.update_idletasks()

        else:
            if line == "":
                messagebox.showinfo(title="Complete", message="Lyrics found.")
                if len(bad_songs) > 0:
                    messagebox.showwarning(title="Uh oh...", message=f"{len(bad_songs)} songs(s) contain profanity.\n{bad_songs}")
                
                if excel:
                    text_file.close()
                    os.remove(name)
                break       
                
            else:
                run = False
                separator = "-"
                if ".csv" in name:
                    separator = ","
                title, artist = line.split(separator)
                print(f"{title} - {artist}")
                logger.log(f"Searching for {title} - {artist}")
                search = genius.search_song(title, artist)

                if search != None:
                    lyrics = search.lyrics
                    for word in BAD_WORDS:
                        if word in lyrics.lower():
                            if var.get() == 1:

                                censor(word)
                            else:
                                output.insert(INSERT, f"CONTAINS: \"{word}\".\n\n")
                            
                            clean = False
                            if f'{title} - {artist}' not in bad_songs:
                                bad_songs.append(f'{title} - {artist}')
                    if clean == True:
                        output.insert(INSERT, f"[{search.full_title}]  |  ")
                        output.insert(INSERT, "THIS SONG IS CLEAN!\n\n")
                else:
                    output.insert(INSERT, f"No results found. for {title} - {artist}")
                
            output.insert(INSERT, f"{lyrics}\n\n")
            progress['value'] = 100
            window.update_idletasks()

            messagebox.showinfo(title="Complete", message="Lyrics found.")
            if len(bad_songs) > 0:
                messagebox.showwarning(title="Uh oh...", message=f"{len(bad_songs)} songs(s) are bad.\n{bad_songs}")
            
            if excel:
                text_file.close()
                os.remove(name)
            break     

def profanity_check(event = None):

    output.delete(1.0,END)
    clean = True

    ARTIST = artist.get()
    TITLE = song.get() 

    if TITLE == "":
        output.insert(INSERT, "Title cannot be left blank.")
    else:
        search = genius.search_song(TITLE, ARTIST)
        logger.log(f"Searching for {TITLE} - {ARTIST}")
        if search != None:
            lyrics = search.lyrics
            for word in BAD_WORDS:
                if word in lyrics.lower():
                    if var.get() == 1:
                        censor(word)
                    else:
                        if word[0] == "n" and word[4] == "a":
                            word = "n***a"
                        elif word[0] == "n" and word[5] == "r":
                            word = "n****r"
                        output.insert(INSERT, f"CONTAINS: \"{word}\".\n\n")
                    clean = False
            if clean == True:
                output.insert(INSERT, f"[{search.full_title}]  |  ")
                output.insert(INSERT, "THIS SONG IS CLEAN!\n\n")
            else:
                output.insert(INSERT, f"[{search.full_title}]  |  ")
                output.insert(INSERT, "THIS SONG IS **NOT** CLEAN!\n\n")
        else:
            output.insert(INSERT, "No results found.")
    output.insert(INSERT, f"{lyrics}\n\n")



def spotify_window(entry=None):
    '''
    Spotify integration is planned for 1.2 release.
    '''
    global spwindow
    spwindow = Toplevel()
    style = ThemedStyle(spwindow) 
    style.theme_use(theme)
    bg = style.lookup('TLabel', 'background')
    spwindow.configure(bg=bg)
    

    spwindow.title("Lyric Checker | Spotify")

    img = ImageTk.PhotoImage(Image.open("spotify.png"))
    canvas = Canvas(spwindow, width=826, height=250, bg=style.lookup('TLabel', 'background'))
    canvas.create_image(420, 125, image=img)
    canvas.grid(column=0, row=0, columnspan=3)

    #LABELS
    playlist_label = ttk.Label(spwindow, text='Playlist URI:')
    playlist_label.grid(column=0, row=1)

    url = ttk.Entry(spwindow, width=60) #song entry field
    url.grid(column=1, row=1)

    search = ttk.Button(spwindow, text="Search",command=lambda: spotify(url.get()))
    search.grid(column=2, row=1)

    spwindow.mainloop()


def spotify(uri):
    '''
    Spotify integration is planned for 1.2 release.
    '''
    uri = cleaner.url_cleanup(uri)
    spwindow.destroy()
    spwindow.update_idletasks()
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    logger.log(f'Searching for playlist {uri}.')

    results = sp.playlist(uri)
    f = open("output.txt", "w")
    for item in results['tracks']['items']:
        print(
            item['track']['name'] + ' - ' +
            item['track']['artists'][0]['name']
        )
        song = item['track']['name']
        song = cleaner.cleanup(song)

        f.write(f"{song} - {item['track']['artists'][0]['name']}\n")
    f.close()
    threading.Thread(target=sp_profanity_check).start()

def sp_profanity_check():
    progress['value'] += 0
    bad_songs = []
    text_file = open("output.txt", "r")
    count = len(text_file.read().splitlines())
    text_file.seek(0)
    name = os.path.basename(text_file.name)
    if text_file is None:
        return
    run = True
    output.delete("1.0", END)
    while run is True:
        try:
            line = text_file.readline()
            print(line)
            clean = True
            if "\n" in line:
                title, artist = line.split("-")
                print(f"{title} - {artist}")
                artist.replace("\n","")
                logger.log(f'Searching for {title} - {artist}')
                search = genius.search_song(title, artist)
                if search != None:
                    lyrics = search.lyrics
                    for word in BAD_WORDS:
                        if word in lyrics.lower():
                            if var.get() == 1:
                                censor(word)
                            else:
                                output.insert(INSERT, f"CONTAINS: \"{word}\".\n\n")
                            clean = False
                            if f'{title} - {artist}' not in bad_songs:
                                bad_songs.append(f'{title} - {artist}')
                    if clean == True:
                        output.insert(INSERT, f"[{search.full_title}]  |  ")
                        output.insert(INSERT, "THIS SONG IS CLEAN!\n\n")
                else:
                    output.insert(INSERT, f"No results found. for {title} - {artist}")
                output.insert(INSERT, f"[{search.full_title}]\n\n")
                output.insert(INSERT, f"{lyrics}\n--------------------------------------\n")
                progress['value'] += 100/count
                window.update_idletasks()

            else:
                if line == "":
                    messagebox.showinfo(title="Complete", message="Lyrics found.")
                    if len(bad_songs) > 0:
                        messagebox.showwarning(title="Uh oh...", message=f"{len(bad_songs)} songs(s) contain profanity.\n{bad_songs}")   
                        messagebox.showwarning(title="Uh oh...", message=f"{len(bad_songs)} songs(s) contain profanity.\n{bad_songs}")   
                        messagebox.showwarning(title="Uh oh...", message=f"{len(bad_songs)} songs(s) contain profanity.\n{bad_songs}")   
                        break
                    
                else:
                    run = False
                    separator = "-"
                    title, artist = line.split(separator)
                    print(f"{title} - {artist}")
                    search = genius.search_song(title, artist)
                    if search != None:
                        lyrics = search.lyrics
                        for word in BAD_WORDS:
                            if word in lyrics.lower():
                                if var.get() == 1:
                                    censor(word)
                                else:
                                    output.insert(INSERT, f"CONTAINS: \"{word}\".\n\n")
                                
                                clean = False
                                if f'{title} - {artist}' not in bad_songs:
                                    bad_songs.append(f'{title} - {artist}')
                        if clean == True:
                            output.insert(INSERT, f"[{search.full_title}]  |  ")
                            output.insert(INSERT, "THIS SONG IS CLEAN!\n\n")
                    else:
                        output.insert(INSERT, f"No results found. for {title} - {artist}")
                if len(bad_songs) > 0:
                    messagebox.showwarning(title="Uh oh...", message=f"{len(bad_songs)} songs(s) are bad.\n{bad_songs}")
                progress['value'] = 100
                window.update_idletasks()
                spwindow.quit()
                break    
        except Exception as e:
            logger.log(e, 2)

def preferences(entry=None):
    '''Allows the user to change some settings.'''
    # PREFERENCE WINDOW SETUP
    pwindow = Tk()
    pwindow.title("Preferences | Lyric Checker v1.2")
    style = ThemedStyle(pwindow) 
    style.theme_use(theme)
    bg = style.lookup('TLabel', 'background')
    pwindow.configure(bg=bg)

    themes = ["black", 'arc', 'yaru', 'adapta', 'aquativo', 'breeze', 'clearlooks', 'equilux', 'radiance', 'ubuntu','classic', 'vista'] # List of all compatable themes
    fonts=list(font.families()) # All Tkinter fonts

    theme_label = ttk.Label(pwindow, text='Theme:') # Label so that preference screen is more understandable
    theme_label.grid(column=0, row=0)

    theme_choices = ttk.Combobox(pwindow, values=themes, state='readonly') # Theme selector
    theme_choices.current(0) # Default theme is "black"
    theme_choices.grid(column=1, row=0)

    font_label = ttk.Label(pwindow, text='Font:') # Label so that preference screen is more understandable
    font_label.grid(column=0, row=1)

    font_choices = ttk.Combobox(pwindow, values = fonts, state='read-only')
    font_choices.current(0)
    font_choices.grid(column=1, row = 1)

    font_size_label = ttk.Label(pwindow, text='Font Size:') # Label so that preference screen is more understandable
    font_size_label.grid(column=0, row=2)

    font_size = ttk.Entry(pwindow, width = 4)
    font_size.grid(column=1, row=2)
    font_size.insert(INSERT, '14')


    def restart():
        '''I'm not really sure '''
        ask = messagebox.askokcancel("Restart?", "To apply changes, the program will need to restart.  Okay to restart?")
        if not ask:
            pwindow.destroy()
            return
        parser = ConfigParser()
        parser.read('config.ini')
        parser.set('settings', 'theme', theme_choices.get())
        parser.set('settings', 'font', font_choices.get())
        parser.set('settings', 'font_size', font_size.get())
        
        with open('config.ini', 'w') as configfile:
            parser.write(configfile)

        window.destroy()
        pwindow.destroy()
        os.startfile("lyric_checker.py")
    button = ttk.Button(pwindow, text="Submit", command = restart)
    button.grid(column=2, row=2)

def quit():
    fade_away()

def fade_away():
    alpha = window.attributes("-alpha")
    if alpha > 0:
        alpha -= .004
        window.attributes("-alpha", alpha)
        window.after(1, fade_away)
    else:
        window.destroy()



def main_window():
    #TKINTER SETUP
    global window
    global artist
    global song
    global var
    global censor_bool
    global theme
    global progress
    window = Tk()
    style = ThemedStyle(window)
    theme = saved_theme
    style.theme_use(theme)  


    window.title("Lyric Checker | v1.2")
    window.iconbitmap("lyric checker.ico")
    my_menu = Menu(window)
    window.config(menu=my_menu)
    bg = style.lookup('TLabel', 'background')
    fg = style.lookup('TLabel', 'foreground')
    window.configure(bg=bg)
    window.resizable(0, 0)
    window.protocol("WM_DELETE_WINDOW", quit)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()




    #MENUS
    file_menu = Menu(my_menu)
    my_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open   (CTRL + O)", command=file_open)
    file_menu.add_command(label="Save as   (CTRL + S)", command=file_save)
    file_menu.add_command(label="Group check   (CTRL + G)", command = group_check)
    file_menu.add_command(label="Search with Spotify", command = spotify_window)
    
    file_menu.add_separator()
    file_menu.add_command(label="About", command=about)
    file_menu.add_command(label="Preferences   (CTRL + .)", command=preferences)
    file_menu.add_command(label="Help   (CTRL + H)", command=help)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=quit)

    #KEYBINDS
    window.bind("<Control-o>", file_open)
    window.bind("<Control-s>", file_save)
    window.bind("<Control-g>", group_check)
    window.bind("<Control-h>", help)
    window.bind("<Control-.>", preferences)
        
    #LABELS
    song_label = ttk.Label(window, text='Song:', font=(saved_font, int(saved_font_size)))
    song_label.grid(column=0, row=1)

    artist_label = ttk.Label(window, text='Artist:', font=(saved_font, int(saved_font_size)))
    artist_label.grid(column=0, row=2)

    censor_label = ttk.Label(window, text='Censor output?', font=(saved_font, int(saved_font_size)))
    censor_label.grid(column=0, row=3)
    
    #BUTTON
    s = ttk.Style()
    s.configure('my.TButton', anchor = CENTER, font=(saved_font, int(saved_font_size)))
    search = ttk.Button(window, text="Search",command=profanity_check, style='my.TButton')
    search.grid(column=2, row=2)

    var = IntVar()
    censor_bool = ttk.Checkbutton(window, variable = var)
    censor_bool.grid(column=2, row=3)
    censor_bool.configure(state="selected")


    song = ttk.Entry(window, width=80, font=(saved_font, int(saved_font_size))) # Song entry field
    song.grid(column=1, row=1)

    progress = ttk.Progressbar(window, length=70*int(saved_font_size))
    progress.grid(column=0, row=4, columnspan=3, pady=10)

    artist = ttk.Entry(window, width=80, font=(saved_font, int(saved_font_size))) # Artist entry field
    artist.grid(column=1, row=2)
    global output
    output = scrolledtext.ScrolledText(window, width=100, height=20,bg = style.lookup('TLabel', 'background'),fg = style.lookup('TLabel', 'foreground'), font = (saved_font, int(saved_font_size))) # Where the results will be shown.
    output.grid(column=0, row=5, columnspan=3)

def splashAfter():
    splash.after(3000, splashfade)
threading.Thread(target=splashAfter).start()
mainloop()
logger.log("Session closed.\n")