from collections.abc import Mapping
from dataclasses import MISSING, dataclass
from typing import Any

import gymnasium as gym
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import ManagerBasedRLEnv, ManagerBasedRLEnvCfg, ViewerCfg
from isaaclab.sensors import SensorBaseCfg
from isaaclab.utils import configclass

from .factory import NFLInteractiveSceneCfg
from .scene_spec import SceneSpec


@configclass
class TaskEnvCfg(ManagerBasedRLEnvCfg):
    """Configuration for a task environment, usually created by `TrainingSpec`."""

    scene: (  # pyright: ignore[reportIncompatibleVariableOverride]
        NFLInteractiveSceneCfg
    ) = MISSING  # pyright: ignore[reportAssignmentType]
    """The actual live scene"""
    spec: SceneSpec = MISSING  # pyright: ignore[reportAssignmentType]
    """Specification for the scene to be used in the environment."""
    sensors: Mapping[str, SensorBaseCfg] = (
        MISSING  # pyright: ignore[reportAssignmentType]
    )
    """Definition of sensors to be used in the environment."""

    def __post_init__(self):
        """Post initialization."""
        # step settings
        self.decimation = 4  # env step every 4 sim steps: 200Hz / 4 = 50Hz
        # simulation settings
        self.sim.dt = 0.005  # sim step every 5ms: 200Hz

    def register(self, id: str, **kwargs: str):
        """Registers the environment within `gymnasium`.

        An instance of this class is stored within globals of this module,
        as `globals()[id]`. Gymnasium is then instructed to get this instance,
        and pass it to `NflEnvMixin`.

        Args:
            id (str): The id of the environment to register.
            **kwargs (str): Additional keyword arguments to pass to `gymnasium.register`.
        """

        globals()[id] = self
        gym.register(
            id=id,
            entry_point=f"{__name__}:NflEnvMixin",
            disable_env_checker=True,
            kwargs={"env_cfg_entry_point": f"{__name__}:{id}", **kwargs},
        )


@dataclass
class TrainingSpec:
    """A complete specification for training a robot in a scene.

    Having defined your scene using a `SceneSpec`, you then have to define your
    task, by deciding which robot to use, what sensors you need, and your
    rewards, terminations, commands, etc... Consult the Isaac Lab documentation
    for more information how to do it properly.

    After creating your `TrainingSpec`, you can create a `ManagerBasedRLEnv`
    instance using the `to_env_cfg` method. This custom environment is best
    registered in gymnasium using the `register` method.
    """

    scene: SceneSpec
    robot: ArticulationCfg

    actions: object
    observations: object
    events: object

    rewards: object
    terminations: object
    commands: object

    sensors: Mapping[str, SensorBaseCfg]

    def to_env_cfg(
        self,
        view_cfg: ViewerCfg,
        decimation: int = 4,
        episode_length_s: float = 100.0,
    ) -> TaskEnvCfg:
        env_cfg = TaskEnvCfg(
            scene=NFLInteractiveSceneCfg(1, 1.0, robot=self.robot),
            viewer=view_cfg,
            decimation=decimation,
            actions=self.actions,
            observations=self.observations,
            events=self.events,
            rewards=self.rewards,
            terminations=self.terminations,
            commands=self.commands,
            episode_length_s=episode_length_s,
            sensors=self.sensors,
            spec=self.scene,
        )

        return env_cfg


class NflEnvMixin(ManagerBasedRLEnv):
    def __init__(self, cfg: TaskEnvCfg, **kwargs: Any):
        factory = cfg.spec.create_instance(cfg.scene.num_envs, cfg.scene.env_spacing)
        for name, sensor in cfg.sensors.items():
            factory.add_sensor(name, sensor)
        cfg.scene = factory.get_scene(cfg.scene.robot)
        self.terrain = factory.terrain
        super().__init__(cfg, **kwargs)
