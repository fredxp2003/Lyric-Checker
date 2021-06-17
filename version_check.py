import requests
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from tkinter import messagebox
from tkinter import *



url = "https://fredxp2003.github.io/download"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


response = requests.get(url, headers=headers)
print(response)
wbst = soup(response.text, "html.parser")
verSection = wbst.find("p")
verString = verSection.text
ver = verString.replace("Current Version: ","")
ver = float(ver)

f = open("ver.txt", "r")
currentStr = f.read()
current = float(currentStr)

if ver == current:
    print("same")
elif ver > current:
    print("Needs updates")
    messagebox.showwarning(title="Updates Needed", message=f"Lyric Checker is out of date.\nYour current version is {current}.  Please update to {ver} to keep compatibility.  Updates can be found at https://fredxp2003.github.io/download.")
    window = Tk()
    window.quit()