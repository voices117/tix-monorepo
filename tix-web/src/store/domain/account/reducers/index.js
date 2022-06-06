import typeToReducer from 'type-to-reducer';

import {
  LOGIN_USER,
  FETCH_USER,
  LOCAL_STORAGE_LOAD,
  FETCH_ALL_USERS,
  IMPERSONATE_USER,
  STOP_IMPERSONATION,
  LOGOUT_USER,
} from '../actions';

export default typeToReducer({
  [LOGIN_USER]: {
    FULFILLED: (state, action) => ({
      ...state,
      user: action.payload,
    }),
  },
  [FETCH_USER]: {
    FULFILLED: (state, action) => ({
      ...state,
      user: {
        ...state.user,
        ...action.payload,
      },
    }),
  },
  [LOCAL_STORAGE_LOAD]: (state, action) => ({
    ...state,
    user: {
      ...state.user,
      ...action.payload,
    },
  }),
  [FETCH_ALL_USERS]: {
    FULFILLED: (state, action) => ({
      ...state,
      users: action.payload,
    }),
  },
  [IMPERSONATE_USER]: {
    FULFILLED: (state, action) => ({
      ...state,
      user: {
        ...state.user,
        ...action.payload,
        isImpersonating: true,
      },
    }),
  },
  [STOP_IMPERSONATION]: state => ({
    ...state,
    user: {
      ...state.user,
      isImpersonating: false,
    },
  }),
  [LOGOUT_USER]: () => ({}),
}, {});
