extends RefCounted
class_name PuzzleSolver
## Eulerian-trail solving for the runtime — used by the hint system and by the
## in-editor conformance tests. Mirrors tools/oneline/solver.py semantics.
##
## `find_completion` powers hints: given the current partial trail it finds a way
## to finish covering all remaining edges, so a hint always suggests a genuinely
## valid next move (docs/GAME_RULES.md §10). A step budget keeps it responsive.

const MAX_STEPS := 200000

## Full Eulerian trail (node sequence) or [] if none.
static func find_eulerian_trail(graph: PuzzleGraph) -> Array[int]:
	if not graph.has_eulerian_trail():
		return []
	var odd := graph.odd_degree_nodes()
	var start := odd[0] if odd.size() > 0 else graph.node_ids[0]
	var used := {}
	var path: Array[int] = [start]
	var steps := [0]
	if _dfs(graph, start, used, graph.edge_count(), path, steps):
		return path
	return []

## Given already-used edges and the current head, return the remaining node
## sequence that completes the puzzle, or [] if the current state is a dead end.
static func find_completion(graph: PuzzleGraph, used_edges: Dictionary, current: int) -> Array[int]:
	if current < 0:
		# Not started: start from an odd vertex if any, else node 0.
		var odd := graph.odd_degree_nodes()
		var start := odd[0] if odd.size() > 0 else graph.node_ids[0]
		return [start]
	var remaining := graph.edge_count() - used_edges.size()
	if remaining <= 0:
		return []
	var used := used_edges.duplicate()
	var path: Array[int] = []
	var steps := [0]
	if _dfs(graph, current, used, remaining, path, steps):
		return path
	return []

static func _dfs(graph: PuzzleGraph, v: int, used: Dictionary, remaining: int, path: Array[int], steps: Array) -> bool:
	if remaining == 0:
		return true
	for w in graph.neighbors(v):
		var key := PuzzleGraph.normalize_edge(v, w)
		if used.has(key):
			continue
		steps[0] += 1
		if steps[0] > MAX_STEPS:
			return false
		used[key] = true
		path.append(w)
		if _dfs(graph, w, used, remaining - 1, path, steps):
			return true
		path.pop_back()
		used.erase(key)
	return false
