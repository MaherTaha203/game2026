"""Level (de)serialization for ONE LINE.

The on-disk format is JSON (schema version 1). This module is the only place that
knows the concrete field layout, so the format can evolve behind a single API.
The Godot ``LevelLoader`` reads the identical files.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .graph import Graph, Node, normalize_edge
from .rules import StarThresholds
from .version import GENERATOR_VERSION, SCHEMA_VERSION


@dataclass
class Level:
    """A fully specified, production-ready level."""

    id: int
    nodes: List[Node]
    edges: List[Tuple[int, int]]
    tier: str
    difficulty_score: float
    seed: int
    solution_length: int
    star_thresholds: StarThresholds
    reference_solution: List[int] = field(default_factory=list)
    generator_version: str = GENERATOR_VERSION
    schema_version: int = SCHEMA_VERSION
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generator_version": self.generator_version,
            "id": self.id,
            "name": self.name or f"Level {self.id}",
            "tier": self.tier,
            "difficulty_score": self.difficulty_score,
            "seed": self.seed,
            "nodes": [
                {"id": n.id, "x": round(n.x, 4), "y": round(n.y, 4)} for n in self.nodes
            ],
            "edges": [{"a": a, "b": b} for (a, b) in self.edges],
            "solution_length": self.solution_length,
            "stars": {
                "three_max_mistakes": self.star_thresholds.three_max_mistakes,
                "two_max_mistakes": self.star_thresholds.two_max_mistakes,
            },
            "reference_solution": self.reference_solution,
        }

    def to_graph(self) -> Graph:
        return Graph(self.nodes, self.edges)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Level":
        nodes = [Node(int(n["id"]), float(n["x"]), float(n["y"])) for n in data["nodes"]]
        edges = [normalize_edge(int(e["a"]), int(e["b"])) for e in data["edges"]]
        stars = data.get("stars", {})
        thresholds = StarThresholds(
            three_max_mistakes=int(stars.get("three_max_mistakes", 0)),
            two_max_mistakes=int(stars.get("two_max_mistakes", 1)),
        )
        return cls(
            id=int(data["id"]),
            nodes=nodes,
            edges=edges,
            tier=str(data.get("tier", "normal")),
            difficulty_score=float(data.get("difficulty_score", 0.0)),
            seed=int(data.get("seed", 0)),
            solution_length=int(data.get("solution_length", len(edges))),
            star_thresholds=thresholds,
            reference_solution=[int(x) for x in data.get("reference_solution", [])],
            generator_version=str(data.get("generator_version", GENERATOR_VERSION)),
            schema_version=int(data.get("schema_version", SCHEMA_VERSION)),
            name=data.get("name"),
        )


def save_level(level: Level, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(level.to_dict(), fh, indent=2, sort_keys=False)
        fh.write("\n")


def load_level(path: str) -> Level:
    with open(path, "r", encoding="utf-8") as fh:
        return Level.from_dict(json.load(fh))


def load_level_dict(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def level_filename(level_id: int) -> str:
    return f"level_{level_id:04d}.json"


def write_index(levels: List[Level], path: str) -> None:
    """Write an ordered campaign index consumed by the runtime level select."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    index = {
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "count": len(levels),
        "levels": [
            {
                "id": lv.id,
                "file": level_filename(lv.id),
                "tier": lv.tier,
                "difficulty_score": lv.difficulty_score,
                "edges": len(lv.edges),
            }
            for lv in levels
        ],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
