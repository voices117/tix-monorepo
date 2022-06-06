import { push } from 'react-router-redux';
import {
  LOGOUT_USER,
  loadFromLocalStorage,
} from '../store/domain/account/actions';

let firstRun = true;

export default function authenticationMiddleware(store) {
  return next => (action) => {
    const { type } = action;

    if (firstRun) {
      firstRun = false;
      const user = localStorage.getItem('user');
      if (user) {
        store.dispatch(loadFromLocalStorage(JSON.parse(user)));
      }
    }

    if (type === LOGOUT_USER) {
      localStorage.clear();
      store.dispatch(push('/'));
    }

    return next(action);
  };
}
