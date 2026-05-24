# Development Guide

You can use [Pixi](https://pixi.sh/latest/installation/) to create an isolated workspace that doesn't depend on system-wide ROS installations or external colcon build/install directories.

Install Pixi first by following [its official documentation](https://pixi.prefix.dev/latest/installation/).

## Prerequisites

The following must be installed system-wide.
See [README.md](../README.md) for installation instructions:

_Dependent repos_: Installed via `pixi run setup` (which runs `vcs import` and registers the colcon-mixin default index)

_libserial-dev_: Required for feetech_ros2_driver. Install via:

```bash
sudo apt update && sudo apt install -y libserial-dev
```

_NVIDIA drivers and CUDA toolkit_: Required for GPU acceleration (system components)

ROS 2 Kilted dependencies are automatically installed via Pixi when you run `pixi install`.

## Quick Start

### 1. Setup Development Environment

Install the base environment and import external repos:

```bash
# Installs the default pixi environment and runs vcs import + colcon mixin setup
pixi run setup
```

If you need PyTorch + LeRobot (for `rosetta-record-mujoco`, policy training, or
inference), install the ML environment:

```bash
# Auto-detects your GPU and installs the right PyTorch wheels
pixi run install-ml-deps
```

This detects your GPU via `nvidia-smi` and installs either:

- **`ml`** — standard PyTorch (most NVIDIA GPUs and CPU-only)
- **`ml-blackwell`** — cu130 PyTorch wheels for RTX 5090 (Blackwell, sm_120)

Use `pixi run verify-gpu` to confirm PyTorch sees your GPU. ML-requiring tasks
like `rosetta-record-mujoco` default to the `ml` env automatically.

### 2. Build

Build the workspace directly from the repository root folder:

```bash
# Navigate to the repository root (where pixi.toml is located)
cd demos

# Build the workspace using Pixi task
pixi run build
```

### 3. Run Demo

The workspace is configured to use Zenoh middleware automatically.
The `RMW_IMPLEMENTATION` environment variable is set to `rmw_zenoh_cpp` via the Pixi activation environment.

Before running any ROS 2 commands, start the Zenoh router in a separate terminal.

Terminal 1 (start Zenoh router):

```bash
pixi run start-zenoh
```

Terminal 2 (launch Gazebo simulation):

```bash
pixi run so-arm-gz
```

MuJoCo simulation (SO-ARM in MuJoCo):

```bash
pixi run so-arm-mujoco
```

### 4. Interactive Mode with Pixi Shell

For interactive development, you can use `pixi shell` to enter an interactive shell with the environment activated.

```bash
cd demos
pixi shell
```

Once in the shell, the ROS environment is automatically sourced and `RMW_IMPLEMENTATION=rmw_zenoh_cpp` is set.
You can run commands (e.g., `colcon build`, Python scripts) directly.
This is useful for interactive debugging, testing, and running multiple commands.

Note: When running ROS 2 commands manually in the shell, ensure the Zenoh router is running.
Start it in a separate terminal using `pixi run start-zenoh`.

Additional resources for using Pixi can be found at this [blog](https://jafarabdi.github.io/blog/2025/ros2-pixi-dev/).

## FAQ

### Warning: "Could not find activation scripts: install/setup.bash"

This warning appears on initial setup because `install/setup.bash` is created by `colcon build`.
It's harmless and will disappear after running `pixi run build`.

### After updating pixi.toml

After modifying `pixi.toml` to add or update dependencies, run `pixi install` to install the new dependencies before building or running tasks.

### Gazebo Warnings and Errors

Common Gazebo-specific warnings and errors that may appear during simulation:

**"Trying to set debug visualization mode while GI is disabled"**: This error occurs when Gazebo's Global Illumination (GI) system tries to set debug visualization before GI is fully initialized.

**"libEGL warning: egl: failed to create dri2 screen"**: This warning appears when Gazebo cannot access the GPU directly.

The simulation will still run using software rendering, but without hardware acceleration.

For resolution steps for these, see:

- [Gazebo Rendering Plugin Documentation](https://gazebosim.org/api/rendering/9/renderingplugin.html)
- [Gazebo Sim Troubleshooting](https://gazebosim.org/docs/ionic/troubleshooting/)
