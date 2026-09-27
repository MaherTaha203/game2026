---
name: mobile-release
description: Prepare ONE LINE for Android and iOS release — export configuration, identifiers, versioning, icons, permissions, signing placeholders, and store assets — without pretending that unavailable credentials or devices were verified. Use for release preparation and packaging tasks.
---

# Mobile Release Skill

## Purpose

Prepare ONE LINE for Android and iOS release without pretending that unavailable external credentials or devices have been verified.

## Responsibilities

* Export configuration.
* Application identifiers.
* Versioning.
* Build numbers.
* Icons.
* Launch/splash configuration where applicable.
* Orientation.
* Permissions.
* Release configuration.
* Signing configuration placeholders.
* Store asset preparation.
* Release documentation.

## Credentials

Never create fake credentials.

Never commit:

* private keys;
* signing certificates;
* provisioning secrets;
* API secrets;
* passwords.

Where credentials are required, document the human action.

## Android

Verify project configuration as far as the available environment permits.

Do not claim a successful signed release build without actual evidence.

## iOS

Verify project configuration as far as the available environment permits.

Do not claim App Store submission readiness if required Apple credentials, signing, or device verification are unavailable.

## Store Requirements

At release time, verify current official Apple and Google requirements.

Do not rely indefinitely on old requirements.

Document the verification date and sources.

## Release Candidate

A release candidate must have:

* fixed version;
* fixed build number;
* known Git commit;
* validated levels;
* passing automated tests;
* documented known issues;
* release notes;
* store assets;
* privacy documentation;
* human-action checklist.

## External Actions

Clearly identify tasks requiring:

* Apple Developer account;
* Google Play Console;
* certificates;
* signing;
* real devices;
* store upload;
* store review.

Never represent these as completed unless actually completed and evidenced.
