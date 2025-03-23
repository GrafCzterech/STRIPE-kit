from isaaclab.source.isaaclab.isaaclab.terrains import (
    SubTerrainBaseCfg,
    TerrainGeneratorCfg,
)

from trimesh import Trimesh
import numpy as np

from dataclasses import dataclass
from typing import Callable, TypeAlias

TerrainGenFunc: TypeAlias = Callable[
    [float, SubTerrainBaseCfg], tuple[list[Trimesh], np.ndarray]
]


@dataclass
class TerrainInstance:
    """A specification for a terrain to be placed in a scene"""

    mesh: list[Trimesh]
    origin: np.ndarray
    size: tuple[float, float]

    def to_terrain_generator_cfg(self) -> TerrainGeneratorCfg:
        """Create a TerrainGeneratorCfg object from a TerrainInstance object

        Returns:
            TerrainGeneratorCfg: The TerrainGeneratorCfg object
        """
        sub_terrain = SubTerrainBaseCfg()
        sub_terrain.function = lambda diff, cfg: (self.mesh, self.origin)
        sub_terrain.size = self.size

        terrain_cfg = TerrainGeneratorCfg()
        terrain_cfg.sub_terrains["main"] = sub_terrain
        terrain_cfg.size = self.size

        return terrain_cfg
