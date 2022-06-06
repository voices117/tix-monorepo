#!/usr/bin/python

import datetime
from FunIamhere import complementa_dic


###############################################################################
# genera un diccionario a partir de los archivos asn
###############################################################################
def concatenar_asn(archivos, arch_sal):
    '''
    archivos asn a concatenar lista ordenada del mas nuevo al mas viejo
    '''
    diccnombre = {}
    for arch in archivos:
        fileasn = open(arch, 'r')
        lineas = fileasn.readlines()
        fileasn.close()
        for linea in lineas:
            nodo = linea.split('\t')[0]
            nombre = linea.split('\t')[1]
            if nodo not in diccnombre:
                diccnombre[nodo] = nombre
    
    arch_salida = open(arch_sal, 'w')
    for clave in diccnombre:
        info = clave + '\t' + diccnombre[clave]
        arch_salida.write(info)
    arch_salida.close()
    return True


def concatenar_routerviews(archivos, arch_sal):
    '''
    archivos routerview a concatenar lista ordenada del mas nuevo al mas viejo
    '''
    diccrouterviews = {}
    for arch in archivos:
        filerouter = open(arch, 'r')
        lineas = filerouter.readlines()
        filerouter.close()
        for linea in lineas:
            ip = linea.split('\t')[0]
            mascara = linea.split('\t')[1]
            nodoas = linea.split('\t')[2]
            if not ('_' in nodoas or ',' in nodoas or '.' in nodoas):
                if  ip + '\t' + mascara not in diccrouterviews:
                    diccrouterviews[ip + '\t' + mascara] = nodoas
    
    arch_salida = open(arch_sal, 'w')
    for clave in diccrouterviews:
        info = clave + '\t' + diccrouterviews[clave]
        arch_salida.write(info)
    arch_salida.close()
    return True

def concatenar_nic(archivos, arch_sal):
    '''
    archivos nic a concatenar lista ordenada del mas nuevo al mas viejo
    '''
    diccnic = {}
    for arch in archivos:
        filerouter = open(arch, 'r')
        lineas = filerouter.readlines()
        filerouter.close()
        for linea in lineas:
            infoline = linea.split('|')
            if not linea.startswith('#') or not len(infoline) < 2:
                if infoline[2] == 'asn' and infoline[3] != '*':
                    pais = infoline[1]
                    asnodo = infoline[3]
                    if  asnodo not in diccnic:
                        diccnic[asnodo] = linea
                    
                #afrinic|ZA|asn|1228|1|19910301|allocated
                #afrinic|LS|ipv4|41.76.16.0|2048|20091127|allocated
                if infoline[2] == 'ipv4':
                    pais = infoline[1]
                    ip = infoline[3]
                    hosts = infoline[4]
                    if  ip + '\t' + hosts not in diccnic:
                        diccnic[ip + '\t' + hosts] = linea
                
    arch_salida = open(arch_sal, 'w')
    for clave in diccnic:
        info = diccnic[clave]
        arch_salida.write(info)
    arch_salida.close()
    return True




if __name__ == '__main__':
    from FunIamhere import parametrosGlobales
    import os
    from FunIamhere import str_mas_lista_str
    dicparametros = parametrosGlobales()
    cgi_datos_dir = dicparametros['cgi_datos_dir']
    lanetvidir = dicparametros['lanetvidir']
    lanetvilogdir = dicparametros['lanetvilogdir']
    dirTrabajo = os.path.abspath(os.path.dirname(__file__))+'/'
    listaArchivosASN=sorted(os.listdir('descargas/asn'), reverse = True)[:10]
    dirlistaArchivosASN = str_mas_lista_str(dirTrabajo+'descargas/asn/', listaArchivosASN)
#    concatenar_asn(dirlistaArchivosASN, 'asndaniel')

    listaArchivosRouter=sorted(os.listdir('descargas/routerviews'), reverse = True)[:1]
    dirlistaArchivosRouter = str_mas_lista_str(dirTrabajo+'descargas/routerviews/', listaArchivosRouter)
    concatenar_routerviews(dirlistaArchivosRouter, 'routerviewsDANIEL')

    listaArchivosnic=sorted(os.listdir('descargas/afrinic'), reverse = True)[:2]
    dirlistaArchivosnic = str_mas_lista_str(dirTrabajo+'descargas/afrinic/', listaArchivosnic)
    print dirlistaArchivosnic
    concatenar_nic(dirlistaArchivosnic, 'afrinicDANIEL')

