---
name: qa-testing
description: Systematic verification procedures for ONE LINE covering core engine, level system, progression, save system, settings, regression, and final pre-release QA. Use when writing tests, running test suites, or producing evidence-based QA reports.
---

# QA Testing Skill

## Purpose

Provide systematic verification of ONE LINE.

## Test Categories

### Core Engine

Test:

* valid paths;
* invalid paths;
* repeated edges;
* completion;
* incomplete paths;
* restart;
* reset;
* level loading;
* level transitions.

### Level System

Test:

* valid level;
* malformed level;
* missing node;
* invalid edge;
* duplicate edge;
* disconnected graph;
* unsolvable graph;
* duplicate level detection.

### Progression

Test:

* level completion;
* unlocking;
* locked levels;
* stars;
* replay;
* reset progress.

### Save System

Test:

* new save;
* save;
* load;
* missing save;
* malformed save;
* corrupted save;
* version migration;
* reset progress.

### Settings

Test:

* audio settings;
* vibration/haptics settings where implemented;
* accessibility settings where implemented;
* persistence after restart.

### Regression

Every fixed bug that could recur should receive a regression test.

## Test Discipline

Run focused tests after a change.

Run the complete relevant suite before declaring a phase complete.

Record failures honestly.

Do not hide failing tests.

Do not weaken tests merely to obtain a PASS.

## Evidence

Every QA report should distinguish:

PASS
FAIL
UNVERIFIED
HUMAN ACTION REQUIRED

## Final QA

Before release:

* clean build;
* automated test suite;
* level validation;
* solver/playtester;
* save migration;
* fresh install;
* upgrade/update path where possible;
* mobile device testing where available;
* performance check;
* visual check;
* privacy/network check.

Unverified external/device checks must remain UNVERIFIED.
