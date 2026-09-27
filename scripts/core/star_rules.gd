extends RefCounted
class_name StarRules
## Deterministic star model — GDScript port of the pure functions in
## tools/oneline/rules.py (docs/GAME_RULES.md §8). Unit-tested in Python;
## mirrored here byte-for-byte in behavior.

## Compute stars (0 if not completed, else 1/2/3).
static func compute_stars(mistakes: int, three_max: int, two_max: int, completed: bool = true) -> int:
	if not completed:
		return 0
	if mistakes <= three_max:
		return 3
	if mistakes <= two_max:
		return 2
	return 1

## Generator default thresholds: {three_max, two_max}.
static func default_thresholds(edge_count: int) -> Dictionary:
	var two := maxi(1, ceili(float(edge_count) / 4.0))
	return {"three_max": 0, "two_max": two}
