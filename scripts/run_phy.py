"""
This script is for running the interactive Phy GUI from a Docker image.

It should support several usage scenarios lile:
 - running on cortex via remote desktop
 - running on cortex via Xpra
 - running locally

It retrieves Phy as a Docker image, in which Phy and its dependencies are installed.
The default image is maintained here: https://github.com/geffenlab/geffenlab-phy-desktop

It attempts to configure GPU access and X11 display access for the Docker container.

For configuration options:

    conda activate geffen-pipelines
    python python run_phy.py --help

See also:

    docs/run-phy.md
"""


import sys
from os import getuid, getgid, environ
from argparse import ArgumentParser, BooleanOptionalAction
from typing import Optional, Sequence
import logging
from datetime import datetime, timezone
from pathlib import Path
import subprocess


def set_up_logging(
    log_path: Path = None
):
    """Set up to copy logs to stdout (the console) and to a log file."""
    logging.root.handlers = []
    handlers = [
        logging.StreamHandler(sys.stdout)
    ]
    if log_path and log_path.parent.exists():
        handlers.append(logging.FileHandler(log_path))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers
    )
    logging.info(f"Writing logs for this script to stdout and {log_path}")


def run_phy_in_docker(
    docker_image: str,
    docker_run_args: list[str],
    gpu_device: str,
    x11: bool,
    user: str,
    params_py: Path
) -> int:
    """Launch Phy via Docker and make the given params_py available inside the container."""
    logging.info("Starting Phy run.\n")

    # Configure GPU access for the Docker container.
    if gpu_device and gpu_device != 'none':
        gpus = ["--gpus", f"'device=${gpu_device}'"]
    else:
        gpus = []

    # Configure X11 display access for the Docker container.
    # This should direct, local display access as well as X display forwarding via Xpra or "ssh -X".
    if x11:
        x11_args = ["--volume", "/tmp/.X11-unix:/tmp/.X11-unix", "--env", "DISPLAY", "--net", "host"]
        if "XAUTHORITY" in environ:
            x_authority_path = Path(environ["XAUTHORITY"])
        else:
            x_authority_path = Path("~/.Xauthority").expanduser()

        if x_authority_path.exists():
            x_authority_host = x_authority_path.absolute().as_posix()
            x_authority_container = "/var/.Xauthority"
            x11_args += ["--volume", f"{x_authority_host}:{x_authority_container}", "--env", f"XAUTHORITY={x_authority_container}"]
    else:
        x11_args = []

    # Configure which user the container will run as -- this is to avoid creating files as root.
    if not user:
        user_args = []
    elif user == 'self':
        user_args = ["--user", f"{getuid()}:{getgid()}"]
    else:
        user_args = ["--user", user]

    # Build up a command line including "docker run" and arguments for launching Phy inside the container.
    phy_dir = params_py.parent.absolute().as_posix()
    step_args = [
        "--data-root", phy_dir,
        "--params-py-pattern", params_py.name,
    ]
    docker_run_command = [
        "docker",
        "run",
    ] + docker_run_args + gpus + x11_args + user_args + [
        "--volume", f"{phy_dir}:{phy_dir}",
        "--workdir", phy_dir,
        docker_image,
        "conda_run", "python", "/opt/code/run_phy.py"
    ] + step_args

    logging.info(f"Running Phy with Docker command: {docker_run_command}.")

    # Invoke Docker and Phy using the command we just built up.
    process = subprocess.Popen(
        docker_run_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Read each line of ouptut from Phy as it comes, log it to the console and a log file.
    for line in process.stdout:
        logging.info(line.strip())

    # Check the exit code from Phy when the container exits.
    exit_code = process.wait()
    if exit_code == 0:
        logging.info(f"OK\n")
    else:
        logging.error(f"Completed with error, exit code {exit_code}")

    return exit_code


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = ArgumentParser(description="Run Phy in a Docker container for maual sorting curation.")

    parser.add_argument(
        "--docker-image", "-I",
        type=str,
        help="Which Docker image to use for running Phy. (default: %(default)s)",
        default="ghcr.io/geffenlab/geffenlab-phy-desktop:v0.0.6"
    )
    parser.add_argument(
        "--docker-run-args", "-D",
        type=str,
        nargs="*",
        help="Args to pass to 'docker run ...'. (default: %(default)s)",
        default=["--rm"]
    )
    parser.add_argument(
        "--gpu-device", "-G",
        type=str,
        help="Which gpu device to use with Docker: integer device index, string device GUID, or 'none' (default: %(default)s)",
        default=0
    )
    parser.add_argument("--x11",
        action=BooleanOptionalAction,
        help="Whether or not to configure an X11 display for the Docker container. (default: %(default)s)",
        default=True
    )
    parser.add_argument("--user",
        type=str,
        help="Specify a user:group to run as in the container, or 'self' to use the caller's uid:gid, omit to use the system or image default. (default: %(default)s)",
        default=None
    )
    parser.add_argument(
        "--data-root",
        type=str,
        help="Root folder with results from Kilosort/Phy/Bombcell. (default: %(default)s)",
        default="/vol/cortex/cd5/geffenlab/processed_data"
    )
    parser.add_argument(
        "--experimenter",
        type=str,
        help="Experimenter initials for the session to be processed. (default: %(default)s)",
        default="BH"
    )
    parser.add_argument(
        "--subject",
        type=str,
        help="Subject of the session to be processed. (default: %(default)s)",
        default="AS20-minimal3"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Date of the session to be processed DDMMYYYY. (default: %(default)s)",
        default="03112025"
    )
    parser.add_argument(
        "--params-py-pattern", "-p",
        type=str,
        help="Glob pattern to locate Phy params.py file(s) within DATA_ROOT/EXPERIMENTER/SUBJECT/DATE/ (default: %(default)s)",
        default="**/params.py"
    )

    cli_args = parser.parse_args(argv)

    # Write logs to the sessions processed output subdirectory.
    data_path = Path(cli_args.data_root, cli_args.experimenter, cli_args.subject, cli_args.date)
    execution_time = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%Z')
    script_log_path = Path(data_path, f"run_phy_{execution_time}.log")
    set_up_logging(script_log_path)

    logging.info(f"Using Docker image: {cli_args.docker_image}")
    logging.info(f"Using 'docker run' args: {cli_args.docker_run_args}")
    logging.info(f"Using GPU device: {cli_args.gpu_device}")
    logging.info(f"Configuring X11 display: {cli_args.x11}")
    logging.info(f"Running container as user and group: {cli_args.user}")
    logging.info(f"Looking for phy/ data in: {data_path}")
    logging.info(f"Looking for params.py files(s) matchign pattern: {cli_args.params_py_pattern}")

    try:
        params_py_matches = list(data_path.glob(cli_args.params_py_pattern))
        match_count = len(params_py_matches)
        params_py_matches.sort()
        logging.info(f"Found {match_count} params.py matches within {data_path}")
        if match_count < 1:
            raise ValueError(f"Found no params.py matching pattern {cli_args.params_py_pattern} within {data_path}")
        elif match_count == 1:
            params_py_path = params_py_matches[0]
        else:
            logging.info(f"Please choose one:")
            for index, params_py_match in enumerate(params_py_matches):
                logging.info(f"  {index}: {params_py_match.relative_to(data_path)}")
            params_py_index = int(input(f"Choose by number 0-{match_count - 1}: ").strip())
            params_py_path = params_py_matches[params_py_index]
        logging.info(f"Using params.py: {params_py_path}")

        main_exit_code = run_phy_in_docker(
            cli_args.docker_image,
            cli_args.docker_run_args,
            cli_args.gpu_device,
            cli_args.x11,
            cli_args.user,
            params_py_path
        )

    except:
        logging.error("Error running Phy.", exc_info=True)
        return -1

    return main_exit_code


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
