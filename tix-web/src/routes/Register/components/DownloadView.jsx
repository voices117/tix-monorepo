import React, { Component } from 'react';
import AppleLogo from './images/applelogo.jpg';
import LinuxLogo from './images/linuxlogo.jpg';
import WindowsLogo from './images/windowslogo.jpg';

class DownloadView extends Component {
  render() {
    return (
      <section id='typography'>
        <div className='page-header'>
          <h1>Nueva instalaci&oacute;n o actualizaci&oacute;n</h1>
        </div>

        <div className='row'>

          <div className='span12'>
            <p>Aqu&iacute; vas a poder descargar la aplicaci&oacute;n seg&uacute;n tu sistema operativo.</p>
          </div>
        </div>

        <div className='row'>
          <div className='span12'>
            <h4>Elige tu sistema operativo</h4>

            <div className='row'>
              <ul className='thumbnails'>
                <li className='col-md-4'>
                  <p >Linux</p>
                  <a href='/downloads/assets/tix-time-client-0.1.0-SNAPSHOT.deb' className='thumbnail'>
                    <img
                      width='150'
                      alt='Linux'
                      src={LinuxLogo}
                    />
                  </a>
                </li>
                <li className='col-md-4'>
                  <p >Windows</p>
                  <a href='/downloads/assets/tix-time-client-0.1.0-SNAPSHOT.exe' className='thumbnail'>
                    <img
                      width='150'
                      alt='Linux'
                      src={WindowsLogo}
                    />
                  </a>
                </li>
                <li className='col-md-4'>
                  <p>OSX</p>
                  <a href='/downloads/assets/tix-time-client-0.1.0-SNAPSHOT.dmg' className='thumbnail'>
                    <img width='150' alt='Apple' src={AppleLogo} />
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div className='row'>
          <div className='span12'>
            <h3>Instrucciones de instalaci&oacute;n</h3>
            <h4>Linux</h4>
            <p>Para instalar tu aplicativo en linux debes seguir los siguientes pasos:</p>
            <ul>
              <li>Descargar el aplicativo haciendo click sobre el logo del sistema operativo elegido</li>
              <li>Ejecutar el archivo .deb haciendo doble click e instalarlo</li>
              <li>Ir a la barra de b&uacute;squeda y buscar por ""TiX". Al hacer click sobre el ícono</li>
              <li>Loguearse con su usuario y contrase&ntilde;a, dar un nombre a la instalaci&oacute;n y aguardar a que
                finalice el proceso y reciba el mensaje de "Instalaci&oacute;n Existosa"</li>
              <li>Correr el comando "ps -ax | egrep startupAppCaller" para verficar que el programa ya est&aacute;
                corriendo</li>
            </ul>
            <h4>Mac</h4>
            <p>Para instalar tu aplicativo en MAC debes seguir los siguientes pasos:</p>
            <ul>
              <li>Descargar el aplicativo haciendo click sobre el logo del sistema operativo elegido</li>
              <li>Ejecutar el archivo .dmg haciendo doble click</li>
              <li>Esperar a que se lance la aplicaci&oacute;n</li>
              <li>Loguearse con su usuario y contrase&ntilde;a, dar un nombre a la instalaci&oacute;n y aguardar a que
                finalice el proceso y reciba el mensaje de "Instalaci&oacute;n Existosa"</li>
              <li>Correr el comando "ps -ax | egrep startupAppCaller" para verficar que el programa ya
                est&aacute; corriendo</li>
            </ul>
            <br />
            <p><b>Al pasar una hora, se podrá empezar a ver los datos de su enlace en el dashboard de la aplicación
              web.</b></p>
          </div>
        </div>

      </section>
    );
  }

}

export default DownloadView;
