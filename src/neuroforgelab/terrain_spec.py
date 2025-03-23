from isaaclab.source.isaaclab.isaaclab.terrains import SubTerrainBaseCfg

from trimesh import Trimesh
import numpy as np

from typing import Callable, TypeAlias

OurGenFunc: TypeAlias = Callable[
    [float, tuple[float, float]], tuple[list[Trimesh], np.ndarray]
]


class GeneratorFunc:
    """A decorator for a terrain generation function"""

    def __init__(self, generate: OurGenFunc):
        """Create a new GeneratorFunc object

        Args:
            generate (OurGenFunc): The terrain generation function
        """
        self._func = generate

    def __call__(
        self, difficulty: float, cfg: SubTerrainBaseCfg
    ) -> tuple[list[Trimesh], np.ndarray]:
        """Generate a terrain

        Args:
            difficulty (float): The difficulty of the terrain
            cfg (SubTerrainBaseCfg): The configuration for the terrain

        Returns:
            tuple[list[Trimesh], np.ndarray]: The generated terrain
        """
        return self._func(difficulty, cfg.size)


class TerrainSpec:
    """A specification for a terrain to be placed in a scene"""

    def __init__(self, generate: OurGenFunc, size: tuple[float, float]):
        """Create a new TerrainSpec object

        Args:
            generate (OurGenFunc): The terrain generation function
        """
        self._func = generate
        self.size = size

    @property
    def generate(
        self,
    ) -> Callable[[float, SubTerrainBaseCfg], tuple[list[Trimesh], np.ndarray]]:
        """Get the terrain generation function

        Returns:
            Callable[[float, SubTerrainBaseCfg], tuple[list[Trimesh], np.ndarray]]: The terrain generation function
        """
        return GeneratorFunc(self._func)
