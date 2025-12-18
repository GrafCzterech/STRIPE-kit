.. STRIPE-kit documentation master file, created by
   sphinx-quickstart on Thu Nov 20 18:37:50 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

STRIPE-kit documentation
========================

Welcome to the STRIPE-kit documentation!

Ideally you should read the entirety of the documentation, as it goes through
the really useful bits like installation, but also the higher level concepts
and how you should use this toolkit.

Nvidia Isaac Lab, is a powerful platform, based on Nvidia Isaac Sim, that
provides a powerful environment for reinforcement learning research.
Robots are simulated in the Isaac Sim simulation, which when integrated with
utilities provided by Isaac Lab allow them to learn from the environment.

STRIPE-kit is a toolkit for defining tasks and plausible training environments
for reinforcement learning (RL) in Nvidia Isaac Lab.

The core idea, is that the Nvidia Isaac Lab provides a rich platform for RL
research, but the code structures for procedural generation and task definition
are lacking. STRIPE-kit solves that issue by providing tools and utilities that
allow you to specify environments, assets, placements etc...
Beyond that, STRIPE-kit should improve your development experience, by acting
as a bridge that should save you from interacting with the Isaac Lab API
directly.

To get started, first read the installation guide (really recommended). It
should get you started with the basics of STRIPE-kit. If you need to see
an example of how to use STRIPE-kit, check out our showcase forest generation
module.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   stripe_kit
   generation
   architecture
   Isaac Lab Documentation <https://isaac-sim.github.io/IsaacLab/main/index.html>
   Repository <https://github.com/GrafCzterech/STRIPE-kit>
