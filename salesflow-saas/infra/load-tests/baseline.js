// V006 — Performance Baseline (k6)
//
// Run against STAGING with production-like data volume (~50K deals,
// ~10K leads, ~5K evidence packs).
//
// Usage:
//   k6 run infra/load-tests/baseline.js \
//     --env STAGING_URL=https://staging.dealix.sa \
//     --env JWT="eyJhbGciOi..." \
//     --summary-export=docs/baselines/perf_$(date +%Y%m%d).json
//
// Output lands at docs/baselines/perf_YYYYMMDD.json — every future
// perf claim references THIS baseline. No "faster than X" without it.

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

const STAGING_URL = __ENV.STAGING_URL || 'http://localhost:8000';
const JWT = __ENV.JWT || '';

const p95_golden_path = new Trend('p95_golden_path_ms');
const p95_weekly_pack = new Trend('p95_weekly_pack_ms');
const p95_approval_center = new Trend('p95_approval_center_ms');
const errors = new Rate('errors');

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // warm-up
    { duration: '2m',  target: 50 },   // ramp to typical load
    { duration: '2m',  target: 200 },  // peak
    { duration: '1m',  target: 0 },    // cool-down
  ],
  thresholds: {
    'http_req_duration{name:golden_path}':     ['p(95)<2000'],  // 2s budget
    'http_req_duration{name:weekly_pack}':     ['p(95)<1500'],  // 1.5s budget
    'http_req_duration{name:approval_center}': ['p(95)<800'],   // 800ms budget
    'errors':                                  ['rate<0.01'],   // <1% errors
  },
};

const H = {
  'Authorization': `Bearer ${JWT}`,
  'Content-Type': 'application/json',
};

export default function () {
  // 1. Golden Path (heaviest endpoint)
  const r1 = http.post(
    `${STAGING_URL}/api/v1/golden-path/run`,
    JSON.stringify({ partner_name: `LoadTest-${__VU}-${__ITER}` }),
    { headers: H, tags: { name: 'golden_path' } },
  );
  p95_golden_path.add(r1.timings.duration);
  errors.add(r1.status !== 200);
  check(r1, { 'golden path 200': (r) => r.status === 200 });

  // 2. Weekly Exec Pack
  const r2 = http.get(
    `${STAGING_URL}/api/v1/executive-room/weekly-pack`,
    { headers: H, tags: { name: 'weekly_pack' } },
  );
  p95_weekly_pack.add(r2.timings.duration);
  errors.add(r2.status !== 200);
  check(r2, { 'weekly pack 200': (r) => r.status === 200 });

  // 3. Approval Center list
  const r3 = http.get(
    `${STAGING_URL}/api/v1/approval-center/pending`,
    { headers: H, tags: { name: 'approval_center' } },
  );
  p95_approval_center.add(r3.timings.duration);
  errors.add(r3.status !== 200);
  check(r3, { 'approval center 200': (r) => r.status === 200 });

  sleep(1);
}

export function handleSummary(data) {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  return {
    [`docs/baselines/perf_${date}.json`]: JSON.stringify(data, null, 2),
    stdout: `\nV006 baseline written to docs/baselines/perf_${date}.json\n`,
  };
}
