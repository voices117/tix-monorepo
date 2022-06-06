import { push } from 'react-router-redux';
import fetch from '../../../../utils/fetch';
import { addAlert } from '../../alerts/actions';

export const LOGIN_USER = 'LOGIN_USER';
export const FETCH_USER = 'FETCH_USER';
export const UNAUTHORIZED = 'UNAUTHORIZED';
export const REGISTER_USER = 'REGISTER_USER';
export const LOGOUT_USER = 'LOGOUT_USER';
export const LOCAL_STORAGE_LOAD = 'LOCAL_STORAGE_LOAD';
export const FETCH_ALL_USERS = 'FETCH_ALL_USERS';
export const IMPERSONATE_USER = 'IMPERSONATE_USER';
export const STOP_IMPERSONATION = 'STOP_IMPERSONATING';
export const UPDATE_USER = 'UPDATE_USER';
export const SEND_RECOVERY_EMAIL = 'SEND_RECOVERY_EMAIL';

export function fetchCurrentUser() {
  return dispatch => dispatch({
    type: FETCH_USER,
    payload: fetch('/user/current'),
  });
}

export function loginUser(login) {
  return dispatch => dispatch({
    type: LOGIN_USER,
    payload: fetch('/login', { method: 'POST', body: login }),
  }).then((response) => {
    localStorage.setItem('user', JSON.stringify(response));
    return dispatch(push('/home'));
  });
}

export function registerUser(register) {
  return dispatch => dispatch({
    type: REGISTER_USER,
    payload: fetch('/register', { method: 'POST', body: register }),
  }).then(() => {
    dispatch(addAlert('Usuario registrado correctamente'));
    return dispatch(push('/'));
  });
}

export function logoutUser() {
  return (dispatch) => {
    dispatch({
      type: LOGOUT_USER,
    });
    return dispatch({ type: UNAUTHORIZED });
  };
}

export function loadFromLocalStorage(user) {
  return dispatch => dispatch({
    type: LOCAL_STORAGE_LOAD,
    payload: user,
  });
}

export function fetchAllUsers() {
  return dispatch => dispatch({
    type: FETCH_ALL_USERS,
    payload: fetch('/admin/users'),
  });
}

export function impersonateUser(id) {
  return dispatch => dispatch({
    type: IMPERSONATE_USER,
    payload: fetch(`/user/${id}`),
  }).then(() => dispatch(push('/home')));
}

export function stopImpersonation() {
  return (dispatch) => {
    dispatch({
      type: STOP_IMPERSONATION,
    });
    return dispatch(fetchCurrentUser()).then(() => dispatch(push('/home')));
  };
}

export function updatePassword(userId, newPassword, oldPassword) {
  const body = {};
  body.newPassword = newPassword;
  body.oldPassword = oldPassword;
  return dispatch => dispatch({
    type: UPDATE_USER,
    payload: fetch(`/user/${userId}`, { method: 'put', body }),
  }).then(() => {
    dispatch(addAlert('Contraseña modificada correctamente'));
    return dispatch(push('/home'));
  });
}

export function updateUsername(userId, username, oldPassword) {
  const body = {};
  body.username = username;
  body.oldPassword = oldPassword;
  return dispatch => dispatch({
    type: UPDATE_USER,
    payload: fetch(`/user/${userId}`, { method: 'put', body }),
  }).then(() => {
    dispatch(addAlert('Usuario modificado correctamente'));
    return dispatch(push('/home'));
  });
}

export function sendRecoveryEmail(email) {
  return dispatch => dispatch({
    type: SEND_RECOVERY_EMAIL,
    payload: fetch('/recover', { method: 'POST', body: { email } }),
  }).then(() => dispatch(addAlert('Email enviado correctamente')));
}

export function sendRecoveryPassword(email, code, password) {
  return dispatch => dispatch({
    type: SEND_RECOVERY_EMAIL,
    payload: fetch('/recover/code', { method: 'POST', body: { email, code, password } }),
  }).then(() => {
    dispatch(addAlert('Contraseña modificada correctamente'));
    return dispatch(push('/'));
  });
}

export function editRole(userId, role) {
  const body = {};
  body.role = role;
  return dispatch => dispatch({
    type: UPDATE_USER,
    payload: fetch(`/user/${userId}`, { method: 'put', body }),
  }).then(() => {
    dispatch(addAlert('Usuario modificado correctamente'));
    return dispatch(push('/home'));
  });
}

