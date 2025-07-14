from logging import getLogger

logger = getLogger(__name__)

# isaaclab imports
from isaaclab.assets import AssetBaseCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import SensorBaseCfg

from .asset import SceneAsset
from .terrain import TerrainInstance, TERRAIN_NAME


class SceneCfgFactory:
    """A factory class for creating InteractiveSceneCfg objects from TerrainInstance and SceneAsset objects"""

    robot_name: str = "robot"

    def __init__(
        self,
        terrain: TerrainInstance,
        robot: AssetBaseCfg | None = None,
        sensors: dict[str, SensorBaseCfg] | None = None,
    ):
        """Create a new SceneCfgFactory object

        Args:
            terrain (TerrainInstance): The terrain to use
        """
        self.terrain = terrain
        self.assets: list[SceneAsset] = []
        self.names = set()
        self.robot = robot
        self.sensors = sensors

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
        num_envs: int = 1,
        env_spacing: float = 0.0,
    ) -> InteractiveSceneCfg:
        """Create a new InteractiveSceneCfg object from the TerrainInstance and SceneAsset objects

        Args:
            num_envs (int): The number of environments to create
            env_spacing (float): The spacing between environments

        Returns:
            InteractiveSceneCfg: The InteractiveSceneCfg object
        """
        logger.debug("Creating scene cfg")

        # this is ever so slightly more performant, that creating a new dynamic class(an object) then an instance of that class (yet another object)
        cfg = InteractiveSceneCfg()

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

        if self.robot is not None:
            if isinstance(self.robot, AssetBaseCfg):
                robot_cfg = self.robot
                robot_cfg.prim_path = "{ENV_REGEX_NS}" + f"/{self.robot_name}"
            else:
                robot_cfg = self.robot.to_cfg()
            setattr(
                cfg,
                self.robot_name,
                robot_cfg,
            )

        if self.sensors is not None:
            for name, sensor in self.sensors.items():
                setattr(
                    cfg,
                    name,
                    sensor,
                )

        setattr(cfg, "num_envs", num_envs)
        setattr(cfg, "env_spacing", env_spacing)

        return cfg
