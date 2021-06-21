import datetime as dt

def log(message = None, Type = 1):
    if Type == 1:
        Type = "INFO"
    elif Type == 2:
        Type = "ERROR"
    elif Type == 3:
        Type = "WARNING"
    elif Type == 4:
        Type = "CRITICAL"
    f = open("lyricchecker.log", "a")
    timestamp = dt.datetime.now()
    f.write(f"[{Type}] [{timestamp}] {message}\n")
    f.close()