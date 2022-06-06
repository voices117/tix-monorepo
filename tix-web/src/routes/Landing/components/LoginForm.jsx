import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Field, reduxForm } from 'redux-form';
import Paper from 'material-ui/Paper';
import {
  TextField,
} from 'redux-form-material-ui';
import RaisedButton from 'material-ui/RaisedButton';
import { Link } from 'react-router';

class LoginForm extends Component {

  render() {
    const { handleSubmit } = this.props;
    return (
      <Paper>
        <h3 className='log-in-header'>{ 'Iniciar sesión' }</h3>
        <div>
          <form onSubmit={handleSubmit} className='hgroup'>
            <Field type='text' name='username' component={TextField} floatingLabelText='Email' />
            <Field type='password' name='password' component={TextField} floatingLabelText={'Constraseña'} />
            <RaisedButton className='button-size' primary label='Log in'type='submit' />
            <Link className='password-forgot-text' to='/recover' > Olvido su contraseña? </Link>
          </form>
        </div>
      </Paper>
    );
  }
}

LoginForm.propTypes = {
  handleSubmit: PropTypes.func,
};

const LoginFormView = reduxForm({
  form: 'login', // a unique name for this form
})(LoginForm);

export default LoginFormView;
