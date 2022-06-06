import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Field, reduxForm } from 'redux-form';
import ReCAPTCHA from 'react-google-recaptcha';
import Paper from 'material-ui/Paper';
import {
  TextField,
} from 'redux-form-material-ui';
import RaisedButton from 'material-ui/RaisedButton';

const Captcha = props => (
  <ReCAPTCHA
    sitekey='6LexqSAUAAAAAKD-PBs2MePg0TCpRuyFi4-HJ66R'
    onChange={props.input.onChange}
  />
);

Captcha.propTypes = {
  input: PropTypes.shape({
    onChange: PropTypes.func,
  }),
};

class RegisterForm extends Component {

  render() {
    const { handleSubmit } = this.props;
    return (
      <div style={{ margin: '20px 0px' }}>
        <Paper>
          <h3 className='log-in-header'>{ 'Registrarse' }</h3>
          <div>
            <form onSubmit={handleSubmit} className='hgroup'>
              <Field type='text' name='username' component={TextField} floatingLabelText='Email' />
              <Field type='password' name='password1' component={TextField} floatingLabelText={'Contraseña'} />
              <Field type='password' name='password2' component={TextField} floatingLabelText={'Contraseña'} />
              <Field name='captcharesponse' component={Captcha} />
              <RaisedButton
                style={{ marginBottom: '15px' }}
                className='button-size'
                primary
                label='Registrarse'
                type='submit'
              />
            </form>
          </div>
        </Paper>
      </div>
    );
  }
}


RegisterForm.propTypes = {
  handleSubmit: PropTypes.func,
};

const ReduxRegisterForm = reduxForm({
  form: 'register',
})(RegisterForm);

export default ReduxRegisterForm;
