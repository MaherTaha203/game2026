# ONE LINE

ONE LINE is a minimalist, premium, offline-first mobile puzzle game for Android and iOS,
built with **Godot 4.x** and **GDScript**.

The player draws a single continuous path through a graph, completing each puzzle
according to the level's defined rules. See [`docs/GAME_RULES.md`](docs/GAME_RULES.md)
for the canonical rules.

## Product Constraints

ONE LINE is deliberately scoped as a one-time paid, offline game. It has **no**
ads, subscriptions, in-app purchases, virtual currencies, accounts, backend,
online multiplayer, leaderboards, chat/social systems, or runtime AI.
See [`.claude/CLAUDE.md`](.claude/CLAUDE.md) section 2 for the full list.

## Repository Layout

```text
ONE-LINE/
├── .claude/                 # Claude Code project instructions and skills
│   ├── CLAUDE.md            # Authoritative project instructions
│   └── skills/              # Task-specific skills (see below)
├── docs/                    # Project rules and standards
│   ├── GAME_RULES.md        # Canonical gameplay rules (authoritative)
│   ├── ARCHITECTURE_RULES.md
│   ├── TESTING_STRATEGY.md
│   ├── LEVEL_QUALITY.md
│   ├── QUALITY_GATES.md
│   ├── DEFINITION_OF_DONE.md
│   └── RELEASE_RULES.md
├── assets/                  # Game assets
├── tests/                   # Automated tests
├── README.md
└── .gitignore
```

## Claude Code Skills

The `.claude/skills/` directory contains the engineering skills that govern how
work is done on this project:

| Skill | Purpose |
| --- | --- |
| `game-development` | Godot 4.x / GDScript implementation rules. |
| `puzzle-design` | Level design, validation, and curation standards. |
| `qa-testing` | Systematic, evidence-based verification. |
| `code-review` | Correctness, security, performance, and maintainability review. |
| `mobile-release` | Android / iOS release preparation. |
| `release-audit` | Final evidence-based release-readiness audit. |

## Engineering Principles

Priorities, in order: **correctness, reliability, maintainability, testability,
performance, user experience, visual polish, simplicity.**

Evidence is more important than confidence. A feature is not "done" until it is
implemented, tested, integrated, and documented. Status is reported using
`PASS` / `FAIL` / `UNVERIFIED` / `HUMAN ACTION REQUIRED` — never fabricated.

See [`docs/DEFINITION_OF_DONE.md`](docs/DEFINITION_OF_DONE.md) and
[`docs/QUALITY_GATES.md`](docs/QUALITY_GATES.md) for the completion standards.

## Status

Project scaffolding and governance documents only. The game implementation has
not yet started. Status: **UNVERIFIED** — no runtime, levels, or tests exist yet.
