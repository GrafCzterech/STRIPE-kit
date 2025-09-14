from dataclasses import dataclass
from logging import getLogger

logger = getLogger(__name__)

from isaaclab.terrains import SubTerrainBaseCfg, TerrainGeneratorCfg
from isaaclab.assets import AssetBaseCfg
from isaaclab.sim.spawners import PreviewSurfaceCfg

from trimesh import Trimesh
import numpy as np

from .mesh import DynamicMesh

TERRAIN_NAME = "terrain"


@dataclass
class TerrainInstance:
    """A specification for a terrain to be placed in a scene"""

    mesh: list[tuple[Trimesh, list[tuple[str, str]]]]
    """The mesh of the terrain and the tags to add to the mesh"""
    origin: tuple[float, float, float]
    """The position where the robot should spawn"""
    size: tuple[float, float]
    """The size of the terrain in meters"""
    color: tuple[float, float, float]
    """The color of the terrain"""

    def to_cfg(self) -> TerrainGeneratorCfg:
        """Create a TerrainGeneratorCfg object from a TerrainInstance object

        Please note that this method does not apply semantic tags to the terrain.

        Returns:
            TerrainGeneratorCfg: The TerrainGeneratorCfg object
        """
        logger.debug("Creating terrain generator cfg")
        sub_terrain = SubTerrainBaseCfg()
        sub_terrain.function = lambda diff, cfg: (
            [m[0] for m in self.mesh],
            np.array(self.origin),
        )
        sub_terrain.size = self.size

        terrain_cfg = TerrainGeneratorCfg()
        terrain_cfg.sub_terrains = {"main": sub_terrain}
        terrain_cfg.size = self.size

        return terrain_cfg

    def to_asset_cfg(self) -> list[AssetBaseCfg]:
        """Create a asset Cfg object from a TerrainInstance object

        Returns:
            AssetBaseCfg: The AssetBaseCfg object
        """
        logger.debug("Creating terrain asset cfg")
        res = []
        for i, (mesh, tags) in enumerate(self.mesh):
            spawner = DynamicMesh(mesh, PreviewSurfaceCfg(diffuse_color=self.color)).to_cfg()
            spawner.semantic_tags = tags
            cfg = AssetBaseCfg(
                prim_path=f"/{TERRAIN_NAME}/{TERRAIN_NAME}_{i}",
                spawn=spawner,
            )
            cfg.init_state = cfg.InitialStateCfg()
            cfg.collision_group = -1
            res.append(cfg)
        return res
