# GitHub Automation Plan - Full Spread (Espalha)

Complete plan to activate triggers, runners, and webhooks across all GitHub repositories.

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│         GitHub Actions & Automation Spread (Espalha)        │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┴────────┬────────────┬─────────────┐
       ▼                ▼            ▼             ▼
   Triggers       Runners         Webhooks      Notifications
   • Push         • Linux          • Push        • Slack
   • PR           • Windows        • PR          • Discord
   • Schedule     • macOS          • Release     • Email
   • Manual       • Custom         • Deploy      • GitHub
```

## Phase 1: Repository Setup

### 1.1 Enable GitHub Actions
```bash
# Repository Settings → Actions → General
✅ Allow all actions and reusable workflows
✅ Require approval for first-time contributors
✅ Read and write permissions
✅ Allow GitHub Actions to create and approve pull requests
```

### 1.2 Create Secrets
```bash
# Settings → Secrets and variables → Actions
- DOCKER_USERNAME
- DOCKER_PASSWORD
- GITHUB_TOKEN (auto-generated)
- SLACK_WEBHOOK_URL
- DISCORD_WEBHOOK_URL
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- GIT_COMMIT_AUTHOR
- DEPLOY_KEY
```

### 1.3 Create Variables
```bash
# Settings → Variables
- DOCKER_REGISTRY = docker.io
- DEPLOYMENT_ENV = production
- NOTIFICATION_CHANNEL = #deployments
```

## Phase 2: GitHub Actions Workflows

### 2.1 Main Branch CI/CD Pipeline
**File**: `.github/workflows/main-pipeline.yml`

Triggers on:
- ✅ Push to main
- ✅ Pull Requests
- ✅ Manual dispatch
- ✅ Scheduled (daily)

Jobs:
1. Lint & Format Check
2. Unit Tests
3. Build Docker Image
4. Security Scan
5. Deploy to Staging
6. Integration Tests
7. Deploy to Production
8. Notification

### 2.2 Workspace Branch Workflows
**File**: `.github/workflows/workspace-sync.yml`

Triggers on:
- ✅ Push to workspace/* branches
- ✅ Pull Requests to workspace/*
- ✅ Manual dispatch

Jobs:
1. Test workspace changes
2. Validate dependencies
3. Sync to shared branches
4. Notify maintainers

### 2.3 Protected Files Enforcement
**File**: `.github/workflows/protect-files.yml`

Triggers on:
- ✅ All pull requests
- ✅ All push attempts

Jobs:
1. Check for protected file modifications
2. Block PR if protected files changed
3. Require maintainer approval
4. Post comment on PR

### 2.4 Release & Versioning
**File**: `.github/workflows/release.yml`

Triggers on:
- ✅ Push tag (v*)
- ✅ Manual dispatch
- ✅ Release creation

Jobs:
1. Build release assets
2. Create GitHub release
3. Upload artifacts
4. Publish documentation
5. Deploy to production
6. Send release notifications

### 2.5 Node & Workflow Validation
**File**: `.github/workflows/validate-nodes.yml`

Triggers on:
- ✅ Changes to nodes/* or workflows/*
- ✅ Manual dispatch

Jobs:
1. Validate node YAML structure
2. Check dependencies
3. Test workflow definitions
4. Generate documentation

## Phase 3: Self-Hosted Runners

### 3.1 Runner Types
```
Windows Runner (Local PC)
├─ Asset generation (ComfyUI, Anime4K)
├─ GPU acceleration
└─ Local file system access

Linux Runner (Cloud VM)
├─ Backend API deployment
├─ Docker builds
└─ Database operations

macOS Runner (Optional)
├─ Frontend testing
└─ Cross-platform builds
```

### 3.2 Windows Runner Setup
```bash
# On your local machine
cd c:\Runners\CodeAgents

# Download latest runner
curl https://github.com/actions/runner/releases/download/v2.310.0/actions-runner-win-x64-2.310.0.zip -o runner.zip
Expand-Archive -Path runner.zip

# Configure
.\config.cmd --url https://github.com/yourusername/repo --token <token>

# Install as service
.\svc.cmd install
.\svc.cmd start
```

### 3.3 Linux Runner Setup
```bash
# On cloud VM
mkdir -p /opt/actions-runner
cd /opt/actions-runner

# Download
curl -o runner.tar.gz https://github.com/actions/runner/releases/download/v2.310.0/actions-runner-linux-x64-2.310.0.tar.gz
tar xzf runner.tar.gz

# Configure
./config.sh --url https://github.com/yourusername/repo --token <token>

# Install systemd service
sudo ./svc.sh install
sudo systemctl start actions-runner
```

### 3.4 Runner Labels
```yaml
windows-gpu:
  - windows
  - gpu
  - local
  - asset-generation

linux-cloud:
  - linux
  - cloud
  - docker
  - deployment

mac-test:
  - macos
  - testing
  - cross-platform
```

### 3.5 Runner Groups (Enterprise)
```
Asset Generation Group
├─ windows-gpu (primary)
├─ windows-gpu-2 (backup)
└─ Auto-scaling enabled

Backend Deployment Group
├─ linux-cloud (primary)
├─ linux-cloud-2 (secondary)
└─ Auto-scaling enabled

Frontend Testing Group
├─ mac-test
├─ linux-test
└─ windows-test
```

## Phase 4: Webhooks Configuration

### 4.1 Push Events
**Trigger**: Every push to any branch

Actions:
- ✅ Run matching workflow
- ✅ Update build status
- ✅ Notify Slack channel
- ✅ Update board/issues
- ✅ Deploy if main branch

### 4.2 Pull Request Events
**Trigger**: PR opened, synchronize, closed

Actions:
- ✅ Run CI tests
- ✅ Check protected files
- ✅ Validate code quality
- ✅ Post review comments
- ✅ Block merge if checks fail

### 4.3 Release Events
**Trigger**: Release created/published

Actions:
- ✅ Build release assets
- ✅ Deploy to production
- ✅ Notify all channels
- ✅ Update documentation
- ✅ Create release notes

### 4.4 Repository Events
**Trigger**: Various repository changes

Actions:
- ✅ New issue: Assign to board
- ✅ New PR: Auto-label
- ✅ Milestone: Notify team
- ✅ Discussion: Notify mods

### 4.5 Webhook Endpoints

**Slack Integration**
```
Webhook URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
Events:
  - Push (all branches)
  - PR (open/merged)
  - Deployment (success/failure)
  - Release
```

**Discord Integration**
```
Webhook URL: https://discordapp.com/api/webhooks/YOUR/URL
Events:
  - Deployment alerts
  - Test failures
  - Security vulnerabilities
  - Release announcements
```

**Custom Webhook**
```
Endpoint: https://your-api.com/github/webhook
Events:
  - All events
  - Full payload
  - Signed with secret
```

## Phase 5: Branch Protection Rules

### 5.1 Main Branch
```yaml
branch: main
protection:
  require_reviews: 2
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
  restrict_who_can_dismiss_reviews: true
  require_status_checks: true
  require_branches_up_to_date: true
  enforce_admins: true
  allow_force_pushes: false
  allow_deletions: false
  allow_auto_merge: true
  auto_merge_method: squash
```

### 5.2 Workspace Branches
```yaml
branch: workspace/*
protection:
  require_reviews: 1
  require_status_checks: true
  allow_force_pushes: false
  allow_deletions: false
  allow_auto_merge: true
```

### 5.3 Shared Branches
```yaml
branch: shared/*
protection:
  require_reviews: 1
  require_status_checks: true
  enforce_admins: true
  allow_force_pushes: false
```

## Phase 6: Automated Triggers

### 6.1 On Push
```yaml
trigger: push
branches:
  - main
  - workspace/*
  - shared/*
  
actions:
  - Run CI/CD pipeline
  - Run tests
  - Build artifacts
  - Deploy staging (main)
  - Update status checks
```

### 6.2 On Pull Request
```yaml
trigger: pull_request
types:
  - opened
  - synchronize
  - reopened
  
actions:
  - Run tests
  - Check protected files
  - Validate code quality
  - Check dependencies
  - Post review
```

### 6.3 On Schedule (Cron)
```yaml
trigger: schedule
jobs:
  - 0 2 * * * (Daily 2 AM): Full test suite
  - 0 0 * * 0 (Weekly Sun): Security scan
  - 0 0 1 * * (Monthly 1st): Dependency update
```

### 6.4 On Release
```yaml
trigger: release
types:
  - published
  - created
  
actions:
  - Build production assets
  - Deploy to live
  - Create release notes
  - Publish documentation
```

## Phase 7: Notifications Setup

### 7.1 Slack Channel
```
Channel: #codingagents-automation
Notifications:
  ✅ Workflow started/completed
  ✅ Test results (pass/fail)
  ✅ Deployment status
  ✅ PR reviews
  ✅ Release alerts
  ✅ Error alerts
```

### 7.2 Discord Server
```
Server: CodeAgents
Channels:
  #deployments (blue for success, red for failure)
  #tests (test results)
  #releases (release announcements)
  #alerts (critical errors)
```

### 7.3 Email Notifications
```
To: team@example.com
Events:
  ✅ Deployment failures
  ✅ Security vulnerabilities
  ✅ Build failures (main)
  ✅ Release published
```

### 7.4 GitHub Notifications
```
✅ Watch repository
✅ Enable notifications for:
  - All Activity
  - Releases
  - Discussions
```

## Implementation Steps

### Step 1: Initial Setup (Day 1)
```bash
# 1. Enable Actions in repo settings
# 2. Create .github/workflows directory
# 3. Add secrets and variables
# 4. Create main-pipeline.yml
# 5. Commit and push
git add .github/
git commit -m "chore: initialize github actions workflows"
git push origin main
```

### Step 2: Runners Setup (Day 2-3)
```bash
# 1. Download runners
# 2. Configure on Windows machine
# 3. Configure on Linux VM
# 4. Register with GitHub
# 5. Verify connections
# 6. Add labels
```

### Step 3: Webhooks & Integrations (Day 3)
```bash
# 1. Create Slack webhook
# 2. Create Discord webhook
# 3. Add webhook URLs as secrets
# 4. Configure notification workflow
# 5. Test notifications
```

### Step 4: Branch Protection (Day 4)
```bash
# 1. Set main branch rules
# 2. Set workspace/* rules
# 3. Set shared/* rules
# 4. Add required status checks
# 5. Test with PR
```

### Step 5: Scheduled Jobs (Day 5)
```bash
# 1. Create schedule.yml workflow
# 2. Add cron triggers
# 3. Test execution
# 4. Verify notifications
```

## Testing Checklist

- [ ] Push to main triggers pipeline
- [ ] PR triggers test suite
- [ ] Protected files cannot be modified
- [ ] Slack notifications working
- [ ] Discord notifications working
- [ ] Release triggers deployment
- [ ] Scheduled jobs run
- [ ] All status checks passing
- [ ] Runners operational (Windows + Linux)
- [ ] Branch protection enforced

## Monitoring & Maintenance

### Weekly
- [ ] Check runner status/logs
- [ ] Review failed workflows
- [ ] Update dependencies

### Monthly
- [ ] Update runners to latest version
- [ ] Review webhook logs
- [ ] Audit secret rotation
- [ ] Performance analysis

### Quarterly
- [ ] Update CI/CD pipeline
- [ ] Review automation costs
- [ ] Optimize workflows
- [ ] Update documentation

## Repository Structure
```
.github/
├── workflows/
│   ├── main-pipeline.yml          (CI/CD)
│   ├── workspace-sync.yml         (Workspace sync)
│   ├── protect-files.yml          (File protection)
│   ├── release.yml                (Release automation)
│   ├── validate-nodes.yml         (Node validation)
│   └── schedule.yml               (Scheduled tasks)
├── CODEOWNERS                      (Code ownership)
├── CONTRIBUTING.md                (Contribution guide)
└── dependabot.yml                 (Dependency updates)

GITHUB_AUTOMATION.md               (This file)
GITHUB_ACTIONS.md                  (Detailed workflows)
RUNNERS.md                         (Runner setup)
WEBHOOKS.md                        (Webhook configuration)
```

## Success Metrics

- CI/CD pipeline runs on every push
- All tests pass before merging
- Deployments are automated
- Zero manual deployment steps
- Protected files are protected
- Team is notified of all critical events
- Runners handle all workloads
- No failed workflows in main branch
- Deployment time < 5 minutes
- 99.9% workflow success rate

## Next Steps

1. ✅ Create `.github/workflows/` directory
2. ✅ Add main-pipeline.yml
3. ✅ Setup self-hosted runners
4. ✅ Configure webhooks
5. ✅ Enable branch protection
6. ✅ Test everything
7. ✅ Deploy to production
8. ✅ Monitor and optimize
