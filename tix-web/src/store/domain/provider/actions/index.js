import fetch from '../../../../utils/fetch';

export const FETCH_ALL_PROVIDERS = 'FETCH_ALL_PROVIDERS';

export function fetchProviders(userId) {
  return dispatch => dispatch({
    type: FETCH_ALL_PROVIDERS,
    payload: fetch(`/user/${userId}/provider`),
  });
}

