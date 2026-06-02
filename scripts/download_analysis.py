"""
This script is for downloading pipeline analysis results from cortex to your local machine.

It searches on cortex within the lab's analysis directory (/cdz/geffenlab/analysis/),
to find results for a given experimenter, subject, and date.
It copies the session results to a local directory, like ./pipeline-analysis/

For configuration options:

    conda activate geffen-pipelines
    python download_analysis.py --help

See also:

    docs/download-analysis.md
"""


import sys
from argparse import ArgumentParser
from typing import Optional, Sequence
import logging
from pathlib import Path
from datetime import datetime, date
from getpass import getpass

from fabric import Connection


def set_up_logging():
    """Enable console logging."""
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def run_main(
    local_path: Path,
    remote_host: str,
    analysis_path: Path,
    experimenter: str,
    subject_id: str,
    session_date: date,
    username: str,
    password: str
):
    """
    Search for pipeine results in {remote_host}:{analysis_path}/{experimenter}/{subject_id}/{session_date} and download to {local_path}.
    """
    # Use consistent date formatting like MMDDYYYY.
    date_string = session_date.strftime("%m%d%Y")

    logging.info(f"Connecting to remote host: {remote_host}.")
    with Connection(host=remote_host, user=username, connect_kwargs={"password": password}) as c:

        # Connect to the remote host, eg cortex.
        try:
            # The call to open() will log connection attempts, results.
            c.open()
        except Exception as e:
            logging.error(f"Connection error: {e.args}")
            return

        # List files and subdirectories in the session analysis directory.
        remote_analysis_path = Path(analysis_path, experimenter, subject_id, date_string)
        logging.info(f"Checking for remote analysis session directory {remote_analysis_path}:")
        c.run(f"ls {remote_analysis_path.as_posix()}")

        # Recursively find regular files within the analysis subdirectory.
        analysis_result = c.run(f"find {remote_analysis_path.as_posix()} -type f")

        # Download each file, preserving session subdirectory structure.
        logging.info(f"Downloading files to: {local_path}")
        analysis_files = analysis_result.stdout.strip().split('\n')
        for analysis_file in analysis_files:
            relative_file_path = Path(analysis_file).relative_to(remote_analysis_path)
            local_file_path = Path(local_path, "analysis", experimenter, subject_id, date_string, relative_file_path)
            local_file_path.parent.mkdir(exist_ok=True, parents=True)
            c.get(remote=analysis_file, local=local_file_path.as_posix())

    logging.info("OK.\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    set_up_logging()

    parser = ArgumentParser(description="Download the analysis/ subdir and selected processed_data/ subdirs for a session.")

    parser.add_argument(
        "--local-root", "-L",
        type=str,
        help="Local root directory to receive donwloads. (default: %(default)s)",
        default="./pipeline-analysis/"
    )
    parser.add_argument(
        "--remote-host", "-r",
        type=str,
        help="Remote host (eg cortex) to connect to. (default: %(default)s)",
        default="128.91.19.199"
    )
    parser.add_argument(
        "--user", "-u",
        type=str,
        help="Remote (eg cortex) username. (default: prompt for input)",
        default=None
    )
    parser.add_argument(
        "--analysis-root", "-A",
        type=str,
        help="Remote root directory containing lab analysis results. (default: %(default)s)",
        default="/cdz/geffenlab/analysis/"
    )
    parser.add_argument(
        "--experimenter", "-e",
        type=str,
        help="Experimenter initials for a session that was processed. (default: prompt for input)",
        default=None
    )
    parser.add_argument(
        "--subject", "-s",
        type=str,
        help="Subject id for a session that was processed. (default: prompt for input)",
        default=None
    )
    parser.add_argument(
        "--date", "-d",
        type=str,
        help="Date of a session that was processed: MMDDYYYY. (default: prompt for input)",
        default=None
    )

    cli_args = parser.parse_args(argv)

    # Prompt for missing input args as needed.
    local_path = Path(cli_args.local_root).expanduser().resolve()
    logging.info(f"Downloading files to local root: {local_path}")

    remote_host = cli_args.remote_host
    logging.info(f"Downloading files from remote host: {remote_host}")

    analysis_path = Path(cli_args.analysis_root)
    logging.info(f"Downloading files from remote analysis root: {analysis_path}")

    experimenter = cli_args.subject
    if experimenter is None:
        experimenter = input("Experimenter initials: ").strip()
    logging.info(f"Downloading files for experimenter: {experimenter}")

    subject = cli_args.subject
    if subject is None:
        subject = input("Subject ID: ").strip()
    logging.info(f"Downloading files for subject id: {subject}")

    session_dates_string = cli_args.date
    if session_dates_string is None:
        session_dates_string = input("Session date MMDDYYYY: ").strip()
    session_date = datetime.strptime(session_dates_string, "%m%d%Y").date()
    logging.info(f"Downloading files for session date: {session_dates_string} ({session_date})")

    username = cli_args.user
    if username is None:
        username = input("Remote username: ").strip()
    logging.info(f"Downloading files as remote user: {username}")

    # Password will not be printed.
    password = getpass(f"Password for remote user {username}: ")

    try:
        run_main(
            local_path,
            remote_host,
            analysis_path,
            experimenter,
            subject,
            session_date,
            username,
            password
        )
    except:
        logging.error("Error downloading analysis files.", exc_info=True)
        return -1


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
