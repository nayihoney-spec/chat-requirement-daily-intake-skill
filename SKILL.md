---
name: chat-requirement-daily-intake
description: Extract feature, improvement, and bug requests from configurable group-chat exports, generate a daily requirement report, compare against historical records and an issue tracker, and create only verified new items. Use for recurring requirement-intake workflows based on local or mounted chat data. Do not use for general chat summaries or when the user has not authorized the data source and destination system.
---

# Chat Requirement Daily Intake

## Purpose

Turn group-chat records into a controlled requirement-intake workflow:

1. Read chat data from a user-defined data source path.
2. Filter groups by user-defined title keywords and optional content rules.
3. Identify and classify actionable requirements.
4. Compare each candidate with historical reports, the local processed-item index, and the destination issue tracker.
5. Generate a daily report.
6. Create only verified new and non-duplicate items.
7. Stop safely when access, authentication, parsing, mapping, or duplicate-checking is uncertain.

This skill is configuration-driven. Never hard-code a user's directory, group title, project URL, credentials, or business terminology into the reusable workflow.

## Required files

Before execution, look for these files in the repository root or current working directory:

- `config.yaml`: the user's active configuration.
- `config.example.yaml`: the shareable example configuration.
- `references/DAILY_REPORT_TEMPLATE.md`: required report structure.
- `references/CONFIGURATION_GUIDE.md`: field definitions and examples.

If `config.yaml` does not exist:

1. Copy `config.example.yaml` to `config.yaml`.
2. Ask the user to fill the required fields using `assets/SETUP_QUESTIONNAIRE.md`.
3. Do not guess missing paths, keywords, destination fields, project identifiers, or write permissions.
4. Do not start destination-system writes until configuration validation succeeds.

## Configuration principles

Treat all values in `config.yaml` as user-owned parameters.

At minimum, require:

- `data_source_path`
- `group_filter.title_includes`
- `time_range`
- `requirement_categories`
- `history_sources`
- `destination`
- `output`
- `write_policy`

Example data source path:

`C:\Users\Administrator\Documents\xwechat_files`

Example group-title rule:

Process only groups whose title contains `XXXXXX`.

The example is illustrative. Never treat it as a default for another user.

## Preconditions

Before processing:

1. Confirm this task is running in a local or mounted environment that can actually access `data_source_path`.
2. Confirm the user has authorized access to the data source.
3. Confirm the destination issue tracker is reachable through an approved connector, API, CLI, or browser session.
4. Confirm the destination project and field mapping are explicit.
5. Confirm the current execution can read historical reports or the configured local index.
6. Confirm secrets are not stored in `config.yaml`, reports, logs, screenshots, or repository files.

If any precondition fails, stop before write operations and produce a blocker report.

## First-run behavior

When `state.last_successful_run_time` is absent:

1. Use the configured initial lookback window.
2. Default to 24 hours only when `time_range.initial_lookback_hours` explicitly says `24`.
3. Scan only the groups matching the configured group-title rules.
4. Build the first processed-message index.
5. Read existing destination items before creating anything.
6. Generate a dry-run report unless `write_policy.first_run_write_enabled` is explicitly `true`.
7. If first-run writes are enabled, create only items classified as verified new and allowed by `write_policy`.

## Incremental behavior

After a successful run:

1. Use `state.last_successful_run_time` as the lower time boundary.
2. Include a small configured overlap window to protect against late-arriving or edited messages.
3. Deduplicate source messages using stable identifiers where available.
4. Otherwise generate a message fingerprint using:
   - source/group identifier
   - sender
   - timestamp
   - normalized text
   - attachment name or reference when relevant
5. Do not process an already completed fingerprint unless the source message changed.
6. Update state only after the report is saved and all approved destination writes are confirmed.

## Group and message filtering

Apply configuration in this order:

1. Data source path scope.
2. File or database scope.
3. Time range.
4. Group-title include rules.
5. Group-title exclude rules.
6. Optional sender filters.
7. Optional message-content include or exclude rules.
8. Requirement relevance test.

A title include rule means at least one configured phrase must appear in the group title unless `match_mode` specifies otherwise.

Do not infer additional groups merely because their content looks related.

## Requirement identification

A candidate must describe an observable problem, desired capability, requested change, or reproducible defect.

Classify candidates using the configured categories. The default shareable categories are:

- `new_feature`: a new user capability, workflow, screen, report, integration, rule, or data object.
- `improvement`: an enhancement to an existing capability, usability, performance, configuration, output, or process.
- `bug_debug`: an existing behavior that fails, produces an incorrect result, is unstable, or requires diagnosis.

Exclude:

- greetings and acknowledgements
- scheduling messages without a product or process request
- pure status updates
- questions already answered in the same context
- unverified assumptions
- general complaints with no identifiable issue or expected result
- duplicate quotations of an earlier request

When information is incomplete, classify the item as `needs_clarification`; do not create it automatically.

## Required fields for each candidate

Extract:

- requirement title
- requirement category
- business or operational background
- current behavior
- expected behavior
- requester or sender
- source group
- source timestamp
- source context
- affected module or process
- suggested priority
- acceptance criteria
- reproduction steps for defects
- attachments or evidence references
- source-message fingerprints
- duplicate-comparison result
- corresponding existing item, when applicable
- confidence and unresolved questions

Do not expose private chat content beyond what is necessary for requirement traceability.

## Priority guidance

Use the user's configured priority model. If none is configured, do not invent destination priority values.

For analysis only, suggest:

- `critical`: safety, security, compliance, data integrity, or widespread service interruption.
- `high`: core workflow blocked with no reasonable workaround.
- `medium`: meaningful degradation with a workaround.
- `low`: convenience, polish, or limited-scope enhancement.

Keep suggested priority separate from the final destination priority unless mapping is configured.

## Duplicate and similarity comparison

Compare every candidate against:

1. Historical daily reports.
2. The local processed-requirement index.
3. Existing items in the configured destination project.

Do not rely on title matching alone. Compare:

- business scenario
- affected object or module
- trigger condition
- current behavior
- expected behavior
- user role
- acceptance criteria
- defect reproduction path
- requested output or integration

Classify the comparison result as one of:

- `verified_new`
- `exact_duplicate`
- `highly_similar`
- `existing_item_supplement`
- `needs_clarification`

When an existing item is found, record its identifier and explain the relationship.

Never create `exact_duplicate`, `highly_similar`, `existing_item_supplement`, or `needs_clarification` items unless the user has configured and authorized a separate update workflow.

## Destination write policy

Before creating an item, verify all conditions:

1. The candidate is `verified_new`.
2. Required destination fields are mapped.
3. The destination project is confirmed.
4. The source evidence is traceable.
5. The item has not already been created in this run.
6. The item has not appeared in a previous successful run.
7. The user-authorized write mode permits creation.
8. No authentication or security prompt is pending.

Use an idempotency key or local creation record whenever the destination supports it.

After creation, save:

- destination item identifier
- destination URL or reference
- creation timestamp
- source fingerprints
- normalized requirement signature

If creation returns an uncertain result, do not retry blindly. Query the destination first to determine whether the item already exists.

## Authentication and session handling

Authentication must be interactive or managed by an approved credential provider.

Allowed behavior:

- Ask the user to complete the first login or authorization.
- Reuse an approved persistent browser profile, connector authorization, CLI login, or token store.
- Re-authenticate only when the session expires, permission is revoked, or the destination requires security verification.

Prohibited behavior:

- Never ask the user to paste passwords, one-time codes, cookies, session values, access tokens, or refresh tokens into chat or configuration files.
- Never print credentials in logs.
- Never commit credentials to GitHub.
- Never copy a browser profile into the repository.
- Never bypass multi-factor authentication or organizational security controls.

The skill cannot guarantee permanent authorization. It should reuse valid authorization where supported and report when reauthorization is required.

## Failure and stop conditions

Stop destination writes and produce a blocker report when:

- `data_source_path` is inaccessible
- the chat format cannot be parsed reliably
- the source database is locked or corrupted
- group titles cannot be determined
- the configured time boundary cannot be established
- history sources are unavailable
- the destination cannot be queried before duplicate checking
- destination authentication is required
- field mapping is missing or ambiguous
- duplicate status is uncertain
- item creation fails or returns an ambiguous result
- the environment cannot safely persist state

Continue read-only analysis only when it does not risk exposing data or producing misleading results.

## Daily report

Use `references/DAILY_REPORT_TEMPLATE.md`.

At minimum report:

- run date and time
- configured data-source scope
- time range
- number of matching groups
- number of scanned messages
- total candidates
- count by configured category
- exact duplicates
- highly similar items
- existing-item supplements
- needs-clarification items
- verified new items
- successfully created destination items
- items withheld from writing
- blockers and authorization status
- state update status

Clearly distinguish:

- observed source facts
- model interpretation
- duplicate-comparison evidence
- destination write results

## State management

Persist state outside the public repository unless it contains no private data.

Recommended state fields:

- `last_successful_run_time`
- processed message fingerprints
- normalized requirement signatures
- destination item identifiers
- successful and failed write records
- parser version
- configuration checksum

Do not advance `last_successful_run_time` when the run fails before the report and required writes complete.

## Completion criteria

A run is complete only when:

1. The configured data scope was accessible.
2. The time range was applied.
3. Matching groups and messages were processed.
4. Candidate requirements were classified.
5. History and destination comparisons were completed.
6. The daily report was saved.
7. Allowed destination writes were verified.
8. State was safely updated.
9. Blockers, withheld items, and unresolved questions were reported.

When these criteria are not met, describe the run as partial or blocked. Never claim successful automation without execution evidence.
