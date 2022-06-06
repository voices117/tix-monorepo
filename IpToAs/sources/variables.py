#Archivo que contiene las carpetas que usaran las diferentes scripts de i_am_here
#todas las variables van separadas por el signo =
#las variables que deven existir son cgi_datos_dir, redesdir, mapasdir, 
#lanetvidir, lanetvilogdir, logdir, descargasdir,dias, proxy
#los directorios especificados deben terminar con el caracter /

#cgi_datos_dir: carpeta cgi donde se gusrdaran los datos que utilizaran los diferentes script
cgi_datos_dir = 'datos/'

#redesdir: carpeta donde se guardaran las redes generadas
redesdir = 'redes/'

#mapasdir: carpeta donde se guardaran los mapas de i_am_here con diferentes resoluciones, colores, nombres
mapasdir = 'datos/figures/'

#lanetvidir: carpeta donde esta compilado el soft lanet-vi
lanetvidir = ''

#lanetvilogdir: carpeta donde se generan los log de lanetvi
#por defecto se toma lanetvidir/log/
lanetvilogdir = 'log/'

#logdir: carpeta donde se generan los log de todo i am here
logdir = 'log/'

#descargasdir: carpeta donde se descargan los diferentes archivos necesarios
descargasdir = 'descargas/'

# cantidad de dias que se tienen en cuanta para armar la red
dias = 30

#si usa proxy indicar ip y puerto en caso contrario dejar vacio, ej proxy = 157.92.49.223:8080
proxy = ''