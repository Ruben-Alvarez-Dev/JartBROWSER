# Definition of Done (DoD)

## Overview

The Definition of Done (DoD) ensures that a user story or task is complete, tested, and ready for production release.

---

## DoD Checklist

### 1. Acceptance Criteria
- [ ] All acceptance criteria from DoR are met
- [ ] Each criterion verified and documented
- [ ] Product owner approval received
- [ ] User acceptance testing passed (if applicable)

### 2. Code Quality
- [ ] Code reviewed by at least one peer
- [ ] No open PRs related to this work
- [ ] Code follows project coding standards
- [ ] No TODOs or FIXMEs left in code
- [ ] Complexity is appropriate (no over-engineering)
- [ ] No dead code or commented-out blocks

### 3. Testing
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] E2E tests passing for main scenarios
- [ ] Performance tests meeting criteria
- [ ] Security review completed
- [ ] Accessibility tests passing (WCAG 2.1 AA)
- [ ] Browser compatibility tests passing (Chrome Canary)

### 4. Documentation
- [ ] API documentation updated (OpenAPI spec)
- [ ] User-facing documentation written
- [ ] Internal documentation updated (architecture changes)
- [ ] Migration guide created (if needed)
- [ ] Release notes drafted
- [ ] Changelog updated

### 5. Deployment
- [ ] Deployed to staging environment
- [ ] Verified in staging environment
- [ ] Deployed to production
- [ ] Smoke tests passing in production
- [ ] Health checks passing
- [ ] Rollback plan tested (if needed)
- [ ] Configuration management updated

### 6. Security
- [ ] No known security vulnerabilities
- [ ] Security review completed
- [ ] OWASP Top 10 vulnerabilities addressed
- [ ] Data encryption verified
- [ ] API keys properly secured
- [ ] Rate limiting configured
- [ ] CORS policies configured

### 7. Performance
- [ ] Performance benchmarks met
- [ ] Response times within SLA (if applicable)
- [ ] Database queries optimized
- [ ] Memory usage optimized
- [ ] No memory leaks detected
- [ ] Token usage optimized

### 8. Monitoring
- [ ] Metrics collection configured
- [ ] Alerting configured for critical issues
- [ ] Dashboard shows healthy status
- [ ] Error tracking configured
- [ ] Uptime monitoring configured

### 9. Release Readiness
- [ ] Release version tag created
- [ ] Release notes published
- [ ] Support team notified
- [ ] Migration scripts tested
- [ ] Rollback procedures documented
- [ ] Backup created before deployment

### 10. Regression Prevention
- [ ] Previous functionality still works
- [ ] No breaking changes introduced
- [ ] Backward compatibility maintained (if applicable)
- [ ] Integration tests cover edge cases
- [ ] Performance not degraded

---

## DoD Template

```markdown
# [Story Name] - DoD Checklist

## Overview
- **Story Points**: 5
- **Sprint**: Sprint 1

## Completion Summary
- All acceptance criteria met: ✅
- Deployment status: ✅ Production
- Release version: v1.0.1

## Acceptance Criteria
- [✅] [Criterion 1]: Verified by [Developer Name]
- [✅ ] [Criterion 2]: Verified by QA
- [✅] [Story completed on Date]

## Code Quality
- [✅] Peer reviewed by [Reviewer Name]
- [✅] No open PRs
- [✅] Follows coding standards
- [✅ ] No TODOs/DEAD CODE
- [✅ ] Code complexity appropriate

## Testing
- [✅ ] Unit tests: 82% coverage (passing)
- [✅ ] Integration tests: all passing
- [✅ ] E2E tests: 3/3 scenarios
- [✅ ] Performance tests: p95 < 2s
- [✅ ] Security review: passed
- [✅ ] Accessibility: WCAG 2.1 AA

## Documentation
- [✅ ] API docs updated
- [✅ ] User docs written
- [✅ ] Architecture docs updated
- [✅ ] Migration guide: not needed
- [✅ ] Release notes: v1.0.1

## Deployment
- [✅ ] Staging: Verified
- [✅ ] Production: Deployed on [Date]
- [✅ ] Smoke tests: All passing
- [✅ Health checks: All green
- [✅ ] Rollback plan: Not needed

## Security
- [✅] Security review: No vulnerabilities found
- [✅ ] Encryption verified
- [✅ API keys secured
- [✅ Rate limiting configured
- [✅ CORS policies configured

## Performance
- [✅ ] Benchmarks met
- [✅ Response times: 850ms (target < 2000ms)
- [✅ ] Memory usage: Optimal
- [✅ No memory leaks
- [✅ Token usage: Optimized

## Monitoring
- [✅ ] Metrics configured
- [✅ ] Alerts configured
- [✅ Dashboard healthy
- [✅ Error tracking enabled

## Release Readiness
- [✅ ] Version tag: v1.0.1
- [✅ Release notes published
- [✅ Support notified
- [✅ Backup created

## Sign-offs
- Known issues:
  - [Issue 1]: [Description], impact: [Low/Medium/High], workaround: [Description]
- [Issue 2]: [Description], impact: [Low/Medium/High], workaround: [Description]

Technical debt tracked:
- [ ] [Debt item 1]: [Description], effort: [Low/Medium/High]
```

---

## DoD Questions

Before marking a story as "Done", ask:

1. **Functionality**: Does it do what it's supposed to do?
2. **Quality**: Is the quality production-ready?
3. **Testing**: Is it thoroughly tested?
4. **Documentation**: Is it documented?
5. **Deployment**: Is it deployed and verified?
6. **Security**: Is it secure?
7. **Performance**: Does it meet performance criteria?

---

## DoD Metrics

### Sprint Health Metrics
- **DoD Completeness**: % of stories meeting full DoD criteria
- **Defect Rate**: Bugs found post-release / total stories
- **Reopen Rate**: Stories reopened after DoD / total stories

### DoD Quality Metrics
- **Stories deployed to production with known issues**: Count
- **Stories with incomplete documentation**: Count
- **Stories with incomplete testing**: Count

---

## Definition of Ready vs Definition of Done

| Aspect | DoR (Ready) | DoD (Done) |
|--------|--------------|------------|
| **Acceptance** | Criteria defined | Criteria verified |
| **Code** | No open PRs, TODOs acceptable | No open PRs, TODOs removed |
| **Tests** | Test strategy planned | Tests executed and passing |
| **Docs** | Drafted | Published and verified |
| **Deployment** | Deployment plan | Deployed and verified |
| **Security** | Review planned | Review completed |
| **Performance** | Criteria defined | Benchmarks met |
| **Monitoring** | Plan configured | Configured and working |

---

**Next Steps**:

1. Apply DoD criteria to all sprint stories
2. Train team on DoD checklist usage
3. Establish DoD review process
4. Monitor and refine DoD criteria based on experience
