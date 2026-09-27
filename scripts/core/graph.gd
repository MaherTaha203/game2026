extends RefCounted
class_name PuzzleGraph
## Immutable undirected simple graph — GDScript port of tools/oneline/graph.py.
##
## Nodes carry a normalized position in [0, 1]. Edges are stored canonically as
## Vector2i(min_id, max_id). This is the runtime counterpart of the authoritative
## Python model; both must agree (docs/GAME_RULES.md §13).

var node_ids: Array[int] = []
var positions: Dictionary = {}          # int id -> Vector2
var edges: Array[Vector2i] = []         # canonical (min, max)
var _adj: Dictionary = {}               # int id -> Dictionary(int -> true)

static func normalize_edge(a: int, b: int) -> Vector2i:
	assert(a != b, "self-loops are not allowed")
	return Vector2i(a, b) if a < b else Vector2i(b, a)

func _init(node_positions: Dictionary, edge_list: Array) -> void:
	for id in node_positions.keys():
		var nid := int(id)
		node_ids.append(nid)
		positions[nid] = node_positions[id]
		_adj[nid] = {}
	node_ids.sort()

	var seen := {}
	for e in edge_list:
		var a := int(e.x) if e is Vector2i else int(e[0])
		var b := int(e.y) if e is Vector2i else int(e[1])
		var key := normalize_edge(a, b)
		if seen.has(key):
			continue
		seen[key] = true
		edges.append(key)
		_adj[key.x][key.y] = true
		_adj[key.y][key.x] = true

func node_count() -> int:
	return node_ids.size()

func edge_count() -> int:
	return edges.size()

func has_node(nid: int) -> bool:
	return positions.has(nid)

func has_edge(a: int, b: int) -> bool:
	return _adj.has(a) and _adj[a].has(b)

func neighbors(nid: int) -> Array[int]:
	var out: Array[int] = []
	if _adj.has(nid):
		for k in _adj[nid].keys():
			out.append(int(k))
	out.sort()
	return out

func degree(nid: int) -> int:
	return _adj[nid].size() if _adj.has(nid) else 0

func odd_degree_nodes() -> Array[int]:
	var out: Array[int] = []
	for nid in node_ids:
		if degree(nid) % 2 == 1:
			out.append(nid)
	out.sort()
	return out

func max_degree() -> int:
	var m := 0
	for nid in node_ids:
		m = maxi(m, degree(nid))
	return m

func is_connected_ignoring_isolated() -> bool:
	if edge_count() == 0:
		return false
	var start := int(edges[0].x)
	var reachable := _bfs(start)
	for nid in node_ids:
		if degree(nid) > 0 and not reachable.has(nid):
			return false
	return true

func _bfs(start: int) -> Dictionary:
	var seen := {start: true}
	var stack := [start]
	while not stack.is_empty():
		var cur = stack.pop_back()
		for nxt in neighbors(cur):
			if not seen.has(nxt):
				seen[nxt] = true
				stack.append(nxt)
	return seen

func has_eulerian_trail() -> bool:
	if not is_connected_ignoring_isolated():
		return false
	var odd := odd_degree_nodes().size()
	return odd == 0 or odd == 2
