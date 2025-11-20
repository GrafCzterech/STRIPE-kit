from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import getLogger

from isaaclab.assets import AssetBaseCfg
from isaaclab.sim.spawners.lights import DistantLightCfg

from .mesh import CLASS_TAG, AssetMesh
from .terrain import TerrainInstance

logger = getLogger(__name__)

@dataclass
class AssetSpec(ABC):
    """A specification for a class of assets to be placed in a scene.
    SceneSpec class uses this to generate AssetInstance objects to be placed on the terrain.
    """

    name: str
    """The name of the asset. For example, "Tree" or "Rock"."""
    asset_cfg_class: type[AssetBaseCfg] = AssetBaseCfg
    """The configuration class for the asset."""

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
        return AssetInstance(
            self,
            asset,
            name,
            position,
            rotation,
            tags,
            asset_cfg_class=self.asset_cfg_class,
        )


class IdenticalAssetSpec(AssetSpec, ABC):
    """A specification for an asset class, that will be identical across all instances"""

    def __init__(
        self,
        name: str,
        mesh: AssetMesh,
        asset_cfg_class: type[AssetBaseCfg] = AssetBaseCfg,
        rotation: tuple[float, float, float, float] = (0, 0, 0, 1),
    ):
        """Create a new IdenticalAssetSpec object

        Args:
            name (str): The name of the asset
            mesh (AssetMesh): The mesh of the asset
            asset_cfg_class (type[AssetBaseCfg], optional): The configuration class for the asset. Defaults to AssetBaseCfg.
        """
        super().__init__(name, asset_cfg_class)
        self.mesh = mesh
        self.rotation = rotation

    @abstractmethod
    def find_positions(
        self, terrain: TerrainInstance
    ) -> list[tuple[float, float, float]]:
        """Find positions to place the asset on the terrain.
        This is essentially a devolved generate() that returns a list of positions instead of creating instances.

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
                self.rotation,
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
            tags (dict[str, str] | None, optional): The tags to assign to the asset instance. Defaults to None.

        Returns:
            AssetInstance: The AssetInstance object
        """
        return super().create_instance(
            name, self.mesh, position, rotation, tags
        )


class SceneAsset(ABC):
    """A scene asset that can be placed in a scene"""

    @abstractmethod
    def to_cfg(self) -> AssetBaseCfg:
        """Create a RigidObjectCfg object from an AssetInstance object

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

    asset_class: AssetSpec | None
    """The class of the asset"""
    mesh: AssetMesh
    """The mesh of the asset"""
    name: str
    """The name of the asset"""
    position: tuple[float, float, float]
    """The position of the asset"""
    rotation: tuple[float, float, float, float]
    """The rotation of the asset"""
    additional_tags: dict[str, str]
    """Additional tags for the asset"""
    asset_cfg_class: type[AssetBaseCfg] = AssetBaseCfg
    """The configuration class for the asset"""

    def to_cfg(self) -> AssetBaseCfg:
        """Create a config class object from an AssetInstance object.
        The returned type is determined by the asset_cfg_class attribute.

        Args:
            scene_name (str, optional): The name of the scene to place the asset into. Defaults to "World".

        Returns:
            asset_cfg_class: The IsaacLab cfg object
        """

        if self.asset_class is None:
            prim_path = f"/{self.name}"
        else:
            prim_path = f"/{self.asset_class.name}/{self.name}"

        obj = self.asset_cfg_class(prim_path=prim_path)

        spawner = self.mesh.to_cfg()

        if spawner.semantic_tags is None:
            spawner.semantic_tags = []

        if self.asset_class is not None:
            spawner.semantic_tags.append((CLASS_TAG, self.asset_class.name))
        spawner.semantic_tags.extend(self.additional_tags.items())

        obj.spawn = spawner

        init_state = obj.InitialStateCfg()
        init_state.pos = (self.position[0], self.position[1], self.position[2])
        init_state.rot = self.rotation
        obj.init_state = init_state

        return obj

    def get_name(self) -> str:
        """Get the name of the asset

        Returns:
            str: The name of the asset
        """
        return self.name


@dataclass
class LightSpec(SceneAsset):
    """A scene light"""

    exposure: float = 11.0
    intensity: float = 7.0
    color: tuple[float, float, float] = (0.988, 0.957, 0.645)

    def to_cfg(self, scene_name: str = "World") -> AssetBaseCfg:

        logger.debug("Creating light cfg")

        light_cfg = DistantLightCfg()
        light_cfg.exposure = self.exposure
        light_cfg.intensity = self.intensity
        light_cfg.color = self.color

        state = AssetBaseCfg.InitialStateCfg()
        state.pos = (0, 0, 0)
        state.rot = (0.82294, 0.28336, -0.4656, -0.16032)

        cfg = AssetBaseCfg()
        cfg.prim_path = f"/{scene_name}/{self.get_name()}"
        cfg.spawn = light_cfg
        cfg.init_state = state
        return cfg

    def get_name(self) -> str:
        return "light"
