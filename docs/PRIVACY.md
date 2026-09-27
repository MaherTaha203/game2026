# ONE LINE — Privacy

_Last verified against the implementation: 2026-09-27 (commit recorded in
`RELEASE_HISTORY.md`)._

ONE LINE is designed to collect **no personal data** and to work **fully offline**.
This document reflects the actual shipped implementation, verified by inspection of
the source and configuration (not merely asserted). See the verification notes
below.

## What the game does NOT do

* No user accounts, sign-in, or profiles.
* No backend or server communication of any kind.
* No internet connection required or used during normal play.
* No analytics or telemetry SDKs.
* No advertising SDKs.
* No tracking or advertising identifiers.
* No access to contacts, location, microphone, camera, or files outside its own
  sandbox.
* No in-app purchases, subscriptions, or virtual currency.

## What the game stores (locally only)

* Level progress (unlocked/completed levels, best star ratings, best mistakes).
* Settings (sound, haptics, reduced motion, high contrast, language).
* Local statistics (puzzles completed, stars, streaks, play time).
* Daily-puzzle local completion/streak.

All of the above is stored on the device in the app's private storage
(`user://save.json`) and is never transmitted. Uninstalling the app removes it
(subject to platform behavior).

## Verification (evidence)

Performed on the source at the recorded commit:

* **Network APIs** — a repository scan of `scripts/` for `HTTPRequest`,
  `HTTPClient`, `StreamPeer*`, `WebSocket`, UDP/TCP peers, and `http(s)://`
  usage returned **no matches**. Status: **PASS**.
* **Analytics / ads SDKs** — no such dependencies exist; `docs/THIRD_PARTY_LICENSES.md`
  lists the complete dependency set (engine only). Status: **PASS**.
* **Permissions** — `export_presets.cfg` requests no INTERNET / network-state /
  wifi capability (Android `permissions/internet=false`). Status: **PASS** for the
  committed configuration; final on-device permission review is **UNVERIFIED**
  until a signed build is produced (see `HUMAN_ACTION_REQUIRED.md`).

## Children & data

Because the game collects and transmits no personal data, it is suitable for a
general audience. Final age-rating declarations are completed during store
submission (see `STORE_LISTING.md`).

## Legal note

This document describes technical behavior. It is not legal advice. A human
should review store-specific privacy declarations (Apple Privacy "Nutrition
Label", Google Play Data Safety) against this document before submission.
