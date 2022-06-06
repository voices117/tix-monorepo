import uuid from 'uuid';

export const ADD_ALERT = 'ADD_ALERT';
export const REMOVE_ALERT = 'REMOVE_ALERT';

export function addAlert(message) {
  const alert = {};
  alert.message = message;
  alert.id = uuid.v1();
  return dispatch => dispatch({
    type: ADD_ALERT,
    payload: alert,
  });
}

export function removeAlert(id) {
  return dispatch => dispatch({
    type: REMOVE_ALERT,
    payload: id,
  });
}
