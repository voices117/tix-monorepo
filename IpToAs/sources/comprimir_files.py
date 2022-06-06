#!/usr/bin/python
from FunIamhere import comGZ
import os

def compFilesInFolder(folder):
    lst = os.listdir(folder)
    for arch in lst:
        if not arch.endswith('.gz'):
            comGZ(folder + arch)
            os.remove(folder + arch)

if __name__ == '__main__':
    descargasdir = '/home/daniel/Documents/descargas/'

    folders = [descargasdir + 'afrinic/', descargasdir + 'lacnic/', descargasdir + 'arin/', descargasdir + 'ripe/', descargasdir + 'apnic/', descargasdir + 'asn/', descargasdir + 'routerviews/', descargasdir + 'team-1/', descargasdir + 'team-2/', descargasdir + 'team-3/']

    for folder in folders:
        compFilesInFolder(folder)
