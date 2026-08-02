import http from 'k6/http';
import { check, sleep } from 'k6';

// Configure the load test: 50 virtual users for 30 seconds
export const options = {
    vus: 50,
    duration: '3m',
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
            'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjVjX3NjMUNKdjlxWWd1bjBPQzlBaSJ9.eyJpc3MiOiJodHRwczovL2Rldi1vcWxoNmZiZGZsODU0ZjRjLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJSM1hsblFNNjJ6QmVuRGtPY3NNTFRKVG1VejlyZnBDdUBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9oZXJtZXMtYXBpLWVuZHBvaW50LyIsImlhdCI6MTc4NTM4Nzg5MiwiZXhwIjoxNzg1NDc0MjkyLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJhenAiOiJSM1hsblFNNjJ6QmVuRGtPY3NNTFRKVG1VejlyZnBDdSJ9.tXStLWiRxL3Hv9Jv4jLcole_92hKoCQ2nHTvfLBFe2pETXaguZxf3daQmVasVZxzvBwlfRnG6RA4aYbkhsTx4TtshBybSK8x0DY0epyULdBqHKMJxpwrhbCSDPKhabHGgYsGwrhjifTuwbmvvWKSpwvFqSskJBm7gNGgRzRIOrMy2wYq9_6vaAYMVBeXZlDpeNU0nIpDydzgAXryzo6MfICBalwl9FZ0fAK_CsRKdMDZzTqx4NQ-iyhe0OOEq469brZGnLea-byf-FtsvkxEZn_ttHR7SOsMJ0xyvOMYSNkEh4QVs_itfbvO5dsPYXOAroBjfwsYjU7H7M9kgFAJKg"
        },
    };

    const res = http.get(url, params);
    check(res, {
        'is status 200 or 401 or 503': (r) => [200, 401, 503].includes(r.status),
    });
    sleep(Math.random() * 2);
}