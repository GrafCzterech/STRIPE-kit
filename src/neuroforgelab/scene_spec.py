from dataclasses import dataclass
from abc import abstractmethod, ABC
from logging import getLogger

logger = getLogger(__name__)

from isaaclab.assets import AssetBaseCfg
from isaaclab.managers import EventTermCfg

# https://docs.isaacsim.omniverse.nvidia.com/4.5.0/py/source/extensions/isaacsim.core.utils/docs/index.html#module-isaacsim.core.utils.stage
import isaacsim.core.utils.stage as stage_utils  # type: ignore

from .asset import AssetSpec, LightSpec
from .terrain import TerrainInstance
from .factory import SceneCfgFactory


def spawn_cfg(cfg: AssetBaseCfg) -> None:
    if cfg.spawn is not None:
        cfg.spawn.func(cfg.prim_path, cfg.spawn)
    else:
        raise ValueError(
            f"Spawn function not set for {cfg.__class__.__name__} asset"
        )


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

    def create_reset_event(self, scene_name: str) -> EventTermCfg:
        """Creates a reset event, that will initialize the scene with the
        terrain and assets specified in the SceneSpec object.

        Args:
            scene_name (str): The name of the scene to use for the reset event

        Returns:
            EventTermCfg: The EventTermCfg object
        """

        def reset_func(*args) -> None:

            # FIXME this scene reset causes a very fun exception
            # suposedly because you cant delete shit while the simulation is running
            # https://forums.developer.nvidia.com/t/delete-prim-from-simulation-and-keep-the-simulation-running/328770

            logger.debug("Resetting scene")
            stage_utils.clear_stage()

            # Reset the terrain
            terrain = self.generate()
            for asset in terrain.to_asset_cfg(scene_name):
                spawn_cfg(asset)
            # Reset the assets
            for asset in self.palette:
                logger.debug(f"Resetting asset {asset.name}")
                children = asset.generate(terrain)
                for child in children:
                    spawn_cfg(child.to_cfg(scene_name))
            # Reset the light
            logger.debug("Resetting light")
            spawn_cfg(self.light.to_cfg(scene_name))
            # Reset the robot
            if self.robot is not None:
                logger.debug("Resetting robot")
                spawn_cfg(self.robot)

        return EventTermCfg(func=reset_func, mode="reset", params={})
