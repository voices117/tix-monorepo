import React from 'react';
import PropTypes from 'prop-types';
import './AboutView.scss';
import InnovaRed from '../assets/innovared.jpg';
import ITBA from '../assets/itba.jpg';
import Lacnic from '../assets/lacnic.jpg';
import Udesa from '../assets/UdeSA.jpg';
import UBA from '../assets/uba.jpg';

function Colaborator({ link, alt, image }) {
  return (
    <li className='col-md-4 collaborator-center'>
      <a
        href={link}
        target='_blank'
      >
        <img
          alt={alt}
          className='img-thumbnail img-sizing'
          src={image}
        />
      </a>
    </li>
  );
}

export const AboutView = () => (
  <div className='container'>
    <section id='typography'>
      <div className='page-header'>
        <h1>Bienvenido al Proyecto TiX</h1>
      </div>

      <div className='row'>
        <div className='col-md-12'>
          <h3>Sobre el Proyecto TiX</h3>
          <p>El proyecto TiX nace de un subsidio de LACNIC con el fin de diponer de
            una herramienta para medir la calidad de los accesos a Internet.</p>
          <p>Del mismo participan las siguintes instituciones:</p>
        </div>
        <div className='col-md-12'>
          <div className='row-fluid'>
            <ul className='thumbnails'>
              <Colaborator alt='LacNIC' link='http://lacnic.net/' image={Lacnic} />
              <Colaborator alt='ITBA' link='http://www.itba.edu.ar/' image={ITBA} />
              <Colaborator alt='UDESA' link='http://www.udesa.edu.ar/' image={Udesa} />
            </ul>
          </div>
        </div>

        <div className='col-md-12 offset2'>
          <div className='row-fluid'>
            <ul className='thumbnails'>
              <Colaborator alt='InnovaRED' link='http://www.innova-red.net/' image={InnovaRed} />
              <Colaborator alt='UBA' link='http://www.uba.ar/' image={UBA} />
            </ul>
          </div>
        </div>

      </div>
      <hr />
      <div className='row'>
        <div className='col-md-12'>
          <h3>Investigadores responsables</h3>
          <p>Dr. Hern&aacute;n Galperin
            (<a href='http://www.conicet.gov.ar/new_scp/detalle.php?id=38012&datos_academicos=yes'>CONICET</a> y
            <a href='http://www.unsa.edu.ar/'>UnSA</a>)</p>
          <p>Dr. Ing. Jos&eacute; Ignacio Alvarez-Hamelin
            (<a href='http://www.conicet.gov.ar/new_scp/detalle.php?id=24474&datos_academicos=yes' >CONICET</a>,
            <a href='http://www.uba.ar/'>UBA</a> e <a href='http://www.itba.edu.ar/'>ITBA</a>)</p>
        </div>
      </div>
      <hr />
      <div className='row'>
        <div className='col-md-12'>
          <h3>Colaboradores</h3>
          <p>Federicio Ezequiel Garcia (<a href='http://www.uba.ar/' target='_blank'>UBA</a>)</p>
          <p>Cristian Pereyra (<a href='http://www.itba.edu.ar/' target='_blank'>ITBA</a>)</p>
          <p>Jose Ignacio Galindo (<a href='http://www.itba.edu.ar/' target='_blank'>ITBA</a>)</p>
          <p>Alan Karpovsky (<a href='http://www.itba.edu.ar/' target='_blank'>ITBA</a>)</p>
          <p>Nicolas Loreti (<a href='http://www.itba.edu.ar/' target='_blank'>ITBA</a>)</p>
          <p>Paula Verghelet (<a href='http://www.uba.ar/' target='_blank'>UBA</a>)</p>
          <p>Ing. Esteban Poggio (<a href='http://www.uba.ar/' target='_blank'>UBA</a>)</p>
          <p>Estudiantes de Introduccion a los sistemas distribuidos, 2do cuatrimestre 2012.</p>
        </div>
      </div>
    </section>
  </div>
);

Colaborator.propTypes = {
  link: PropTypes.string,
  alt: PropTypes.string,
  image: PropTypes.string,
};

export default AboutView;
