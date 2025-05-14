from dataclasses import dataclass
from abc import abstractmethod, ABC
from logging import getLogger

logger = getLogger(__name__)

from trimesh import Trimesh

import isaacsim.core.utils.prims as prim_utils  # type: ignore
from pxr.Sdf import Path  # type: ignore
from Semantics import SemanticsAPI  # type: ignore

from isaaclab.sim.converters import MeshConverterCfg, MeshConverter
from isaaclab.sim.spawners import UsdFileCfg, SpawnerCfg
from isaaclab.sim.spawners.meshes import MeshCfg

# thats right a secret forbidden import!
from isaaclab.sim.spawners.meshes.meshes import _spawn_mesh_geom_from_mesh

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


def apply_semantics(prim: Path, type: str, value: str) -> None:
    """Applies a semantic type and data to a prim.

    Args:
        prim (Path): A special type of a string that represents a prim in a stage
        type (str): Label
        value (str): Value
    """
    instance_name = f"{type}_{value}"
    sem = SemanticsAPI.Apply(prim, instance_name)
    # create semantic type and data attributes
    sem.CreateSemanticTypeAttr()
    sem.CreateSemanticDataAttr()
    sem.GetSemanticTypeAttr().Set(type)
    sem.GetSemanticDataAttr().Set(value)


@dataclass
class DynamicMesh(AssetMesh):

    mesh: Trimesh

    # inspiration:
    # https://github.com/isaac-sim/IsaacLab/blob/2e6946afb9b26f6949d4b1fd0a00e9f4ef733fcc/source/isaaclab/isaaclab/sim/spawners/meshes/meshes.py#L99

    def to_cfg(self) -> MeshCfg:
        logger.debug("Creating dynamic mesh cfg")

        # https://github.com/isaac-sim/IsaacLab/blob/2e6946afb9b26f6949d4b1fd0a00e9f4ef733fcc/source/isaaclab/isaaclab/sim/spawners/meshes/meshes.py#L320
        # FIXME this applies a solid cube like collider to the mesh, which is not what we want

        def func_wrapper(prim: str, cfg: MeshCfg, *args, **kwargs):
            _spawn_mesh_geom_from_mesh(prim, cfg, self.mesh, *args, **kwargs)
            p = prim_utils.get_prim_at_path(prim)
            if cfg.semantic_tags is not None:
                for tag, value in cfg.semantic_tags:
                    apply_semantics(p, tag, value)
            return p

        return MeshCfg(func=func_wrapper)
