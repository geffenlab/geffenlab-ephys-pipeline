"""
This script is for uploading raw data from a rig machine to cortex.

It searches a local directories for behavior and/or ecephys files for a given experimenter, subject, and date.
It uses several glob patterns to match files and directories of interest.
It can apply experimenter-, session-, and date-specific placeholders to the glob patterns.
It copies files found to cortex, using a standard directory structure expected by pipelines.
It sets file permissions on the uploaded files, so only geffenlab members can read and write.

For configuration options:

    conda activate geffen-pipelines
    python upload_data.py --help

See also:

    docs/upload-data.md
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


def walk_flat(
    path: Path
) -> list[Path]:
    """Find regular files within the given path, recursively."""
    flat_list = []
    for parent, dirs, files in path.walk():
        for file in files:
            flat_list.append(Path(parent, file))
    return flat_list


def apply_placeholders(
    original: str,
    experimenter: str,
    subject_id: str,
    session_date: date
) -> str:
    """Fill in session placeholders <EXPERIMENTER> <SUBJECT>, <YY>, <YYYY>, <MM>, and <DD>."""
    yy = session_date.strftime("%y")
    yyyy = session_date.strftime("%Y")
    mm = session_date.strftime("%m")
    dd = session_date.strftime("%d")
    applied = (
        original
        .replace('<EXPERIMENTER>', experimenter)
        .replace("<SUBJECT>", subject_id)
        .replace("<YYYY>", yyyy)
        .replace("<YY>", yy)
        .replace("<MM>", mm)
        .replace("<DD>", dd)
    )
    return applied


def run_main(
    behavior_path: Path,
    behavior_txt_pattern_original: str,
    behavior_mat_pattern_original: str,
    behavior_hdf5_pattern_original: str,
    ephys_path: Path,
    spikeglx_run_patterns_original: list[str],
    oebin_pattern_original: str,
    remote_host: str,
    raw_data_path: Path,
    experimenter: str,
    subject: str,
    session_dates: list[date],
    qualifier: str,
    username: str,
    group_permissions: str,
    other_permissions: str,
):
    """
    Search the given behavior_path and ephys_path for files that match patterns of interest, upload them to cortex.
    """

    # Collect files to upload as a list of (source_root, source_relative, destination_relative, session_mmddyyyy)
    to_upload = []

    # Look for one or more session dates for the same experimenter and subject.
    for session_date in session_dates:
        session_mmddyyyy = session_date.strftime("%m%d%Y")
        logging.info(f"Looking for session date: {session_date} AKA {session_mmddyyyy}")

        # Resolve session-specific placeholders in glob patterns.
        behavior_txt_pattern = apply_placeholders(behavior_txt_pattern_original, experimenter, subject, session_date)
        behavior_mat_pattern = apply_placeholders(behavior_mat_pattern_original, experimenter, subject, session_date)
        behavior_hdf5_pattern = apply_placeholders(behavior_hdf5_pattern_original, experimenter, subject, session_date)
        spikeglx_run_patterns = [
            apply_placeholders(pattern, experimenter, subject, session_date)
            for pattern in spikeglx_run_patterns_original
        ]
        openephys_oebin_pattern = apply_placeholders(oebin_pattern_original, experimenter, subject, session_date)

        # Locate behavior .mat and .txt within behavior_path.
        logging.info(f"Searching local behavior_root for .txt like: {behavior_txt_pattern}")
        for txt_match in behavior_path.glob(behavior_txt_pattern):
            txt_relative = txt_match.relative_to(behavior_path)
            logging.info(f"  {txt_relative}")
            destination_relative = Path(experimenter, subject, session_mmddyyyy, "behavior", txt_match.name)
            to_upload.append((behavior_path, txt_relative, destination_relative, session_mmddyyyy))

        logging.info(f"Searching local behavior_root for .mat like: {behavior_mat_pattern}")
        for mat_match in behavior_path.glob(behavior_mat_pattern):
            mat_relative = mat_match.relative_to(behavior_path)
            logging.info(f"  {mat_relative}")
            destination_relative = Path(experimenter, subject, session_mmddyyyy, "behavior", mat_match.name)
            to_upload.append((behavior_path, mat_relative, destination_relative, session_mmddyyyy))

        # Locate behavior .hdf5 within behavior_path.
        logging.info(f"Searching local behavior_root for .hdf5 like: {behavior_hdf5_pattern}")
        for hdf5_match in behavior_path.glob(behavior_hdf5_pattern):
            hdf5_relative = hdf5_match.relative_to(behavior_path)
            logging.info(f"  {hdf5_relative}")
            destination_relative = Path(experimenter, subject, session_mmddyyyy, "behavior", hdf5_match.name)
            to_upload.append((behavior_path, hdf5_relative, destination_relative, session_mmddyyyy))

        # Locate spikeglx meta files as representatives of spikeglx run dirs.
        for spikeglx_run_pattern in spikeglx_run_patterns:
            logging.info(f"Searching local ephys_root for SpikeGlx files like: {spikeglx_run_pattern}")
            spikeglx_matches = list(ephys_path.glob(spikeglx_run_pattern))
            logging.info(f"Found {len(spikeglx_matches)} SpikeGlx matches: {spikeglx_matches}")
            for spikeglx_match in spikeglx_matches:
                run_dir = spikeglx_match.parent
                logging.info(f"Found spikeglx run dir: {run_dir}")
                for spikglx_file in walk_flat(run_dir):
                    spikglx_relative = spikglx_file.relative_to(ephys_path)
                    logging.info(f"  {spikglx_relative}")
                    destination_relative = Path(
                        experimenter,
                        subject,
                        session_mmddyyyy,
                        "ecephys",
                        spikglx_file.relative_to(run_dir.parent)
                    )
                    to_upload.append((ephys_path, spikglx_relative, destination_relative, session_mmddyyyy))

        # Locate openephys oebin files as representatives of recording dirs.
        logging.info(f"Searching local ephys_root for .oebin like: {openephys_oebin_pattern}")
        oebins = list(ephys_path.glob(openephys_oebin_pattern))
        logging.info(f"Found {len(oebins)} .oebin matches: {oebins}")

        # Walk up several parents from an .oebin to find the run dir.
        #   date/record_node/experiment/recording/structure.oebin
        # Only keep unique run dirs (Open Ephys can put multiple experiment and recording subdirs in one run dir)
        run_dirs = {oebin.parent.parent.parent.parent for oebin in oebins}
        logging.info(f"Found {len(run_dirs)} run dirs: {run_dirs}")
        for run_dir in run_dirs:
            logging.info(f"Found openephys run dir: {run_dir}")
            for openephys_file in walk_flat(run_dir):
                openephys_relative = openephys_file.relative_to(ephys_path)
                logging.info(f"  {openephys_relative}")
                destination_relative = Path(
                    experimenter,
                    subject,
                    session_mmddyyyy,
                    "ecephys",
                    openephys_file.relative_to(run_dir.parent)
                )
                to_upload.append((ephys_path, openephys_relative, destination_relative, session_mmddyyyy))

    # Optionally filter files that were found, using a given qualifier to match file names.
    if qualifier:
        logging.info(f"Keeping only files that match qualifier: {qualifier}")
        to_upload = [item for item in to_upload if qualifier in item[1].as_posix()]

    if not to_upload:
        logging.warning("No files to upload.")
        return

    # List files before uploading.
    logging.info(f"Planning to create {len(to_upload)} files in remote dir {raw_data_path}:")
    for source_root, source_relative, destination_relative, session_mmddyyyy in to_upload:
        logging.info(f"  {destination_relative}")

    # Confirm before uploading.
    go_ahead = input(f"Do you want to upload these {len(to_upload)} files?  Type 'yes' to proceed: ").strip()
    if go_ahead != "yes":
        logging.warning("Stopping without uploading files.")
        return

    logging.warning("Proceeding to upload files.")

    # Password will not be printed.
    password = getpass(f"Password for remote user {username}: ")

    logging.info(f"Connecting to remote host: {remote_host}.")
    with Connection(host=remote_host, user=username, connect_kwargs={"password": password}) as c:
        try:
            # Call to open() will log connection attempts, results.
            c.open()

            # Upload each individual file.
            logging.info(f"Uploading to {raw_data_path}:")
            for source_root, source_relative, destination_relative, session_mmddyyyy in to_upload:
                source = Path(source_root, source_relative)
                destination = Path(raw_data_path, destination_relative)
                logging.info(f"  {destination_relative}")
                c.run(f"mkdir -p {destination.parent.as_posix()}")
                c.put(source.as_posix(), destination.as_posix())

            # Set directory and file permissions for each unique session date.
            session_paths = {
                Path(raw_data_path, experimenter, subject, session_mmddyyyy)
                for _, _, _, session_mmddyyyy in to_upload
            }
            for session_path in session_paths:
                logging.info(f"Setting 'group' and 'other' permissions for session dir {session_path}:")
                c.run(f"chmod -R g{group_permissions} {session_path.as_posix()}")
                c.run(f"chmod -R o{other_permissions} {session_path.as_posix()}")

        except Exception as e:
            logging.warning(f"Upload error: {e.args}")

    logging.info("OK.\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    set_up_logging()

    parser = ArgumentParser(description="Upload raw session data from the local machine to cortex.")

    parser.add_argument(
        "--behavior-root", "-b",
        type=str,
        help="Local root directory to search for behavior files. (default: %(default)s)",
        default="."
    )
    parser.add_argument(
        "--behavior-txt-pattern", "-T",
        type=str,
        help="Glob pattern to match behavior .txt files within BEHAVIOR_ROOT. May include placeholders <EXPERIMENTER>, <SUBJECT>, <YYYY>, <YY>, <MM>, <DD> (default: %(default)s)",
        default="<SUBJECT>/**/*_<MM><DD><YY>_*.txt"
    )
    parser.add_argument(
        "--behavior-mat-pattern", "-M",
        type=str,
        help="Glob pattern to match behavior .mat files within BEHAVIOR_ROOT. May include placeholders <EXPERIMENTER>, <SUBJECT>, <YYYY>, <YY>, <MM>, <DD> (default: %(default)s)",
        default="<SUBJECT>/**/*_<MM><DD><YY>_*.mat"
    )
    parser.add_argument(
        "--behavior-hdf5-pattern", "-H",
        type=str,
        help="Glob pattern to match behavior .hdf5 files within BEHAVIOR_ROOT. May include placeholders <EXPERIMENTER>, <SUBJECT>, <YYYY>, <YY>, <MM>, <DD> (default: %(default)s)",
        default="<SUBJECT>/**/*_<YYYY><MM><DD>_*.hdf5"
    )
    parser.add_argument(
        "--ephys-root", "-E",
        type=str,
        help="Local root directory to search for a SpikeGLX run directory. (default: %(default)s)",
        default="."
    )
    parser.add_argument(
        "--spikeglx-run-patterns", "-S",
        type=str,
        nargs="+",
        help="Glob pattern(s) to match files in SpikeGLX run dirs ('nidq.meta', 'obx.bin', etc) within EPHYS_ROOT. May include placeholders <EXPERIMENTER>, <SUBJECT>, <YYYY>, <YY>, <MM>, <DD> (default: %(default)s)",
        default=[
            "<SUBJECT>/**/*_<MM><DD><YYYY>_*.nidq.meta",
            "<SUBJECT>/**/*_<MM><DD><YYYY>_*.obx.bin",
            "<SUBJECT>/**/*_<YY><MM><DD>_*.nidq.meta",
            "<SUBJECT>/**/*_<YY><MM><DD>_*.obx.bin"
        ]
    )
    parser.add_argument(
        "--openephys-oebin-pattern", "-O",
        type=str,
        help="Glob pattern to match OpenEphys structure.oebin files within EPHYS_ROOT. May include placeholders <EXPERIMENTER>, <SUBJECT>, <YYYY>, <YY>, <MM>, <DD> (default: %(default)s)",
        default="<SUBJECT>/**/<YYYY>-<MM>-<DD>_*/*/*/*/structure.oebin"
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
        "--raw-data-root", "-R",
        type=str,
        help="Remote root directory containing lab raw data. (default: %(default)s)",
        default="/cdz/geffenlab/raw_data/"
    )
    parser.add_argument(
        "--experimenter", "-e",
        type=str,
        help="Experimenter initials to group related data. (default: prompt for input)",
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
        nargs="+",
        help="Date of a session that was processed: MMDDYYYY.  Multiple dates may be separated by spaces. (default: prompt for input)",
        default=[]
    )
    parser.add_argument(
        "--qualifier", "-q",
        type=str,
        help="Additional text that must match uploaded file names, for example 'training', 'test', or 'ap.bin'. (default: None, upload all files)",
        default=None
    )
    parser.add_argument(
        "--group-permissions", "-g",
        type=str,
        help="Permission to set on uploaded dirs and files, for users in the same group. (default: %(default)s)",
        default="+rwx"
    )
    parser.add_argument(
        "--other-permissions", "-o",
        type=str,
        help="Permission to set on uploaded dirs and files, for other users (the universe). (default: %(default)s)",
        default="-rwx"
    )

    cli_args = parser.parse_args(argv)

    # Prompt for missing input args as needed.
    behavior_path = Path(cli_args.behavior_root).expanduser().resolve()
    logging.info(f"Uploading behavior files from: {behavior_path}")

    behavior_txt_pattern = cli_args.behavior_txt_pattern
    logging.info(f"Using behavior .txt pattern: {behavior_txt_pattern}")

    behavior_mat_pattern = cli_args.behavior_mat_pattern
    logging.info(f"Using behavior .mat pattern: {behavior_mat_pattern}")

    behavior_hdf5_pattern = cli_args.behavior_hdf5_pattern
    logging.info(f"Using behavior .hdf5 pattern: {behavior_hdf5_pattern}")

    ephys_path = Path(cli_args.ephys_root).expanduser().resolve()
    logging.info(f"Uploading ephys files from: {ephys_path}")

    spikeglx_run_patterns = cli_args.spikeglx_run_patterns
    logging.info(f"Using SpikeGLX matching pattern(s): {spikeglx_run_patterns}")

    openephys_oebin_pattern = cli_args.openephys_oebin_pattern
    logging.info(f"Using Open Ephys .oebin matching pattern: {openephys_oebin_pattern}")

    remote_host = cli_args.remote_host
    logging.info(f"Uploading files to remote host: {remote_host}")

    raw_data_path = Path(cli_args.raw_data_root)
    logging.info(f"Uploading files to remote raw data root: {raw_data_path}")

    experimenter = cli_args.experimenter
    if experimenter is None:
        experimenter = input("Experimenter initials: ").strip()
    logging.info(f"Uploading files for experimenter: {experimenter}")

    subject = cli_args.subject
    if subject is None:
        subject = input("Subject ID: ").strip()
    logging.info(f"Uploading files for subject id: {subject}")

    date_strings = cli_args.date
    if not date_strings:
        date_strings = input("Session date MMDDYYYY (multiple dates may be separated by spaces): ").strip().split(' ')
    session_dates = [datetime.strptime(s, "%m%d%Y").date() for s in date_strings]
    session_dates_formated = [str(d) for d in session_dates]
    logging.info(f"Uploading files for session date(s): {session_dates_formated}")

    qualifier = cli_args.qualifier
    if qualifier is None:
        qualifier = input("Qualifier like 'training','ap.bin', 'recording1', etc.  Leave blank to upload all: ").strip()
    if qualifier:
        logging.info(f"Uploading files matching qualifier: {qualifier}.")
    else:
        logging.info(f"Uploading all files.")

    username = cli_args.user
    if username is None:
        username = input("Remote username: ").strip()
    logging.info(f"Uploading files as remote user: {username}")

    try:
        run_main(
            behavior_path,
            behavior_txt_pattern,
            behavior_mat_pattern,
            behavior_hdf5_pattern,
            ephys_path,
            spikeglx_run_patterns,
            openephys_oebin_pattern,
            remote_host,
            raw_data_path,
            experimenter,
            subject,
            session_dates,
            qualifier,
            username,
            cli_args.group_permissions,
            cli_args.other_permissions,
        )
    except:
        logging.error("Error uploading files.", exc_info=True)
        return -1


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
