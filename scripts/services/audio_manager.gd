extends Node
## Autoload: subtle SFX playback that always respects the sound setting and never
## crashes when an audio asset is missing (docs/GAME_RULES.md §9, MASTER_PROMPT §12).
##
## Sound effects are original, procedurally-generated tones (see
## tools/gen_audio.py and docs/THIRD_PARTY_LICENSES.md). Music is not shipped in
## v1; the music setting is preserved for a future update.

const SFX := {
	"node": "res://assets/audio/node.wav",
	"connect": "res://assets/audio/connect.wav",
	"invalid": "res://assets/audio/invalid.wav",
	"complete": "res://assets/audio/complete.wav",
	"button": "res://assets/audio/button.wav",
}

var _players: Array[AudioStreamPlayer] = []
var _streams: Dictionary = {}
var _next := 0
const POOL_SIZE := 6

func _ready() -> void:
	for i in POOL_SIZE:
		var p := AudioStreamPlayer.new()
		p.bus = "Master"
		add_child(p)
		_players.append(p)
	for key in SFX.keys():
		var path: String = SFX[key]
		if ResourceLoader.exists(path):
			_streams[key] = load(path)

func play(sfx_name: String) -> void:
	if not bool(SaveManager.settings().get("sound", true)):
		return
	if not _streams.has(sfx_name):
		return
	var p := _players[_next]
	_next = (_next + 1) % _players.size()
	p.stream = _streams[sfx_name]
	p.play()
