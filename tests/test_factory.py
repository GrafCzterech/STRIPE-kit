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
        from neuroforgelab import SceneCfgFactory, TerrainInstance

        terrain = TerrainInstance(
            mesh=[
                Trimesh(
                    vertices=np.array([[0, 0, 0]]), faces=np.array([[0, 0, 0]])
                )
            ],
            origin=np.array([0, 0, 0]),
            size=(1, 1),
        )

        factory = SceneCfgFactory(terrain)
        cfg = factory.new_scene()
        scene = InteractiveScene(cfg)
        print(scene.get_state())
