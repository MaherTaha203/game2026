# ONE LINE — Human Action Required

Tasks that genuinely require credentials, hardware, store accounts, or human
decisions that cannot be performed safely/automatically in this environment
(MASTER_PROMPT §90). Everything else has been completed in the repository.

## Apple / iOS

- [ ] Apple Developer Program account.
- [ ] iOS signing certificate + provisioning profile (never commit them).
- [ ] Set bundle identifier (replace placeholder `com.example.oneline`) and team.
- [ ] Build/archive on macOS with Xcode; validate.
- [ ] Test on real iPhone(s), including a notch / Dynamic Island device.
- [ ] Complete App Store privacy ("nutrition label") from `PRIVACY.md`.
- [ ] Prepare and upload screenshots (`STORE_ASSETS.md`).
- [ ] Submit for review.

## Google / Android

- [ ] Google Play Console account.
- [ ] Release keystore (never commit); configure signing.
- [ ] Set application id (replace placeholder `com.example.oneline`), version code.
- [ ] Build a signed `.aab`.
- [ ] Test on real Android device(s) and densities.
- [ ] Complete Play Data Safety form from `PRIVACY.md`.
- [ ] Prepare screenshots + 1024×500 feature graphic (`STORE_ASSETS.md`).
- [ ] Submit for review.

## Cross-platform

- [ ] Install Godot 4.3 export templates locally.
- [ ] Decide final price (~US$0.99 suggested) and store metadata wording.
- [ ] Export icon sizes from `assets/icon.svg` for each store.
- [ ] Run the on-device QA sequences and fill `DEVICE_TEST_MATRIX.md`.
- [ ] Record the released commit + versions in `RELEASE_HISTORY.md`.
- [ ] Legal review of privacy/store declarations if desired.

## Explicitly NOT required from a human

These are already done in-repo: puzzle engine, 210 validated/solved levels,
generator/validator/solver/quality tooling, save system + migration, all screens,
audio, icon, CI, and documentation. See `FINAL_ACCEPTANCE.md` for evidence.

## Never do

- Never commit signing keys, certificates, provisioning profiles, or passwords.
- Never fabricate store approval, device tests, or signed-build results.
