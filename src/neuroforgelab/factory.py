from logging import getLogger

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

    def __init__(self, terrain: TerrainInstance):
        """Create a new SceneCfgFactory object

        Args:
            terrain (TerrainInstance): The terrain to use
        """
        self.terrain = terrain
        self.assets: list[SceneAsset] = []
        self.names = set()

    def set_terrain_spec(self, spec: TerrainInstance) -> None:
        """Set the TerrainInstance object to use

        Args:
            spec (TerrainInstance): The TerrainInstance object to use
        """
        self.terrain = spec

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
        self.assets.append(asset)
        self.names.add(asset.get_name())
        logger.debug(f"Added asset {asset.get_name()}")

    def new_scene(
        self,
        robot: AssetBaseCfg | None = None,
        sensors: dict[str, SensorBaseCfg] | None = None,
        num_envs: int = 1,
        env_spacing: float = 0.0,
        **kwargs,
    ) -> NFLInteractiveSceneCfg:
        """Create a new InteractiveSceneCfg object from the TerrainInstance and SceneAsset objects

        Args:
            robot (AssetBaseCfg | None): The robot asset configuration
            sensors (dict[str, SensorBaseCfg] | None): The sensor configurations
            num_envs (int): The number of environments to create
            env_spacing (float): The spacing between environments
            kwargs: Additional keyword arguments to pass to the InteractiveSceneCfg constructor

        Returns:
            InteractiveSceneCfg: The InteractiveSceneCfg object
        """
        logger.debug("Creating scene cfg")

        # this is ever so slightly more performant, that creating a new dynamic class(an object) then an instance of that class (yet another object)
        cfg = NFLInteractiveSceneCfg(num_envs, env_spacing, **kwargs)

        for i, asset in enumerate(self.terrain.to_asset_cfg()):
            setattr(
                cfg,
                TERRAIN_NAME + f"_{i}",
                asset,
            )

        for asset in self.assets:
            setattr(
                cfg,
                asset.get_name(),
                asset.to_cfg(),
            )

        if robot is not None:
            setattr(cfg, "robot", robot)
            robot.prim_path = "{ENV_REGEX_NS}/Robot"

        if sensors is not None:
            for name, sensor in sensors.items():
                setattr(cfg, name, sensor)

        return cfg
