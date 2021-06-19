from tkinter import *
from tkinter import scrolledtext, filedialog, messagebox
import webbrowser
import lyricsgenius
import os
import sys
import requests

# Local Files
import version_check
import excel_convert as ex
import config


response = requests.get("https://raw.githubusercontent.com/RobertJGabriel/Google-profanity-words/master/list.txt")
BAD_WORDS = response.text.splitlines()
BAD_WORDS.remove("nob")
BAD_WORDS = [w.replace("ass", " ass") for w in BAD_WORDS]

# Information for Genius API.  Removed for open-source.
# Enter your API token into config.py
token = config.token
genius = lyricsgenius.Genius(token)

def about(event = None):
    '''
    Opens a small messagebox with some information
    '''
    messagebox.showinfo(title="About Lyric Checker", message="Version: 1.1-beta (This is not a stable release)\nCreated by Fredxp2003 on Github\n\nFor help, click the help menu option, or go to https://fredxp2003.github.io")
    
    '''
    Opens help website
    '''
    webbrowser.open('https://fredxp2003.github.io', new=2)

# Iterated through each word that would be flagged as explicit
# Change the first and last letter of each word to a '*'
# Output the changed word
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
        output.insert(INSERT, f"CONTAINS: \"{word}\".\n\n")



def file_open(event = None):
    text_file = filedialog.askopenfile(title = "Select file", filetypes = (("Text files","*.txt"), ("All files", "*.*")))
    print(text_file)

    if text_file is None:
        return
    output.delete("1.0", END)
    stuff = text_file.read()
    output.insert(END, stuff)
    text_file.close()

def file_save(event = None):
    f = filedialog.asksaveasfile(title = "Select file",filetypes = (("Text files","*.txt"), ("All files", "*.*")))

    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = str(output.get(1.0, END)) # starts from `1.0`, not `0.0`
    try:
        f.write(text2save)
    except Exception as e:
        messagebox.showerror(title="Failed to save", message="Was unable to save this file.")
    f.close() # `()` was missing.

def group_check(event = None):
    bad_songs = []
    excel = False
    text_file = filedialog.askopenfile(title = "Select file", filetypes = (("Compatible files","*.txt *.csv *.xlsx"), ("All files", "*.*")))
    name = os.path.basename(text_file.name)
    path = os.path.realpath(text_file.name)
    if text_file is None:
        return
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
            title, artist = line.split(separator)
            print(f"{title} - {artist}")
            search = genius.search_song(title, artist)
            if search != None:
                lyrics = search.lyrics
                for word in BAD_WORDS:
                    if word in lyrics.lower():
                        censor(word)
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

        else:
            if line == "":
                output.insert(INSERT, f"{lyrics}\n\n")
                messagebox.showinfo(title="Complete", message="Lyrics found.")
                if len(bad_songs) > 0:
                    messagebox.showwaring(title="Uh oh...", message=f"{len(bad_songs)} songs(s) contain profanity.\n{bad_songs}")
                
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
                search = genius.search_song(title, artist)
                if search != None:
                    lyrics = search.lyrics
                    for word in BAD_WORDS:
                        if word in lyrics.lower():
                            censor(word)
                            
                            clean = False
                            if f'{title} - {artist}' not in bad_songs:
                                bad_songs.append(f'{title} - {artist}')
                    if clean == True:
                        output.insert(INSERT, f"[{search.full_title}]  |  ")
                        output.insert(INSERT, "THIS SONG IS CLEAN!\n\n")
                else:
                    output.insert(INSERT, f"No results found. for {title} - {artist}")
            output.insert(INSERT, f"{lyrics}\n\n")
            messagebox.showinfo(title="Complete", message="Lyrics found.")
            if len(bad_songs) > 0:
                messagebox.showwarning(title="Uh oh...", message=f"{len(bad_songs)} songs(s) are bad.\n{bad_songs}")
            
            if excel:
                text_file.close()
                os.remove(name)
            break     

def profanity_check():
    output.delete(1.0,END)
    clean = True

    ARTIST = artist.get()
    TITLE = song.get() 

    if TITLE == "":
        output.insert(INSERT, "Title cannot be left blank.")
    else:
        search = genius.search_song(TITLE, ARTIST)
        if search != None:
            lyrics = search.lyrics
            for word in BAD_WORDS:
                if word in lyrics.lower():
                    censor(word)
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


#TKINTER SETUP
window = Tk()

window.title("Lyric Checker | v1.1-beta")
my_menu = Menu(window)
window.config(menu=my_menu)

#MENUS
file_menu = Menu(my_menu)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open   (CTRL + O)", command=file_open)
file_menu.add_command(label="Save as   (CTRL + S)", command=file_save)
file_menu.add_command(label="Group check   (CTRL + G)", command = group_check)
file_menu.add_separator()
file_menu.add_command(label="About   (CTRL + A)", command=about)
file_menu.add_command(label="Help   (CTRL + H)", command=help)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=window.quit)

#KEYBINDS
window.bind("<Control-o>", file_open)
window.bind("<Control-s>", file_save)
window.bind("<Control-g>", group_check)
window.bind("<Control-a>", about)
window.bind("<Control-h>", help)

#LABELS
song_label = Label(window, text='Song:')
song_label.grid(column=0, row=1)

artist_label = Label(window, text='Artist:')
artist_label.grid(column=0, row=2)


search = Button(window, text="Search",command=profanity_check)
search.grid(column=2, row=2)

song = Entry(window, width=60) #song entry field
song.grid(column=1, row=1)


artist = Entry(window, width=60) #artist entry field
artist.grid(column=1, row=2)

output = scrolledtext.ScrolledText(window, width=100, height=20) #where the results will be shown.
output.grid(column=0, row=3, columnspan=3)

window.mainloop()