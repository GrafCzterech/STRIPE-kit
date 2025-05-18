from dataclasses import dataclass
from abc import abstractmethod, ABC
from logging import getLogger

logger = getLogger(__name__)

from trimesh import Trimesh

import isaacsim.core.utils.prims as prim_utils  # type: ignore
import isaacsim.core.utils.semantics as semantics_utils  # type: ignore
from pxr.Usd import Prim  # type: ignore

from isaaclab.sim.converters import MeshConverterCfg, MeshConverter
from isaaclab.sim.spawners import UsdFileCfg, SpawnerCfg
from isaaclab.terrains.utils import create_prim_from_mesh
from isaaclab.assets import AssetBaseCfg

CLASS_TAG = "class"


class AssetMesh(ABC):
    """A mesh asset that can be converted to a USD file"""

    @abstractmethod
    def to_cfg(self) -> SpawnerCfg:
        """Create a SpawnerCfg object from an AssetMesh object

        Returns:
            SpawnerCfg: The IsaacLab cfg object
        """
        ...


@dataclass
class USDMesh(AssetMesh):

    usd_path: str
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)

    def to_cfg(self) -> UsdFileCfg:
        """Create a MeshConverterCfg object from an AssetMesh object

        Returns:
            UsdFileCfg: The IsaacLab cfg object
        """
        logger.debug("Creating USD mesh cfg")
        mesh_cfg = UsdFileCfg(usd_path=self.usd_path, scale=self.scale)
        mesh_cfg.usd_path = self.usd_path
        return mesh_cfg


class UniversalMesh(AssetMesh):

    def __init__(self, path: str, **kwargs):
        logger.debug("Creating universal mesh")
        cfg = MeshConverterCfg(path, **kwargs)
        self.converter = MeshConverter(cfg)

    def to_cfg(self) -> UsdFileCfg:
        """Create a MeshConverterCfg object from an AssetMesh object

        Returns:
            SpawnerCfg: The IsaacLab cfg object
        """
        mesh_cfg = UsdFileCfg()
        mesh_cfg.usd_path = self.converter.usd_path
        return mesh_cfg


def apply_semantics(prim: Prim, type: str, value: str) -> None:
    """Applies a semantic type and data to a prim.

    Args:
        prim (Prim): A special type of a string that represents a prim in a stage
        type (str): Label
        value (str): Value
    """
    semantics_utils.add_update_semantics(prim, value, type)


@dataclass
class DynamicMesh(AssetMesh):

    mesh: Trimesh

    # inspiration:
    # https://github.com/isaac-sim/IsaacLab/blob/963b53b96bc6140670fa0fe41d9fbafa68d8382f/source/isaaclab/isaaclab/terrains/utils.py#L61

    def to_cfg(self) -> SpawnerCfg:
        logger.debug("Creating dynamic mesh cfg")

        def func_wrapper(prim: str, cfg: SpawnerCfg, *args, **kwargs):
            create_prim_from_mesh(
                prim,
                self.mesh,
                # visual_material=cfg.visual_material,
                # physics_material=cfg.physics_material,
                *args,
                **kwargs,
            )
            p = prim_utils.get_prim_at_path(prim)
            if cfg.semantic_tags is not None:
                for tag, value in cfg.semantic_tags:
                    apply_semantics(p, tag, value)
            return p

        return SpawnerCfg(func=func_wrapper)
