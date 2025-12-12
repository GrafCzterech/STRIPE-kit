from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from logging import getLogger
from typing import Any

import isaacsim.core.utils.prims as prim_utils  # pyright: ignore[reportMissingImports]
import isaacsim.core.utils.semantics as semantics_utils  # pyright: ignore[reportMissingImports]
from isaaclab.sim.converters import MeshConverter, MeshConverterCfg
from isaaclab.sim.spawners import (
    MdlFileCfg,
    PreviewSurfaceCfg,
    RigidBodyMaterialCfg,
    SpawnerCfg,
    UsdFileCfg,
    VisualMaterialCfg,
    # spawn_from_mdl_file,
)
from isaaclab.terrains.utils import create_prim_from_mesh
from pxr.Usd import Prim  # pyright: ignore[reportMissingImports]
from trimesh import Trimesh, primitives

logger = getLogger(__name__)

CLASS_TAG = "class"


class AssetMesh(ABC):
    """A mesh that can be spawned within Isaac Sim"""

    @abstractmethod
    def to_cfg(self, **kwargs: Any) -> SpawnerCfg:
        """Create a SpawnerCfg object from an AssetMesh object

        Logically this should return a new object, thus nullifying any effects
        of instancing. If you wish to prevent this behavior, use the `instancable` decorator.

        Args:
            **kwargs: Additional keyword arguments, passed to the SpawnerCfg constructor

        Returns:
            SpawnerCfg: The IsaacLab cfg object
        """
        ...


@dataclass
class USDMesh(AssetMesh):
    """A mesh derived from a USD file"""

    usd_path: str

    def to_cfg(self, **kwargs: Any) -> UsdFileCfg:
        """Create a UsdFileCfg object from an AssetMesh object

        Args:
            **kwargs: Additional keyword arguments, passed to the UsdFileCfg constructor

        Returns:
            UsdFileCfg: The IsaacLab cfg object
        """
        logger.debug("Creating USD mesh cfg")
        mesh_cfg = UsdFileCfg(usd_path=self.usd_path, **kwargs)
        return mesh_cfg


class UniversalMesh(AssetMesh):
    """A mesh derived from any file format, accepted by MeshConverterCfg"""

    def __init__(self, path: str, **kwargs: Any):
        """Initialize a UniversalMesh object

        Args:
            path (str): Path to the mesh file
            kwargs: Additional keyword arguments to pass to the MeshConverterCfg
        """
        logger.debug("Creating universal mesh")
        cfg = MeshConverterCfg(path, **kwargs)
        self.converter = MeshConverter(cfg)

    def to_cfg(self, **kwargs: Any) -> UsdFileCfg:
        """Create a UsdFileCfg object utilizing the MeshConverterCfg from an AssetMesh object

        Args:
            **kwargs: Additional keyword arguments, passed to the UsdFileCfg constructor

        Returns:
            UsdFileCfg: The IsaacLab cfg object
        """
        mesh_cfg = UsdFileCfg(usd_path=self.converter.usd_path, **kwargs)
        return mesh_cfg


def instancable(cls: type[AssetMesh]) -> type[AssetMesh]:
    """Decorator to make the assets work as instancables

    Overrides `to_cfg` to return a single instance of `SpawnerCfg`
    """

    class _instancable(cls):
        spawner: SpawnerCfg | None = None

        def to_cfg(self, **kwargs: Any) -> SpawnerCfg:
            if self.spawner is None:
                self.spawner = cls.to_cfg(self, **kwargs)
            elif kwargs:
                logger.warning("Ignoring additional keyword arguments")
            return self.spawner

    return _instancable


def apply_semantics(
    prim: Prim, type: str, value: str  # pyright: ignore[reportUnknownParameterType]
) -> None:
    """Applies a semantic type and data to a prim.

    Args:
        prim (Prim): A special type of a string that represents a prim in a stage
        type (str): Label
        value (str): Value
    """
    semantics_utils.add_update_semantics(prim, value, type)


@dataclass
class DynamicMesh(AssetMesh):
    """A dynamic mesh asset defined by a Trimesh object"""

    mesh: Trimesh
    """The Trimesh object that defines the mesh"""
    visual_material_path: str | None = None
    """Path to the visual material file, needed for MDL materials only"""
    visual_material: VisualMaterialCfg = field(default_factory=PreviewSurfaceCfg)
    """The visual material configuration for the mesh"""
    physics_material: RigidBodyMaterialCfg = field(default_factory=RigidBodyMaterialCfg)
    """The physics material configuration for the mesh"""

    # inspiration:
    # https://github.com/isaac-sim/IsaacLab/blob/963b53b96bc6140670fa0fe41d9fbafa68d8382f/source/isaaclab/isaaclab/terrains/utils.py#L61

    def to_cfg(self, **kwargs: Any) -> SpawnerCfg:
        """Converts the dynamic mesh to a SpawnerCfg object

        Args:
            **kwargs: Additional keyword arguments, passed to the SpawnerCfg constructor

        Returns:
            SpawnerCfg: A SpawnerCfg object representing the dynamic mesh
        """
        logger.debug("Creating dynamic mesh cfg")

        if self.visual_material_path:
            self.visual_material = MdlFileCfg(mdl_path=self.visual_material_path)

        def func_wrapper(  # pyright: ignore[reportUnknownParameterType]
            prim: str, cfg: SpawnerCfg, *args: Any, **kwargs: Any
        ) -> Prim:
            create_prim_from_mesh(
                prim,
                self.mesh,
                visual_material=self.visual_material,
                physics_material=self.physics_material,
                *args,
                **kwargs,
            )
            p: Prim = prim_utils.get_prim_at_path(prim)
            if cfg.semantic_tags is not None:
                for tag, value in cfg.semantic_tags:
                    apply_semantics(p, tag, value)
            return p

        return SpawnerCfg(func=func_wrapper, **kwargs)


@instancable
class DebugMesh(DynamicMesh):
    def __init__(self):
        super().__init__(mesh=primitives.Box(extents=[1.0, 1.0, 1.0]))
