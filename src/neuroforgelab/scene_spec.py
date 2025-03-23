from dataclasses import dataclass
from abc import abstractmethod, ABC

from .asset import AssetSpec, AssetInstance
from .terrain import TerrainInstance
from .factory import SceneCfgFactory


@dataclass
class SceneSpec(ABC):
    """A specification for a scene to be generated"""

    size: tuple[float, float]
    palette: list[tuple[AssetSpec, int]] = []
    static: list[AssetInstance] = []

    def add_asset(self, asset: AssetSpec, count: int = 1):
        """Add an asset to the scene palette

        Args:
            asset (AssetSpec): The asset to add
            count (int, optional): The number of instances of the asset to add. Defaults to 1.
        """
        self.palette.append((asset, count))

    @abstractmethod
    def generate(self) -> TerrainInstance:
        """Generate a terrain instance

        Returns:
            TerrainInstance: The generated terrain instance
        """
        ...

    def create_instance(self) -> SceneCfgFactory:
        """Create a SceneCfgFactory object from the SceneSpec object

        Returns:
            SceneCfgFactory: The SceneCfgFactory object
        """
        terrain = self.generate()
        factory = SceneCfgFactory(terrain)
        for asset, count in self.palette:
            pos = asset.find_positions(terrain)
            for i in range(count):
                position = pos[i % len(pos)]
                factory.add_asset(
                    asset.create_instance(
                        f"{asset.name}_{i}", position, (0, 0, 0, 1)
                    )
                )
        return factory
