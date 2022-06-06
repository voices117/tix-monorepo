#!/usr/bin/python
from subprocess import call
import os
import shutil
import sys
import datetime

################
# GENERO grafo #
################
def runlanet(red, Width='800', Height='600', Back='black', Color='col', etiquetasnodos='', lanetvidir='/var/www/lanet-vi.fi.uba.ar/Soft/LaNet-vi_2.2.3/', render='pov'):

    fechahora = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    dirTrabajo = os.path.abspath(os.path.dirname(__file__)) + '/'
    log_gen_mapas = open(dirTrabajo + 'log/gen_mapas_error.log', "a")
#    dirtmplanetvi = dirTrabajo + 'tmp/lanetvi/'
    os.chdir(lanetvidir)
    os.environ['HOME'] = '/var/www/lanet-vi.fi.uba.ar/'

#    shutil.copy2(lanetvidir + 'lanet', 'tmp/figures/')
#    os.chdir('tmp/figures/')

    if red.endswith('frec'):
        multigraph = ' -multigraph'
    else:
        multigraph = ''
    
    if etiquetasnodos == '':
        if render == 'svg': # SVG
            command_lanet='./lanet -input ' + red + ' -W ' + str(Width) + ' -H ' + str(Height) + ' -edges 1 -opacity 0.1 -bckgnd ' + Back + ' -color ' + Color + ' -render svg' + multigraph
        else: #POVRAY
            command_lanet='./lanet -input ' + red + ' -W ' + str(Width) + ' -H ' + str(Height) + ' -edges 1 -bckgnd ' + Back + ' -color ' + Color + multigraph
    else:
        if render == 'svg': # SVG      
            command_lanet='./lanet -input ' + red + ' -W ' + str(Width) + ' -H ' + str(Height) + ' -edges 1 -opacity 0.1 -bckgnd ' + Back + ' -color ' + Color + ' -names ' + etiquetasnodos + ' -render svg' + multigraph 
        else: #POVRAY
            command_lanet='./lanet -input ' + red + ' -W ' + str(Width) + ' -H ' + str(Height) + ' -edges 1 -bckgnd ' + Back + ' -color ' + Color + ' -names ' + etiquetasnodos + multigraph

    print command_lanet
    #./lanet -input /var/www/lanet-vi.fi.uba.ar/i_am_here/sources/redes/red_AR -W 800 -H 600 -edges 1 -bckgnd white -color col
    

    try:
        retcode = call(command_lanet, shell=True)
        if retcode < 0:
            print >>sys.stderr, ' Child was terminated by signal', -retcode
            log_gen_mapas.write(fechahora + ' Child was terminated by signal -' + str(retcode) + '\n')
            log_gen_mapas.close()
            return False
        elif retcode == 0:
            print >>sys.stderr, ' Child returned', retcode
            return True
        else:
            print >>sys.stderr, ' Child returned', retcode
            log_gen_mapas.write(fechahora + ' Child returned' + str(retcode) + '\n')
            log_gen_mapas.close()
            return False
            
    except OSError as e:
        print >>sys.stderr, 'Execution failed: ', e
        log_gen_mapas.write(fechahora + ' Execution failed: ' + str(e) + '\n')
        log_gen_mapas.close()
        return False

    finally:
        log_gen_mapas.close()


########################
# Mapas para i am here #
########################
def genmapas(redIn, lanetvidir, savefiguresdir, render='svg'):
    '''
    lanetvidir: directorio donde esta lanet-vi
    red: nombre de la red si tiene nombre de nodos el archivo debe terminar en -_nodes_asname.txt' 
    y si tiene nombre de pais debe terminar en -_nodes_asname.txt'
    '''
    #MAPAS PARA DESCARGAR
#    dirTrabajo = os.path.abspath(os.path.dirname(__file__)) + '/'
#    dirtmplanetvi = ldirTrabajo + 'tmp/lanetvi/'
#    dirtmpfigures = dirTrabajo + 'tmp/figures/'
    
    dimen=([800,600],[1200,900],[1600,1200],[2400,1800])
    Colors=['col','bwi']
    Backgnd=['white', 'black']
    nombres_nodos=['', '-_nodes_Asname.txt', '-_nodes_Country.txt']
    lstfrec = ['', '-_frec']
    for frec in lstfrec:
        for res in dimen:
            Width=res[0]
            Height=res[1]
            for Color in Colors:
                for Back in Backgnd:
                    for nombreNode in nombres_nodos:
                        red = redIn + frec
                        if nombreNode.endswith('nodes_Country.txt'):
                            nombre = red + '_' + Color + '_' + Back[0] + '_' + str(Width) + 'x' + str(Height) + '_names'
                            nombre_save = red + '_' + Color + '_' + Back[0] + '_' + str(Width) + 'x' + str(Height) + '_namesCountry'
                            etiquetasnodos = redIn + nombreNode
                        elif nombreNode.endswith('nodes_Asname.txt'):
                            nombre = red + '_' + Color + '_' + Back[0] + '_' + str(Width) + 'x' + str(Height) + '_names'
                            nombre_save = red + '_' + Color + '_' + Back[0] + '_' + str(Width) + 'x' + str(Height) + '_namesAs'
                            etiquetasnodos = redIn + nombreNode
                        else:
                            nombre = red + '_' + Color + '_' + Back[0] + '_' + str(Width) + 'x' + str(Height)
                            nombre_save = nombre + '_nameLess'
                            etiquetasnodos = ''
                            
                        
                        if render == 'svg':
                            nombre_mapa = nombre + 'SVG.png' 
                            nombre_mapa_render = nombre + '.svg'
                        else:
                            nombre_mapa = nombre + 'POV.png' 
                            nombre_mapa_render = nombre + '.pov'
                        
                        nombre_mapa_save = nombre_save + '.png' 
                        nombre_log_save = nombre_save + '.log'
                        
                        #print nombre
                        if runlanet(red, Width, Height, Back, Color, etiquetasnodos, lanetvidir, render=render):
                            shutil.copy2(lanetvidir + nombre_mapa, savefiguresdir + nombre_mapa_save)
                            shutil.copy2(lanetvidir + 'log/pixels.log', savefiguresdir + nombre_log_save)
                            os.remove(lanetvidir + nombre_mapa)
                            os.remove(lanetvidir + nombre_mapa_render)
                        else:
                            return False
        
#        archivosmapas = os.listdir(dirtmpfigures)
#        if len(archivosmapas) == 0:
#            for archivo in  archivosmapas:
#                if os.path.isfile(archivo):
#                    shutil.copy2(dirtmpfigures + archivo, savedir)
#            for archivo in archivosmapas:
#                if os.path.isfile(archivo):
#                    os.remove(dirtmpfigures + archivo)

    return True

if __name__ == '__main__':
    from FunIamhere import parametrosGlobales
    dicparametros = parametrosGlobales()
    lanetvidir = dicparametros['lanetvidir']
    mapasdir = dicparametros['mapasdir']
    #print runlanet('/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/redes/red_AR', render='pov')
    #print genmapas('/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/redes/red_AR', '/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/tmp/', lanetvidir, 'svg')
    print genmapas('/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/redes/red_completa', '/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/tmp/', lanetvidir, 'svg')
