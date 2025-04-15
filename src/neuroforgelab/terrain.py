from dataclasses import dataclass
from typing import Callable, TypeAlias
import logging

from isaaclab.terrains import SubTerrainBaseCfg, TerrainGeneratorCfg

from trimesh import Trimesh
import numpy as np

TerrainGenFunc: TypeAlias = Callable[
    [float, SubTerrainBaseCfg],
    tuple[list[Trimesh], np.ndarray],
]


@dataclass
class TerrainInstance:
    """A specification for a terrain to be placed in a scene"""

    mesh: Trimesh
    """The mesh of the terrain"""
    # slight performance hickup, as this form of data init causes a new object allocation, but this is more readable
    origin: tuple[float, float, float]
    """The position where the robot should spawn"""
    size: tuple[float, float]
    """The size of the terrain in meters"""

    def to_terrain_generator_cfg(self) -> TerrainGeneratorCfg:
        """Create a TerrainGeneratorCfg object from a TerrainInstance object

        Returns:
            TerrainGeneratorCfg: The TerrainGeneratorCfg object
        """
        logging.debug("Creating terrain generator cfg")
        sub_terrain = SubTerrainBaseCfg()
        sub_terrain.function = lambda diff, cfg: (
            [self.mesh],
            np.array(self.origin),
        )
        sub_terrain.size = self.size

        terrain_cfg = TerrainGeneratorCfg()
        terrain_cfg.sub_terrains = {"main": sub_terrain}
        terrain_cfg.size = self.size

        return terrain_cfg
