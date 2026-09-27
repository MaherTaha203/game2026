extends RefCounted
class_name PuzzleSolver
## Eulerian-trail solving for the runtime — GDScript mirror of
## tools/oneline/solver.py. Uses **Hierholzer's algorithm** (O(E)) for both the
## full solve and hint completion, so hints are provably reliable on every level,
## including expert graphs, with no search budget to exhaust.
##
## `find_completion` powers hints: given the current partial trail it returns a
## way to finish covering all remaining edges, so a hint always suggests a
## genuinely valid next move (docs/GAME_RULES.md §10). If the current state is a
## dead end (remaining edges cannot all be covered from here), it returns [].

## Stack-based Hierholzer from `start` over edges not already in `used_pre`.
## Returns the node sequence of the trail it can build. It covers every remaining
## edge iff an Eulerian trail with `start` as an endpoint exists in the remaining
## graph. Deterministic: neighbors explored in ascending id order.
static func _hierholzer(graph: PuzzleGraph, start: int, used_pre: Dictionary) -> Array[int]:
	var used := used_pre.duplicate()
	var stack: Array[int] = [start]
	var circuit: Array[int] = []
	while not stack.is_empty():
		var v: int = stack[stack.size() - 1]
		var advanced := false
		for w in graph.neighbors(v):
			var key := PuzzleGraph.normalize_edge(v, w)
			if not used.has(key):
				used[key] = true
				stack.append(w)
				advanced = true
				break
		if not advanced:
			circuit.append(stack.pop_back())
	circuit.reverse()
	return circuit

## Full Eulerian trail (node sequence) or [] if none.
static func find_eulerian_trail(graph: PuzzleGraph) -> Array[int]:
	if not graph.has_eulerian_trail():
		return []
	var odd := graph.odd_degree_nodes()
	var start := odd[0] if odd.size() > 0 else graph.node_ids[0]
	var circuit := _hierholzer(graph, start, {})
	if circuit.size() != graph.edge_count() + 1:
		return []
	return circuit

## Given already-used edges and the current head, return the remaining node
## sequence that completes the puzzle, or [] if the current state is a dead end.
static func find_completion(graph: PuzzleGraph, used_edges: Dictionary, current: int) -> Array[int]:
	if current < 0:
		# Not started: suggest a valid start (an odd vertex if any, else node 0).
		var odd := graph.odd_degree_nodes()
		return [odd[0] if odd.size() > 0 else graph.node_ids[0]] as Array[int]
	var remaining := graph.edge_count() - used_edges.size()
	if remaining <= 0:
		return [] as Array[int]
	var trail := _hierholzer(graph, current, used_edges)
	if trail.size() != remaining + 1:
		return [] as Array[int]  # cannot cover all remaining edges from here
	return trail.slice(1)
