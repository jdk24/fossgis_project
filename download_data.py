if(PY2):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

x = urlopen("https://de.wikipedia.org/wiki/Deutschland")
print()



