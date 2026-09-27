---
name: release-audit
description: Perform the final evidence-based audit before ONE LINE is considered release-ready, assigning each audit item a PASS/FAIL/UNVERIFIED/HUMAN ACTION REQUIRED status with evidence. Use when auditing the project for release readiness or compiling a release blocker report.
---

# Release Audit Skill

## Purpose

Perform the final evidence-based audit before ONE LINE is considered release-ready.

## Audit Areas

1. Product scope.
2. Gameplay.
3. Level quality.
4. Solver verification.
5. Automated tests.
6. Regression tests.
7. Save system.
8. Save migration.
9. Performance.
10. Mobile input.
11. Safe areas.
12. Accessibility.
13. Localization architecture.
14. Privacy.
15. Permissions.
16. Dependencies.
17. Secrets.
18. Debug code.
19. Build configuration.
20. Versioning.
21. Store assets.
22. Documentation.
23. Git repository hygiene.

## Required Status

Every audit item must have one status:

PASS
FAIL
UNVERIFIED
HUMAN ACTION REQUIRED

## Evidence

Each PASS should identify evidence where practical.

Examples:

* test command;
* test result;
* file;
* commit;
* build artifact;
* device;
* screenshot;
* manual verification.

## No False Completion

Do not convert UNVERIFIED into PASS merely because implementation appears correct.

Do not convert HUMAN ACTION REQUIRED into PASS.

## Final Result

The audit must produce:

* total PASS items;
* FAIL items;
* UNVERIFIED items;
* HUMAN ACTION REQUIRED items;
* known limitations;
* release blockers;
* recommended next actions.

The audit itself does not approve the product.

It reports evidence.
