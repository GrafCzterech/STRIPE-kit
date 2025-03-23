import unittest
from trimesh import Trimesh
import numpy as np
from isaacsim import SimulationApp


class TestFactory(unittest.TestCase):

    def setUp(self):
        self.app = SimulationApp({"headless": True})  # type: ignore
        super().setUp()

    def tearDown(self):
        self.app.close()
        super().tearDown()

    def test_factory(self):
        from isaaclab.source.isaaclab.isaaclab.scene import InteractiveScene
        from neuroforgelab import SceneCfgFactory, TerrainSpec, AssetSpec

        def generate_terrain(
            diff: float, size: tuple[float, float]
        ) -> tuple[list[Trimesh], np.ndarray]:
            # generate a flat plane
            width, height = size
            vertices = [
                [0, 0, 0],
                [0, height, 0],
                [width, height, 0],
                [width, 0, 0],
            ]
            faces = [
                [0, 1, 2],
                [0, 2, 3],
            ]
            mesh = Trimesh(vertices=vertices, faces=faces)
            return [mesh], np.array(vertices)

        terrain = TerrainSpec(generate_terrain, (1, 1))
        factory = SceneCfgFactory(terrain)
        cfg = factory.new_scene()
        scene = InteractiveScene(cfg)
        print(scene.get_state())
