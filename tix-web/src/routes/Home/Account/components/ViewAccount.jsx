import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import UsernameForm from './UsernameForm';
import PasswordForm from './PasswordForm';
import { updatePassword, updateUsername } from '../../../../store/domain/account/actions';
import './ViewAccount.scss';

class AdminView extends Component {

  componentWillMount() {
    this.onUserSubmit = this.onUserSubmit.bind(this);
    this.onPasswordSubmit = this.onPasswordSubmit.bind(this);
  }

  onUserSubmit(values) {
    this.props.updateUsername(this.props.user.id, values.username, values.oldPassword);
  }

  onPasswordSubmit(values) {
    this.props.updatePassword(this.props.user.id, values.newPassword, values.oldPassword);
  }

  render() {
    return (
      <div className='hero-unit'>
        <div className='row-fluid'>
          <span className='span12' >
            <h3>Usuario</h3>
          </span>
          <span className='row'>
            <div className='col-md-6'>
              <UsernameForm onSubmit={this.onUserSubmit} />
            </div>
            <div className='col-md-6'>
              <PasswordForm onSubmit={this.onPasswordSubmit} />
            </div>
          </span>
        </div>
      </div>
    );
  }
}

AdminView.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number,
  }),
  updateUsername: PropTypes.func,
  updatePassword: PropTypes.func,
};

const mapStateToProps = store => ({
  user: store.account.user,
});

const mapDispatchToProps = dispatch => ({
  updatePassword: (userId, newPassword, oldPassword) => dispatch(updatePassword(userId, newPassword, oldPassword)),
  updateUsername: (userId, username, oldPassword) => dispatch(updateUsername(userId, username, oldPassword)),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(AdminView);
