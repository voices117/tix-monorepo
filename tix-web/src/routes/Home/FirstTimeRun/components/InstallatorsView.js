import React, { Component } from 'react';
import AppleLogo from './images/applelogo.jpg';
import LinuxLogo from './images/linuxlogo.jpg';
import WindowsLogo from './images/windowslogo.jpg';

class InstallatorsView extends Component {
  render() {
    return (
      <div>
        <div className='span12' style={{ marginRight: '35px' }}>
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
    );
  }

}

export default InstallatorsView;
