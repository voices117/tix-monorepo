import 'whatwg-fetch';

function getApiURL() {
    if (location.hostname == 'localhost' || location.hostname == '127.0.0.1') {
        // assume we are running in a local environment and
        // just call the local service
        return "http://localhost:3001"
    } else {
        // assume production and call the real service
        return "https://tix.innova-red.net"
    }
}

function getAuthentication(token) {
  if (token) {
    return { Authorization: `JWT ${token}` };
  }
  return {};
}

export default function isoFetch(url, options = {}) {
  const method = options.method || 'GET';
  const body = JSON.stringify(options.body) || undefined;
  const fullUrl = `${getApiURL()}/api${url}`;
  return (token) => {
    const headers = {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...options.headers,
      ...getAuthentication(token),
    };
    return fetch(fullUrl, { headers, method, body });
  };
}
