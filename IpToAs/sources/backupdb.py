#!/usr/bin/python

import os
import time
import shutil

def backupdb():
    # START: configuration
    username = 'daniel'
    password = 't22mo'
    hostname = 'localhost'
    dest_folder = '/var/www/lanet-vi.fi.uba.ar/dbassr'
    database = 'iamheredb'
    # END: configuration

    # timestamp
    filestamp = time.strftime('%Y%m%d')
    database_list_command="mysql -u%s -p%s -h %s --silent -N -e 'show databases'" % (username, password, hostname)
    filename = "%s/%s-%s.sql" % (dest_folder, filestamp, database)
    lastfilenamegz = "%s/last_%s-%s.sql.gz" % (dest_folder, filestamp, database)
    #print filename
    #print lastfilenamegz

    os.popen("mysqldump -u%s -p%s -h %s -e --opt -c %s | gzip -c > %s.gz" % (username, password, hostname, database, filename))

    shutil.copy2(filename + '.gz', lastfilenamegz)

if __name__ == '__main__':
    backupdb()
