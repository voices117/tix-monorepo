import fetch from '../../../../utils/fetch';

export const FETCH_REPORTS = 'FETCH_REPORTS';
export const FETCH_ALL_REPORTS = 'FETCH_ALL_REPORTS';
export const FETCH_ADMIN_REPORTS = 'FETCH_ADMIN_REPORTS';
export const DOWNLOAD_ADMIN_REPORTS = 'DOWNLOAD_ADMIN_REPORTS';

export function fetchReports(userId, installationId, providerId, startDate, endDate) {
  const url = `/user/${userId}/reports?installationId=${installationId}&providerId=${
    providerId}&startDate=${startDate}&endDate=${endDate}`;
  return dispatch => dispatch({
    type: FETCH_REPORTS,
    payload: fetch(url),
  });
}

export function fetchAllReports(userId) {
  return dispatch => dispatch({
    type: FETCH_ALL_REPORTS,
    payload: fetch(`/user/${userId}/reports`),
  });
}

export function fetchAdminReports(providerId, startDate, endDate) {
  return dispatch => dispatch({
    type: FETCH_ADMIN_REPORTS,
    payload: fetch(`/admin/reports?providerId=${providerId}&startDate=${startDate}&endDate=${endDate}`),
  });
}
