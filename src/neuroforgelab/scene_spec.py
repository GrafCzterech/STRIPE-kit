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

        def reset_func(env: ManagerBasedRLEnv, *args) -> None:

            env.sim.pause()

            # print(dir(env.sim))
            # ['RenderMode', ... ,  'add_physics_callback', 'add_render_callback', 'add_stage_callback', 'add_timeline_callback', 'app', 'backend', 'backend_utils', 'cfg', 'clear', 'clear_all_callbacks', 'clear_instance', 'clear_physics_callbacks', 'clear_render_callbacks', 'clear_stage_callbacks', 'clear_timeline_callbacks', 'current_time', 'current_time_step_index', 'device', 'forward', 'get_block_on_render', 'get_physics_context', 'get_physics_dt', 'get_rendering_dt', 'get_setting', 'get_version', 'has_gui', 'has_rtx_sensors', 'initialize_physics', 'initialize_simulation_context_async', 'instance', 'is_fabric_enabled', 'is_playing', 'is_simulating', 'is_stopped', 'pause', 'pause_async', 'physics_callback_exists', 'physics_sim_view', 'play', 'play_async', 'remove_physics_callback', 'remove_render_callback', 'remove_stage_callback', 'remove_timeline_callback', 'render', 'render_async', 'render_callback_exists', 'render_mode', 'reset', 'reset_async', 'set_block_on_render', 'set_camera_view', 'set_render_mode', 'set_setting', 'set_simulation_dt', 'stage', 'stage_callback_exists', 'step', 'stop', 'stop_async', 'timeline_callback_exists']

            # if env.sim.is_simulating():
            #    raise RuntimeError(
            #        "Cannot reset scene while simulation is running. Please stop the simulation first."
            #    )

            logger.debug("Resetting scene")
            # [omni.physx.tensors.plugin] prim '/World/terrain/robot/hr_uleg/collisions/mesh_0' was deleted while being used by a shape in a tensor view class. The physics.tensors simulationView was invalidated.

            stage_utils.clear_stage(lambda prim: "robot" not in prim)

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

            env.sim.play()

            # Reset the robot
            # TODO

        return EventTermCfg(func=reset_func, mode="reset", params={})
