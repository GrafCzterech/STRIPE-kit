from dataclasses import dataclass
from abc import abstractmethod, ABC
from logging import getLogger

logger = getLogger(__name__)

from isaaclab.assets import AssetBaseCfg
from isaaclab.sim.spawners.lights import DistantLightCfg


from .terrain import TerrainInstance
from .mesh import AssetMesh, CLASS_TAG


@dataclass
class AssetSpec(ABC):
    """A specification for an asset to be placed in a scene. We know nothing
    about the asset, beyond that it has a name. This is a base class for all
    assets"""

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
            usd_path: Path to an USD file, from which the asset mesh originates
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

    usd_path: str

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

    asset_class: AssetSpec | None
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

        if self.asset_class is None:
            prim_path = f"/{scene_name}/{self.name}"
        else:
            prim_path = f"/{scene_name}/{self.asset_class.name}/{self.name}"

        obj = AssetBaseCfg(prim_path=prim_path)

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
