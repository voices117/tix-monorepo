import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Field, reduxForm } from 'redux-form';
import { connect } from 'react-redux';
import Paper from 'material-ui/Paper';
import {
  TextField,
} from 'redux-form-material-ui';
import RaisedButton from 'material-ui/RaisedButton';

class RecoverForm extends Component {

  renderCodeLink() {
    if (!this.props.showCode) {
      return <a onTouchTap={this.props.toggleRecoveryCode} className='password-recovery-text'>Ya tiene el codigo? </a>;
    }
    return <div />;
  }


  renderCodeFields() {
    if (this.props.showCode) {
      return (
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <Field type='text' name='code' component={TextField} floatingLabelText='Codigo' />
          <Field type='password' name='password' component={TextField} floatingLabelText='Nueva Contraseña' />
        </div>
      );
    }
    return <div />;
  }

  render() {
    const { handleSubmit, showCode } = this.props;
    return (
      <div style={{ margin: '20px 0px' }}>
        <Paper>
          <h3 className='log-in-header'>{ 'Recuperar Contraseña' }</h3>
          <div>
            <form onSubmit={handleSubmit} className='hgroup' style={{ paddingBottom: '15px' }}>
              <Field type='text' name='email' component={TextField} floatingLabelText='Email' />
              {this.renderCodeFields()}
              <RaisedButton
                primary
                style={{ marginTop: '15px' }}
                label={showCode ? 'Cambiar Contraseña' : 'Recuperar Contraseña'}
                type='submit'
              />
              {this.renderCodeLink()}
            </form>
          </div>
        </Paper>
      </div>
    );
  }
}

RecoverForm.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  showCode: PropTypes.bool.isRequired,
  toggleRecoveryCode: PropTypes.func,
};

function mapStateToProps(state, ownProps) {
  if (ownProps.showCode) {
    return {
      initialValues: {
        code: ownProps.code,
        email: ownProps.email,
      },
    };
  }
  return {};
}

const RecoverFormView = reduxForm({
  form: 'recoverForm',
})(RecoverForm);

export default connect(mapStateToProps)(RecoverFormView);
