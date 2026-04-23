/*
 * Dealix Production Smoke Test — k6 load test
 *
 * Usage:
 *   k6 run --env API_BASE=https://api.dealix.me scripts/k6_smoke_test.js
 *   k6 run --env API_BASE=http://localhost:8001 --env API_KEY=your-key scripts/k6_smoke_test.js
 *
 * Thresholds:
 *   - p95 response time < 500ms
 *   - error rate < 1%
 *   - http_req_duration p99 < 2000ms
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const healthDuration = new Trend('health_duration');
const pricingDuration = new Trend('pricing_duration');

const BASE = __ENV.API_BASE || 'http://localhost:8001';
const API_KEY = __ENV.API_KEY || '';

const headers = API_KEY ? { 'Authorization': `Bearer ${API_KEY}` } : {};

export const options = {
  stages: [
    { duration: '10s', target: 5 },   // ramp up
    { duration: '30s', target: 10 },   // steady
    { duration: '10s', target: 20 },   // peak
    { duration: '10s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<2000'],
    errors: ['rate<0.01'],
    health_duration: ['p(95)<200'],
    pricing_duration: ['p(95)<300'],
  },
};

export default function () {
  // 1. Health check (public, no auth)
  const healthRes = http.get(`${BASE}/api/v1/health`);
  healthDuration.add(healthRes.timings.duration);
  check(healthRes, {
    'health 200': (r) => r.status === 200,
    'health has status': (r) => JSON.parse(r.body).status !== undefined,
  }) || errorRate.add(1);

  // 2. Pricing plans (public, no auth)
  const pricingRes = http.get(`${BASE}/api/v1/pricing/plans`);
  pricingDuration.add(pricingRes.timings.duration);
  check(pricingRes, {
    'pricing 200': (r) => r.status === 200,
    'pricing has plans': (r) => JSON.parse(r.body).plans.length >= 3,
    'pricing SAR': (r) => JSON.parse(r.body).currency === 'SAR',
  }) || errorRate.add(1);

  // 3. Pricing single plan
  const planRes = http.get(`${BASE}/api/v1/pricing/plans/growth`);
  check(planRes, {
    'plan 200': (r) => r.status === 200,
    'plan is growth': (r) => JSON.parse(r.body).plan.id === 'growth',
  }) || errorRate.add(1);

  // 4. Deep health (with auth if configured)
  if (API_KEY) {
    const deepRes = http.get(`${BASE}/api/v1/health/deep`, { headers });
    check(deepRes, {
      'deep health 200': (r) => r.status === 200,
    }) || errorRate.add(1);

    // 5. Admin stats
    const statsRes = http.get(`${BASE}/api/v1/admin/dlq/queues`, { headers });
    check(statsRes, {
      'dlq queues 200': (r) => r.status === 200,
    }) || errorRate.add(1);

    // 6. Circuit breaker status
    const cbRes = http.get(`${BASE}/api/v1/admin/circuit-breakers`, { headers });
    check(cbRes, {
      'circuit breakers 200': (r) => r.status === 200,
    }) || errorRate.add(1);

    // 7. Approval stats
    const approvalRes = http.get(`${BASE}/api/v1/approval-center/stats`, { headers });
    check(approvalRes, {
      'approval stats 200': (r) => r.status === 200,
    }) || errorRate.add(1);
  }

  sleep(1);
}

export function handleSummary(data) {
  const p95 = data.metrics.http_req_duration.values['p(95)'];
  const p99 = data.metrics.http_req_duration.values['p(99)'];
  const errRate = data.metrics.errors ? data.metrics.errors.values.rate : 0;
  const totalReqs = data.metrics.http_reqs.values.count;

  const summary = {
    timestamp: new Date().toISOString(),
    total_requests: totalReqs,
    p95_ms: Math.round(p95),
    p99_ms: Math.round(p99),
    error_rate: errRate,
    pass: p95 < 500 && errRate < 0.01,
  };

  return {
    'stdout': JSON.stringify(summary, null, 2) + '\n',
    'k6_results.json': JSON.stringify(summary),
  };
}
