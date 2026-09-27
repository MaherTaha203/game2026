extends Node
## Autoload: version constants for ONE LINE.
##
## These MUST stay in sync with tools/oneline/version.py (guarded by
## tests/python/test_versions.py). See MASTER_PROMPT §68-§69.

const APP_VERSION := "1.0.0"
const GENERATOR_VERSION := "1.0.0"
const SCHEMA_VERSION := 1
const SAVE_DATA_VERSION := 2

## Populated at runtime where available (see build_info()).
func build_info() -> Dictionary:
	return {
		"app_version": APP_VERSION,
		"generator_version": GENERATOR_VERSION,
		"schema_version": SCHEMA_VERSION,
		"save_data_version": SAVE_DATA_VERSION,
		"godot_version": Engine.get_version_info().get("string", "unknown"),
	}
