# Author: Vu Anh Vu <anh.vu.vu@huawei.com>
#
# pai_demo multi-stage Dockerfile
#
# Three stages, two targets:
#
#   dev      — devcontainer base: system toolchain + pixi, no source baked in.
#              VS Code mounts the workspace and pixi installs via postCreateCommand.
#              Target this in devcontainer.json.
#
#   builder  — extends dev: COPYs source, runs pixi install + colcon build.
#              Not targeted directly — intermediate stage for the runtime build.
#
#   runtime  — deployment image: pre-built pixi env + workspace overlay.
#              Uses `pixi run` as entrypoint (same invocation devs use locally).
#              Runs as non-root `ros` user. Target this for production / Docker Hub.
#
# Usage:
#   Devcontainer:  devcontainer.json → "target": "dev"
#   Runtime build: docker buildx build -f docker/Dockerfile --target runtime -t demos --load .
#   Compose:       docker compose -f docker/docker-compose.yaml up

# ===========================================================================
# Stage: dev — the devcontainer base
# ===========================================================================
FROM ghcr.io/prefix-dev/pixi:0.69.0-noble-cuda-12.9.1 AS dev

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# System deps not on conda-forge (libserial, X11/GL for RViz/Gazebo rendering)
RUN apt-get update && apt-get install -y --no-install-recommends \
      locales \
      tzdata \
      ca-certificates \
      git \
      git-lfs \
      build-essential \
      pkg-config \
      sudo \
      vim \
      less \
      libserial-dev \
      libxrandr2 \
      libxcursor1 \
      libxinerama1 \
      libxi6 \
      libxss1 \
      libegl1 \
      libgl1 \
    && rm -rf /var/lib/apt/lists/* \
    && locale-gen en_US.UTF-8

ENV LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Create ros user (1000:1000), handling pre-existing UID/GID in the base image
RUN existing_group=$(getent group 1000 | cut -d: -f1) \
    && if [ -z "$existing_group" ]; then groupadd --gid 1000 ros; \
       elif [ "$existing_group" != "ros" ]; then groupmod -n ros "$existing_group"; fi \
    && existing_user=$(getent passwd 1000 | cut -d: -f1) \
    && if [ -z "$existing_user" ]; then useradd -ms /bin/bash --uid 1000 --gid 1000 ros; \
       elif [ "$existing_user" != "ros" ]; then usermod -l ros -d /home/ros -m "$existing_user"; fi \
    && mkdir -p /home/ros/.cache \
    && chown -R ros:ros /home/ros \
    && echo "ros ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ros \
    && chmod 0440 /etc/sudoers.d/ros

RUN echo 'eval "$(pixi completion -s bash)"' >> /home/ros/.bashrc

USER ros
WORKDIR /workspaces/demos

# ===========================================================================
# Stage: builder — extends dev, builds the workspace for deployment
# ===========================================================================
FROM dev AS builder

USER root
WORKDIR /demos

COPY pixi.toml pixi.lock ./
COPY scripts/activate.sh ./scripts/activate.sh
COPY .colcon ./.colcon
COPY repos/external.repos ./repos/external.repos

RUN pixi install --locked
RUN pixi run _vcs-import
RUN pixi run _register-mixins

COPY src/pai ./src/pai
RUN pixi run build

# ===========================================================================
# Stage: runtime — deployment image with pixi for activation
# ===========================================================================
FROM dev AS runtime

USER root
WORKDIR /demos

COPY --from=builder /demos/.pixi /demos/.pixi
COPY --from=builder /demos/pixi.toml /demos/pixi.toml
COPY --from=builder /demos/pixi.lock /demos/pixi.lock
COPY --from=builder /demos/scripts/activate.sh /demos/scripts/activate.sh
COPY --from=builder /demos/.colcon /demos/.colcon

COPY --from=builder /demos/install /demos/install

USER ros
ENTRYPOINT ["pixi", "run"]
CMD ["ros2", "launch", "pai_bringup", "so_arm_gz_bringup.launch.py"]
