import React from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import Header from '../../components/Header';
import Footer from '../../components/Footer';
import './CoreLayout.scss';
import '../../styles/core.scss';

export const CoreLayout = ({ children }) => (
  <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
    <Header />
    <div style={{ flex: '1 0 auto' }}>
      {children}
    </div>
    <Footer />
  </div>
);

CoreLayout.propTypes = {
  children : PropTypes.element.isRequired,
};

export default connect()(CoreLayout);
