// k6 smoke load test for Dealix API
// Run:  k6 run tests/load/k6_smoke.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m',  target: 50 },
    { duration: '30s', target: 100 },
    { duration: '1m',  target: 100 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.02'],
    http_req_duration: ['p(95)<2000'],
  },
};

const BASE = __ENV.API_BASE || 'https://api.dealix.sa';
const KEY = __ENV.API_KEY || '';

export default function () {
  const params = KEY ? { headers: { 'X-API-Key': KEY } } : {};
  const h = http.get(`${BASE}/health`, params);
  check(h, { 'health 200': r => r.status === 200 });

  const deep = http.get(`${BASE}/health/deep`, params);
  check(deep, { 'deep ok/degraded': r => [200, 503].includes(r.status) });

  sleep(1);
}
