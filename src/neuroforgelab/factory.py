from logging import getLogger
from copy import copy, deepcopy

logger = getLogger(__name__)

# isaaclab imports
from isaaclab.assets import AssetBaseCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import SensorBaseCfg

from .asset import SceneAsset
from .terrain import TerrainInstance, TERRAIN_NAME


class NFLInteractiveSceneCfg(InteractiveSceneCfg):

    pass


class SceneCfgFactory:
    """A factory class for creating InteractiveSceneCfg objects from TerrainInstance and SceneAsset objects"""

    robot_name: str = "robot"

    def __init__(self, terrain: TerrainInstance, num_envs: int = 1, env_spacing: float = 0.0, **kwargs):
        """Create a new SceneCfgFactory object

        Args:
            num_envs (int): The number of environments to create
            env_spacing (float): The spacing between environments
        """
        self.cfg = NFLInteractiveSceneCfg(num_envs, env_spacing, **kwargs)
        self.names = set()
        self.terrain = terrain

    def add_asset(self, asset: SceneAsset) -> None:
        """Add an AssetInstance object to the factory

        Args:
            asset (AssetInstance): The AssetInstance object to add

        Raises:
            ValueError: If an asset with the same name already exists
        """
        if asset.get_name() in self.names:
            raise ValueError(
                f"Asset with name {asset.get_name()} already exists"
            )

        setattr(
            self.cfg,
            asset.get_name(),
            asset.to_cfg(),
        )

        self.names.add(asset.get_name())
        logger.debug(f"Added asset {asset.get_name()}")

    def set_robot(self, robot: AssetBaseCfg) -> None:
        """Set the robot asset configuration

        Args:
            robot (AssetBaseCfg): The robot asset configuration
        """
        robot = deepcopy(robot)
        setattr(self.cfg, "robot", robot)
        robot.prim_path = "{ENV_REGEX_NS}/robot"
        robot.init_state.pos = self.terrain.origin

    def add_sensor(self, name: str, sensor: SensorBaseCfg) -> None:
        """Add sensors to the scene

        Args:
            name (str): The name of the sensor
            sensor (SensorBaseCfg): The sensor configuration
        """
        setattr(self.cfg, name, sensor)

    def get_scene(
        self,
        **kwargs,
    ) -> NFLInteractiveSceneCfg:
        """Gets the scene configuration

        Args:
            **kwargs: Additional keyword arguments to pass to the terrain asset configuration

        Returns:
            NFLInteractiveSceneCfg: Shallow copy of the NFLInteractiveSceneCfg object
        """
        logger.debug("Creating scene cfg")

        for i, asset in enumerate(self.terrain.to_asset_cfg(**kwargs)):
            setattr(
                self.cfg,
                TERRAIN_NAME + f"_{i}",
                asset,
            )

        return copy(self.cfg)
