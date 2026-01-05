Architecture Overview
======================

This is meant to act as a rough guide and overview of how you should organise
your work with STRIPE-kit. Since STRIPE-kit is a library, with modular design at
its core, no specifics are provided here. This is essentially an even
higher-level overview of the library's architecture.

.. figure:: STRIPE_kit.png
   :scale: 50 %

   STRIPE-kit general architecture deployment diagram

Project Elements
-----------------

To use `stripe_kit` in your project, you need to provide the following elements:

1. Task specification as :py:class:`stripe_kit.TrainingSpec`
2. Scene generation module as :py:class:`stripe_kit.SceneSpec`

For convenience, we advise you keep those separate and generic, so that you can
easily switch and reuse them across different projects. Ideally, you can
keep them as separate repositories and python modules, as we did during the
development of this library.

Technically speaking, :py:class:`stripe_kit.TrainingSpec` holds a reference
to :py:class:`stripe_kit.SceneSpec` as :py:attr:`stripe_kit.TrainingSpec.scene`.
Via this reference, the training specification acts as a facade of your project
through which `stripe_kit` can interact with your project's scene generation
module.

Consult with :doc:`generation` guide to learn more how to build these elements.

Internal Flow
--------------

Internally, `stripe_kit` can be separated into two main components of separate
functions:

1. Task Interface
2. Scene Interface

Task interface is responsible for registering tasks and binding them to a given
scene. On the other hand, the scene interface provides tools that allow you to
express how your scene should look like.

These two can be used separately to provide a modular and flexible framework for
generating scenes and training. To learn more about these specific components,
consult with the :doc:`stripe_kit` module documentation.

However, for most users, this knowledge is not necessary. You should only keep
this in mind, while extending the functionality of the library in your own
classes.

Training Machine
-----------------

You are going to need to find a machine powerful enough to run Nvidia Isaac Lab.
That's a bit of a tall order, since it requires ~100GB of space and at least
an RTX 4060, realistically speaking of course.

In our case, we utilized a computing cluster, provided by our faculty, to run
the training process. Since having video output out of clusters is usually
not possible, we had to resort to using a livestreaming client to visualize
scene simulation. You can find more information about this in the
`Isaac Sim documentation <https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/manual_livestream_clients.html>`_.

For visualizing the training process, Isaac Lab allows you to generate short
films every couple of iterations. This is the ideal solution for monitoring
the training progress and you can find more information about this in the
`Isaac Lab documentation <https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/run_rl_training.html>`_.

Showcase
----------

Feel free to explore our `codebase <https://github.com/GrafCzterech>`_,
especially beyond the `stripe_kit` repository. There you can find our scene
generation module `forest_gen <https://github.com/GrafCzterech/forest_gen>`_, it
should be useful for understanding how to implement your own tasks and scenes.

Be sure to check out `sim.py` and `task.py` at `forest_gen` repo root. They
provide a reference of how you can simulate in IsaacLab the generated scene -
in case of `sim.py`, and how to build a task with `stripe_kit` in case of
`task.py`.

Generally speaking, if you were to wrap `task.py` in another script, that
was to import the exported `task_spec`, and then registered the spec, you
would be 90% there when it comes to training a robot to walk in a forest.
You would just have to follow the instructions on how to build a `training
script <https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/run_rl_training.html>`_
