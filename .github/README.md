# GitHub Infrastructure

This directory contains all GitHub-related configuration and automation for the EudoraX project.

## Directory Structure

```
.github/
├── workflows/              # GitHub Actions workflows
│   ├── ci.yml              # Comprehensive CI pipeline
│   ├── agent-validation.yml # Agent compliance validation
│   ├── security.yml        # Security scanning
│   ├── release.yml         # Release management
│   ├── branch-sync.yml     # Branch synchronization
│   ├── merge-orchestrator.yml # Auto-merge orchestration
│   ├── telemetry-collector.yml # Telemetry aggregation
│   ├── dependabot-auto-merge.yml # Dependabot automation
│   └── reusable/          # Reusable workflows
│       ├── python-setup.yml
│       └── telemetry-validator.yml
├── ISSUE_TEMPLATE/         # Issue templates
│   └── agent-task.yml     # Agent task template
├── CODEOWNERS             # Code ownership rules
├── dependabot.yml         # Dependabot configuration
├── FUNDING.yml            # Funding/sponsorship info
├── labeler.yml            # Auto-labeling rules
├── PULL_REQUEST_TEMPLATE.md # PR template
├── DEPLOYMENT.md          # Deployment guide
└── README.md             # This file
```

## Workflows Overview

### Core Workflows

| Workflow | Purpose | Frequency |
|----------|---------|-----------|
| `ci.yml` | Comprehensive CI pipeline | On push/PR |
| `agent-validation.yml` | Validate Agents.MD compliance | On push/PR |
| `security.yml` | Security scanning | Weekly + on push/PR |
| `release.yml` | Release management | On tag push or manual |

### Automation Workflows

| Workflow | Purpose | Frequency |
|----------|---------|-----------|
| `branch-sync.yml` | Sync agent branches | Daily + on main push |
| `merge-orchestrator.yml` | Auto-merge PRs | On PR events |
| `telemetry-collector.yml` | Aggregate telemetry | Every 6 hours |
| `dependabot-auto-merge.yml` | Auto-merge Dependabot PRs | On Dependabot PRs |

### Reusable Workflows

| Workflow | Purpose |
|----------|---------|
| `python-setup.yml` | Python environment setup |
| `telemetry-validator.yml` | Telemetry schema validation |

## Quick Start

### Running Workflows Manually

```bash
# Run CI pipeline
gh workflow run ci.yml

# Run security scan
gh workflow run security.yml

# Create release
gh workflow run release.yml -f version=1.2.3 -f release_type=minor

# Sync branches
gh workflow run branch-sync.yml

# Collect telemetry
gh workflow run telemetry-collector.yml -f days=7
```

### Viewing Workflow Status

```bash
# List recent runs
gh run list

# View specific run
gh run view <run-id>

# Watch workflow
gh run watch <run-id>
```

## Configuration Files

### CODEOWNERS

Defines code ownership for automatic PR reviews. See [CODEOWNERS](CODEOWNERS) for details.

### dependabot.yml

Configures automatic dependency updates:
- Python packages (weekly)
- GitHub Actions (weekly)
- Multiple directories supported

### FUNDING.yml

Sponsorship and funding information. Currently placeholder - update with actual funding links.

### labeler.yml

Auto-labeling rules based on:
- Changed files (backend, frontend, docs)
- Branch names (agent-specific labels)

## Issue Templates

### Agent Task Template

Comprehensive template for creating agent tasks with:
- Agent selection
- Task type and priority
- Acceptance criteria
- Context and constraints
- Dependencies

## PR Template

Standardized PR template with:
- Agent information
- Change description
- Validation checklists
- Impact analysis
- Security considerations
- Deployment strategy

## Best Practices

1. **Always Use Workflows**
   - Don't bypass CI checks
   - Wait for validation before merging
   - Review security findings

2. **Follow Branch Naming**
   - Format: `agent/AgentName/feature-description`
   - Use descriptive names
   - Keep branches focused

3. **Create Proper PRs**
   - Fill out PR template completely
   - Link related issues
   - Request appropriate reviewers

4. **Monitor Workflows**
   - Check workflow status regularly
   - Address failures promptly
   - Review telemetry reports

5. **Keep Dependencies Updated**
   - Review Dependabot PRs
   - Test updates before merging
   - Update lock files

## Troubleshooting

### Workflow Not Running

- Check workflow file syntax
- Verify trigger conditions
- Check branch protection rules
- Review workflow permissions

### Workflow Failing

- Check workflow logs
- Review error messages
- Verify dependencies
- Check environment variables

### Auto-merge Not Working

- Verify PR has `auto-merge` label
- Check all required checks pass
- Ensure no merge conflicts
- Verify PR is not draft

## Contributing

When adding or modifying workflows:

1. Follow existing patterns
2. Include proper documentation
3. Test workflows thoroughly
4. Update this README if needed
5. Follow Agents.MD protocol

## Resources

- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [Agents.MD](../Agents.MD) - Protocol specification
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

## Support

For issues or questions:
- Open an issue on GitHub
- Contact maintainers via CODEOWNERS
- Check workflow logs
- Review DEPLOYMENT.md troubleshooting section
