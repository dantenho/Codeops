# GitHub Deployment Guide

This document provides comprehensive information about deploying and managing the EudoraX project using GitHub Actions workflows.

## Table of Contents

1. [Overview](#overview)
2. [Workflow Descriptions](#workflow-descriptions)
3. [Deployment Process](#deployment-process)
4. [Troubleshooting](#troubleshooting)
5. [Best Practices](#best-practices)

## Overview

The EudoraX project uses GitHub Actions for continuous integration, deployment, and automation. All workflows are located in `.github/workflows/` and follow the Agents.MD protocol.

### Key Workflows

- **CI Pipeline** - Comprehensive testing and validation
- **Agent Validation** - Ensures code complies with Agents.MD protocol
- **Security Scanning** - CodeQL, secret scanning, dependency checks
- **Release Management** - Automated versioning and releases
- **Branch Synchronization** - Keeps agent branches in sync
- **Telemetry Collection** - Aggregates and reports telemetry data

## Workflow Descriptions

### CI Pipeline (`ci.yml`)

**Purpose:** Comprehensive CI pipeline for all code changes.

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main`, `develop`, or `staging`
- Manual dispatch

**Jobs:**
1. **Lint & Format** - Runs Ruff, Black, isort, and MyPy across Python 3.10, 3.11, 3.12
2. **Test** - Executes test suites with coverage reporting
3. **Build** - Validates build dependencies
4. **CI Summary** - Generates summary report

**Usage:**
```bash
# Trigger manually
gh workflow run ci.yml
```

### Agent Validation (`agent-validation.yml`)

**Purpose:** Validates that all code changes comply with Agents.MD protocol.

**Triggers:**
- Pull requests to `main`, `develop`, or `staging`
- Push to `main` or `develop`

**Jobs:**
1. **Detect Agent** - Identifies agent from branch name or commit message
2. **Validate Documentation** - Checks docstring coverage and format
3. **Validate Code Quality** - Runs linting and type checking
4. **Run Tests** - Executes unit tests
5. **Validate Telemetry** - Validates telemetry JSON schemas
6. **Compliance Report** - Generates compliance summary

**Supported Agents:**
- GrokIA
- GeminiFlash25, GeminiPro25, GeminiPro30
- Jules
- ClaudeCode
- Composer
- DeepSeekR1
- GPT-5.1-Codex
- Antigravity
- Z.AI

### Security Scanning (`security.yml`)

**Purpose:** Security scanning and vulnerability detection.

**Triggers:**
- Push to `main` or `develop`
- Pull requests
- Weekly schedule (Sundays)
- Manual dispatch

**Jobs:**
1. **CodeQL Analysis** - Static code analysis for Python and JavaScript
2. **Secret Scanning** - Detects hardcoded secrets using Gitleaks
3. **Dependency Scan** - Checks for vulnerable dependencies
4. **Security Summary** - Generates security report

**Usage:**
```bash
# Run security scan manually
gh workflow run security.yml
```

### Release Management (`release.yml`)

**Purpose:** Automated versioning and GitHub release creation.

**Triggers:**
- Push of version tags (`v*.*.*`)
- Manual dispatch with version input

**Jobs:**
1. **Determine Version** - Calculates version from tags or inputs
2. **Generate Changelog** - Creates changelog from git commits
3. **Create Release** - Creates GitHub release with changelog
4. **Update Version Files** - Updates version in code files

**Usage:**
```bash
# Create release manually
gh workflow run release.yml \
  -f version=1.2.3 \
  -f release_type=minor \
  -f create_tag=true
```

### Branch Synchronization (`branch-sync.yml`)

**Purpose:** Keeps agent branches synchronized with `main`.

**Triggers:**
- Push to `main`
- Daily schedule (midnight UTC)
- Manual dispatch

**Features:**
- Automatically merges `main` into agent branches
- Creates PRs for merge conflicts
- Handles all supported agent branches

**Usage:**
```bash
# Sync branches manually
gh workflow run branch-sync.yml
```

### Merge Orchestrator (`merge-orchestrator.yml`)

**Purpose:** Automatically merges PRs that pass all checks.

**Triggers:**
- Pull request events (labeled, synchronize, opened, reopened)
- Completion of Agent Compliance Validation workflow

**Features:**
- Checks PR status and requirements
- Auto-merges trusted agent PRs
- Notifies on failures

**Auto-merge Conditions:**
- PR labeled with `auto-merge`
- All checks pass
- No merge conflicts
- Not a draft PR

### Telemetry Collector (`telemetry-collector.yml`)

**Purpose:** Collects and aggregates telemetry data from all agents.

**Triggers:**
- Every 6 hours (scheduled)
- Manual dispatch

**Outputs:**
- Markdown report (`telemetry_report.md`)
- JSON summary (`telemetry_summary.json`)
- Uploaded as artifacts

**Usage:**
```bash
# Collect telemetry manually
gh workflow run telemetry-collector.yml -f days=7
```

## Deployment Process

### Standard Deployment

1. **Create Feature Branch**
   ```bash
   git checkout -b agent/YourAgent/feature-name
   ```

2. **Make Changes**
   - Follow Agents.MD protocol
   - Add operation tags `[CREATE]`, `[REFACTOR]`, etc.
   - Include agent signature in files
   - Create telemetry logs

3. **Push and Create PR**
   ```bash
   git push origin agent/YourAgent/feature-name
   gh pr create --title "Description" --body "Details"
   ```

4. **Wait for Validation**
   - Agent Validation workflow runs automatically
   - Review compliance report
   - Fix any issues

5. **Merge**
   - Manual merge after review, or
   - Auto-merge if labeled with `auto-merge` and checks pass

### Release Deployment

1. **Prepare Release**
   ```bash
   # Update version in code
   # Commit changes
   git commit -m "chore: prepare release v1.2.3"
   ```

2. **Create Release**
   ```bash
   # Via GitHub UI or workflow dispatch
   gh workflow run release.yml -f version=1.2.3 -f release_type=minor
   ```

3. **Verify Release**
   - Check GitHub Releases page
   - Verify changelog is correct
   - Test release artifacts

## Troubleshooting

### Workflow Failures

**Agent Validation Fails:**
- Check docstring coverage (minimum 90%)
- Verify operation tags are present
- Ensure agent signature is included
- Check telemetry JSON schema compliance

**CI Pipeline Fails:**
- Review linting errors
- Fix type checking issues
- Update failing tests
- Check dependency compatibility

**Security Scan Finds Issues:**
- Review CodeQL findings in Security tab
- Remove hardcoded secrets
- Update vulnerable dependencies
- Address security warnings

### Common Issues

**Branch Sync Conflicts:**
- Workflow creates PR automatically
- Resolve conflicts manually
- Merge the sync PR

**Telemetry Validation Errors:**
- Check JSON syntax
- Verify schema compliance
- Ensure required fields are present
- Review `CodeAgents/schemas/` for schema definitions

**Auto-merge Not Working:**
- Verify PR has `auto-merge` label
- Check all required checks pass
- Ensure no merge conflicts
- Verify PR is not draft

## Best Practices

### For Agents

1. **Always Use Operation Tags**
   - `[CREATE]` for new code
   - `[REFACTOR]` for restructuring
   - `[DEBUG]` for bug fixes
   - `[MODIFY]` for changes

2. **Include Agent Signature**
   ```python
   # Agent: YourAgentName
   # Timestamp: 2025-12-03T23:30:00Z
   ```

3. **Create Telemetry Logs**
   - Log all operations in `CodeAgents/ID/YourAgent/logs/`
   - Use JSON format with proper schema
   - Include timestamps and status

4. **Follow Branch Naming**
   - Format: `agent/AgentName/feature-description`
   - Use descriptive names
   - Keep branches focused

### For Maintainers

1. **Review PRs Thoroughly**
   - Check compliance report
   - Verify telemetry logs
   - Review code quality
   - Test changes locally

2. **Monitor Workflows**
   - Check workflow status regularly
   - Review security findings
   - Monitor telemetry reports
   - Address failures promptly

3. **Keep Dependencies Updated**
   - Review Dependabot PRs
   - Test updates before merging
   - Update lock files
   - Document breaking changes

### For DevOps

1. **Monitor Workflow Performance**
   - Check execution times
   - Optimize slow workflows
   - Use caching effectively
   - Scale runners as needed

2. **Maintain Workflows**
   - Update action versions
   - Review workflow logs
   - Fix deprecated syntax
   - Document changes

3. **Security**
   - Review security scans
   - Rotate secrets regularly
   - Limit workflow permissions
   - Monitor for vulnerabilities

## Additional Resources

- [Agents.MD](../Agents.MD) - Protocol specification
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [docs/WORKFLOWS.md](../docs/WORKFLOWS.md) - Workflow documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Support

For issues or questions:
- Open an issue on GitHub
- Contact maintainers via CODEOWNERS
- Check workflow logs for details
- Review troubleshooting section above
