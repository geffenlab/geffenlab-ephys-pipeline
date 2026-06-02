"""
This script is for archiving raw session data from cortex to the lab's S3 bucket.

It searches on cortex within the lab's raw_data directory (/cdz/geffenlab/raw_data/),
to find data for a given experimenter, subject, and date.
It copies the session data to S3, using the lab's standard directory layout.
It adds tags to uploaded data including the year and a given project_name.
It looks for UPenn/AWS service account credentials that are already installed on cortex.

For configuration options:

    conda activate geffen-pipelines
    python archive_data.py --help

See also:

    docs/archive-data.md
"""


import sys
from os import environ
from argparse import ArgumentParser, BooleanOptionalAction
from typing import Optional, Sequence
import logging
from pathlib import Path
from datetime import datetime, date
from urllib.parse import urlencode

import boto3


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


def archive(
    s3_client,
    bucket_name: str,
    bucket_path_prefix: str,
    storage_class: str,
    tags: dict[str, str],
    local_root: Path,
    local_relative: Path,
    dry_run: bool
):
    """
    Archive the file at the given {local_root}/{local_relative}, to S3 at {bucket_name}/{bucket_path_prefix}/{local_relative}.

    Add the given tags to the file in S3.
    """
    local_path = Path(local_root, local_relative)
    s3_key = f"{bucket_path_prefix}/{local_relative}"
    s3_url = f"s3://{bucket_name}/{s3_key}"

    # AWS S3 supports two kinds of user-supplied key-value annotations for storage objects: "metadata" and "tags":
    #   https://stackoverflow.com/questions/42126348/difference-between-object-tags-and-object-metadata
    # The "tags" seem to support lifecycle automation, which might be what we want.
    # The "metadta" ride with the objcets themselves, which might be what we want.
    # Maybe we don't need to choose, and we can just supply the same annotations to both.
    encoded_tags = urlencode(tags)

    if dry_run:
        logging.info(f"Dry run archiving {s3_url}")
    else:
        logging.info(f"Archiving {s3_url}")
        s3_client.upload_file(
            Filename=local_path,
            Bucket=bucket_name,
            Key=s3_key,
            ExtraArgs={
                "StorageClass": storage_class,
                "Metadata": tags,
                "Tagging": encoded_tags
            }
        )


def run_main(
    raw_data_path: Path,
    experimenter: str,
    subject: str,
    session_dates: list[date],
    project_name: str,
    qualifier: str,
    bucket: str,
    bucket_path_prefix: str,
    storage_class: str,
    delete: bool,
    dry_run: bool
):
    """
    Search the given {raw_data_path}/{experimenter}/{subject}/{session_date(s)} for files to archive, and optionally delete.
    """
    # Collect files to archive, relative to the raw_data_path.
    to_archive = []

    # Look for files by experimenter and subject.
    subject_path = session_path = Path(raw_data_path, experimenter, subject)

    # Look for one or more session dates for the same experimenter and subject.
    for session_date in session_dates:
        session_mmddyyyy = session_date.strftime("%m%d%Y")
        logging.info(f"Looking for session date: {session_date} AKA {session_mmddyyyy}")

        # Add tags to the uploaded data, especially the year and the given project_name.
        tags = {
            "experimenter": experimenter,
            "subject": subject,
            "year": session_date.strftime("%Y"),
            "month": session_date.strftime("%m"),
            "day": session_date.strftime("%d"),
            "project_name": project_name
        }
        logging.info(f"Using these tags for this date: {tags}")

        # Locate multiple files for this session.
        session_path = Path(subject_path, session_mmddyyyy)
        session_files = walk_flat(session_path)
        logging.info(f"Found {len(session_files)} files within: {session_path}")
        for file in session_files:
            raw_relative = file.relative_to(raw_data_path)
            to_archive.append((raw_relative, tags))

    # Optionally filter files that were found, using a given qualifier to match file names.
    if qualifier:
        logging.info(f"Keeping only files that match qualifier: {qualifier}")
        to_archive = [
            (raw_relative, tags)
            for (raw_relative, tags) in to_archive
            if qualifier in raw_relative.as_posix()
        ]

    if not to_archive:
        logging.warning("No files to archive.")
        return

    # List files before archiving.
    logging.info(f"Planning to archive {len(to_archive)} files within {subject_path}:")
    for (raw_relative, tags) in to_archive:
        full_path = Path(raw_data_path, raw_relative)
        subject_relative = full_path.relative_to(subject_path)
        logging.info(f"  {subject_relative}")

    # Confirm before archiving.
    go_ahead = input(f"Do you want to archive these {len(to_archive)} files?  Type 'yes' to proceed: ").strip()
    if go_ahead != "yes":
        logging.warning("Stopping without to_archive files.")
        return

    logging.warning("Proceeding to archive files.")

    # The boto3 client should find env vars we set earlier: AWS_SHARED_CREDENTIALS_FILE and AWS_CONFIG_FILE.
    # These credentials should already be stored on cortex.
    # See also: docs/cortex-user-setup.md, "AWS account setup"
    s3_client = boto3.client("s3")
    for (raw_relative, tags) in to_archive:
        archive(s3_client, bucket, bucket_path_prefix, storage_class, tags, raw_data_path, raw_relative, dry_run)

    logging.info(f"Archived {len(to_archive)} files")

    # Only delete files if the user explicitly asked to!
    if delete:
        logging.warning("Proceeding to delete local files.")
        for (raw_relative, tags) in to_archive:
            full_path = Path(raw_data_path, raw_relative)
            if dry_run:
                logging.info(f"Dry run deleting {raw_relative}")
            else:
                logging.info(f"Deleting {raw_relative}")
                full_path.unlink()


def main(argv: Optional[Sequence[str]] = None) -> int:
    set_up_logging()

    parser = ArgumentParser(description="Archive raw session data to an S3 bucket, optionally delete from cortex.")
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
        "--project-name", "-n",
        type=str,
        help="Value to use for stored object tag 'project_name'. (default: prompt for input)",
        default=None
    )
    parser.add_argument(
        "--bucket", "-b",
        type=str,
        help="The S3 bucket that holds archived data. (default: %(default)s)",
        default="upenn-research.geffen-lab-01.us-east-1"
    )
    parser.add_argument(
        "--bucket-path-prefix", "-p",
        type=str,
        help="Which key prefix (subfolder) to use within the S3 BUCKET. (default: %(default)s)",
        default="cortex/raw_data"
    )
    parser.add_argument(
        "--storage-class", "-S",
        type=str,
        help="Which S3 storage class to use for archived files. (default: %(default)s)",
        default="DEEP_ARCHIVE"
    )
    parser.add_argument(
        "--aws-shared-credentials-file", "-C",
        type=str,
        help="Location of AWS credentials, eg from 'aws configure'. (default: %(default)s)",
        default="/cdz/geffenlab/.aws/credentials"
    )
    parser.add_argument(
        "--aws-config-file", "-c",
        type=str,
        help="Location of AWS config, eg from 'aws configure'. (default: %(default)s)",
        default="/cdz/geffenlab/.aws/config"
    )
    parser.add_argument(
        "--delete",
        action=BooleanOptionalAction,
        help="Whether to delete local files after archiving. (default: %(default)s)",
        default=False
    )
    parser.add_argument(
        "--dry-run",
        action=BooleanOptionalAction,
        help="Whether to search for files and log info, but skip actual archiving or deleting. (default: %(default)s)",
        default=False
    )

    cli_args = parser.parse_args(argv)

    raw_data_path = Path(cli_args.raw_data_root)
    logging.info(f"Archiving files within raw data root: {raw_data_path}")

    experimenter = cli_args.experimenter
    if experimenter is None:
        experimenter = input("Experimenter initials: ").strip()
    logging.info(f"Archiving files for experimenter: {experimenter}")

    subject = cli_args.subject
    if subject is None:
        subject = input("Subject ID: ").strip()
    logging.info(f"Archiving files for subject id: {subject}")

    session_dates_strings = cli_args.date
    if not session_dates_strings:
        session_dates_raw = input("Session date MMDDYYYY (multiple dates may be separated by spaces): ")
        session_dates_strings = session_dates_raw.strip().split(' ')
    session_dates = [datetime.strptime(s, "%m%d%Y").date() for s in session_dates_strings]
    session_dates_formated = [str(d) for d in session_dates]
    logging.info(f"Archiving files for session date(s): {session_dates_formated}")

    qualifier = cli_args.qualifier
    if qualifier is None:
        qualifier = input("Qualifier like 'training','ap.bin', 'recording1', etc.  Leave blank to upload all: ").strip()
    if qualifier:
        logging.info(f"Archiving files matching qualifier: {qualifier}.")
    else:
        logging.info(f"Archiving all files")

    project_name = cli_args.project_name
    if project_name is None:
        project_name = input("Project name (for tag 'project_name' on stored objects): ").strip()
    logging.info(f"Adding stored object tag project_name={project_name}.")

    logging.info(f"Using S3 bucket: {cli_args.bucket}")
    logging.info(f"Using S3 bucket path prefix: {cli_args.bucket_path_prefix}")
    logging.info(f"Using S3 storage class: {cli_args.storage_class}")

    aws_shared_credentials_path = Path(cli_args.aws_shared_credentials_file).expanduser().resolve()
    logging.info(f"Using AWS credentials from: {aws_shared_credentials_path}")
    environ['AWS_SHARED_CREDENTIALS_FILE'] = aws_shared_credentials_path.as_posix()

    aws_config_path = Path(cli_args.aws_config_file).expanduser().resolve()
    logging.info(f"Using AWS config from: {aws_config_path}")
    environ['AWS_CONFIG_FILE'] = aws_config_path.as_posix()

    if cli_args.delete:
        logging.warning(f"Deleting local files after archiving.")
    else:
        logging.info(f"Keeping local files after archiving (pass flag --delete to delete them).")

    if cli_args.dry_run:
        logging.warning(f"This is only a dry run: no actual archiving or deleting.")

    try:
        run_main(
            raw_data_path,
            experimenter,
            subject,
            session_dates,
            project_name,
            qualifier,
            cli_args.bucket,
            cli_args.bucket_path_prefix,
            cli_args.storage_class,
            cli_args.delete,
            cli_args.dry_run
        )
    except:
        logging.error("Error archiving files.", exc_info=True)
        return -1


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
