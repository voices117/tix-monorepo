import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { push } from 'react-router-redux';
import LogoTix from '../assets/LogoTix.png';
import LoginForm from './LoginForm';
import { loginUser } from '../../../store/domain/account/actions/index';

import './LandingView.scss';

class LandingView extends Component {

  componentWillMount() {
    if (this.props.user) {
      this.props.redirectHome();
    }
  }

  render() {
    return (
      <div className='container margin-fix'>
        <div className='row line-margin'>
          <div className='col-md-8'>
            <h3>Proyecto TiX</h3>
            <div className='thumb_image'>
              <img alt='Logo Tix' src={LogoTix} />
            </div>
            <div className='row caption pull-left head'>
              <div className='col-md-12'>
                <h4>
                  { 'Qué es el Proyecto Tix?' }
                </h4>
                <p>
                  {
                    `TiX (Traffic information eXchange) es una herramienta que
                  permite efectuar una medición de la calidad de su acceso a
                  Internet.`
                  }
                </p>
                <a className='btn btn-info btn-large' href='/register'>Instalar TiX</a>

              </div>
            </div>
            <div className='clear' />


          </div>
          <div className='col-md-4'>
            <LoginForm onSubmit={this.props.submitLogin} />
          </div>
        </div>
        <div className='row'>
          <div className='col-md-4'>
            <h4>
              { 'Cuál es el objetivo?' }
            </h4>
            <p>
              {
                `El algoritmo ejecuta la medición enviando un paquete
              de datos por segundo, asegurando un consumo inperceptible de su
              conexión a Internet y permitiendo un monitoreo las 24hs del
              día y los 365 días del año.`
              }
            </p>
          </div>
          <div className='col-md-4'>
            <h4>
              { 'Qué resultados arroja?' }
            </h4>
            <p>
              {
                `Las mediciones se realizan todo el tiempo, generando un
              informe, tanto en formato web interactivo como en PDF mensual,
              detallando los momentos en que su proveedor de Internet no puede
              entregarle el tráfico máximo contratado.`
              }
            </p>
          </div>
          <div className='col-md-4'>
            <h4>
              { 'Cómo puedo usar TiX?' }
            </h4>
            <p>
              {
                `Puede crear su cuenta e instalar el software de medición en
              su PC y/o computadora portátil aquí: `
              }
              <a className='btn btn-info' href='/register'>Instalar TiX</a>
            </p>
          </div>
        </div>
        <hr />
      </div>
    );
  }
}

LandingView.propTypes = {
  submitLogin: PropTypes.func,
  user: PropTypes.shape({
    id: PropTypes.number,
  }),
  redirectHome: PropTypes.func,
};

const mapStateToProps = store => ({
  user: store.account.user,
});

const mapDispatchToProps = dispatch => ({
  submitLogin: (data) => {
    dispatch(loginUser(data));
  },
  redirectHome: () => dispatch(push('/home')),
});


export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(LandingView);

