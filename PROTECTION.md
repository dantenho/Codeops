# Protected Files & Immutable Workflow

⚠️ **CRITICAL: These files are immutable and protected by Git hooks**

## Protected Files

### Node Specifications (nodes/*.yaml)

All node YAML files are **READ-ONLY** and cannot be modified:

```
nodes/anime4k/node.yaml           ✓ PROTECTED
nodes/civitai/node.yaml           ✓ PROTECTED
nodes/comfyui/node.yaml           ✓ PROTECTED
nodes/gradio_eval/node.yaml       ✓ PROTECTED
nodes/nft_mint/node.yaml          ✓ PROTECTED
nodes/rag/node.yaml               ✓ PROTECTED
nodes/gas_tracker/node.yaml       ✓ PROTECTED
nodes/social_media/node.yaml      ✓ PROTECTED
nodes/sales_strategy/node.yaml    ✓ PROTECTED
nodes/gemini_analysis/node.yaml   ✓ PROTECTED
```

### Workflow Definition (workflows/pipeline.yaml)

```
workflows/pipeline.yaml           ✓ PROTECTED
```

## Protection Levels

| Level | Protection |
|-------|-----------|
| **Immutable** | Cannot be modified after creation |
| **Git Hooks** | Pre-commit hooks prevent commits |
| **Admin Only** | Only maintainer can request changes |
| **Review** | Changes require 2 maintainer approvals |

## What You Cannot Do

❌ Modify node specifications
❌ Change workflow stages
❌ Update dependencies
❌ Alter function definitions
❌ Change branch mappings
❌ Modify protection rules

## What You CAN Do

✅ Read specifications
✅ Create new nodes (if authorized)
✅ Extend with new files
✅ Submit change requests
✅ Report issues

## If You Need to Change Something

### Request Process

1. **Identify the change needed**
   ```
   Example: Add new function to comfyui node
   ```

2. **Create an issue with:**
   - Current specification
   - Proposed changes
   - Justification
   - Impact analysis

3. **Get approval from:**
   - 2 Maintainers minimum
   - Project lead

4. **Maintainer will:**
   - Review the change
   - Update the protected file
   - Document the modification
   - Tag with new version

### Change Request Template

```markdown
## Change Request: [Node/Workflow Name]

### Current State
[Current specification excerpt]

### Proposed Changes
[Detailed changes]

### Justification
[Why this change is needed]

### Impact
- Affected workspaces: [list]
- Dependencies: [list]
- Risk level: [Low/Medium/High]

### Approval
- [ ] Maintainer 1: ___________
- [ ] Maintainer 2: ___________
```

## Git Hook Protection

### How It Works

When you try to commit changes to protected files:

```bash
$ git commit -m "fix: update comfyui"

================================================
⚠️  PROTECTION CHECK: Node & Workflow YAML files
================================================
❌ ERROR: Cannot modify protected file: nodes/comfyui/node.yaml
   This file is immutable and protected.
   Contact maintainer for changes.

================================================
COMMIT REJECTED: Protected files cannot be modified
================================================
```

### Bypass (Maintainer Only)

To bypass protection (maintainers only):

```bash
git commit --no-verify  # Skip pre-commit hooks
```

**⚠️ Use only with explicit justification and version update**

## Node Specifications

Each node.yaml file contains:

```yaml
node:
  name: "Node Name"
  id: "node_id"
  version: "1.0.0"
  status: "protected"

protected: true                    # Cannot be modified
immutable: true                    # Locked in place
modification_locked: true          # Prevents changes

protection:
  level: "critical"
  rule: "NO MODIFICATIONS ALLOWED"
  admin_only: true
  
changes:
  allowed: false                   # All modifications blocked
  requires_approval: "MAINTAINER_ONLY"
  requires_review: "2_MAINTAINERS"
```

## Workflow Pipeline Structure

Protected workflow includes:

1. **Stage 1**: Market Research (social_media, nft_trend)
2. **Stage 2**: Strategy Development (sales_strategy, rag)
3. **Stage 3**: Asset Generation (civitai, comfyui)
4. **Stage 4**: Quality Enhancement (real_esrgan, anime4k)
5. **Stage 5**: Human Evaluation (gradio_eval)
6. **Stage 6**: Database Integration (chromadb)
7. **Stage 7**: Blockchain Publishing (gas_tracker, nft_mint)

Each stage is immutable to ensure workflow integrity.

## Important Notes

⚠️ **These protections exist to:**
- Maintain system stability
- Prevent accidental modifications
- Ensure consistent workflow execution
- Protect critical specifications

⚠️ **All changes must:**
- Follow formal request process
- Have proper justification
- Get maintainer approval
- Be properly documented
- Include version updates

## Version History

| Version | Date | Status | Maintainer |
|---------|------|--------|-----------|
| 1.0.0 | 2025-12-05 | Protected | Admin |

## Support

For questions or change requests:
- Contact: Admin/Maintainer
- Issue: [Create issue in repository]
- Request: Follow Change Request Template

---

**Last Updated**: 2025-12-05  
**Status**: ACTIVE PROTECTION  
**Git Hooks**: ENABLED
