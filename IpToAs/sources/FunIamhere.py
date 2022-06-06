#!/usr/bin/python
# -*- coding: utf-8 -*-
#FunIamhere
from sgmllib import SGMLParser
import os
import sys
import urllib2
from ftplib import FTP
import hashlib
import gzip
import bz2
import re
from datetime import timedelta, date, datetime
from unicodedata import normalize

#parser para obtener los archivos de descarga disponibles en una pagina web saca los href
class Parser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []

    def start_a(self, attrs):
        href = [v for k, v in attrs if k=='href']
        if href:
            self.urls.extend(href)


####eliminar elementos repetidos de una lista y/o devuelve ordenados alfabeticamente

    ### No ordena alfabeticamente
def ordena(lista):
    '''
    ordena(lista)
    lista: una lista de elementos 
    retorna una lista de elementos no repetidos 
    '''
    setOrdFilt = list(set(lista))
    return setOrdFilt

    ### Ordena Alfabeticamente
def ordena_1(lista):
    '''
    ordena_1(lista)
    lista: una lista de elementos 
    retorna una lista de elementos no repetidos ordenados alfabeticamente 
    '''
    lstOrdFilt = sorted(list(set(lista)))
    return lstOrdFilt


### filtra datos mostrando solo dos columnas con los as archivos obtenidos de caida
def filtrar_datos_caida(origen,destino='red.txt'):
    '''
    filtrar_datos(origen,destino)
    origen: lista con path y nombre archivo a filtrar
    destino: path y nombre del archivo filtrado
    '''
    lst_conc=concatena(origen)
    lstTeam=ordena(lst_conc)
    fichero_out=open(destino,'wb')
    for j in lstTeam:
        #print j
        if j.startswith('D') or j.startswith('I'): 
            as1=j.split()[1]
            as2=j.split()[2]
            if len(as1.split('_'))==1 and len(as2.split('_'))==1:
                if len(as1.split('.'))==1 and len(as2.split('.'))==1:
                    if len(as1.split(','))==1 and len(as2.split(','))==1:
                        #print as1+'   '+as2
                        fichero_out.write(as1+'\t'+as2+'\n')    
    fichero_out.close() 
    return True
      

### concatena archivos
def concatena(listaArchivos):
    listaConcatenada=[]
    for archivo in listaArchivos:
        fileIN=open(archivo,'rb')
        listaConcatenada += fileIN.readlines()
    fileIN.close()
    return listaConcatenada

#check MD5
def check_md5(archivo):
    check='False'
    if  os.path.isfile(archivo) and os.path.isfile(archivo+'.md5'):
        md5=hashlib.md5()
        fileAux=open(archivo, 'rb')
      
        for line in fileAux:
            md5.update(line)
            f=open(archivo+'.md5', 'rb')
            m=re.findall(r'\w{32}',f.readline())
   
            if m and md5.hexdigest() == m[0]:
                check='True'
            #    print 'check md5... ok\n'
            #else:
            #    print 'check md5... bad\n' 
            f.close()
        fileAux.close()
    #else:
        #print 'check md5... bad\n' 
    if check:
         print 'check md5 ... ok\n'
    else:
        print 'check md5 ... ok\n'
    return check

### comprimir archivo en gz
def comGZ(archivoIN, archivoOUT=''):
    if not os.path.exists(archivoIN):
        print 'archivo no existe'
        return False
    f_in = open(archivoIN, 'rb')
    if archivoOUT == '':
        archivoOUT = archivoIN + '.gz'
    elif not archivoOUT.endswith('.gz'):
        archivoOUT = archivoOUT + '.gz'
    f_out = gzip.open(archivoOUT, 'wb')     
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()


### descomprimir archivos .gz 
def descomGZ(archivoIN, archivoOUT=''):
    #print 'descomprimiendo archivo...\n'
    if not os.path.exists(archivoIN):
        print 'archivo no existe'
        return False
    if not archivoIN.endswith('.gz'):
        print 'archivo no es .gz'
        return False 
    if archivoOUT == '':
        archivoOUT = archivoIN[:-3]
    if archivoOUT.endswith('.gz'):
        archivoOUT = archivoOUT[:-3]
    inF = gzip.GzipFile(archivoIN, 'rb');
    s=inF.read()
    inF.close()
    outF = open(archivoOUT, 'wb');
    outF.write(s)
    outF.close()
    return True

### comprimir archivo en .bz2
def comBZ2(archivoIN, archivoOUT=''):
    if not os.path.exists(archivoIN):
        print 'archivo no existe'
        return False
    f_in = open(archivoIN, 'rb')
    if archivoOUT == '':
        archivoOUT = archivoIN + '.bz2'
    elif not archivoOUT.endswith('.bz2'):
        archivoOUT = archivoOUT + '.bz2'
    f_out = bz2.BZ2File(archivoOUT + '.bz2', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()

### descomprimir archivos .bz2 
def descomBZ2(archivoIN, archivoOUT=''):
    #print 'descomprimiendo archivo...\n'
    if not os.path.exists(archivoIN):
        print 'archivo no existe'
        return False
    if not archivoIN.endswith('.bz2'):
        print 'archivo no es .bz2'
        return False
    if archivoOUT == '':
        archivoOUT = archivoIN[:-4]
    if archivoOUT.endswith('.bz2'):
        archivoOUT = archivoOUT[:-4]
    inF = bz2.BZ2File(archivoIN, 'rb')
    s=inF.read()
    inF.close()
    outF = open(archivoOUT, 'wb');
    outF.write(s)
    outF.close()
    return True


### descarga de archivos
def descarga(server,carpeta=[],archivo=[], destino=os.getcwd(), proto='ftp', proxy=''):
    print 'descargando archivo: ' + archivo + ' ...\n'

    if proto == 'http':
        try:
            webFile = urllib2.urlopen(server + archivo)
            localFile = open(destino + archivo, 'wb' )
            localFile.write(webFile.read())
            webFile.close()
            localFile.close()    
            return True
        except:
            print 'error en la descarga' 
            try: 
                os.remove( destino + archivo )
                return False
            except:
                return False
 
    if not proxy =='':
        if proto == 'ftp':
            try:
                ftpFile = urllib2.urlopen('ftp://' + server + carpeta + archivo )
                localFile = open( destino + archivo, 'wb' )
                localFile.write(ftpFile.read())
                ftpFile.close()
                localFile.close()
                return True
            except:
                print 'no se pudo realizar la descarga' 
                try: 
                    os.remove( destino + archivo )
                    return False
                except:
                    return False

    else:
        if proto == 'ftp':
            try:
                ftp = FTP(server)
                ftp.login()
                ftp.cwd(carpeta)
                ftp.retrbinary('RETR ' + archivo, open(destino + archivo,'wb').write)
                ftp.quit()
                return True
            except:
                print 'no se pudo realizar la descarga'
                try: 
                    os.remove( destino + archivo )
                    return False
                except:
                    return False
 
     
### genera una lista de archivos para descargar de los diferentes lugares
def lista_archivo_server(server,carpeta=[],proto='ftp', proxy=''):
    '''
    server: es la direccion url del servidor 
    carpeta: es la carpeta del servidor 
    proto: protocolo ftp o http
    retorna una lista con los nombres de los archivos disponibles para descargar
    si no encuentra nada retorna una lista vacia
    '''

    dirs=[]

    if proto == 'http':
        #print 'Obteniendo lista de archivos del servidor http: ' + server + '...\n'
        try:
            URLv = urllib2.urlopen(server)
            DownloadURL = Parser()
            DownloadURL.feed(URLv.read())
            DownloadURL.close()
            URLv.close()
            dirs = DownloadURL.urls[5:]
        except:
            print 'no se pudo listar los archivos'

    if not proxy == '':
        try:

            if proto == 'ftp':
                #print 'Obteniendo lista de archivos del servidor: ' + server + '...\n'
                URLf = urllib2.urlopen('ftp://'+server+carpeta)
                DownloadURL = Parser()
                DownloadURL.feed(URLf.read())
                dirsaux = DownloadURL.urls
                URLf.close()
                DownloadURL.close()
                for i in dirsaux:
                    aux2=i.split(';')[0]
                    dirs.append(aux2) 
                dirs=ordena_1(dirs)

        except:
            print 'server caido no se pudo listar los archivos'

    else:
        try:
            if proto == 'ftp':
                ftp = FTP(server)
                ftp.login()
                ftp.cwd(carpeta)
                dirs = ftp.nlst()
                ftp.quit()
        except:
            print 'server caido o no se pudo listar los archivos'
 
    return dirs

########################################################
# parametros globales usados en los diferentes scripts #
########################################################

def parametrosGlobales():
    dirTrabajo = os.path.abspath(os.path.dirname(__file__)) + '/'
    try:
        dicVariables={}
        archivoVariables = open(dirTrabajo + "variables.conf", "r")
        lista_conf = archivoVariables.readlines()
        for linea in lista_conf:
            linea = linea.strip()
            if not (linea.startswith('#') or linea.startswith('\n') or linea == ''):
                if ( ('=' in linea) and (linea.startswith('proxy') or linea.startswith('dias')) ) or ( ('=' in linea) and (linea.endswith('/')) ):
                  #  print linea.split('=')
                    parametro = linea.split('=')
                    dicVariables[parametro[0].strip()] = parametro[1].strip()
                else:
                    print 'los directorios deben terminar con slash (/) o variable dias o proxy no estan definidos\n las variables que deven existir son: cgi_datos_dir, redesdir, mapasdir,\n lanetvidir, lanetvilogdir, logdir, descargasdir,dias, proxy'
                    exit(1)
                    
        return dicVariables

    except:
        print 'error en variables.conf'
            
##########################################        
# unir un string con una lista de string #
##########################################
def str_mas_lista_str(cadena,lstcadena):
    salida=[]
    for element in lstcadena:
        salida.append(cadena+element)
    return salida


###############################################################################
# combina dos diccionarios
###############################################################################
def complementa_dic(diccionario1, diccionario2):
    '''
    la funcion toma dos diccionarios y devuelve uno nuevo
    si la clave de un diccionario no esta en el otro se agrega, si la clave existe y los valores
    son diferentes se agrega los valores que no existen
    '''
    diccionarioOut = diccionario1.copy()
    for elemento in diccionario2:
        if elemento not in diccionario1:
            diccionarioOut[elemento] = diccionario2[elemento]
        else:
            valores1 = diccionario1[elemento]
            valores2 = diccionario2[elemento]
            valor = list(set(valores1) | set(valores2))
            diccionarioOut[elemento] = valor
    return diccionarioOut


#######################################################
# selector de archivos fechados de los ultimos x dias #
#######################################################
def selectforlastdays(carpeta, days, separador, ubicacionfecha):
    '''
    la fecha debe estar en formato, year, month, day y de forma completa 20130501
    carpeta: carpeta donde se encuantran los archivos
    days(int): cantidad de dias de los archivos con los que me quedo una semana = 7
    separador: para hacer el split con que caracter separar
    ubucacionfecha: en que posicion se encuentra la fecha se puede usar indice negativo
    '''
    listaArchivos=sorted(os.listdir(carpeta), reverse = True)[:days]
    #print listaArchivos
    hoy = date.today()
    intervalo = hoy - timedelta(days=days)
    listaFILES = []
    for archivo in listaArchivos:
        datofecha = archivo.split(separador)[ubicacionfecha]
        fecha = datofecha[:4] + '-' + datofecha[4:6] + '-' + datofecha[6:8]
        fechatime = datetime.strptime(fecha, "%Y-%m-%d").date()
        if fechatime > intervalo:
            listaFILES.append(archivo)
    return listaFILES




def normalizar_string(unicode_string):
    u"""Retorna unicode_string sin normalizado para efectuar una búsqueda respetando mayúsculas y minúsculas.

    >>> normalizar_string(u'ñandú')
    'nandu'
    
    """
    return normalize('NFKD', unicode_string).encode('ASCII', 'ignore')


if __name__ == '__main__':
#    pass
    print parametrosGlobales()
    
    #comGZ('/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/routeviews', archivoOUT='tmp/routerviews.gz')
    #comBZ2('/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/routeviews', archivoOUT='tmp/routerviews.bz2')
    #print selectforlastdays('/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/descargas/ripe/', 7, '-', -1)
    #print selectforlastdays('/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/descargas/team-1/', 30, '.', -2)
    

### probar str_mas_lista_str
    #print str_mas_lista_str('dani',['1','2','3','hola0'])

### probar ordenar listas  
    #print ordena([9,8,7,6,5,4]) 
    
### probar listar archivos del server para descargar
    #print lista_archivo_server('http://data.caida.org/datasets/routing/routeviews-prefix2as/2013/',proto='http')

### probar filtrar los datos de los team de caida
    #cgi_datos_dir= '/var/www/lanet-vi.fi.uba.ar/i_am_here/i_am_here_cgi/datos/'
    #lista_concatenar = [cgi_datos_dir + 'team-1', cgi_datos_dir + 'team-2', cgi_datos_dir + 'team-3']
    #print filtrar_datos(lista_concatenar)

### probar parametros globales
    #dicparametros = parametrosGlobales()
    #a = dicparametros['cgi_datos_dir']
    #print a
