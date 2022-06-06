import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { sendRecoveryEmail, sendRecoveryPassword } from '../../../store/domain/account/actions';
import RecoverForm from './RecoverForm';
import './RecoverView.css';

class HomeView extends Component {

  componentWillMount() {
    this.submitRecoveryForm = this.submitRecoveryForm.bind(this);
    this.toggleRecoveryCode = this.toggleRecoveryCode.bind(this);
    if (this.props.code) {
      this.setState({ showRecoveryCode: true });
    } else {
      this.setState({ showRecoveryCode: false });
    }
  }

  toggleRecoveryCode() {
    this.setState({ showRecoveryCode: !this.state.showRecoveryCode });
  }

  submitRecoveryForm(formData) {
    if (this.state.showRecoveryCode) {
      this.props.sendRecoveryPassword(formData.email, formData.code, formData.password);
    } else {
      this.props.sendRecoveryEmail(formData.email).then(() => {
        this.toggleRecoveryCode();
      });
    }
  }

  render() {
    const {
      code,
      email,
    } = this.props;
    return (
      <div className='row'>
        <div className='col-md-4' />
        <div className='col-md-4'>
          <RecoverForm
            onSubmit={this.submitRecoveryForm}
            code={code}
            email={email}
            showCode={this.state.showRecoveryCode}
            toggleRecoveryCode={this.toggleRecoveryCode}
          />
        </div>
      </div>
    );
  }
}

HomeView.propTypes = {
  code: PropTypes.string,
  email: PropTypes.string,
  sendRecoveryPassword: PropTypes.func.isRequired,
  sendRecoveryEmail: PropTypes.func.isRequired,
};

const mapStateToProps = (store, state) => ({
  code: state.location.query.code,
  email: state.location.query.email,
});

const mapDispatchToProps = dispatch => ({
  sendRecoveryEmail: email => dispatch(sendRecoveryEmail(email)),
  sendRecoveryPassword: (email, code, password) => dispatch(sendRecoveryPassword(email, code, password)),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(HomeView);
