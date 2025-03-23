from isaaclab.source.isaaclab.isaaclab.terrains import SubTerrainBaseCfg

from trimesh import Trimesh
import numpy as np

from typing import Callable, TypeAlias

OurGenFunc: TypeAlias = Callable[
    [float, tuple[float, float]], tuple[list[Trimesh], np.ndarray]
]


class GeneratorFunc:
    def __init__(self, generate: OurGenFunc):
        self._func = generate

    def __call__(
        self, difficulty: float, cfg: SubTerrainBaseCfg
    ) -> tuple[list[Trimesh], np.ndarray]:
        return self._func(difficulty, cfg.size)


class TerrainSpec:
    def __init__(self, generate: OurGenFunc):
        self._func = generate

    @property
    def generate(
        self,
    ) -> Callable[[float, SubTerrainBaseCfg], tuple[list[Trimesh], np.ndarray]]:
        return GeneratorFunc(self._func)
