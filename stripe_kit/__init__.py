"""
STRIPE-kit is a kit of utilities wrapping over various Isaac Lab and Isaac
Sim utilities. The core idea, is that you define your scene by inheriting and
utilizing different classes provided here, ideally in a separate module, and
then after providing the task specification simply register it with gymnasium
and run your Isaac Lab RL training.

----------

Here's a step-by-step guide to get you started:

1. Create your `SceneSpec`
    This is where you define how the scene should be generated. Create a new
    class that inherits from `SceneSpec` and implement the methods as needed.
2. Define your task
    This is done via standard Isaac Lab `configclass`es, so you define your
    reward terms, termination terms, etc...
3. Couple your task with your scene
    This is done by creating a new instance of `TrainingSpec`, which takes in
    a `SceneSpec` and all the necessary parameters for the task.
4. Register your task with gymnasium
    `TrainingSpec` can be transformed into a `TaskEnvCfg`, which can be directly
    registered with gymnasium.
5. Run your training
    Once your task is registered, any training script that uses gymnasium works
    just fine. We actually have a convenient pre-built script for that, which
    once the package is installed should be accessible via the CLI as
    `skrl_train`.

----------

There are a few core concepts you need to understand when working with this
module.

- Spec: A specification, that defines how something should be generated
- Scene: An instance of a generated scene
- Mesh: A 3d mesh (3d model) that can be used in a scene
- configclass: The preferred Isaac Lab way of creating things, is via creating a subclass or instance of a configclass
"""

from .asset import AssetInstance, AssetSpec, IdenticalAssetSpec
from .env import TaskEnvCfg, TrainingSpec
from .factory import SceneCfgFactory
from .mesh import AssetMesh, DynamicMesh, UniversalMesh, USDMesh, instancable
from .scene_spec import SceneSpec
from .terrain import TerrainInstance

__all__ = [
    "SceneCfgFactory",
    "AssetSpec",
    "IdenticalAssetSpec",
    "TerrainInstance",
    "AssetInstance",
    "SceneSpec",
    "AssetMesh",
    "DynamicMesh",
    "USDMesh",
    "UniversalMesh",
    "TrainingSpec",
    "TaskEnvCfg",
    "instancable",
]
