import string

numbers = string.digits

def cleanup(song):
    song = song.replace("Remastered","")
    song = song.replace("Remaster","")
    song = song.replace(";","")
    song = song.replace("\"","")
    song = song.replace("\'","")
    song = song.replace("(","")
    song = song.replace(")","")
    song = song.replace("Mix","")
    song = song.replace("Single Version","")
    song = song.replace("Mono","")
    song = song.replace("-", "")
    song = song.replace("th ", "")
    song = song.replace("Original Stereo Version", "")
    song = song.replace("Stereo Version", "")
    song = song.replace("Version", "")
    song = song.replace("Extended", "")
    song = song.replace("Anniversary", "")
    song = song.replace("Edition", "")

    


    for number in numbers:
        if number in song:
            song = song.replace(number,"")
    return song

def url_cleanup(url):
    url = url[34:]
    url = url[:22]
    return url