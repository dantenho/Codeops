# 🔀 Git Local Branches Policy

## [CREATE] Documentation for local-only branch policy
**Agent:** Composer
**Timestamp:** 2025-12-05T01:45:00Z

---

## ⚠️ CRITICAL POLICY: All Branches Are Local

**All branches MUST be local-only by default.**

This policy prevents common Git errors and keeps your workflow clean.

---

## ✅ What This Means

### Allowed:
- ✅ Create branches locally: `git checkout -b agent/YourAgent/feature-name`
- ✅ Work on branches locally without remote tracking
- ✅ Push branches only when explicitly needed for PRs
- ✅ Unset upstream tracking if accidentally set

### Forbidden:
- ❌ Automatic upstream tracking: `git push -u origin branch` (use without `-u`)
- ❌ Setting up remote tracking by default
- ❌ Pulling from non-existent remote branches

---

## 🚀 Common Workflows

### Create a Local Branch

```bash
# Create and switch to new branch (local-only)
git checkout -b agent/Composer/new-feature

# Work on your changes
# ... make edits ...

# Commit locally
git add .
git commit -m "[Composer] feat: add new feature"
```

### Push When Ready for PR

```bash
# Push branch to remote (without tracking)
git push origin agent/Composer/new-feature

# Create PR via GitHub CLI or web interface
gh pr create --title "Add new feature" --body "Description"
```

### Fix Accidental Upstream Tracking

If you accidentally set upstream tracking and get errors:

```bash
# Check current branch tracking
git branch -vv

# Unset upstream tracking
git branch --unset-upstream

# Verify it's now local-only
git branch -vv
```

---

## 🔧 Configuration

### Git Global Config

Apply these settings globally:

```bash
git config --global push.default simple
git config --global push.autoSetupRemote false
git config --global branch.autoSetupMerge false
```

Or copy from `.gitconfig.local`:

```bash
# Windows PowerShell
cat .gitconfig.local | git config --global --list --file -
```

### Cursor IDE Settings

The workspace settings (`.vscode/settings.json`) are already configured to:
- Not auto-fetch remote branches
- Not auto-setup remote tracking
- Keep branches local by default

---

## 🐛 Troubleshooting

### Error: "couldn't find remote ref"

**Cause:** Branch is tracking a remote branch that doesn't exist.

**Fix:**
```bash
git branch --unset-upstream
```

### Error: "fatal: The current branch has no upstream branch"

**Cause:** Git is trying to push/pull but no upstream is set.

**Fix:** This is expected! Push explicitly:
```bash
git push origin branch-name
```

### VS Code Showing "Branch is ahead/behind"

**Cause:** Branch has upstream tracking set.

**Fix:**
```bash
git branch --unset-upstream
```

Then reload VS Code/Cursor.

---

## 📋 Quick Reference

| Command | Purpose |
|---------|---------|
| `git checkout -b branch-name` | Create local branch |
| `git branch --unset-upstream` | Remove upstream tracking |
| `git branch -vv` | Check branch tracking status |
| `git push origin branch-name` | Push without tracking |
| `git push -u origin branch-name` | ❌ Don't use `-u` flag |

---

## 📚 Related Documentation

- **Agents.MD:** See "GitHub Integration & Merge Protocol" section
- **Cursor Settings:** `.vscode/settings.json`
- **Git Config Template:** `.gitconfig.local`

---

**Agent:** Composer
**Last Updated:** 2025-12-05T01:45:00Z
