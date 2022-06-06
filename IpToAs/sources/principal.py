#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pwd
import datetime
import shutil
from FunIamhere import parametrosGlobales, selectforlastdays, str_mas_lista_str, descomGZ, normalizar_string
from gen_red import genred
from creaDBiamhere import reddb, reddbtmp, paisdb, paisdbtmp, nombreasdb, nombreasdbtmp, nicdb, routerviewdb, findnodospais, findnodosname, nodos_x_pais_o_nic, selectpaisname
from concatenar_files import *
from gen_mapas import genmapas
import backupdb
import variables

##########################################
# Parametros globales ver variables.py #
##########################################
dirTrabajo = os.path.abspath(os.path.dirname(__file__)) + '/'
cgi_datos_dir = dirTrabajo + variables.cgi_datos_dir
lanetvidir = dirTrabajo + variables.lanetvidir
lanetvilogdir = dirTrabajo + variables.lanetvilogdir
descargasdir = dirTrabajo + variables.descargasdir
logdir = dirTrabajo + variables.logdir
mapasdir = dirTrabajo + variables.mapasdir
redesdir = dirTrabajo + variables.redesdir

printmpdir = dirTrabajo + 'tmp/'
redesdir = dirTrabajo + 'redes/'
listanics = ['afrinic', 'apnic', 'arin', 'lacnic', 'ripe']

########################
# guardar fecha actual #
########################
fechahora = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
today = str(datetime.date.today()).split('-')
year = today[0]
mes = today[1]
dia = today[2]

#crea las carpetas de datos si no existen
directorios=('tmp', logdir, 'redes', 'log')
for indice in directorios:
    if not os.path.exists(indice):
        os.makedirs(indice)
        #os.chown(indice, uid, gid)


##activo log
log_principal = open(logdir + 'i_am_here_principal.log', "a")

###################################
### GENERO LOS ARCHIVOS NECESARIOS#
###################################
cantidad = int(variables.dias) # cantidad de dias que voy a concatenar los archivos
cgi_datos_dir_tmp = printmpdir + 'cgi_dato_dir_tmp' + '/'
if os.path.isdir(cgi_datos_dir_tmp):
    shutil.rmtree(cgi_datos_dir_tmp)
os.mkdir(cgi_datos_dir_tmp)

def concateno():
    ### concatenos los nic
    #######################
    for nic in listanics:
        listaArchivosnic = selectforlastdays(descargasdir + nic + '/', cantidad, '-', -1)
        dirlistaArchivosnic = str_mas_lista_str(dirTrabajo + 'descargas/' + nic + '/', listaArchivosnic)
        
        printmpdirnic = printmpdir + nic + '/'
        if os.path.isdir(printmpdirnic):
            shutil.rmtree(printmpdirnic, ignore_errors=True)
        os.mkdir(printmpdirnic)    

        tmplistaArchivosnic =  []
        for archGZ in dirlistaArchivosnic:
            shutil.copy2(archGZ, printmpdirnic)
            descomGZ(printmpdirnic + archGZ.split('/')[-1])
            os.remove(printmpdirnic + archGZ.split('/')[-1])
            tmplistaArchivosnic.append(printmpdirnic + archGZ.split('/')[-1][:-3])
        #print tmplistaArchivosnic
        
        if concatenar_nic(tmplistaArchivosnic, cgi_datos_dir_tmp + nic):
            print 'concatenado nic ' + nic
            shutil.rmtree(printmpdirnic, ignore_errors=True)
        else:
            print 'error concatenar nic '  + nic
            log_principal.write(fechahora + '\t error concatenar nic '  + nic + '\n')
            log_principal.close()
            shutil.rmtree(printmpdirnic, ignore_errors=True)
            exit(1)

    ###concateno los nombres de as
    ##############################
    listaArchivosASN = selectforlastdays(descargasdir + 'asn/', cantidad, 'asn', -1)
    #print listaArchivosASN
    dirlistaArchivosASN = str_mas_lista_str(descargasdir + 'asn/', listaArchivosASN)

    printmpdirAsn = printmpdir + 'Asn' + '/'
    if os.path.isdir(printmpdirAsn):
        shutil.rmtree(printmpdirAsn, ignore_errors=True)
    os.mkdir(printmpdirAsn)    

    tmplistaArchivosASN =  []
    for archGZ in dirlistaArchivosASN:
        shutil.copy2(archGZ, printmpdirAsn)
        descomGZ(printmpdirAsn + archGZ.split('/')[-1])
        os.remove(printmpdirAsn + archGZ.split('/')[-1])
        tmplistaArchivosASN.append(printmpdirAsn + archGZ.split('/')[-1][:-3])
    #print tmplistaArchivosASN

    if concatenar_asn(tmplistaArchivosASN, cgi_datos_dir_tmp + 'asn'):
        print 'concatenado asn'
        shutil.rmtree(printmpdirAsn, ignore_errors=True)

    else:
        print 'error concatenar asn'
        log_principal.write(fechahora + '\t error concatenar asn \n')
        log_principal.close()
        exit(1)

    ###concateno routerviews
    ########################
    #routeviews-rv2-20130508-1200.pfx2as.gz
    listaArchivosRouter = selectforlastdays(descargasdir + 'routerviews/', cantidad, '-', -2)
    #print listaArchivosRouter
    dirlistaArchivosRouter = str_mas_lista_str(descargasdir + 'routerviews/', listaArchivosRouter)
    printmpdirRv = printmpdir + 'Rv'+'/'
    if os.path.isdir(printmpdirRv):
        shutil.rmtree(printmpdirRv, ignore_errors=True)
    os.mkdir(printmpdirRv)    

    tmplistaArchivosRouter =  []
    for archGZ in dirlistaArchivosRouter:
        shutil.copy2(archGZ, printmpdirRv)
        descomGZ(printmpdirRv + archGZ.split('/')[-1])
        os.remove(printmpdirRv + archGZ.split('/')[-1])
        tmplistaArchivosRouter.append(printmpdirRv + archGZ.split('/')[-1][:-3])
    #print tmplistaArchivosRouter

    if concatenar_routerviews(tmplistaArchivosRouter, cgi_datos_dir_tmp + 'routerviews'):
        print 'concatenado routerviews'
        shutil.rmtree(printmpdirRv, ignore_errors=True)
    else:
        print 'error concatenar routerviews'
        log_principal.write(fechahora + '\t error routerviews \n')
        log_principal.close()
        shutil.rmtree(printmpdirRv, ignore_errors=True)
        exit(1)
concateno()        

###################
### GENERO LA RED #
################### 
namered = 'red_completa'
nombredelared = redesdir + namered
printmpdirRedes = printmpdir + 'Redes'  + '/'
nombredelaredtmp = printmpdirRedes + namered

if os.path.isdir(printmpdirRedes):
    shutil.rmtree(printmpdirRedes, ignore_errors=True)
os.mkdir(printmpdirRedes)

printmpdirTeam = printmpdir + 'Team'  + '/'
if os.path.isdir(printmpdirTeam):
    shutil.rmtree(printmpdirTeam, ignore_errors=True)
os.mkdir(printmpdirTeam)    

def generolared():
    teams = ['team-1/', 'team-2/', 'team-3/']
    lista_files_teams = []
    for team in teams:
        listaArchivosTeam = selectforlastdays(descargasdir + team, cantidad, '.', -3)
        #print listaArchivosTeam
        dirlistaArchivosTeam = str_mas_lista_str(descargasdir + team, listaArchivosTeam)
        for arch in dirlistaArchivosTeam:
            lista_files_teams.append(arch)
    
    if len(lista_files_teams) == 0:
        print 'no hay archivos de los ultimos ' + str(cantidad) + ' dias para concatenar'
        log_principal.write(fechahora + '\t error no hay archivos de los ' + str(cantidad) + ' dias seleccionado \n')    
        log_principal.close()    
        exit(1)

    #print lista_files_teams
    tmp_lista_files_teams =  []
    for archGZ in lista_files_teams:
        shutil.copy2(archGZ, printmpdirTeam)
        descomGZ(printmpdirTeam + archGZ.split('/')[-1])
        os.remove(printmpdirTeam + archGZ.split('/')[-1])
        tmp_lista_files_teams.append(printmpdirTeam + archGZ.split('/')[-1][:-3])
    #print tmp_lista_files_teams
        

    #print lista_files_teams
    isokgenred = genred(tmp_lista_files_teams, nombredelaredtmp)

    if isokgenred:
        fileredes = os.listdir(printmpdirRedes)
        for filered in fileredes:
            shutil.copy2(printmpdirRedes + filered, redesdir)
            #if os.path.isfile(redesdir + filered):
             #   os.chown(redesdir + filered, uid, gid)
        print 'red ' + nombredelared + ' generada'
        return True
    else:
        print 'error al generar la red'
        log_principal.write(fechahora + '\t error al generar la red \n')
        log_principal.close()
        exit(1)
isokgenerolared = generolared()        

def guardardatosendbtmp():
    ##############################################
    ### GUARDAR INFO EN BASE DE DATOS TEMPORAL ###
    #############################################

    print 'guardando red en db TMP'
    reddbtmp(nombredelared + '-_frec')
    listaArchivos = str_mas_lista_str(cgi_datos_dir_tmp, listanics)
    print 'guardando pais en db TMP'
    paisdbtmp(listaArchivos)
    print 'guardando nombres en db TMP'
    nombreasdbtmp(cgi_datos_dir_tmp + 'asn')
    return True

if isokgenerolared:
    isokguardardbtmp = guardardatosendbtmp()

###############################################################
### GENERA ARCHIVOS CON NOMBRE DE PAISES Y CON NOMBRE de as ###
###############################################################

def cleaname(txt_name):
    chars = ('\'', '"', '\%', '¿', '¡' ,'·' ,'<' , '&')        #('/',':','*','?','"','<','>','\\','&','%')
    txt_name = txt_name.replace(' ', '_')
    for i in chars:
        txt_name = txt_name.replace(i,'?')
    try:
        txt_name =  txt_name.decode('latin-1').encode('utf-8', 'replace')
    except:
        txt_name = ''
    return txt_name

def generolosnombres():
    nodoname = findnodosname()
    archnodoname = open(nombredelaredtmp + '-_nodes_Asname.txt', 'w')
    for n in nodoname:
        nodo = n.split('\t')[0].strip()
        name = n.split('\t')[1].strip()
        if len(name) >= 37:
            name = name[:36]+ '...'
        nombrefinal = cleaname(name)
        if nombrefinal == '' or nombrefinal == '-Private_Use_AS-':
            nombrefinal = nodo
        texto = nodo + ' ' + nombrefinal + '\n'
        archnodoname.write(texto)
    archnodoname.close()
    print 'nombres de as para la red completa  generados'

    nodopais = findnodospais()
    archnodopais = open(nombredelaredtmp + '-_nodes_Country.txt', 'w')
    for n in nodopais:
        nodop = n.split('\t')[0].strip()
        pais = n.split('\t')[1].strip()
        if not pais == '':
            texto = nodop + ' ' + pais.decode('latin-1').encode('utf-8') + '\n'
            archnodopais.write(texto)
    archnodopais.close()
    #if os.path.isfile(nombredelared + '-_nodes_Asname.txt'):
    #    os.chown(nombredelared + '-_nodes_Asname.txt', uid, gid)
    #if os.path.isfile(nombredelared + '-_nodes_Country.txt'):
    #    os.chown(nombredelared + '-_nodes_Country.txt', uid, gid)
   
    print 'nombres de paises para la red completa  generados'
    return True

if isokguardardbtmp:
    isokgenerolosnombres = generolosnombres()

def guardardatosendb():
    #####################################
    ### GUARDAR INFO EN BASE DE DATOS ###
    #####################################
    #### deberia ser una base de datos temporal para guardar solo la red y paises y nombres de as
    print 'guardando red en db'
    reddb()
#    listaArchivos = str_mas_lista_str(cgi_datos_dir_tmp, listanics)
    print 'guardando pais en db'
    paisdb()
    print 'guardando nombres en db'
    nombreasdb()
    print 'guardando ip de nic y pais'
    for nic in ['afrinic', 'apnic', 'arin', 'lacnic', 'ripe']:
        nicdb(cgi_datos_dir_tmp + nic, nic)
    print 'guardando routerviews'
    routerviewdb(cgi_datos_dir_tmp + 'routerviews')
    return True
if isokgenerolosnombres:
    isokguardatendbfinal = guardardatosendb()

#borrar datos viejos
def borrardatosviejos():
    datosviejos = [printmpdir, dirTrabajo + 'images/maps/', dirTrabajo + 'tmp/']
    for datoold in datosviejos:
        for root, dirs, files in os.walk(datoold):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
borrardatosviejos()


            
### cierro el log
log_principal.write(fechahora + '\t OK se realizo completo \n')
log_principal.close()

### back up db
#backupdb.backupdb()
