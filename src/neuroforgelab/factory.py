# isaaclab imports
from isaaclab.source.isaaclab.isaaclab.scene import InteractiveSceneCfg
from isaaclab.source.isaaclab.isaaclab.terrains import (
    TerrainGeneratorCfg,
    SubTerrainBaseCfg,
)
from isaaclab.source.isaaclab.isaaclab.assets import RigidObjectCfg
from isaaclab.source.isaaclab.isaaclab.sim.spawners import (
    UsdFileCfg,
)

# our imports
from .terrain_spec import TerrainSpec
from .asset_spec import AssetSpec


def new_terrain_generator_cfg(terrain_spec: TerrainSpec) -> TerrainGeneratorCfg:
    """Create a TerrainGeneratorCfg object from a TerrainSpec object

    Args:
        terrain_spec (TerrainSpec): The TerrainSpec object to use

    Returns:
        TerrainGeneratorCfg: The TerrainGeneratorCfg object
    """
    sub_terrain = SubTerrainBaseCfg()
    sub_terrain.function = terrain_spec.generate
    sub_terrain.size = terrain_spec.size

    terrain = TerrainGeneratorCfg()
    terrain.sub_terrains["main"] = sub_terrain
    terrain.size = terrain_spec.size

    return terrain


def new_rigid_object_cfg(asset: AssetSpec) -> RigidObjectCfg:
    """Create a RigidObjectCfg object from an AssetSpec object

    Args:
        asset (AssetSpec): The AssetSpec object to use

    Returns:
        RigidObjectCfg: The RigidObjectCfg object
    """
    obj = RigidObjectCfg()
    obj.prim_path = "/World/" + asset.name

    spawner = UsdFileCfg()
    spawner.semantic_tags = [("name", asset.name), ("class", asset.asset_class)]
    spawner.usd_path = asset.path

    obj.spawn = spawner

    init_state = obj.InitialStateCfg()
    init_state.pos = asset.pos
    init_state.rot = asset.rot

    return obj


class SceneCfgFactory:
    """A factory class for creating InteractiveSceneCfg objects from TerrainSpec and AssetSpec objects"""

    def __init__(self, terrain_spec: TerrainSpec):
        """Create a new SceneCfgFactory object

        Args:
            terrain_spec (TerrainSpec): The TerrainSpec object to use
        """
        self.terrain_spec: TerrainSpec = terrain_spec
        self.assets: list[AssetSpec] = []
        self.names = set()

    def set_terrain_spec(self, spec: TerrainSpec) -> None:
        """Set the TerrainSpec object to use

        Args:
            spec (TerrainSpec): The TerrainSpec object to use
        """
        self.terrain_spec = spec

    def add_asset(self, asset: AssetSpec) -> None:
        """Add an AssetSpec object to the factory

        Args:
            asset (AssetSpec): The AssetSpec object to add

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

        cfg.__setattr__("terrain", new_terrain_generator_cfg(self.terrain_spec))

        for asset in self.assets:
            cfg.__setattr__(asset.name, new_rigid_object_cfg(asset))

        return cfg
