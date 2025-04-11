# isaaclab imports
from isaaclab.source.isaaclab.isaaclab.scene import InteractiveSceneCfg

from .asset import AssetInstance
from .terrain import TerrainInstance


class SceneCfgFactory:
    """A factory class for creating InteractiveSceneCfg objects from TerrainSpec and AssetSpec objects"""

    def __init__(
        self,
        terrain: TerrainInstance,
        name: str = "World",
    ):
        """Create a new SceneCfgFactory object

        Args:
            terrain (TerrainInstance): The terrain to use
        """
        self.terrain = terrain
        self.assets: list[AssetInstance] = []
        self.names = set()
        self.name = name

    def set_terrain_spec(self, spec: TerrainInstance) -> None:
        """Set the TerrainInstance object to use

        Args:
            spec (TerrainInstance): The TerrainInstance object to use
        """
        self.terrain = spec

    def add_asset(self, asset: AssetInstance) -> None:
        """Add an AssetInstance object to the factory

        Args:
            asset (AssetInstance): The AssetInstance object to add

        Raises:
            ValueError: If an asset with the same name already exists
        """
        if asset.name in self.names:
            raise ValueError(f"Asset with name {asset.name} already exists")
        self.assets.append(asset)
        self.names.add(asset.name)

    def new_scene(self) -> InteractiveSceneCfg:
        """Create a new InteractiveSceneCfg object from the TerrainSpec and AssetSpec objects

        Returns:
            InteractiveSceneCfg: The InteractiveSceneCfg object
        """

        cfg = InteractiveSceneCfg()

        cfg.__setattr__("terrain", self.terrain.to_terrain_generator_cfg())

        for asset in self.assets:
            cfg.__setattr__(asset.name, asset.to_rigid_object_cfg(self.name))

        return cfg
