#!/usr/bin/python
import os
from creaDBiamhere import nodos_x_pais_o_nic
from FunIamhere import parametrosGlobales, normalizar_string
from gen_mapas import runlanet
import time
#import sys
#reload(sys)
#sys.setdefaultencoding('latin_1')


dicparametros = parametrosGlobales()
cgi_datos_dir = dicparametros['cgi_datos_dir']
lanetvidir = dicparametros['lanetvidir']
dirTrabajo = os.path.abspath(os.path.dirname(__file__)) + '/'
redesdir = dirTrabajo + 'redes/'

inicio = time.time()

buscapor = 'AR'
[red, pais, nombres, red_frec] = nodos_x_pais_o_nic(buscapor)

#archredfrec = open('redes/red_' + buscapor + '_frec', 'w')
#for rf in red_frec:
#    archredfrec.write(rf)
#archredfrec.close()

nombrered = redesdir + 'red_' + buscapor
archred = open(nombrered, 'w')
for r in red:
    archred.write(r)
archred.close()

nombreredfrec = redesdir + 'red_' + buscapor + '_frec'
archredfrec = open(nombreredfrec, 'w')
for r in red_frec:
    archredfrec.write(r)
archredfrec.close()

nombrepaises = redesdir + 'red_' + buscapor + '-_nodes_country.txt'
archpais = open(nombrepaises, 'w')
for p in pais:
    archpais.write(p)
archpais.close()


nombrenombres = redesdir + 'red_' + buscapor + '-_nodes_asname.txt'
archnombres = open(nombrenombres, 'w')
for n in nombres:
    nodo = n.split('\t')[0]
    nombrenormalize = normalizar_string(n.split('\t')[1].decode('latin-1'))
    nombre = "_".join(nombrenormalize.split())
    #print type(nombre), nombre
    texto =  nodo + '\t' + nombre + '\n'
    archnombres.write(texto)
archnombres.close()  

#os.chdir(lanetvidir)
runlanet(nombrered, Width='2400', Height='1800', Back='black', Color='col', etiquetasnodos=nombrenombres, lanetvidir='/var/www/lanet-vi.fi.uba.ar/Soft/LaNet-vi_2.2.3')
fin = time.time()
print 'timepo de generacion: ' + str(fin - inicio)
