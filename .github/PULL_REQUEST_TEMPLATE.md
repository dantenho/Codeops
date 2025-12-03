# 🚀 Pull Request

<!--
=============================================================================
PULL REQUEST TEMPLATE v4.0 - State of the Art
Usage: Fill out the sections below. Delete sections that are not applicable.
=============================================================================
-->

## 🤖 Agent Information
<!-- Please provide details about the agent that initiated this PR. -->

| Attribute | Value |
|-----------|-------|
| **Agent Identity** | [Select: GrokIA | Claude | GPT-4 | Copilot | CodeWhisperer | Gemini | Custom | Human] |
| **Agent Version** | <!-- e.g., v2.1.0 | gpt-4-turbo-2024-01-25 --> |
| **Session ID** | <!-- e.g., sess_abc123xyz --> |
| **Task Type** | [ ] CREATE [ ] REFACTOR [ ] DEBUG [ ] MODIFY [ ] ANALYZE [ ] DOCS [ ] TEST [ ] PERF [ ] SECURITY [ ] DEPRECATE [ ] CONFIG [ ] DEPS |
| **Priority** | [ ] 🔴 P0 (Critical) [ ] 🟠 P1 (High) [ ] 🟡 P2 (Medium) [ ] 🟢 P3 (Low) |
| **Related Issue(s)** | <!-- Fixes #123, Related to #456 --> |

---

## 📝 Change Description

### Summary
<!-- Concise overview of changes (2-3 sentences). What does this PR do at a high level? -->

### Motivation & Context
<!-- Why is this change needed? What problem does it solve?
- Business justification
- Technical debt addressed
- User pain points resolved
-->

### Solution Approach
<!-- Technical implementation details.
### Approach
- Describe the solution architecture
- Key design decisions made

### Alternatives Considered
- Option A: [Why rejected]
- Option B: [Why rejected]
-->

### Detailed Changes
<!-- Itemized list of modifications -->
#### Added
-

#### Changed
-

#### Deprecated
-

#### Removed
-

#### Fixed
-

#### Security
-

---

## ✅ Validation & Quality Assurance

### Code Quality Checklist
- [ ] **Linting:** Passes PEP 8 / ESLint / Prettier standards
- [ ] **Type Safety:** Type hints/annotations complete (mypy/TypeScript strict)
- [ ] **Complexity:** Cyclomatic complexity within threshold (<10)
- [ ] **DRY:** No duplicate code introduced
- [ ] **SOLID:** Adheres to SOLID principles
- [ ] **Naming:** Clear, descriptive variable/function names

### Documentation Checklist
- [ ] **Docstrings:** Added/updated for all public functions/classes
- [ ] **README:** Updated if applicable
- [ ] **API Docs:** OpenAPI/Swagger specs updated
- [ ] **Changelog:** CHANGELOG.md entry added
- [ ] **Architecture:** ADRs created for significant decisions
- [ ] **Comments:** Complex logic explained inline

### Testing Checklist
- [ ] **Unit Tests:** Added/updated with adequate coverage (>80%)
- [ ] **Integration Tests:** E2E scenarios covered
- [ ] **Edge Cases:** Boundary conditions tested
- [ ] **Regression:** No existing tests broken
- [ ] **Performance Tests:** Benchmarks added if applicable
- [ ] **Mutation Testing:** Critical paths validated

### Agent Protocol Compliance
- [ ] **Protocol:** Adheres to `Agents.MD` v3.0 specification
- [ ] **Telemetry:** Operation logs created in `CodeAgents/{Agent}/logs/`
- [ ] **Audit Trail:** Decision rationale documented
- [ ] **Guardrails:** Stayed within defined scope boundaries
- [ ] **Human Review:** Flagged uncertain decisions for review

### Test Evidence
<!-- Paste test output, coverage reports, or CI links below -->
```shell
# Example:
# ======================== test session starts ========================
# collected 42 items
# tests/test_feature.py::test_example PASSED
# ======================== 42 passed in 2.34s =========================
# Coverage: 87%
```

---

## 📊 Impact Analysis

### Affected Components
| File/Component | Change Type | Risk Level |
|----------------|-------------|------------|
| `src/module.py` | Modified | 🟡 Medium |
| `tests/test_module.py` | Added | 🟢 Low |

### Breaking Changes
- [ ] ✅ None - Backward compatible
- [ ] ⚠️ Minor - Deprecation warnings added
- [ ] 🔴 Major - Migration required

### Migration Guide
<!-- Required if breaking changes exist -->
<!--
#### Before
```python
old_function(param)
```
#### After
```python
new_function(param, new_required_arg)
```
-->

### Semantic Version Impact
- [ ] 📦 PATCH (x.x.X) - Bug fixes, no API changes
- [ ] 📦 MINOR (x.X.0) - New features, backward compatible
- [ ] 📦 MAJOR (X.0.0) - Breaking changes
- [ ] 🚫 No version bump needed

---

## 🔒 Security & Performance

### Security Checklist
- [ ] **Secrets:** No hardcoded credentials, tokens, or API keys
- [ ] **Input Validation:** All user inputs sanitized
- [ ] **Authentication:** Auth/AuthZ properly implemented
- [ ] **Dependencies:** No known vulnerabilities (CVEs checked)
- [ ] **OWASP:** Reviewed against OWASP Top 10
- [ ] **Data Privacy:** PII handling compliant with policies

### Security Considerations
<!-- Document any security implications, potential attack vectors, permissions required -->

### Performance Impact
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Response Time (p95) | - | - | - |
| Memory Usage | - | - | - |
| CPU Usage | - | - | - |
| Bundle Size | - | - | - |

---

## 🚀 Deployment Strategy

### Deployment Checklist
- [ ] **Feature Flag:** Changes behind feature toggle
- [ ] **Database:** Migrations tested (up/down)
- [ ] **Config:** Environment variables documented
- [ ] **Dependencies:** Lock files updated
- [ ] **Infrastructure:** IaC changes reviewed

### Deployment Strategy
- [ ] 🔄 Standard - Normal CI/CD pipeline
- [ ] 🐤 Canary - Gradual rollout
- [ ] 🔵🟢 Blue/Green - Zero-downtime switch
- [ ] 🎚️ Feature Flag - Toggle controlled
- [ ] 🌊 Rolling - Incremental update

### Rollback Plan
<!-- Steps to revert if issues arise -->
<!--
1. Revert commit: `git revert <sha>`
2. Database rollback: `migrate:down`
3. Feature flag disable: `feature.disable('new_feature')`
-->

### Observability & Monitoring
<!-- Metrics to watch, dashboards, alerts -->

---

## 📦 Dependencies

### Dependency Changes
| Package | Previous | New | Reason |
|---------|----------|-----|--------|
| - | - | - | - |

### Compatibility Verification
- [ ] **Browser:** Tested on target browsers
- [ ] **Node/Python Version:** Compatible with supported versions
- [ ] **OS:** Cross-platform compatibility verified
- [ ] **Mobile:** Responsive/mobile tested
- [ ] **Accessibility:** WCAG 2.1 AA compliant

---

## 📸 Visual Evidence

<!-- Before/After comparisons, demo GIFs -->
<!--
### Before
![Before](url)

### After
![After](url)
-->

---

## ⚠️ Risk Assessment

### Overall Risk Level
- [ ] 🟢 Low - Minimal impact, well-tested
- [ ] 🟡 Medium - Moderate impact, standard review
- [ ] 🟠 High - Significant impact, thorough review needed
- [ ] 🔴 Critical - Core system changes, requires senior review

### Known Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Database migration failure | Low | High | Tested in staging, rollback ready |

---

## 👀 Reviewer Guidance

### Review Focus Areas
<!-- Guide reviewers to critical sections -->
<!--
### 🔴 Critical (Must Review)
- `src/auth/handler.py:45-89` - New authentication logic

### 🟡 Important
- `src/api/routes.py` - New endpoints
-->

### Estimated Review Time
<!-- e.g., 15 min | 30 min | 1 hour -->

### Open Questions
<!-- Specific feedback requested -->

---

## 🔗 References
<!-- Links to relevant documentation, discussions, designs -->
<!--
- **Design Doc:** [Link]
- **RFC/ADR:** [Link]
- **Figma:** [Link]
-->

---

## ✍️ Final Confirmations

### Pre-Submit Checklist
- [ ] I have performed a self-review of my code
- [ ] I have tested this change locally
- [ ] CI pipeline passes all checks
- [ ] This PR is scoped appropriately (not too large)
- [ ] Branch is up-to-date with target branch

### Preferred Merge Strategy
- [ ] Squash and merge
- [ ] Create a merge commit
- [ ] Rebase and merge

### Additional Notes
<!-- Anything else reviewers should know... -->
