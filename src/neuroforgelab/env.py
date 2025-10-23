from collections.abc import Mapping
from dataclasses import dataclass, MISSING

from isaaclab.scene import InteractiveSceneCfg
from isaaclab.envs import ManagerBasedRLEnv, ManagerBasedRLEnvCfg, ViewerCfg
from isaaclab.utils import configclass
from isaaclab.assets import ArticulationCfg
from isaaclab.sensors import ContactSensorCfg

from .scene_spec import SceneSpec


@configclass
class TaskEnvCfg(ManagerBasedRLEnvCfg):

    spec: SceneSpec = MISSING
    sensors: Mapping[str, ContactSensorCfg] = MISSING

    def register(self, id: str, **kwargs):
        import gymnasium as gym

        globals()[id] = self
        gym.register(
            id=id,
            entry_point=f"{__name__}:NflEnvMixin",
            disable_env_checker=True,
            kwargs={"env_cfg_entry_point": f"{__name__}:{id}", **kwargs},
        )


@dataclass
class TrainingSpec:
    scene: SceneSpec
    robot: ArticulationCfg

    actions: object
    observations: object
    events: object

    rewards: object
    terminations: object
    commands: object

    sensors: Mapping[str, ContactSensorCfg]

    def to_env_cfg(
        self, view_cfg: ViewerCfg, decimation: int, episode_length_s: float
    ) -> TaskEnvCfg:
        dummy_scene = InteractiveSceneCfg(1, 1.0)
        setattr(dummy_scene, "robot", self.robot)

        env_cfg = TaskEnvCfg(
            scene=dummy_scene,
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
    def __init__(self, cfg: TaskEnvCfg, **kwargs):
        factory = cfg.spec.create_instance(cfg.scene.num_envs, cfg.scene.env_spacing)
        factory.set_robot(cfg.scene.robot)
        for name, sensor in cfg.sensors.items():
            factory.add_sensor(name, sensor)
        cfg.scene = factory.get_scene()
        super().__init__(cfg, **kwargs)
        self.cfg = cfg
