from isaaclab.assets import RigidObjectCfg
from isaaclab.sim.spawners import UsdFileCfg

from dataclasses import dataclass
from abc import abstractmethod, ABC

from .terrain import TerrainInstance


@dataclass
class AssetSpec(ABC):
    """A specification for an asset to be placed in a scene"""

    name: str
    path: str

    @abstractmethod
    def find_positions(
        self,
        terrain: TerrainInstance,
    ) -> list[tuple[float, float, float]]:
        """Find positions to place the asset on the terrain

        Args:
            terrain (TerrainInstance): The terrain to place the asset on

        Returns:
            list[tuple[float, float, float]]: A list of positions to place the asset
        """
        ...

    def create_instance(
        self,
        name: str,
        position: tuple[float, float, float],
        rotation: tuple[float, float, float, float],
    ) -> "AssetInstance":
        """Create an AssetInstance object from an AssetSpec object

        Args:
            name (str): The name of the asset instance
            position (tuple[float, float, float]): The position of the asset instance
            rotation (tuple[float, float, float, float]): The rotation of the asset instance

        Returns:
            AssetInstance: The AssetInstance object
        """
        return AssetInstance(self, name, position, rotation)


@dataclass
class AssetInstance:
    """A specification for an asset to be placed in a scene"""

    asset_class: AssetSpec
    name: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float, float]

    def to_rigid_object_cfg(self, scene_name: str = "World") -> RigidObjectCfg:
        """Create a RigidObjectCfg object from an AssetInstance object

        Args:
            scene_name (str, optional): The name of the scene to place the asset into. Defaults to "World".

        Returns:
            RigidObjectCfg: The RigidObjectCfg object
        """
        obj = RigidObjectCfg()

        obj.prim_path = f"/{scene_name}/{self.name}"

        spawner = UsdFileCfg()
        spawner.semantic_tags = [
            ("name", self.name),
            ("class", self.asset_class.name),
        ]
        spawner.usd_path = self.asset_class.path

        obj.spawn = spawner

        init_state = obj.InitialStateCfg()
        init_state.pos = self.position
        init_state.rot = self.rotation

        return obj
