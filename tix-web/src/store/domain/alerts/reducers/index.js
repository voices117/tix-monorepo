import typeToReducer from 'type-to-reducer';

import { ADD_ALERT, REMOVE_ALERT } from '../actions';

export default typeToReducer({
  [ADD_ALERT]: (state, action) => ({
    ...state,
    [action.payload.id]: action.payload.message,
  }),
  [REMOVE_ALERT]: (state, action) => {
    const newState = delete state[action.payload];
    return newState;
  },
}, {});
