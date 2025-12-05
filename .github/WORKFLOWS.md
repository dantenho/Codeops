# GitHub Actions Workflows Documentation

This document describes all the automated workflows configured for this repository.

## Overview

The repository uses GitHub Actions for CI/CD, monitoring, and automation. All workflows are located in [`.github/workflows/`](.github/workflows/).

## Workflows

### 1. Main CI/CD Pipeline
**File**: [`main-pipeline.yml`](workflows/main-pipeline.yml)

**Triggers**:
- Push to `main`, `workspace/*`, `shared/*` branches
- Pull requests to `main`, `workspace/*`
- Daily at 2 AM UTC (scheduled)
- Manual dispatch

**Path Filters**: Ignores documentation, markdown files, and GitHub templates.

**Concurrency**: Cancels in-progress runs for the same branch.

**Stages**:
1. **Lint & Format** - Code quality checks (black, isort, flake8)
2. **Unit Tests** - Runs pytest with coverage reporting
3. **Protected Files Check** - Prevents modification of protected YAML files
4. **Build Docker Image** - Builds and pushes to Docker Hub
5. **Security Scan** - Trivy vulnerability scanning
6. **Deploy to Staging** - Automatic staging deployment
7. **Integration Tests** - Post-deployment tests
8. **Deploy to Production** - Production deployment (requires approval)
9. **Summary & Notifications** - Slack/Discord notifications

**Required Secrets**:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `SLACK_WEBHOOK_URL`
- `DISCORD_WEBHOOK_URL`

---

### 2. Worker Nodes CI/CD
**File**: [`worker-nodes.yml`](workflows/worker-nodes.yml)

**Purpose**: Specialized workflow for Celery worker and node testing.

**Triggers**:
- Push to branches with changes in:
  - `packages/worker/**`
  - `nodes/comfyui/**`
  - `nodes/anime4k/**`
  - `nodes/civitai/**`
  - `requirements.txt`
- Pull requests affecting worker/node code
- Manual dispatch with options

**Concurrency**: Cancels in-progress worker builds for the same branch.

**Jobs**:
1. **Detect Changes** - Smart path filtering to run only affected tests
2. **Lint Worker Code** - Python linting (black, isort, flake8, mypy, pylint)
3. **Test Worker Tasks** - Unit tests with Redis service
4. **Celery Integration Tests** - Full Celery worker testing
5. **Performance Tests** - Benchmarking with pytest-benchmark
6. **Build Worker Image** - Docker image build and push
7. **Deploy to Staging** - Worker deployment
8. **Notifications** - Slack/Discord alerts

**Features**:
- Automatic Redis service provisioning
- Coverage reporting to Codecov
- Performance benchmarking with historical tracking
- Smoke tests after deployment

---

### 3. Dependency Updates & Security
**File**: [`dependency-updates.yml`](workflows/dependency-updates.yml)

**Triggers**:
- Weekly on Mondays at 9 AM UTC
- Manual dispatch with update type selection

**Update Types**:
- `patch` - Patch version updates only
- `minor` - Minor version updates (default)
- `major` - Major version updates
- `all` - All available updates

**Jobs**:
1. **Check Python Dependencies** - Detects available updates
2. **Update Python Dependencies** - Creates PR with updates
3. **Check Node.js Dependencies** - npm package updates
4. **Security Scan** - Trivy, Bandit, and pip-audit
5. **CVE Check** - Safety check for known vulnerabilities
6. **Generate Report** - Summary and notifications

**Features**:
- Automatic PR creation with test results
- Security vulnerability alerts
- Creates GitHub issues for critical CVEs
- Weekly dependency health reports

**Required Tools**:
- `pur` - Python dependency updates
- `pip-audit` - Security auditing
- `safety` - CVE checking
- `bandit` - Security linting

---

### 4. Health Monitoring & Alerts
**File**: [`health-monitoring.yml`](workflows/health-monitoring.yml)

**Triggers**:
- Hourly health checks
- Deep checks every 6 hours
- Manual dispatch

**Check Types**:
- `quick` - Basic health check
- `full` - Complete health check
- `deep` - Deep analysis with performance tests

**Jobs**:
1. **Check Workers** - Celery worker status and count
2. **Check Redis** - Redis connection and memory
3. **Check Queues** - Task queue lengths and backlogs
4. **Performance Check** - Response time and latency
5. **Alert on Issues** - Creates incidents and sends alerts
6. **Auto-remediation** - Attempts automatic fixes
7. **Health Report** - Comprehensive status summary

**Alert Conditions**:
- No active workers detected
- Queue backlog > 100 tasks
- High latency (>1000ms)
- Redis connection failures

**Remediation**:
- Automatic worker restart attempts
- Queue backlog analysis
- Stale task purging

**Notifications**:
- GitHub issues for incidents
- Slack alerts
- Discord notifications

---

### 5. Branch Synchronization
**File**: [`branch-sync.yml`](workflows/branch-sync.yml)

**Triggers**:
- Push to `main` or `master`
- Every 6 hours (scheduled)
- Weekly deep sync (Sunday 2 AM)
- Manual dispatch

**Features**:
- Discovers all `agent/` branches
- Supports merge, rebase, or squash strategies
- Handles merge conflicts gracefully
- Creates PRs for conflicts
- Dry-run mode available
- Stale branch cleanup
- Historical metrics tracking

**Manual Options**:
- `sync_strategy` - merge/rebase/squash
- `dry_run` - Test without changes
- `specific_branch` - Sync single branch
- `force_sync` - Overwrite conflicts
- `cleanup_stale` - Remove old branches
- `create_conflict_prs` - Auto-create conflict PRs

---

### 6. Workspace Sync & Validation
**File**: [`workspace-sync.yml`](workflows/workspace-sync.yml)

**Triggers**:
- Push to `workspace/*` or `shared/*` branches
- Pull requests
- Manual dispatch

**Workspaces**:
- `workspace/agents`
- `workspace/assets-generator`
- `workspace/frontend-streamlit`
- `workspace/backend`
- `shared/chromadb`

**Jobs**:
1. **Validate Workspace** - Dependency and configuration checks
2. **Sync Shared Branches** - Propagates shared code to workspaces
3. **Validate YAML** - Node and workflow YAML validation
4. **Status Check** - Summary and reporting

---

### 7. Release & Deployment
**File**: [`release.yml`](workflows/release.yml)

**Triggers**:
- Push tags matching `v*` (e.g., v1.0.0)
- Published releases
- Manual dispatch with version input

**Jobs**:
1. **Build Release Assets** - Creates distribution packages
2. **Publish Docker Image** - Multi-tag Docker images
3. **Deploy to Production** - Production deployment
4. **Publish GitHub Release** - Creates/updates release
5. **Update Documentation** - CHANGELOG updates
6. **Final Notification** - Complete pipeline status

**Version Tags**:
- `latest` - Most recent release
- `v1.2.3` - Specific version
- `${{ github.sha }}` - Commit-specific

---

## Configuration

### Required Secrets

Configure these in repository settings → Secrets and variables → Actions:

```
DOCKER_USERNAME          # Docker Hub username
DOCKER_PASSWORD          # Docker Hub password/token
SLACK_WEBHOOK_URL        # Slack incoming webhook
DISCORD_WEBHOOK_URL      # Discord webhook
GITHUB_TOKEN             # Auto-provided by GitHub
```

### Required Permissions

Workflows need these permissions:
- `contents: write` - For releases and commits
- `packages: write` - For Docker registry
- `issues: write` - For creating alerts
- `pull-requests: write` - For automated PRs

### Environment Variables

Common environment variables:
```yaml
REDIS_URL: redis://localhost:6379/0
PYTHON_VERSION: '3.11'
NODE_VERSION: '18'
REGISTRY: docker.io
```

---

## Usage Examples

### Manual Workflow Dispatch

#### Run Worker Tests
```bash
# Via GitHub CLI
gh workflow run worker-nodes.yml \
  -f test_mode=full \
  -f run_performance_tests=true

# Via GitHub UI
Actions → Worker Nodes CI/CD → Run workflow
```

#### Update Dependencies
```bash
gh workflow run dependency-updates.yml \
  -f update_type=minor \
  -f create_pr=true
```

#### Health Check
```bash
gh workflow run health-monitoring.yml \
  -f check_type=deep \
  -f send_notifications=true
```

#### Branch Sync
```bash
gh workflow run branch-sync.yml \
  -f sync_strategy=merge \
  -f specific_branch=agent/feature-x
```

---

## Monitoring & Alerts

### Status Badges

Add to your README:

```markdown
![Main Pipeline](https://github.com/your-org/your-repo/workflows/Main%20CI/CD%20Pipeline/badge.svg)
![Worker Health](https://github.com/your-org/your-repo/workflows/Worker%20Nodes%20CI/CD/badge.svg)
![Dependencies](https://github.com/your-org/your-repo/workflows/Dependency%20Updates%20%26%20Security/badge.svg)
```

### Alert Channels

- **Slack**: Receives all pipeline and health alerts
- **Discord**: Production deployments and critical alerts
- **GitHub Issues**: Created for incidents and security issues
- **Email**: GitHub notifications for failed workflows

---

## Troubleshooting

### Workflow Not Triggering

**Check**:
1. Path filters - ensure changed files aren't excluded
2. Branch patterns - verify branch name matches triggers
3. Concurrency groups - previous run may have canceled it
4. Required secrets - missing secrets cause silent failures

### Failed Jobs

**Common Issues**:
- Redis connection: Ensure Redis service is configured
- Docker login: Verify DOCKER_USERNAME and DOCKER_PASSWORD
- Test failures: Check test logs in workflow run
- Permission denied: Review workflow permissions

### Performance Issues

**Optimizations**:
- Use path filters to skip unnecessary jobs
- Enable concurrency cancellation
- Cache dependencies (pip, npm)
- Use matrix builds for parallelization
- Run expensive jobs conditionally

---

## Best Practices

### Workflow Design

1. **Use Path Filters** - Only run when relevant files change
2. **Add Concurrency Controls** - Cancel outdated runs
3. **Enable Caching** - Speed up dependency installation
4. **Fail Fast** - Set `fail-fast: false` for matrix builds
5. **Add Timeouts** - Prevent hung jobs from blocking queue

### Security

1. **Use Secrets** - Never hardcode credentials
2. **Pin Action Versions** - Use `@v4` not `@main`
3. **Review Dependencies** - Check third-party actions
4. **Least Privilege** - Minimal required permissions
5. **Audit Logs** - Review workflow execution logs

### Notifications

1. **Alert on Failure** - But not every run
2. **Use Job Summary** - `$GITHUB_STEP_SUMMARY` for reports
3. **Group Related Alerts** - Avoid notification spam
4. **Include Context** - Links to runs, commits, logs

---

## Development

### Testing Workflows Locally

Use [act](https://github.com/nektos/act) to test locally:

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow locally
act -j lint-worker

# With secrets
act -j test-worker --secret-file .secrets
```

### Debugging

Add to workflow for debugging:
```yaml
- name: Debug
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
    env
```

Enable debug logging:
```bash
# Repository settings → Secrets → New secret
ACTIONS_STEP_DEBUG = true
ACTIONS_RUNNER_DEBUG = true
```

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Hub](https://hub.docker.com/)

---

## Contributing

When adding new workflows:

1. Document the workflow in this file
2. Add required secrets to the secrets list
3. Include usage examples
4. Test with manual dispatch first
5. Add status badges to README
6. Update troubleshooting section if needed

---

**Last Updated**: 2025-12-05
**Maintained By**: DevOps Team
