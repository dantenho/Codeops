[1mdiff --git a/.github/ISSUE_TEMPLATE/agent-task.yml b/.github/ISSUE_TEMPLATE/agent-task.yml[m
[1mindex 4395f41..57b3190 100644[m
[1m--- a/.github/ISSUE_TEMPLATE/agent-task.yml[m
[1m+++ b/.github/ISSUE_TEMPLATE/agent-task.yml[m
[36m@@ -1,51 +1,449 @@[m
[31m-name: Agent Task[m
[31m-description: Create a new task for an AI agent[m
[31m-title: "[Task]: "[m
[31m-labels: ["agent-task", "triage"][m
[32m+[m[32m# .github/ISSUE_TEMPLATE/agent-task.yml[m
[32m+[m[32m# ══════════════════════════════════════════════════════════════════════════════[m
[32m+[m[32m# 🤖 AI Agent Task Template - SOTA Configuration[m
[32m+[m[32m# ══════════════════════════════════════════════════════════════════════════════[m
[32m+[m
[32m+[m[32mname: "🤖 Agent Task"[m
[32m+[m[32mdescription: "Create a new task for an AI coding agent"[m
[32m+[m[32mtitle: "[Agent]: "[m
[32m+[m[32mlabels: ["agent-task", "triage", "awaiting-assignment"][m
[32m+[m[32massignees: [][m
[32m+[m
 body:[m
[32m+[m[32m  # ──────────────────────────────────────────────────────────────────────────────[m
[32m+[m[32m  # 📋 HEADER SECTION[m
[32m+[m[32m  # ──────────────────────────────────────────────────────────────────────────────[m
[32m+[m
[32m+[m[32m  - type: markdown[m
[32m+[m[32m    attributes:[m
[32m+[m[32m      value: |[m
[32m+[m[32m        ## 🤖 AI Agent Task Request[m
[32m+[m
[32m+[m[32m        Complete this form to create a well-structured task for an AI coding agent.[m
[32m+[m[32m        The more context you provide, the better the agent can execute the task.[m
[32m+[m
[32m+[m[32m        ---[m
[32m+[m
[32m+[m[32m  # ──────────────────────────────────────────────────────────────────────────────[m
[32m+[m[32m  # 🎯 CORE TASK DEFINITION[m
[32m+[m[32m  # ──────────────────────────────────────────────────────────────────────────────[m
[32m+[m
   - type: dropdown[m
     id: agent[m
     attributes:[m
[31m-      label: Assigned Agent[m
[32m+[m[32m      label: "🤖 Assigned Agent"[m
[32m+[m[32m      description: "Select the AI agent best suited for this task"[m
       options:[m
[31m-        - GrokIA[m
[31m-        - GeminiFlash25[m
[31m-        - GeminiPro25[m
[31m-        - GeminiPro30[m
[31m-        - Jules[m
[31m-        - ClaudeCode[m
[31m-        - Composer[m
[31m-        - Antigravity[m
[32m+[m[32m        - "🔮 Auto-Assign (Let maintainers decide)"[m
[32m+[m[32m        - "── Claude Family ──"[m
[32m+[m[32m        - "ClaudeCode (Precise coding, documentation)"[m
[32m+[m[32m        - "Composer (Real-time editing, IDE integration)"[m
[32m+[m[32m        - "── Google Family ──"[m
[32m+[m[32m        - "GeminiFlash25 (Gemini CLI Flash 2.5)"[m
[32m+[m[32m        - "GeminiPro25 (Gemini CLI Pro 2.5)"[m
[32m+[m[32m        - "GeminiPro30 (Gemini Pro 3.0)"[m
[32m+[m[32m        - "Jules (CI/CD automation, DevOps)"[m
[32m+[m[32m        - "── OpenAI Family ──"[m
[32m+[m[32m        - "Codex (OpenAI)"[m
[32m+[m[32m        - "GitHub Copilot"[m
[32m+[m[32m        - "── xAI Family ──"[m
[32m+[m[32m        - "GrokIA (Contextual analysis, intelligent refactoring)"[m
[32m+[m[32m        - "Grok 3"[m
[32m+[m[32m        - "── Other Agents ──"[m
[32m+[m[32m        - "Windsurf (Codeium)"[m
[32m+[m[32m        - "Aider"[m
[32m+[m[32m        - "Devin (Cognition)"[m
[32m+[m[32m        - "Amazon Q Developer"[m
[32m+[m[32m        - "Cody (Sourcegraph)"[m
[32m+[m[32m        - "Tabnine"[m
[32m+[m[32m        - "Replit Ghostwriter"[m
[32m+[m[32m        - "Antigravity"[m
[32m+[m[32m        - "── Custom/Other ──"[m
[32m+[m[32m        - "Custom Agent (specify below)"[m
     validations:[m
       required: true[m
 [m
[32m+[m[32m  - type: input[m
[32m+[m[32m    id: custom_agent[m
[32m+[m[32m    attributes:[m
[32m+[m[32m      label: "Custom Agent Name"[m
[32m+[m[32m      description: "If you selected 'Custom Agent' above, specify the agent name"[m
[32m+[m[32m      placeholder: "e.g., MyCustomAgent v2.1"[m
[32m+[m[32m    validations:[m
[32m+[m[32m      required: false[m
[32m+[m
   - type: dropdown[m
     id: task_type[m
     attributes:[m
[31m-      label: Task Type[m
[32m+[m[32m      label: "📌 Task Type"[m
[32m+[m[32m      description: "Primary type of work required"[m
       options:[m
[31m-        - CREATE[m
[31m-        - REFACTOR[m
[31m-        - DEBUG[m
[31m-        - OPTIMIZE[m
[31m-        - DOCUMENT[m
[31m-        - ANALYZE[m
[32m+[m[32m        - "🆕 CREATE - Build new feature/component"[m
[32m+[m[32m        - "♻️ REFACTOR - Improve existing code structure"[m
[32m+[m[32m        - "🐛 DEBUG - Find and fix bugs"[m
[32m+[m[32m        - "⚡ OPTIMIZE - Improve performance"[m
[32m+[m[32m        - "📝 DOCUMENT - Write/update documentation"[m
[32m+[m[32m        - "🔍 ANALYZE - Code review/analysis"[m
[32m+[m[32m        - "🧪 TEST - Write/improve tests"[m
[32m+[m[32m        - "🔧 CONFIGURE - Setup/configuration changes"[m
[32m+[m[32m        - "🔗 INTEGRATE - Third-party integration"[m
[32m+[m[32m        - "🔒 SECURITY - Security improvements"[m
[32m+[m[32m        - "🗃️ DATABASE - Schema/migration changes"[m
[32m+[m[32m        - "🎨 UI/UX - Frontend/styling changes"[m
[32m+[m[32m        - "🏗️ INFRASTRUCTURE - DevOps/CI/CD changes"[m
[32m+[m[32m        - "📦 DEPENDENCY - Update/manage dependencies"[m
[32m+[m[32m        - "🧹 CLEANUP - Remove dead code/tech debt"[m
     validations:[m
       required: true[m
 [m
[32m+[m[32m  - type: dropdown[m
[32m+[m[32m    id: priority[m
[32m+[m[32m    attributes:[m
[32m+[m[32m      label: "🚨 Priority Level"[m
[32m+[m[32m      description: "How urgent is this task?"[m
[32m+[m[32m      options:[m
[32m+[m[32m        - "🔴 P0 - Critical (Production blocker)"[m
[32m+[m[32m        - "🟠 P1 - High (Needed this sprint)"[m
[32m+[m[32m        - "🟡 P2 - Medium (Planned work)"[m
[32m+[m[32m        - "🟢 P3 - Low (Nice to have)"[m
[32m+[m[32m        - "⚪ P4 - Backlog (Future consideration)"[m
[32m+[m[32m      default: 2[m
[32m+[m[32m    validations:[m
[32m+[m[32m      required: true[m
[32m+[m
[32m+[m[32m  - type: dropdown[m
[32m+[m[32m    id: complexity[m
[32m+[m[32m    attributes:[m
[32m+[m[32m      label: "📊 Estimated Complexity"[m
[32m+[m[32m      description: "How complex is this task?"[m
[32m+[m[32m      options:[m
[32m+[m[32m        - "🟢 Trivial (< 30 min, single file change)"[m
[32m+[m[32m        - "🟡 Simple (< 2 hours, few files)"[m
[32m+[m[32m        - "🟠 Medium (< 1 day, multiple components)"[m
[32m+[m[32m        - "🔴 Complex (< 1 week, architectural changes)"[m
[32m+[m[32m        - "⚫ Epic (> 1 week, major feature)"[m
[32m+[m[32m      default: 1[m
[32m+[m[32m    validations:[m
[32m+[m[32m      required: true[m
[32m+[m
[32m+[m[32m  # ─────────────