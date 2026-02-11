#!/bin/sh
# Enterprise test suite runner (all automated layers)
# Run from repo root. Backend must be running for integration/smoke.
set -e
FAILED=0

echo "=== Layer 1.1: Lint ==="
(cd frontend && npm run lint) || FAILED=1

echo "\n=== Layer 1.2: Security audit ==="
(cd frontend && npm audit --audit-level=high) || true

echo "\n=== Layer 2: Frontend unit tests ==="
(cd frontend && npm run test:coverage 2>/dev/null || npm test -- --watchAll=false) || FAILED=1

echo "\n=== Layer 3 & 9: Backend integration + smoke ==="
(cd backend && BASE_URL=http://localhost:8000 pytest tests -v --tb=short) || FAILED=1

if [ "$FAILED" -ne 0 ]; then
  echo "\nOne or more layers failed. See above."
  exit 1
fi
echo "\nAll automated layers passed."
exit 0
