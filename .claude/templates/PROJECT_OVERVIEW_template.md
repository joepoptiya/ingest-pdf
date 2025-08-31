---
project_id: PROJ-####
name: <project name>
owner: @handle
stakeholders: [@handle1, @handle2]
repo: <url or path>
environments: [local, dev, stage, prod]
created: YYYY-MM-DD
target_release: YYYY-MM-DD
risk_level: low | medium | high
status: Proposed | Active | Paused | Complete
labels: [area/backend, security, infra]
---

# Project Overview — PROJ-#### <project name>

## Vision

One short paragraph describing the user value and the change in the world after this ships.

## Goals (Measurable)

- <goal 1>
- <goal 2>

## Non-Goals

- <non-goal 1>
- <non-goal 2>

## Success Metrics

- <metric name>: baseline → target by <date>
- <metric name>: baseline → target by <date>

## Scope

### In-Scope

- <item>

### Out-of-Scope

- <item>

## Architecture (High Level)

- System context: <one-paragraph overview>
- Components/services: <list or links to ADR/diagrams>
- Data model links: <schema/ERD paths>
- External deps/integrations: <APIs, vendors, auth>

## Security & Compliance

- Data classification: <none | PII | secrets>
- Threats considered: <prompt injection, XSS, authZ, secrets>
- Controls: <least-privilege, audit logging, rate limits>
- Compliance notes: <SOC2/GDPR/PCI>, if any

## Rollout Plan

- Toggles/flags: <flag names>
- Environments & order: <local → dev → stage → prod>
- Observability: <logs/metrics/traces, dashboards, alerts>
- Rollback: <high-level approach>

## Work Breakdown

### Epics

- EPIC-#### — <title>: <one-sentence goal>
- EPIC-#### — <title>: <one-sentence goal>

### Milestones

- M1 — <name>: due YYYY-MM-DD
- M2 — <name>: due YYYY-MM-DD

---

## Task Seeds (YAML)

Below YAML will be parsed to generate atomic task files. Keep each task ≤ 2h and single-outcome. Use EPIC IDs from above.

```yaml
tasks:
  - id_hint: 1                      # used to help with ordering; final ID auto-assigned
    title: <actionable title>
    epic: EPIC-####                 # parent epic
    priority: P1
    owner: @handle
    timebox: 90m
    environments: [local]
    labels: [area/backend]
    prerequisites:
      - TASK-####                   # if any
    objective: >
      <what will exist when done; outcome not activity>
    in_scope:
      - <item>
    out_of_scope:
      - <item>
    components:
      - <component name>
    commands:
      - type: shell
        cwd: ./app
        run:
          - pnpm install
          - pnpm test
    file_changes:
      - path: app/src/config.ts
        intent: Enable FEATURE_X
        patch: |
          --- a/app/src/config.ts
          +++ b/app/src/config.ts
          @@
          -export const FEATURE_X = false;
          +export const FEATURE_X = true;
    acceptance:
      - Given <precondition>, When <action>, Then <outcome>
    verification:
      - curl http://localhost:3000/healthz # expect 200
    require_confirm: [publish, deploy, delete, network-external]

  - id_hint: 2
    title: <next task>
    epic: EPIC-#### 
    priority: P2
    owner: @handle
    timebox: 60m
    environments: [local]
    labels: [area/infra]
    objective: >
      <outcome>
    commands:
      - type: shell
        cwd: ./infra
        run:
          - terraform fmt -check
          - terraform validate
    acceptance:
      - Given <precondition>, When <action>, Then <outcome>
