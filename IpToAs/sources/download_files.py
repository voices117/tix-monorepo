#!/usr/bin/python
# -*- coding: utf-8 -*-
#download_files.py
import os
import pwd
import sys
import datetime
import shutil
import urllib2
from FunIamhere import lista_archivo_server, descarga, descomGZ, descomBZ2, check_md5, parametrosGlobales, comGZ
import variables

def downloadFiles():

    baseRoot = os.path.abspath(os.path.dirname(__file__)) + '/'

    ### DEFINICION DE PARAMETROS GENERALES
    proxy_ip_port = variables.proxy
    logdir = baseRoot + variables.logdir
    descargasdir = baseRoot + variables.descargasdir
    directorioDescargaTemp = descargasdir + 'tmp/'
    
    ### directorio de trabajo

   
    #### guardar fecha actual 
    fechahora = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    today = str(datetime.date.today()).split('-')
    year = today[0]
    mes = today[1]
    dia = today[2]

    ### crea las carpetas de datos si no existen
    directorios = ('descargas/tmp', 'descargas/afrinic', 'descargas/apnic', 'descargas/arin', 'descargas/ripe', 'descargas/lacnic', 'descargas/team-1', 'descargas/team-2', 'descargas/team-3', 'descargas/asn', 'descargas/routerviews')
    for indice in directorios:
        if not os.path.exists(indice):
            os.makedirs(indice)
  
    ### config del proxy si existe
    if proxy_ip_port != '':
        proxy_support = urllib2.ProxyHandler({'http':'http://' + proxy_ip_port, 'ftp':'http://' + proxy_ip_port})
        opener = urllib2.build_opener(proxy_support,urllib2.CacheFTPHandler)
        urllib2.install_opener(opener)

   
    ### Datos server FTP de los diferentes NICs
    servidores_ftp = { 'ftp.afrinic.net':'/pub/stats/afrinic/'+year+'/', 'ftp.apnic.net':'/pub/stats/apnic/'+year+'/' , 'ftp.arin.net':'/pub/stats/arin/', 'ftp.ripe.net':'/pub/stats/ripencc/'+year+'/' , 'ftp.lacnic.net':'/pub/stats/lacnic/'}

    ### Datos de los nombres de ases
    asn = 'http://www.potaroo.net/bgp/iana/asn.txt'
  
    ### Datos caida, conexiones de as
    as_conect = ['http://data.caida.org/datasets/topology/ipv4.allpref24-aslinks/team-1/'+year+'/' , 'http://data.caida.org/datasets/topology/ipv4.allpref24-aslinks/team-2/'+year+'/' , 'http://data.caida.org/datasets/topology/ipv4.allpref24-aslinks/team-3/'+year+'/' ]

    ### Datos routerview, con las ip de los as
    routerviews = 'http://data.caida.org/datasets/routing/routeviews-prefix2as/'+year+'/' #+mes+'/' #recorrer meses


    ##### DESCARGA DE ARCHIVOS DE LOS DIFERENTES SERVIDORES
    print "Iniciando descarga"

    descarga_log = open(logdir + 'i_am_here_download_files.log', 'a+')
    print '\ndescarga todos los archivos de los servidores\n'


    ####### descarga servers ftp afrinic ripe lanic arin apnic

#    try: 
    print '--------------------------------------------'
    for servidor, carpeta in servidores_ftp.items():
        print '--------------------------------------------'
        print 'descargando servidor: ' + servidor + carpeta
        dirs1 = lista_archivo_server(servidor,carpeta,proto='ftp', proxy=proxy_ip_port)
        directorioDescargaFtp = descargasdir + servidor.split('.')[1]+'/'
        for archivo in dirs1:
            if archivo.startswith('delegated-'+servidor.split('.')[1]+'-'+year) or archivo.startswith('delegated-'+servidor.split('.')[1]+'ncc-'+year):
                if not (archivo.endswith('.asc.gz') or archivo.endswith('.asc') or archivo.endswith('asc.bz2') or archivo.endswith('md5') or archivo.endswith('md5.gz')):
                    #print directorioDescargaFtp, archivo
                    if not (os.path.isfile(directorioDescargaFtp+archivo) or os.path.isfile(directorioDescargaFtp+archivo[:-4] + '.gz') or os.path.isfile(directorioDescargaFtp+archivo + '.gz')):
                        #print archivo + '\r'

                        if archivo.endswith('.gz'):
                            nombre = archivo[:-3]
                            if descarga(servidor, carpeta, archivo, directorioDescargaTemp, proto='ftp', proxy=proxy_ip_port):
                                descomGZ(directorioDescargaTemp + archivo)
                                if descarga(servidor, carpeta, nombre + '.md5.gz', directorioDescargaTemp, proto='ftp', proxy=proxy_ip_port):
                                    descomGZ(directorioDescargaTemp + nombre + '.md5.gz')

                        elif archivo.endswith('.bz2'):
                            nombre = archivo[:-4]
                            if descarga(servidor, carpeta, archivo, directorioDescargaTemp, proto='ftp', proxy=proxy_ip_port):
                                if descarga(servidor, carpeta, nombre+'.md5', directorioDescargaTemp, proto='ftp', proxy=proxy_ip_port):
                                    descomBZ2(directorioDescargaTemp + archivo)
                                    comGZ(directorioDescargaTemp + nombre)
                                    os.remove(directorioDescargaTemp + archivo)
                                    archivo = nombre + '.gz'

                        else:
                            nombre = archivo
                            archivo = archivo + '.gz'
                            if descarga(servidor, carpeta, nombre, directorioDescargaTemp, proto='ftp', proxy=proxy_ip_port):
                                if descarga(servidor, carpeta, nombre + '.md5', directorioDescargaTemp, proto='ftp', proxy=proxy_ip_port):
                                    comGZ(directorioDescargaTemp + nombre)

                        if os.path.isfile(directorioDescargaTemp + nombre) and os.path.isfile(directorioDescargaTemp + nombre + '.md5'):
                            verif=check_md5(directorioDescargaTemp + nombre)
                            if verif=='True':
                                shutil.copy2(directorioDescargaTemp + archivo, directorioDescargaFtp)
                                #if os.path.isfile(directorioDescargaFtp + archivo):
                                 #   os.chown(directorioDescargaFtp + archivo, uid, gid)

                        print(os.path.isdir(directorioDescargaTemp))
                        if  len(os.listdir(directorioDescargaTemp)) != 0:
                            rmfiles = os.listdir(directorioDescargaTemp)
                            for rmfile in rmfiles:
                                os.remove(directorioDescargaTemp + rmfile)
#    except:
#        descarga_log.write( fechahora + '\t' + servidor + ' DOWNLOAD FAIL' + '\n' )
      
               
    #### Descargar caida team
    print '--------------------------------------------'
    print 'descarga team'
    try:
        for servidor in as_conect:
            archivos = lista_archivo_server(servidor, proto='http')
            directorioDescargaTeam = descargasdir + servidor.split('/')[-3] + '/'
            for archivoteam in archivos:
                if not os.path.isfile(directorioDescargaTeam + archivoteam):  
                    descarga(server=servidor, archivo=archivoteam, destino=directorioDescargaTemp, proto='http', proxy=proxy_ip_port)
                    shutil.copy2(directorioDescargaTemp + archivoteam, directorioDescargaTeam)
                    #if os.path.isfile(directorioDescargaTeam + archivoteam):
                     #   os.chown(directorioDescargaTeam + archivoteam, uid, gid)
                    os.remove(directorioDescargaTemp + archivoteam)
    except:
        descarga_log.write( fechahora + '\t' + servidor[-12:-6] + '--' + ' DOWNLOAD FAIL' + '\n' )

	  
    ### Descargar asn
    print '--------------------------------------------'
    print 'descarga asn'
    try:
        directorioDescargaAsn = descargasdir + 'asn/'
        nombre = 'asn' + year + mes + dia
        nombrecomp = nombre + '.gz'
        if not os.path.isfile(directorioDescargaAsn + nombrecomp):
            descarga(server=asn[:-7], archivo=asn[-7:], destino=directorioDescargaTemp, proto='http', proxy=proxy_ip_port)
            os.rename(directorioDescargaTemp+asn[-7:], directorioDescargaTemp+nombre)
            comGZ(directorioDescargaTemp + nombre)
            shutil.copy2(directorioDescargaTemp + nombrecomp, directorioDescargaAsn)
            #if os.path.isfile(directorioDescargaAsn + nombrecomp):
            #    os.chown(directorioDescargaAsn + nombrecomp, uid, gid)
            os.remove(directorioDescargaTemp + nombre)
            os.remove(directorioDescargaTemp + nombrecomp)

    except:
        descarga_log.write( fechahora + '\t' + '--' + ' asn DOWNLOAD FAIL' + '\n' )


    ### Descargar routerview
    print '--------------------------------------------'
    print 'descarga routerview'
    try:
        directoriosRV=lista_archivo_server(routerviews, proto='http')
        directorioDescargaRV = descargasdir + 'routerviews/'
        for directorio in directoriosRV:
            archivosRV = lista_archivo_server(routerviews + directorio, proto='http')
            for fileRV in archivosRV:
                if not os.path.isfile(directorioDescargaRV+fileRV):
                    descarga(server=routerviews+directorio, archivo=fileRV, destino=directorioDescargaTemp, proto='http', proxy=proxy_ip_port)
                    shutil.copy2(directorioDescargaTemp+fileRV, directorioDescargaRV)
                    #if os.path.isfile(directorioDescargaRV + fileRV):
                     #   os.chown(directorioDescargaRV + fileRV, uid, gid)

                    os.remove(directorioDescargaTemp+fileRV)
    except:
        descarga_log.write(fechahora + '\t' + '--' + ' routerview DOWNLOAD FAIL' + '\n' )


if __name__ == '__main__':
    downloadFiles()
