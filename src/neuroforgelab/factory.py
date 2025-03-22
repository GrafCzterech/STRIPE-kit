from isaaclab.source.isaaclab.isaaclab.scene import InteractiveSceneCfg
from isaaclab.source.isaaclab.isaaclab.terrains import (
    SubTerrainBaseCfg,
    TerrainGeneratorCfg,
)
from trimesh import Trimesh
import numpy as np
from typing import Callable, TypeAlias

our_gen_func: TypeAlias = Callable[[float], tuple[list[Trimesh], np.ndarray]]


class GeneratorFunc:
    def __init__(self, generate: our_gen_func):
        self._func = generate

    def __call__(
        self, difficulty: float, cfg: SubTerrainBaseCfg
    ) -> tuple[list[Trimesh], np.ndarray]:
        return self._func(difficulty)


class TerrainSpec:
    def __init__(self, generate: our_gen_func):
        self._func = generate

    @property
    def generate(
        self,
    ) -> Callable[[float, SubTerrainBaseCfg], tuple[list[Trimesh], np.ndarray]]:
        return GeneratorFunc(self._func)


class AssetSpec:
    def __init__(self, path: str, asset_class: str):
        self.path = path
        self.asset_class = asset_class


class SceneCfgFactory:
    def __init__(self):
        self.terrain_spec: TerrainSpec | None = None
        self.assets: list[AssetSpec] = []

    def set_terrain_spec(self, spec: TerrainSpec) -> None:
        self.terrain_spec = spec

    def add_asset(self, asset: AssetSpec) -> None:
        self.assets.append(asset)

    def new_scene(self) -> InteractiveSceneCfg:
        cfg = InteractiveSceneCfg()
        # TODO actually do the thing
        return cfg
