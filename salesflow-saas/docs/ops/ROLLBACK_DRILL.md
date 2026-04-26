# Dealix — Rollback Drill

## If API crashes after deploy:
1. Railway dashboard → Deployments → click previous "ACTIVE" deployment → Rollback
2. Verify: `curl https://api.dealix.me/health`
3. Investigate deploy logs for error
4. Fix in code → push → redeploy

## If database corrupted:
1. Railway dashboard → Database → Backups → Restore latest
2. Verify: test API endpoints
3. Check data integrity

## If domain stops working:
1. Check Railway networking → verify domain mapping
2. Check DNS settings
3. If Railway down → wait or contact support

## Recovery time target: < 30 minutes
