from copy import deepcopy
from dataclasses import MISSING
from logging import getLogger

# isaaclab imports
from isaaclab.assets import AssetBaseCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import SensorBaseCfg
from isaaclab.utils import configclass

from .asset import SceneAsset
from .terrain import TERRAIN_NAME, TerrainInstance

logger = getLogger(__name__)


@configclass
class NFLInteractiveSceneCfg(InteractiveSceneCfg):
    robot: AssetBaseCfg = MISSING  # pyright: ignore[reportAssignmentType]


class SceneCfgFactory:
    """A factory class for creating InteractiveSceneCfg objects from
    TerrainInstance and SceneAsset objects.

    Logically, this represents a generated scene, that for some reason
    you might want to alter or create multiple instances of.
    """

    robot_name: str = "robot"

    def __init__(
        self,
        terrain: TerrainInstance,
        num_envs: int = 1,
        env_spacing: float = 0.0,
        **kwargs: bool,
    ):
        """Create a new SceneCfgFactory object

        Args:
            num_envs (int): The number of environments to create
            env_spacing (float): The spacing between environments
        """
        self.num_envs = num_envs
        self.env_spacing = env_spacing
        self.kwargs = kwargs

        self.terrain = terrain

        self.assets: dict[str, AssetBaseCfg] = {}
        self.sensors: dict[str, SensorBaseCfg] = {}

    def add_asset(self, asset: SceneAsset) -> None:
        """Add an AssetInstance object to the factory

        Args:
            asset (AssetInstance): The AssetInstance object to add

        Raises:
            ValueError: If an asset with the same name already exists
        """
        self.assets[asset.get_name()] = asset.to_cfg()

        logger.debug(f"Added asset {asset.get_name()}")

    def add_sensor(self, name: str, sensor: SensorBaseCfg) -> None:
        """Add sensors to the scene

        Args:
            name (str): The name of the sensor
            sensor (SensorBaseCfg): The sensor configuration
        """
        self.sensors[name] = sensor

    def get_scene(
        self,
        robot: AssetBaseCfg,
    ) -> NFLInteractiveSceneCfg:
        """Gets the scene configuration

        Returns:
            NFLInteractiveSceneCfg: Shallow copy of the NFLInteractiveSceneCfg object
        """
        logger.debug("Creating scene cfg")
        robot = deepcopy(robot)
        robot.prim_path = "{ENV_REGEX_NS}/robot"
        robot.init_state.pos = self.terrain.origin

        cfg = NFLInteractiveSceneCfg(
            self.num_envs, self.env_spacing, robot=robot, **self.kwargs
        )

        for name, asset in self.assets.items():
            setattr(
                cfg,
                name,
                asset,
            )

        for name, sensor in self.sensors.items():
            setattr(
                cfg,
                name,
                sensor,
            )

        for i, asset in enumerate(self.terrain.to_asset_cfg()):
            setattr(
                cfg,
                TERRAIN_NAME + f"_{i}",
                asset,
            )

        return cfg
