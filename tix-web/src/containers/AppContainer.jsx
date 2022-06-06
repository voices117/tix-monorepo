import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { browserHistory, Router } from 'react-router';
import { Provider } from 'react-redux';
import { syncHistoryWithStore } from 'react-router-redux';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import injectTapEventPlugin from 'react-tap-event-plugin';

class AppContainer extends Component {
  static propTypes = {
    routes : PropTypes.object.isRequired,
    store  : PropTypes.object.isRequired,
  }

  shouldComponentUpdate() {
    return false;
  }

  render() {
    const { routes, store } = this.props;
    const history = syncHistoryWithStore(browserHistory, store);
    injectTapEventPlugin();
    return (
      <MuiThemeProvider>
        <Provider store={store}>
          <div style={{ height: '100%' }}>
            <Router history={history} children={routes} />
          </div>
        </Provider>
      </MuiThemeProvider>
    );
  }
}

export default AppContainer;
