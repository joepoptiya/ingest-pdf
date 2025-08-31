Claude Code rule to generate tasks from PROJECT_OVERVIEW (save as .claude/rules/overview-to-tasks.mdc)
```md
---
description: Parse PROJECT_OVERVIEW.md "Task Seeds (YAML)" and generate atomic task files ready for execution.
globs:
  - PROJECT_OVERVIEW.md
alwaysApply: true
---

When the user says "Generate tasks" (or opens PROJECT_OVERVIEW.md and requests generation):

1) Parse the "Task Seeds (YAML)" block under the heading exactly named "Task Seeds (YAML)".
2) For each entry in tasks:
   - Allocate a new sequential ID TASK-#### (use zero-padded 4 digits; order by id_hint then title).
   - Create file: tasks/TASK-####-<kebab-title>.md using the established atomic task template (the one provided earlier).
   - Populate frontmatter fields: id, title, status=Pending, priority, owner, parent=<epic>, created=<today>, due=<empty>, timebox, labels, environments, require_confirm.
   - Fill sections: Summary (from objective), Prerequisites, Objective, Scope (split into In-Scope/Out-of-Scope), Components to Install, Commands, File Changes, Acceptance Criteria, Verification, Rollback (empty unless specified).
   - If file_changes patches are present, insert exactly as provided.
   - If commands are present, preserve order and cwd.
3) After creating all tasks:
   - Write an index file at tasks/INDEX.md listing TASK-####, titles, owners, priorities, epic links.
   - Reply with the list of created task file paths and ask for confirmation to proceed with execution if requested.
4) Safety:
   - Never run commands during generation; only scaffold files.
   - If any patch fails to apply cleanly during later execution, pause and request user guidance.