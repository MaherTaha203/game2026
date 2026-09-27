extends RefCounted
class_name Level
## Parsed ONE LINE level — GDScript counterpart of tools/oneline/levelio.py.
## Reads the identical JSON produced by the generation pipeline.

var id: int = 0
var name: String = ""
var tier: String = "normal"
var difficulty_score: float = 0.0
var seed: int = 0
var solution_length: int = 0
var three_max_mistakes: int = 0
var two_max_mistakes: int = 1
var reference_solution: Array[int] = []
var generator_version: String = ""
var schema_version: int = 1

var _positions: Dictionary = {}     # int id -> Vector2
var _edges: Array[Vector2i] = []

static func from_dict(data: Dictionary) -> Level:
	var lv := Level.new()
	lv.id = int(data.get("id", 0))
	lv.name = str(data.get("name", "Level %d" % lv.id))
	lv.tier = str(data.get("tier", "normal"))
	lv.difficulty_score = float(data.get("difficulty_score", 0.0))
	lv.seed = int(data.get("seed", 0))
	lv.solution_length = int(data.get("solution_length", 0))
	lv.generator_version = str(data.get("generator_version", ""))
	lv.schema_version = int(data.get("schema_version", 1))

	var stars: Dictionary = data.get("stars", {})
	lv.three_max_mistakes = int(stars.get("three_max_mistakes", 0))
	lv.two_max_mistakes = int(stars.get("two_max_mistakes", 1))

	for n in data.get("nodes", []):
		lv._positions[int(n["id"])] = Vector2(float(n["x"]), float(n["y"]))
	for e in data.get("edges", []):
		lv._edges.append(PuzzleGraph.normalize_edge(int(e["a"]), int(e["b"])))

	for v in data.get("reference_solution", []):
		lv.reference_solution.append(int(v))
	return lv

func positions() -> Dictionary:
	return _positions

func edges() -> Array[Vector2i]:
	return _edges

func to_graph() -> PuzzleGraph:
	return PuzzleGraph.new(_positions, _edges)
