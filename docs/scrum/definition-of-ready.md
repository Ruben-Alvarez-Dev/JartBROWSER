# Definition of Ready (DoR)

## Overview

The Definition of Ready (DoR) ensures that a user story or task is well-understood, estimated, and ready to be worked on by the development team.

---

## DoR Criteria Checklist

### 1. Value & Clarity
- [ ] User story has a clear business value
- [ ] Acceptance criteria are specific and measurable
- [ ] Scope is bounded and achievable within sprint
- [ ] Story is prioritized in backlog

### 2. Technical Understanding
- [ ] Technical approach is defined and agreed upon
- [ ] Dependencies are identified and accounted for
- [ ] API contracts are documented (OpenAPI spec)
- [ ] Database schema changes are approved
- [ ] Performance requirements are specified
- [ ] Security implications are considered

### 3. Acceptance Criteria
- [ ] Acceptance criteria are testable
- [ ] Each criterion has clear pass/fail conditions
- [ ] Performance criteria defined (e.g., <2s response time)
- [ ] Security criteria defined (e.g., no data leaks)
- [ ] User experience criteria defined (e.g., loading states)

### 4. Design & UX
- [ ] Wireframes or mockups are provided
- [ ] UI/UX is reviewed and approved
- [ ] Edge cases are considered
- [ ] Error states are designed
- [ ] Loading and empty states are designed
- [ ] Accessibility requirements are met

### 5. Testing Strategy
- [ ] Unit tests are planned
- [ ] Integration tests are planned
- [ ] E2E test scenarios are defined
- [ ] Test data is prepared
- [ ] Performance testing is planned

### 6. Documentation
- [ ] API documentation is updated
- [ ] User-facing documentation is drafted
- [ ] Internal documentation (architecture) is updated
- [ ] Migration guides are provided if needed

### 7. Estimation
- [ ] Story points are estimated (Fibonacci or T-shirt sizes)
- [ ] Time estimate is provided (hours)
- [ ] Estimation considers complexity
- [ ] Contingencies are factored in
- [ ] Risk is identified

### 8. Dependencies
- [ ] All dependencies are listed
- [ ] Dependency stories are in backlog
- [ ] Cross-team dependencies are communicated
- [ ] External dependencies are identified

### 9. Resources
- [ ] Required skills are available
- [ ] Team capacity is accounted for
- [ ] Timezone considerations are noted
- [ ] Holidays/time-off is considered

### 10. Release Readiness
- [ ] Release notes are drafted
- [ ] Rollback plan is defined
- [ ] Monitoring and alerting is configured
- [ ] Support documentation is prepared

---

## DoR Template

```markdown
# [Story Name] - DoR Checklist

## Overview
- **Story Points**: 5
- **Estimate**: 16 hours
- **Sprint**: Sprint 1

## User Story
As a [user role], I want to [goal], so that [benefit].

## Acceptance Criteria
1. [ ] [Criterion 1]: Specific, measurable, testable]
2. [ ] [Criterion 2]
3. [ ] [Criterion 3]

## Technical Requirements
- [ ] [Requirement 1]
- [ ] [Requirement 2]
- [ ] [Requirement 3]

## Design Requirements
- [ ] Wireframes reviewed
- [ ] UX patterns defined
- [ ] Accessibility: WCAG 2.1 AA compliant

## Dependencies
- [ ] [Dependency 1]: Story #123 in backlog
- [ ] [Dependency 2]: API endpoint /api/v1/feature

## Testing Strategy
- Unit tests: coverage target 80%
- Integration tests: API integration
- E2E: 3 key scenarios
- Performance: p95 < 2s response time

## DoD Checklist
- [ ] All acceptance criteria met
- [ ] Code reviewed by peer
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance tests passing
- [ ] Security review completed
- [ ] Documentation updated
- [ ] Deployed to staging and verified
- [ ] Product owner approval received
```

---

## DoR Questions

Before marking a story as "Ready", ask:

1. **Value**: Does this story deliver clear user value?
2. **Clarity**: Is the scope well-understood by the team?
3. **Estimation**: Is the time estimate realistic?
4. **Dependencies**: Are all dependencies unblocked?
5. **Complexity**: Is the complexity appropriate for the team's experience?
6. **Risk**: Have risks been identified and mitigated?

---

## Sprint Planning Considerations

### DoR Review Process
1. **Before Sprint**: Review all stories for DoR compliance
2. **During Sprint**: Ensure new stories meet DoR before pulling
3. **At Sprint Review**: DoR completeness is evaluated

### Backlog Refinement
1. **Weekly backlog refinement sessions**
2. **Update DoR criteria based on lessons learned
3. **Maintain backlog health (DEEP, WIP, blockers)

### Capacity Planning
1. **Plan at 70% team capacity**
2. **Reserve 30% for bugs and research spikes
3. **Account for team holidays and time-off

### Risk Management
1. **High risk items go in first sprints**
2. Maintain risk register
3. Have mitigation plans for each risk
4. Review risks weekly

---

## DoR Metrics

### Sprint Health Metrics
- **DoR Compliance**: % of stories that met DoR criteria
- **Estimate Accuracy**: (estimated / actual) * 100%
- **Blockers**: Number of blockers at sprint end
- **Carryover**: % of story points carried over

### DoR Quality Metrics
- **Stories with incomplete DoR**: Count
- **Stories with ambiguous acceptance criteria**: Count
- **Stories missing technical requirements**: Count
- **Stories without test strategy**: Count

---

**Next Steps**:

1. Apply DoR criteria to all backlog items
2. Train team on DoR checklist usage
3. Establish DoR review process
4. Monitor and refine DoR criteria
