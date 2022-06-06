import { reducer as formReducer } from 'redux-form';
import { routerReducer } from 'react-router-redux';
import { combineReducers } from 'redux';
import locationReducer from './location';
import accountReducer from './domain/account/reducers';
import installationReducer from './domain/installation/reducers';
import alertReducer from './domain/alerts/reducers';
import reportReducer from './domain/report/reducers';
import providerReducer from './domain/provider/reducers';

export const makeRootReducer = asyncReducers => combineReducers({
  location: locationReducer,
  form: formReducer,
  routing: routerReducer,
  account: accountReducer,
  installations: installationReducer,
  alerts: alertReducer,
  reports: reportReducer,
  providers: providerReducer,
  ...asyncReducers,
});

export const injectReducer = (store, { key, reducer }) => {
  if (Object.hasOwnProperty.call(store.asyncReducers, key)) return;
  store.asyncReducers[key] = reducer;
  store.replaceReducer(makeRootReducer(store.asyncReducers));
};

export default makeRootReducer;
