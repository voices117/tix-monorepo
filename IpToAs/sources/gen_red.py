#!/usr/bin/python

import datetime
from FunIamhere import complementa_dic


###############################################################################
# genera un diccionario a partir de los archivos de caida (teams)
###############################################################################
def inicia_dic(archivo):
    '''
    archivos caida de los teams 
    '''
    diccLink = {}
    monitorKeys = {}
    arch = open(archivo, 'r')
    lineas = arch.readlines()
    arch.close()
    for linea in lineas:
        if linea.startswith('M'):
            monitorKeys[linea.split()[3]] = linea.split()[1]
        elif linea.startswith('D') and not ('_' in linea or ',' in linea or '.' in linea):
            valor = linea.split()[3:]
            monitores = []
            for v in valor:
                monitores.append(monitorKeys[v])
            diccLink[linea.split()[1] + '\t' + linea.split()[2]] = monitores
        elif linea.startswith('I') and not ('_' in linea or ',' in linea or '.' in linea):
            elemento = linea.split()[1] + '\t' + linea.split()[2]
            if elemento not in diccLink:
                valor = linea.split()[4:]
                monitores = []
                for v in valor:
                    monitores.append(monitorKeys[v])
                diccLink[elemento] = monitores
            else:
                valor = linea.split()[4:]
                monitores_nuevos = []
                for v in valor:
                    monitores_nuevos.append(monitorKeys[v])
                monitores_cargados = diccLink[elemento]
                valor_concatenado = list(set(monitores_nuevos) | set(monitores_cargados))
                diccLink[elemento] = valor_concatenado

    return diccLink



###############################################################################
# genera la red con el valor de frecuencia de descubrimiento del enlace
###############################################################################
def red_frec(diccionario, red_frec_out='red_frec.txt', red_solo_out='red.txt'):
    '''
    entrada diccionario con enlaces y monitores que lo descubrieron, y los archivos de salida
    '''
    arch_frec = open(red_frec_out, 'w')
    arch_solo = open(red_solo_out, 'w')

    for clave in diccionario:
        dato = clave + '\t' + str(len(diccionario[clave])) + '\n'
        arch_frec.write(dato)
        arch_solo.write(clave + '\n')
    arch_frec.close()
    arch_solo.close()
    return True

def genred(teams,outfile):
    '''
    teams: lista de teams (path + nombre) del archivo de caida que se utilizaran para generar las redes
    outfile: path y nombre del archivo de salida (frec_, red_, y la fecha y hora se agregan al nombre elegido)
    retorna true si anda 
    '''
    fechahora = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    diccFinal = {}
    for archivo in teams:
        dicc = inicia_dic(archivo)
        diccFinal = complementa_dic(diccFinal, dicc)
    return red_frec(diccFinal, outfile + '-_frec', outfile ), fechahora

if __name__ == '__main__':
    import os
    import shutil
    from FunIamhere import parametrosGlobales, selectforlastdays, str_mas_lista_str, descomGZ, normalizar_string
    dicparametros = parametrosGlobales()
    descargasdir = dicparametros['descargasdir']
    carpeta_script = os.getcwd()
    carpeta_temp = carpeta_script + '/tmp/teams/'
    if not os.path.isdir(carpeta_temp):
        os.mkdir(carpeta_temp)

    ###################
    ### GENERO LA RED #
    ################### 
    cantidad = 7
    printmpdir = 'tmp/'
    redesdir = 'redes/'
    teams = ['team-1/', 'team-2/', 'team-3/']
    lista_files_teams = []
    for team in teams:
        listaArchivosTeam = selectforlastdays(descargasdir + team, cantidad, '.', -3)
        dirlistaArchivosTeam = str_mas_lista_str(descargasdir + team, listaArchivosTeam)
        for arch in dirlistaArchivosTeam:
            lista_files_teams.append(arch)

    #print lista_files_teams
    tmp_lista_files_teams =  []
    for archGZ in lista_files_teams:
        shutil.copy2(archGZ, printmpdir)
        descomGZ(printmpdir + archGZ.split('/')[-1])
        os.remove(printmpdir + archGZ.split('/')[-1])
        tmp_lista_files_teams.append(printmpdir + archGZ.split('/')[-1][:-3])
    #print tmp_lista_files_teams
        
    if len(lista_files_teams) == 0:
        print 'no hay archivos de los ultimos ' + str(cantidad) + ' dias para concatenar'
        log_principal.write(fechahora + '\t error no hay archivos de los ' + str(cantidad) + ' dias seleccionado \n')    
        log_principal.close()    
        exit(1)

    #print lista_files_teams
    nombredelared = redesdir + 'red_completa'
    [isokgenred, fechahora] = genred(tmp_lista_files_teams, nombredelared)

    for arch in tmp_lista_files_teams:
        os.remove(arch) 

