# isaaclab imports
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.assets import AssetBaseCfg

from .asset import SceneAsset
from .terrain import TerrainInstance

TERRAIN_NAME = "terrain"


class SceneCfgFactory:
    """A factory class for creating InteractiveSceneCfg objects from TerrainSpec and AssetSpec objects"""

    def __init__(
        self,
        terrain: TerrainInstance,
        robot: AssetBaseCfg,
        name: str = "World",
    ):
        """Create a new SceneCfgFactory object

        Args:
            terrain (TerrainInstance): The terrain to use
        """
        self.terrain = terrain
        self.assets: list[SceneAsset] = []
        self.names = set()
        self.name = name
        self.robot = robot

    def set_terrain_spec(self, spec: TerrainInstance) -> None:
        """Set the TerrainInstance object to use

        Args:
            spec (TerrainInstance): The TerrainInstance object to use
        """
        self.terrain = spec

    def add_asset(self, asset: SceneAsset) -> None:
        """Add an AssetInstance object to the factory

        Args:
            asset (AssetInstance): The AssetInstance object to add

        Raises:
            ValueError: If an asset with the same name already exists
        """
        if asset.get_name() in self.names:
            raise ValueError(
                f"Asset with name {asset.get_name()} already exists"
            )
        self.assets.append(asset)
        self.names.add(asset.get_name())

    def new_scene(self) -> InteractiveSceneCfg:
        """Create a new InteractiveSceneCfg object from the TerrainSpec and AssetSpec objects

        Returns:
            InteractiveSceneCfg: The InteractiveSceneCfg object
        """

        # this is ever so slightly more performant, that creating a new dynamic class(an object) then an instance of that class (yet another object)
        cfg = InteractiveSceneCfg()

        importer = TerrainImporterCfg()
        importer.prim_path = f"/{self.name}/{TERRAIN_NAME}"
        importer.terrain_type = "generator"
        importer.terrain_generator = self.terrain.to_terrain_generator_cfg()
        setattr(cfg, TERRAIN_NAME, importer)

        for asset in self.assets:
            setattr(cfg, asset.get_name(), asset.to_cfg(self.name))

        setattr(cfg, "robot", self.robot)

        setattr(cfg, "num_envs", 1)
        setattr(cfg, "env_spacing", 0.0)

        return cfg
