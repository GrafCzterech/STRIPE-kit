from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from logging import getLogger

from isaaclab.assets import AssetBaseCfg

from .asset import AssetSpec, LightSpec
from .factory import SceneCfgFactory
from .terrain import TerrainInstance

logger = getLogger(__name__)


def spawn_cfg(cfg: AssetBaseCfg) -> None:
    if cfg.spawn is not None:
        cfg.spawn.func(cfg.prim_path, cfg.spawn)
    else:
        raise ValueError(
            f"Spawn function not set for {cfg.__class__.__name__} asset"
        )


@dataclass
class SceneSpec(ABC):
    """A specification for a scene to be generated.

    You can think of this like a factory of scenes, which it is.
    Here you define how big the scenes will be, what **type** of assets they
    will have and what light should be added to the scene.

    ----------

    You **have to** implement the `generate` method, which is used to generate the
    terrain for the scene. Beyond that, for more complex scenes it's a good
    idea to implement `create_instance` on your own, but for simpler use
    cases that shouldn't be necessary.

    ----------

    The idea is, that your scene *should* have a logical palette of asset types.
    Think of it this way: a forest, will have trees, rocks, bushes etc...
    Logically you would create an AssetSpec for trees, rocks and bushes, and
    these would go to the palette. If you need contextual generation, you
    should place them in a single `AssetSpec`.

    """

    size: tuple[float, float]
    """The size of the scene"""
    palette: list[AssetSpec]
    """The palette of asset classes to be used in the scene"""
    light: LightSpec = field(default_factory=LightSpec)
    """The light specification for the scene"""

    def add_asset(self, asset: AssetSpec):
        """Add an asset to the scene palette.

        The default implementation of `create_instance` will use that palette
        to generate instances of the assets to be placed in the scene.

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

    def create_instance(
        self, num_envs: int = 1, env_spacing: float = 0.0, **kwargs: bool
    ) -> SceneCfgFactory:
        """Create a SceneCfgFactory object from the SceneSpec object.

        The default implementation, generates the terrain using the generate
        method, and then generates the assets using the asset specifications
        in the palette. The generated scene is then returned.

        Args:
            num_envs (int): The number of environments to generate
            env_spacing (float): The spacing between environments
            **kwargs: Additional keyword arguments to pass to the SceneCfgFactory

        Returns:
            SceneCfgFactory: The SceneCfgFactory object
        """
        logger.debug("Generating terrain")
        terrain = self.generate()
        factory = SceneCfgFactory(terrain, num_envs, env_spacing, **kwargs)
        for asset in self.palette:
            logger.debug(f"Generating asset {asset.name}")
            for child in asset.generate(terrain):
                factory.add_asset(child)
        logger.debug("Adding light")
        factory.add_asset(self.light)
        return factory
