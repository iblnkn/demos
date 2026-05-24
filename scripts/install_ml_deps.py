#!/usr/bin/env python3
"""Auto-detect GPU and install the matching pixi ML environment."""

import subprocess


def detect_gpu():
    """Return the name of the first NVIDIA GPU, or empty string if none."""
    try:
        output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return output.strip().split('\n')[0]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ''


def main():
    """Detect the GPU and install the matching pixi ML environment."""
    gpu = detect_gpu()
    env = 'ml-blackwell' if '5090' in gpu else 'ml'

    print('Detected GPU:', gpu or 'none (CPU-only)')
    print('Installing pixi environment:', env)

    subprocess.check_call(['pixi', 'install', '-e', env])

    print()
    print('Done. ML tasks like rosetta-record-mujoco will use the ml env by default.')
    if env == 'ml-blackwell':
        print(
            'For native Blackwell performance, run ML tasks with: pixi run -e ml-blackwell <task>'
        )


if __name__ == '__main__':
    main()
