from dataclasses import dataclass
from abc import abstractmethod, ABC

from .asset import AssetSpec, LightSpec
from .terrain import TerrainInstance
from .factory import SceneCfgFactory

from isaaclab.assets import AssetBaseCfg


@dataclass
class SceneSpec(ABC):
    """A specification for a scene to be generated"""

    size: tuple[float, float]
    palette: list[AssetSpec]
    robot: AssetBaseCfg
    light: LightSpec = LightSpec()

    def add_asset(self, asset: AssetSpec):
        """Add an asset to the scene palette

        Args:
            asset (AssetSpec): The asset to add
        """
        self.palette.append(asset)

    @abstractmethod
    def generate(self) -> TerrainInstance:
        """Generate a terrain instance. This method is used to generate the
        terrain for the scene.

        While implementing this method, you can store extra data in the
        returned object, that then can be used by the asset specifications, thus
        allowing for more performant scene generation, where interesting spots
        encountered during terrain generation can be used to place assets.

        Returns:
            TerrainInstance: The generated terrain instance
        """
        ...

    def create_instance(self) -> SceneCfgFactory:
        """Create a SceneCfgFactory object from the SceneSpec object.

        The default implementation, generates the terrain using the generate
        method, and then generates the assets using the asset specifications
        in the palette. The generated scene is then returned.

        Returns:
            SceneCfgFactory: The SceneCfgFactory object
        """
        terrain = self.generate()
        factory = SceneCfgFactory(terrain, self.robot)
        for asset in self.palette:
            children = asset.generate(terrain)
            for child in children:
                factory.add_asset(child)
        factory.add_asset(self.light)
        return factory
