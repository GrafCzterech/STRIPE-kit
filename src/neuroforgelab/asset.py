from dataclasses import dataclass
from abc import abstractmethod, ABC
import logging

from isaaclab.assets import RigidObjectCfg, AssetBaseCfg
from isaaclab.sim.spawners import UsdFileCfg, SpawnerCfg
from isaaclab.sim.spawners.lights import DistantLightCfg
from isaaclab.sim.converters import MeshConverterCfg, MeshConverter

from .terrain import TerrainInstance


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
        mesh_cfg = UsdFileCfg()
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
        logging.debug("Creating universal mesh cfg")
        mesh_cfg = UsdFileCfg()
        mesh_cfg.usd_path = self.converter.usd_path
        return mesh_cfg


@dataclass
class AssetSpec(ABC):
    """A specification for an asset to be placed in a scene. We know nothing
    about the asset, beyond that it has a name."""

    name: str

    @abstractmethod
    def generate(
        self,
        terrain: TerrainInstance,
    ) -> list["AssetInstance"]:
        """Generate instances of the asset to be placed on the terrain

        Args:
            terrain (TerrainInstance): The terrain to place the asset on

        Returns:
            list[AssetInstance]: A list of instances of the asset to be placed on the terrain
        """
        ...

    def create_instance(
        self,
        name: str,
        asset: AssetMesh,
        position: tuple[float, float, float],
        rotation: tuple[float, float, float, float],
        tags: dict[str, str] | None = None,
    ) -> "AssetInstance":
        """Create an AssetInstance object from an AssetSpec object

        Args:
            name (str): The name of the asset instance
            asset (AssetMesh): The mesh of the asset instance
            position (tuple[float, float, float]): The position of the asset instance
            rotation (tuple[float, float, float, float]): The rotation of the asset instance
            tags (dict[str, str], optional): Additional tags to add to the asset instance. Defaults to None.

        Returns:
            AssetInstance: The AssetInstance object
        """
        if tags is None:
            tags = {}
        return AssetInstance(self, asset, name, position, rotation, tags)


class IdenticalAssetSpec(AssetSpec):
    """A specification for an asset that is identical to the original asset.
    The ideal use case for this class, is when you have a single asset, like a
    street lamp, and you want to place it in multiple locations. This simplifies
    the generation step, and only requires the asset to be loaded once.
    """

    def __init__(self, name: str, mesh: AssetMesh):
        """Create a new IdenticalAssetSpec object

        Args:
            name (str): The name of the asset
            mesh (AssetMesh): The mesh of the asset
        """
        super().__init__(name)
        self.mesh = mesh

    @abstractmethod
    def find_positions(
        self, terrain: TerrainInstance
    ) -> list[tuple[float, float, float]]:
        """Find positions to place the asset on the terrain

        Args:
            terrain (TerrainInstance): The terrain to place the asset on

        Returns:
            list[tuple[float, float, float]]: A list of positions to place the asset on the terrain
        """
        ...

    def generate(self, terrain: TerrainInstance) -> list["AssetInstance"]:
        """Generate instances of the asset to be placed on the terrain

        Args:
            terrain (TerrainInstance): The terrain to place the asset on

        Returns:
            list[AssetInstance]: A list of instances of the asset to be placed on the terrain
        """
        return [
            self.create_instance(
                f"{self.name}_{i}",
                position,
                (0, 0, 0, 1),
            )
            for i, position in enumerate(self.find_positions(terrain))
        ]

    def create_instance(
        self,
        name: str,
        position: tuple[float, float, float],
        rotation: tuple[float, float, float, float],
        tags: dict[str, str] | None = None,
    ) -> "AssetInstance":
        """Create an AssetInstance object from an AssetSpec object

        Args:
            name (str): The name of the asset instance
            position (tuple[float, float, float]): The position of the asset instance
            rotation (tuple[float, float, float, float]): The rotation of the asset instance

        Returns:
            AssetInstance: The AssetInstance object
        """
        return super().create_instance(
            name, self.mesh, position, rotation, tags
        )


class SceneAsset(ABC):
    """A scene asset that can be placed in a scene"""

    @abstractmethod
    def to_cfg(self, scene_name: str = "World") -> AssetBaseCfg:
        """Create a RigidObjectCfg object from an AssetInstance object

        Args:
            scene_name (str, optional): The name of the scene to place the asset into. Defaults to "World".

        Returns:
            AssetBaseCfg: The IsaacLab cfg object
        """
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the asset

        Returns:
            str: The name of the asset
        """
        ...


@dataclass
class AssetInstance(SceneAsset):
    """A specification for an asset to be placed in a scene"""

    asset_class: AssetSpec
    mesh: AssetMesh
    name: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float, float]
    additional_tags: dict[str, str]

    def to_cfg(self, scene_name: str = "World") -> AssetBaseCfg:
        """Create a RigidObjectCfg object from an AssetInstance object

        Args:
            scene_name (str, optional): The name of the scene to place the asset into. Defaults to "World".

        Returns:
            AssetBaseCfg: The IsaacLab cfg object
        """
        logging.debug("Creating asset cfg")
        obj = RigidObjectCfg()

        obj.prim_path = f"/{scene_name}/{self.name}"

        spawner = self.mesh.to_cfg()

        if spawner.semantic_tags is None:
            spawner.semantic_tags = []

        spawner.semantic_tags.append(("name", self.name))
        spawner.semantic_tags.append(("class", self.asset_class.name))
        spawner.semantic_tags.extend(self.additional_tags.items())

        obj.spawn = spawner

        init_state = obj.InitialStateCfg()
        init_state.pos = self.position
        init_state.rot = self.rotation

        return obj

    def get_name(self) -> str:
        """Get the name of the asset

        Returns:
            str: The name of the asset
        """
        return self.name


@dataclass
class LightSpec(SceneAsset):

    exposure: float = 0.0
    intensity: float = 1.0
    color: tuple[float, float, float] = (1.0, 1.0, 1.0)

    def to_cfg(self, scene_name: str = "World") -> AssetBaseCfg:

        logging.debug("Creating light cfg")

        light_cfg = DistantLightCfg()
        light_cfg.exposure = self.exposure
        light_cfg.intensity = self.intensity
        light_cfg.color = self.color

        state = AssetBaseCfg.InitialStateCfg()
        state.pos = (0, 0, 0)
        state.rot = (0, 0, 0, 1)

        cfg = AssetBaseCfg()
        cfg.prim_path = f"/{scene_name}/{self.get_name()}"
        cfg.spawn = light_cfg
        cfg.init_state = state
        return cfg

    def get_name(self) -> str:
        return "light"
