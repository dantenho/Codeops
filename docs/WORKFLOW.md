# Workflow Documentation

## Local Branching Strategy

**Rule #1**: Never push directly to the remote `main` branch without approval.

### Workflow Steps

1.  **Plan**: Define the task in `implementation_plan.md`.
2.  **Branch**: Create a local branch `feat/your-feature`.
3.  **Implement**: Write code following "The Scheme".
4.  **Verify**: Run tests locally.
5.  **Review**: Ask user for review.
6.  **Commit**: Commit with conventional message.

## Auto-Coding with Cursor

- Use **Agent Mode** for implementation.
- Reference `.cursor/rules` for context.
- Keep `instructions.md` updated.
