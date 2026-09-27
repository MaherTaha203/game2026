---
name: code-review
description: Review ONE LINE for correctness, maintainability, security, performance, and unnecessary complexity, classifying findings by severity without inflation. Use when reviewing code changes, auditing existing code, or evaluating a pull request for this project.
---

# Code Review Skill

## Purpose

Review ONE LINE for correctness, maintainability, security, performance, and unnecessary complexity.

## Review Checklist

### Correctness

* Does the implementation match the documented game rules?
* Are edge cases handled?
* Can invalid state occur?
* Can player progress be lost?

### Architecture

* Are responsibilities separated?
* Is core gameplay testable?
* Are dependencies reasonable?
* Is global state minimized?

### Security

* Are secrets absent?
* Are permissions minimized?
* Are unnecessary network calls absent?
* Are third-party SDKs justified?

### Performance

* Are unnecessary per-frame operations present?
* Are expensive allocations repeated?
* Are large resources loaded unnecessarily?
* Could level loading cause visible stutter?

### Maintainability

* Is the code understandable?
* Are names meaningful?
* Are duplicated rules centralized?
* Are magic constants minimized?

### Testing

* Are important behaviors tested?
* Are bugs covered by regression tests?
* Are level validators tested?

## Review Severity

Classify findings as:

CRITICAL
HIGH
MEDIUM
LOW
INFORMATIONAL

Do not inflate severity.

Do not hide findings merely because the application currently works.

## Final Review

A review should distinguish:

* confirmed defect;
* potential risk;
* design trade-off;
* unverified assumption.

Do not present speculation as fact.
