import 'whatwg-fetch';

const TIX_API_URL = "http://localhost:3001";

function getAuthentication(token) {
    if (token) {
        return { Authorization: `JWT ${token}` };
    }
    return {};
}

export default function isoFetch(url, options = {}) {
    const method = options.method || 'GET';
    const body = JSON.stringify(options.body) || undefined;
    console.log(process.env.TIX_API_URL)
    console.log(TIX_API_URL)
    const fullUrl = `${TIX_API_URL}/api${url}`;
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