extends RefCounted
class_name LevelValidator
## Runtime structural/solvability validation — GDScript port of
## tools/oneline/validator.py. Used defensively before a level is played so a
## malformed data file can never put the engine into an invalid state.

## Returns {ok: bool, errors: Array[String]}.
static func validate(level: Level) -> Dictionary:
	var errors: Array[String] = []
	var positions := level.positions()
	var edges := level.edges()

	if positions.size() < 2:
		errors.append("a level must have at least 2 nodes")
	if edges.size() < 1:
		errors.append("a level must have at least 1 edge")

	for id in positions.keys():
		var p: Vector2 = positions[id]
		if p.x < 0.0 or p.x > 1.0 or p.y < 0.0 or p.y > 1.0:
			errors.append("node %d position out of range" % int(id))

	for e in edges:
		if not positions.has(e.x) or not positions.has(e.y):
			errors.append("edge references unknown node: (%d, %d)" % [e.x, e.y])
		if e.x == e.y:
			errors.append("self-loop not allowed: (%d, %d)" % [e.x, e.y])

	if not errors.is_empty():
		return {"ok": false, "errors": errors}

	var graph := level.to_graph()
	if not graph.is_connected_ignoring_isolated():
		errors.append("graph is disconnected")
	var odd := graph.odd_degree_nodes().size()
	if odd != 0 and odd != 2:
		errors.append("no Eulerian trail: %d odd-degree vertices" % odd)

	return {"ok": errors.is_empty(), "errors": errors}
