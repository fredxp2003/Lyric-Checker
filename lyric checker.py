from tkinter import *
from tkinter import scrolledtext, filedialog, messagebox
import webbrowser
import lyricsgenius
import version_check
import os
import sys



#Sorry about this next line :/
BAD_WORDS = ["BITCH", "ASS", "BASTARD", "SHIT", "FUCK", "COCK", 'CUNT', 'NIGGER', 'NIGGA', 'PENIS', 'PUSSY', 'DICK', 'TIT', 'BOOB', 'THOT', 'HELL', 'DAMN', 'PISS', 'SEX', 'SLUT']

#Information for Genius API.  Removed for open-source.
key = ""
secret = ""
token = "" 

def about():
    '''
    Opens a small messagebox with some information
    '''
    messagebox.showinfo(title="About Lyric Checker", message="Created by Fredxp2003 on Github\n\nFor help, click the help menu option, or go to https://fredxp2003.github.io")
    
def help():
    '''
    Opens help website
    '''
    webbrowser.open('https://fredxp2003.github.io', new=2)

#Iterated through each word that would be flagged as explicit
#Change the first and last letter of each word to a '*'
#Output the changed word
def censor(word):
    try:
        for letters in word:
            if(word == "ASS"):
                word = "A**S"
            elif(letters == word[0] or letters == word[-1]):
                pass
            else:
                word = word.replace(word[word.index(letters)], "*")
    except:
        pass
    finally:
        output.insert(INSERT, f"CONTAINS: \"{word}\".\n\n")



def file_open():
    text_file = filedialog.askopenfile(title = "Select file", filetypes = (("Text files","*.txt"), ("All files", "*.*")))
    print(text_file)

    if text_file is None:
        return
    output.delete("1.0", END)
    stuff = text_file.read()
    output.insert(END, stuff)
    text_file.close()

def file_save():
    f = filedialog.asksaveasfile(title = "Select file",filetypes = (("Text files","*.txt"), ("All files", "*.*")))

    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = str(output.get(1.0, END)) # starts from `1.0`, not `0.0`
    try:
        f.write(text2save)
    except Exception as e:
        messagebox.showerror(title="Failed to save", message="Was unable to save this file.")
    f.close() # `()` was missing.

def group_check():
    text_file = filedialog.askopenfile(title = "Select file", filetypes = (("Compatible files","*.txt *.csv"), ("All files", "*.*")))
    name = os.path.basename(text_file.name)
    if text_file is None:
        return
    run = True
    output.delete("1.0", END)
    while run is True:
        line = text_file.readline()
        print(line)
        clean = True
        if "\n" in line:
            run = True
            separator = "-"
            title, artist = line.split(separator)
            print(f"{title} - {artist}")
            search = genius.search_song(title, artist)
            if search != None:
                lyrics = search.lyrics
                for word in BAD_WORDS:
                    if word in lyrics.upper():
                        censor(word)
                        clean = False
                if clean == True:
                    output.insert(INSERT, f"[{search.full_title}]  |  ")
                    output.insert(INSERT, "THIS SONG IS CLEAN!\n\n")
            else:
                output.insert(INSERT, f"No results found. for {title} - {artist}")
            output.insert(INSERT, f"[{search.full_title}]\n\n")
            output.insert(INSERT, f"{lyrics}\n--------------------------------------\n")

        else:
            run = False
            separator = "-"
            title, artist = line.split(separator)
            print(f"{title} - {artist}")
            search = genius.search_song(title, artist)
            if search != None:
                lyrics = search.lyrics
                for word in BAD_WORDS:
                    if word in lyrics.upper():
                        censor(word)
                        
                        clean = False
                if clean == True:
                    output.insert(INSERT, f"[{search.full_title}]  |  ")
                    output.insert(INSERT, "THIS SONG IS CLEAN!\n\n")
            else:
                output.insert(INSERT, f"No results found. for {title} - {artist}")
            
            output.insert(INSERT, f"{lyrics}\n\n")
            messagebox.showinfo(title="Complete", message="Lyrics found.")
            break
        

genius = lyricsgenius.Genius(token)
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
                if word in lyrics.upper():
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

window.title("Lyric Checker")
my_menu = Menu(window)
window.config(menu=my_menu)

#MENUS
file_menu = Menu(my_menu)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open...", command=file_open)
file_menu.add_command(label="Save as...", command=file_save)
file_menu.add_command(label="Group check...", command = group_check)
file_menu.add_separator()
file_menu.add_command(label="About...", command=about)
file_menu.add_command(label="Help...", command=help)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=window.quit)

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
