Installation
=============

Installing Isaac Lab, and then subsequently installing Stripe Kit, can be
a daunting task. That's why this guide will walk you through the process
step-by-step.

Create a Virtual Environment
-----------------------------

You are going to want to have a virtual environment for this. Trust me, the
package bloat is real and a pain to manage. While normally, personally,
we consider Conda to be overkill, here it's also necessary. So let's create
a conda environment:

.. code-block:: bash

    conda create -p ~/env_isaaclab python=3.10
    conda activate ~/env_isaaclab

Now we have to install Isaac Lab. Unfortunately, since Isaac Lab isn't on
the normal PyPI, we have to run a separate command for this:

.. code-block:: bash

    pip install isaaclab[isaacsim,all] --extra-index-url https://pypi.nvidia.com

Wonderful. Now we are going to have a problem though, where static analyzers
won't like this setup one bit. To alleviate that issue, run the following
commands:

.. code-block:: bash

    conda develop ~/env_isaaclab/lib/python3.10/site-packages/isaaclab/source/isaaclab
    conda develop ~/env_isaaclab/lib/python3.10/site-packages/isaaclab/source/isaaclab_tasks
    conda develop ~/env_isaaclab/lib/python3.10/site-packages/isaaclab/source/isaaclab_rl
    conda develop ~/env_isaaclab/lib/python3.10/site-packages/isaaclab/source/isaaclab_assets

This will create necessary symlinks for the packages to be recognized by the
Python interpreter, during development in your IDE.

Install STRIPE-kit
-------------------

This step is actually fairly straightforward. We will use pip to install
the Stripe Kit package:

.. code-block:: bash

    pip install stripe_kit

However, there's nothing stopping you from installing it from the git repo
directly:

.. code-block:: bash

    pip install git+https://github.com/GrafCzterech/STRIPE-kit.git

Test
-----

First, let's test if IsaacSim actually works:

.. code-block:: bash

    isaacsim

Then, we are going to need to have a ready to use Isaac Lab script. In order
to test that we can simulate things, here's a very simple one:

.. code-block:: python3

    import argparse
    parser = argparse.ArgumentParser(
        description="Basic scene loading"
    )
    AppLauncher.add_app_launcher_args(parser)
    args_cli = parser.parse_args()

    simulation_app = AppLauncher(args_cli).app

    from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
    from isaaclab.sim import SimulationContext, SimulationCfg

    from isaaclab_assets.robots.spot import SPOT_CFG


    def run_simulation(sim: SimulationContext, scene: InteractiveScene) -> None:
        """Function to run a simulation.
        Pretty basic as of now.

        Args:
            sim (sim_utils.SimulationContext): Simulation Context as defined by Isaac Lab
            scene (InteractiveScene): Scene generated from NFL Interface config class
        """
        sim_dt = sim.get_physics_dt()

        sim.pause()

        while simulation_app.is_running():
            scene.write_data_to_sim()
            sim.step()
            scene.update(sim_dt)


    if __name__ == "__main__":

        # Simulation Context initialization
        sim_cfg = SimulationCfg(device=args_cli.device)
        sim = SimulationContext(sim_cfg)

        logger.debug("Simulation context initialized")

        # Camera setting
        sim.set_camera_view((0.0, 0.0, 5.0), (1.0, 1.0, 4.0))

        # Scene generation
        my_scene_cfg = InteractiveSceneCfg(1, 0.0)

        logger.debug("Scene generated")
        my_scene = InteractiveScene(my_scene_cfg)

        # Reset simulation context - required by Isaac Lab
        sim.reset()

        # Run scene
        logger.info("Setup completed!")  # Yipeee! Cola trinken!
        run_simulation(sim, my_scene)
        simulation_app.close()

Assuming it's saved as `sim.py`, we can run it using the following command:

.. code-block:: bash

    python3 sim.py

You can launch Isaac Lab / Sim integrating scripts in a multitude of ways,
however, the one which we have found the easiest is to have each script
launch Isaac Lab, as it's done in the script above. **Be sure** to manage
import accordingly however, modules such as: `isaaclab`, `isaacsim`,
`gymnasium`, `skrl`, `pxr` will not be importable, as long as there isn't
a running instance of Isaac Lab. Since `stripe_kit` uses these imports
to provide type hints, you should only import `stripe_kit` after you have
a running instance of the simulation.
