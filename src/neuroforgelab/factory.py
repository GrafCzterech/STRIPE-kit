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
    sub_terrain = SubTerrainBaseCfg()
    sub_terrain.function = terrain_spec.generate

    terrain = TerrainGeneratorCfg()
    terrain.sub_terrains["main"] = sub_terrain

    return terrain


def new_rigid_object_cfg(asset: AssetSpec) -> RigidObjectCfg:
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
    def __init__(self, terrain_spec: TerrainSpec):
        self.terrain_spec: TerrainSpec = terrain_spec
        self.assets: list[AssetSpec] = []
        self.names = set()

    def set_terrain_spec(self, spec: TerrainSpec) -> None:
        self.terrain_spec = spec

    def add_asset(self, asset: AssetSpec) -> None:
        if asset.name in self.names:
            raise ValueError(f"Asset with name {asset.name} already exists")
        self.assets.append(asset)
        self.names.add(asset.name)

    def new_scene(self) -> InteractiveSceneCfg:

        cfg = InteractiveSceneCfg()

        cfg.__setattr__("terrain", new_terrain_generator_cfg(self.terrain_spec))

        for asset in self.assets:
            cfg.__setattr__(asset.name, new_rigid_object_cfg(asset))

        return cfg
