import requests
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from tkinter import messagebox
from tkinter import *
import logger
import threading

logger.log("Session open.")

url = "https://fredxp2003.github.io/download"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def vercheck():
    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        messagebox.showerror("No Internet Connection", "Unable to connect to the Internet.  Lyric Checker needs an Internet connection to work.")
        logger.log("No Internet connection.", 4)
        logger.log("Session closed.\n")
        return
    logger.log("Checking current version...")
    print(response)
    wbst = soup(response.text, "html.parser")
    verSection = wbst.find("p")
    verString = verSection.text
    ver = verString.replace("Current Version: ","")
    ver = float(ver)
    logger.log(f"Current version {ver}")

    f = open("ver.txt", "r")
    logger.log("Checking local version...")
    currentStr = f.read()
    current = float(currentStr)

    if ver == current:
        print("same")
        logger.log(f"Program is up to date.  Version = {ver}")
    elif ver > current:
        print("Needs updates")
        logger.log(f"Program is not up to date.  Version = {ver}.  Newest version = {current}", 2)
        messagebox.showwarning(title="Updates Needed", message=f"Lyric Checker is out of date.\nYour current version is {current}.  Please update to {ver} to keep compatibility.  Updates can be found at https://fredxp2003.github.io/download.")
        window = Tk()
        window.quit()

threading.Thread(target=vercheck()).start()