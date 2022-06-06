from gen_mapas import genmapas
def generarmapas():
#if genmapas('/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/redes/red_AR', mapasdir, lanetvidir, 'svg'):
    nombredelared = '/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/redes/red_completa'
    mapasdir = '/var/www/lanet-vi.fi.uba.ar/i_am_here/sources/tmp/'
    lanetvidir = '/var/www/lanet-vi.fi.uba.ar/Soft/LaNet-vi_2.2.3/'
    if genmapas(nombredelared, mapasdir, lanetvidir, 'svg'):
        print 'todos los mapas fueron generados'
    else:
        print 'error al generar los mapas'
        log_principal.write(fechahora + '\t error genmapas \n')
        log_principal.close()
        exit(1)
###cierro log
generarmapas()
