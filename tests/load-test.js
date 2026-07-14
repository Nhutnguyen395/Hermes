import http from 'k6/http';
import { check, sleep } from 'k6';

// Configure the load test: 50 virtual users for 30 seconds
export const options = {
    vus: 50,
    duration: '30s',
};

const regions = ['US', 'EU', 'AP', 'SA'];

function getRandomIP() {
    return `${Math.floor(Math.random() * 225)}.${Math.floor(Math.random() * 225)}.${Math.floor(Math.random() * 225)}.${Math.floor(Math.random() * 255)}`;
}

export default function () {
    const randomRegion = regions[Math.floor(Math.random() * regions.length)];
    const fakeIP = getRandomIP();

    const url = 'http://localhost:8080/api/v1/assets/viral-video-1';

    const params = {
        headers: {
            'X-User-Region': randomRegion,
            'X-simulated-IP': fakeIP,
            'Authorization': // Enter your own Bearer Token from Auth0 here "Bearer TOKEN"
        },
    };

    const res = http.get(url, params);
    check(res, {
        'is status 200 or 401 or 503': (r) => [200, 401, 503].includes(r.status),
    });
    sleep(Math.random() * 2);
}