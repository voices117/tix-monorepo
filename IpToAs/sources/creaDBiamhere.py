#!/usr/bin/python
# -*- coding: utf-8 -*-
import psycopg2 as mbd2
import MySQLdb as mdb
import time


'''
la base de datos iamhere debe existir
con las siguientes tablas, linknodes (red armada conexion de ases tiene columna de id, columna numero as1, columna numero as2) , paisnodes (numero de as y columna con pais y columna con nic, indexar por numero de as)
'''

def connectarDb():
    db_host = 'localhost'
    usuario = 'tix'
    clave = 'password'
    base_de_datos = 'iptoas'
    conndb = mdb.connect(host=db_host, user=usuario, passwd=clave, db=base_de_datos)
    cursor = conndb.cursor()
    return cursor, conndb

def psqlConnect():
    hostName = 'localhost'
    username = 'tix'
    password = 'password'
    dbName = 'iptoas'
    connection = mbd2.connect(dbname=dbName, user=username, host=hostName, password=password)
    cursor = connection.cursor()
    return cursor, connection

def psqlConnecttmp():
    db_host = 'localhost'
    usuario = 'tix'
    clave = 'password'
    base_de_datos = 'iptoas'
    conndb = mdb.connect(host=db_host, user=usuario, passwd=clave, db=base_de_datos)
    cursor = conndb.cursor()
    return cursor, conndb

### creacion tablas base tmp
def reddbtmp(nombrered):
    '''
    nombrered: path y nombre del archivo que contiene la red a cargar
    crea y carga la tabla de enlaces de la red
    '''

    cursor, conndb = psqlConnect()

    cursor.execute('DROP TABLE IF EXISTS linknodestmp;')
    cursor.execute('CREATE TABLE linknodestmp (link_id SERIAL PRIMARY KEY, nodeA INT, nodeB BIGINT, frec INT);')

    datared = open(nombrered, 'r')

    for linea in datared:
        nodos = linea.split('\t')
        if not '.' in nodos[0] and not '.' in nodos[1]:
            node1 = int(nodos[0].strip())
            node2 = int(nodos[1].strip())
            frec = int(nodos[2].strip())
            cursor.execute( 'INSERT INTO linknodestmp (nodeA, nodeB, frec) VALUES (%s,%s,%s);', (node1, node2, frec) )

    conndb.commit()

    datared.close()    
    cursor.close()
    conndb.close()


def paisdbtmp(archivopais):
    '''
    archivodb: lista con los archivo con los paises de los nodos
    crea y carga la tabla de paises de los nodos
    '''
    cursor, conndb = psqlConnect()

    cursor.execute('DROP TABLE IF EXISTS paisnodestmp;')
    cursor.execute('CREATE TABLE paisnodestmp (nodep INT, pais CHAR(2), nic TEXT, PRIMARY KEY (nodep) );')

    list = {}
    for archivo in archivopais:
        datapais = open(archivo, 'r')
        for indice in datapais:
            linea = indice.split('|')
            if len(linea)>=4 and linea[2] == 'asn' and linea[1]!='*':
                nodo = linea[3].strip()
                pais = linea[1].strip()
                nic = archivo.split('/')[-1]
                if(nodo in list):
                    cursor.execute('UPDATE paisnodestmp SET (pais, nic) = (%s, %s) WHERE nodep=%s', (pais, nic, nodo))
                else:
                    list[nodo] = True
                    cursor.execute( 'INSERT INTO paisnodestmp (nodep, pais, nic) VALUES (%s,%s,%s)', (nodo,pais,nic))
    conndb.commit()
    datapais.close()

    cursor.close()
    conndb.close()

def nombreasdbtmp(archivoasn):
    '''
    archivoasn: archivo con los nombres de los ases
    crea y carga la tabla con los nombres de los nodos
    '''
    cursor, conndb = psqlConnect()

    cursor.execute('DROP TABLE IF EXISTS namenodestmp;')
    cursor.execute('CREATE TABLE namenodestmp (noden INT, name TEXT, PRIMARY KEY (noden) );')

    dataname = open(archivoasn, 'r')

    list = {}
    for linea in dataname:
        datos = linea.split('\t')
        if len(datos) == 2:
            nodo = datos[0].strip()
            name = unicode(datos[1].strip(),'latin-1')
            #print type(name)
            if(nodo in list):
                cursor.execute('UPDATE namenodestmp SET (name) = (%s) where noden=%s', (name, nodo))
            else:
                cursor.execute( 'INSERT INTO namenodestmp (noden, name) VALUES (%s,%s)', (nodo,name) )
#            cursor.execute( 'INSERT INTO iptoas.namenodes (noden, name) VALUES (%s,%s);', (nodo,name) )
    conndb.commit()

    dataname.close()    
    cursor.close()
    conndb.close()



### CREACION DE TABLAS
def reddb():
    '''
    nombrered: path y nombre del archivo que contiene la red a cargar
    crea y carga la tabla de enlaces de la red
    '''

    cursor, conndb = psqlConnect()

    cursor.execute('DROP TABLE IF EXISTS linknodes;')
#    cursor.execute('CREATE TABLE linknodes (link_id int AUTO_INCREMENT, nodeA INT, nodeB INT, frec INT, PRIMARY KEY (link_Id) );')
    cursor.execute('CREATE TABLE linknodes (LIKE linknodestmp);')
    cursor.execute('INSERT INTO linknodes SELECT * FROM linknodestmp;')
#    datared = open(nombrered, 'r')

#    for linea in datared:
#        nodos = linea.split('\t')
#        if not '.' in nodos[0] and not '.' in nodos[1]:
#            node1 = int(nodos[0].strip())
#            node2 = int(nodos[1].strip())
#            frec = int(nodos[2].strip())
#            cursor.execute( 'INSERT INTO iptoas.linknodes (nodeA, nodeB, frec) VALUES (%s,%s,%s);', (node1, node2, frec) )

    conndb.commit()

#    datared.close()    
    cursor.close()
    conndb.close()


def paisdb():
    '''
    archivodb: lista con los archivo con los paises de los nodos
    crea y carga la tabla de paises de los nodos
    '''
    cursor, conndb = psqlConnect()

    cursor.execute('DROP TABLE IF EXISTS paisnodes;')
 #   cursor.execute('CREATE TABLE paisnodes (nodep INT, pais CHAR(2), nic TEXT, PRIMARY KEY (nodep) );')
    cursor.execute('CREATE TABLE paisnodes (LIKE paisnodestmp);')
    cursor.execute('INSERT INTO paisnodes SELECT * FROM paisnodestmp;')
#    for archivo in archivopais:
#        datapais = open(archivo, 'r')
#        for indice in datapais:
#            linea = indice.split('|')
#            if len(linea)>=4 and linea[2] == 'asn' and linea[1]!='*':
#                nodo = linea[3].strip()
#                pais = linea[1].strip()
#                nic = archivo.split('/')[-1]
#ON DUPLICATE KEY UPDATE pais=pais, nic=nic
#                cursor.execute( 'INSERT INTO iptoas.paisnodes (nodep, pais, nic) VALUES (%s,%s,%s);', (nodo,pais,nic) )
    conndb.commit()
#    datapais.close()

    cursor.close()
    conndb.close()

def nombreasdb():
    '''
    archivoasn: archivo con los nombres de los ases
    crea y carga la tabla con los nombres de los nodos
    '''
    cursor, conndb = psqlConnect()

    cursor.execute('DROP TABLE IF EXISTS namenodes;')
#    cursor.execute('CREATE TABLE namenodes (noden INT, name TEXT, PRIMARY KEY (noden) );')
    cursor.execute('CREATE TABLE namenodes (LIKE namenodestmp);')
    cursor.execute('INSERT INTO namenodes SELECT * FROM namenodestmp;')
#    dataname = open(archivoasn, 'r')

#    for linea in dataname:
#        datos = linea.split('\t')
#        if len(datos) == 2:
#            nodo = datos[0].strip()
#            name = datos[1].strip()
            #print type(name)
#            cursor.execute( 'INSERT INTO iptoas.namenodes (noden, name) VALUES (%s,%s) ON DUPLICATE KEY UPDATE name=name;', (nodo,name) )
#            cursor.execute( 'INSERT INTO iptoas.namenodes (noden, name) VALUES (%s,%s);', (nodo,name) )
    conndb.commit()

#    dataname.close()    
    cursor.close()
    conndb.close()

def nicdb(archivonic, nic):
    '''
    archivnic: lista con los archivo de los diferentes nic (afrinic, apnic, arin, lacnic, ripe) que contiene
    los paises asignados por ip. Se crea y carga la tabla de paises ip y cantidad de host por nic
    '''
    cursor, conndb = psqlConnect()
#    afrinic|ZA|ipv4|198.54.148.0|256|19930505|assigned

    if nic in ['afrinic', 'apnic', 'arin', 'lacnic', 'ripe']:
        cursor.execute('DROP TABLE IF EXISTS ' + nic + ';')
        cursor.execute('CREATE TABLE ' + nic + ' (' + nic + '_id SERIAL PRIMARY KEY, pais_' + nic + ' CHAR(2), ip_' + nic + ' TEXT, host_' + nic + ' INT, fecha_' + nic + ' INT, cond_' + nic + ' TEXT);')
    else:
        print 'nic no conocido use afrinic, apnic, arin, lacnic, ripe'
        exit(1)

    datanic = open(archivonic, 'r')
    for indice in datanic:
        linea = indice.split('|')
        if linea[0].startswith(nic) and len(linea)==7 and linea[2] == 'ipv4':
            pais = linea[1].strip()
            ip = linea[3].strip()
            hosts = linea[4].strip()
            fecha = linea[5].strip()
            cond = linea[6].strip()
            cursor.execute( 'INSERT INTO ' + nic + ' (pais_' + nic + ', ip_' + nic + ', host_' + nic + ', fecha_' + nic + ', cond_' + nic + ') VALUES (%s,%s,%s,%s,%s);', (pais, ip, hosts, fecha, cond) )
    conndb.commit()
    datanic.close()
    cursor.close()
    conndb.close()

def routerviewdb(archivorouter):
    '''
    archivorouter: archivo caida routerviews contiene ip mascara y numero de as
    '''
    cursor, conndb = psqlConnect()

    cursor.execute('DROP TABLE IF EXISTS routerviews;')
    cursor.execute('CREATE TABLE routerviews (router_id SERIAL PRIMARY KEY, noderouter BIGINT, ip_router TEXT, mask INT);')

    datarouter = open(archivorouter, 'r')

    for linea in datarouter:
        datos = linea.split('\t')
        if len(datos) == 3:
            ip = datos[0].strip()
            mask = datos[1].strip()
            nodo = datos [2].strip()
            cursor.execute( 'INSERT INTO routerviews (noderouter, ip_router, mask) VALUES (%s,%s,%s);', (nodo, ip, mask) )
    conndb.commit()
    datarouter.close()    
    cursor.close()
    conndb.close()

#######################################################################################################
### BUSQUEDA DE INFO
def findlistanodos():
    '''
    devuelve una lista de los nodos que componen la red completa    
    '''
    cursor, conndb = psqlConnect()
    cursor.execute('SELECT nodeA FROM linknodes UNION SELECT nodeB FROM linknodes ORDER by nodeA;')
    resultado=cursor.fetchall()
    cursor.close()
    conndb.close ()
    lstnodos=[]
    for nodo in resultado:
        lstnodos.append(int(nodo[0]))
    return lstnodos

def findnodosname():
    '''
    busca los nombres de los nodos de la red completa si no tiene nombre pone un string vacio
    '''
    cursor, conndb = psqlConnect()
    sql = "SELECT nodeA, COALESCE(name,'') AS name FROM (SELECT nodeA FROM linknodestmp UNION SELECT nodeB FROM linknodestmp) AS nodealias LEFT JOIN namenodestmp ON noden=nodeA ORDER BY nodeA;"

    cursor.execute(sql)
    resultado=cursor.fetchall()
    cursor.close()
    conndb.close ()
    lstnodosname=[]
    for nodo in resultado:
        node = nodo[0]
        nombre = nodo[1]
        #pais = nodo[2]
        #nic = nodo[3]
        lstnodosname.append(str(node) + '\t' + nombre)
    return lstnodosname

def findnodospais():
    '''
    busca los paises de los nodos de la red completa
    '''
    cursor, conndb = psqlConnect()
    sql = "SELECT nodeA, COALESCE(pais,'') FROM (SELECT nodeA FROM linknodestmp UNION SELECT nodeB FROM linknodestmp) AS nodealias LEFT JOIN paisnodestmp ON nodep=nodeA GROUP BY nodeA, pais;"

    cursor.execute(sql)
    resultado=cursor.fetchall()
    cursor.close()
    conndb.close ()
    lstnodospais=[]
    for nodo in resultado:
        node = nodo[0]
        pais = nodo[1]
        lstnodospais.append(str(node) + '\t' + pais)
    return lstnodospais


def nodos_x_pais_o_nic(buscapor=''):
    '''
    devuelve lista de nodos por pais o por nic (afrinic, apnic, arin, lacnic, ripe) si es vacio devuelve todos
    '''

    cursor, conndb = psqlConnect()
    if buscapor in ['afrinic', 'apnic', 'arin', 'lacnic', 'ripe']:

        ### devuelve tabla de enlaces de nodos a partir de la red completa donde ambos nodos perteneces al pais elejido
        sqlred = 'SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '");'

        ### devuelve tabla nodos y pais que estan en la red completa y que pertenecen al pais elejido 
        sqlpaises = 'SELECT nodeA AS node, pais, nic FROM (SELECT nodeA FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '")) AS redpais1 UNION SELECT nodeB FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '")) AS redpais2) AS listapais INNER JOIN paisnodes ON nodep=listapais.nodeA ORDER BY node;'

        ###devuelve los nombres de los nodos de la red perteneciente al pais elegido si hay un nodo del pais que no tiene nombre devuelve un string vacio como nombre,
        sqlnombres = 'SELECT nodeA AS node, COALESCE(name,"") AS nombre FROM (SELECT nodeA FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '")) AS redpais1 UNION SELECT nodeB FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '")) AS redpais2) AS listapais LEFT JOIN namenodes ON noden=listapais.nodeA ORDER BY node;'

        
    else:
        ### devuelve tabla de enlaces de nodos a partir de la red completa donde ambos nodos perteneces al pais elejido
        sqlred = 'SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '");'

        ### devuelve tabla nodos y pais que estan en la red completa y que pertenecen al pais elejido 
        sqlpaises = 'SELECT nodeA AS node, pais, nic FROM (SELECT nodeA FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '")) AS redpais1 UNION SELECT nodeB FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '")) AS redpais2) AS listapais INNER JOIN paisnodes ON nodep=listapais.nodeA ORDER BY node;'

        ###devuelve los nombres de los nodos de la red perteneciente al pais elegido si hay un nodo del pais que no tiene nombre devuelve un string vacio como nombre,
        sqlnombres = 'SELECT nodeA AS node, COALESCE(name,"") AS nombre FROM (SELECT nodeA FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '")) AS redpais1 UNION SELECT nodeB FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '")) AS redpais2) AS listapais LEFT JOIN namenodes ON noden=listapais.nodeA ORDER BY node;'

    cursor.execute(sqlred)
    resultadored=cursor.fetchall()
    lstred=[]
    lstred_frec=[]
    for nodo in resultadored:
        node1 = nodo[0]
        nodo2 = nodo[1]
        frec = nodo[2]
        #print str(node1) + '\t' + str(nodo2)
        lstred.append(str(node1) + '\t' + str(nodo2) + '\n')
        lstred_frec.append(str(node1) + '\t' + str(nodo2) + '\t' + str(frec) + '\n')


    cursor.execute(sqlnombres)
    resultadonombres=cursor.fetchall()
    lstnodosnombres=[]
    for nodo in resultadonombres:
        node = nodo[0]
        nombre = nodo[1].strip('\n')#.decode('latin-1')
        #print type(nombre), nombre
        #pais = nodo[2]
        #nic = nodo[3]
        #print str(node) + '\t' + nombre
        lstnodosnombres.append(str(node) + '\t' + nombre + '\n')


    cursor.execute(sqlpaises)
    resultadopaises=cursor.fetchall()
    lstnodospaises=[]
    for nodo in resultadopaises:
        node = nodo[0]
        pais = nodo[1]
        #print str(node) + '\t' + pais
        lstnodospaises.append(str(node) + '\t' + pais + '\n')

    cursor.close()
    conndb.close ()
    return lstred, lstnodospaises, lstnodosnombres, lstred_frec


def selectpaisname(codigopais):
    '''
    devuelve el nombre del pais a partir del codigo de 2 letras en ingles y spanish  

    '''
    cursor, conndb = psqlConnect()
    if codigopais != '*':
        cursor.execute('SELECT alpha2, langEN, langES, FROM countries WHERE alpha2 = "' + codigopais + '" GROUP BY alpha2 ;')
    else:
        cursor.execute('SELECT alpha2, langEN, langES FROM countries order by alpha2;')
    resultado=cursor.fetchall()
    cursor.close()
    conndb.close()
    if len(resultado) == 0:
        resultado = False
    else:
        return resultado


if __name__ == '__main__':
    from FunIamhere import parametrosGlobales
    dicparametros = parametrosGlobales()
    cgi_datos_dir = dicparametros['cgi_datos_dir']
    lanetvidir = dicparametros['lanetvidir']
    lanetvilogdir = dicparametros['lanetvilogdir']
    
    nombreasdb(cgi_datos_dir + 'asn')
#    print selectpaisname()
#    nicdb(cgi_datos_dir + 'arin', nic='arin')
#    routerviewdb(cgi_datos_dir +'routerviews')
