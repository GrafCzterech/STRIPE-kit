from dataclasses import dataclass
from abc import abstractmethod, ABC
from logging import getLogger

logger = getLogger(__name__)

from isaaclab.assets import AssetBaseCfg
from isaaclab.managers import EventTermCfg
from isaaclab.sim import SimulationContext
from isaaclab.envs import ManagerBasedRLEnv

# https://docs.isaacsim.omniverse.nvidia.com/4.5.0/py/source/extensions/isaacsim.core.utils/docs/index.html#module-isaacsim.core.utils.stage
import isaacsim.core.utils.stage as stage_utils  # type: ignore

from .asset import AssetSpec, LightSpec
from .terrain import TerrainInstance
from .factory import SceneCfgFactory


def spawn_cfg(cfg: AssetBaseCfg) -> None:
    if cfg.spawn is not None:
        cfg.spawn.func(cfg.prim_path, cfg.spawn)
    else:
        raise ValueError(f"Spawn function not set for {cfg.__class__.__name__} asset")


@dataclass
class SceneSpec(ABC):
    """A specification for a scene to be generated"""

    size: tuple[float, float]
    palette: list[AssetSpec]
    robot: AssetBaseCfg | None = None
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
        logger.debug("Generating terrain")
        terrain = self.generate()
        factory = SceneCfgFactory(terrain, self.robot)
        for asset in self.palette:
            logger.debug(f"Generating asset {asset.name}")
            children = asset.generate(terrain)
            for child in children:
                factory.add_asset(child)
        logger.debug("Adding light")
        factory.add_asset(self.light)
        return factory
