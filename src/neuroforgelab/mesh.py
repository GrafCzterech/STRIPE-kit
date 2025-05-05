from dataclasses import dataclass
from abc import abstractmethod, ABC
import logging

from trimesh import Trimesh

from isaaclab.sim.converters import MeshConverterCfg, MeshConverter
from isaaclab.sim.spawners import UsdFileCfg, SpawnerCfg
from isaaclab.sim.spawners.meshes import MeshCfg

# thats right a secret forbidden import!
from isaaclab.sim.spawners.meshes.meshes import _spawn_mesh_geom_from_mesh


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

    def to_cfg(self) -> UsdFileCfg:
        """Create a MeshConverterCfg object from an AssetMesh object

        Returns:
            UsdFileCfg: The IsaacLab cfg object
        """
        logging.debug("Creating USD mesh cfg")
        mesh_cfg = UsdFileCfg(usd_path=self.usd_path, scale=(0.1, 0.1, 0.1))
        mesh_cfg.usd_path = self.usd_path
        return mesh_cfg


class UniversalMesh(AssetMesh):

    def __init__(self, path: str, **kwargs):
        logging.debug("Creating universal mesh")
        cfg = MeshConverterCfg(path, **kwargs)
        self.converter = MeshConverter(cfg)

    def to_cfg(self) -> SpawnerCfg:
        """Create a MeshConverterCfg object from an AssetMesh object

        Returns:
            SpawnerCfg: The IsaacLab cfg object
        """
        mesh_cfg = UsdFileCfg()
        mesh_cfg.usd_path = self.converter.usd_path
        return mesh_cfg


@dataclass
class DynamicMesh(AssetMesh):

    mesh: Trimesh

    # inspiration:
    # https://github.com/isaac-sim/IsaacLab/blob/2e6946afb9b26f6949d4b1fd0a00e9f4ef733fcc/source/isaaclab/isaaclab/sim/spawners/meshes/meshes.py#L99

    def to_cfg(self) -> SpawnerCfg:
        def func_wrapper(prim: str, cfg: MeshCfg, *args, **kwargs):
            return _spawn_mesh_geom_from_mesh(
                prim, cfg, self.mesh, *args, **kwargs
            )

        return MeshCfg(func=func_wrapper)
