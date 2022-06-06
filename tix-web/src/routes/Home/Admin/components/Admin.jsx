import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

class InstallationsView extends Component {

  render() {
    return (
      <div>
        { this.props.children }
      </div>
    );
  }
}

InstallationsView.propTypes = {
  children: PropTypes.node,
};

export default connect()(InstallationsView);
