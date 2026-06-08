# Cortex Upload Data

This doc should help you upload raw session data from a local lab machine to cortex.

First, you'll need to do the one-time [cortex user setup](./cortex-user-setup.md) for your cortex user account and local lab machine.

## Rig data

To start with, here's an example of rig data where behavioral data files are located in the same folder as a SpikeGLX run directory.

![Windows Explorer view of a rig-data/ directory containing behavioral and neural data](./rig-data.png)

## Upload data to cortex

This repo has a Python script [upload_data.py](../scripts/upload_data.py) that to help find rig data like the example above and upload to cortex using standard directory layout and file permissions.  Internally this uses `ssh` to connect to cortex using your own user credentials.

Run this script from the WSL environment of your local lab machine:

```
# Use our conda environment with Python, etc.
conda activate geffen-pipelines

# Go to the directory that contains your data, for example:
cd /mnt/c/Users/labuser/Desktop/rig-data

# Run the data upload Python script.
python ~/geffenlab-ephys-pipeline/scripts/upload_data.py
```

This will prompt you for the experimenter initials, subject id, and session date(s) that you want to upload.  You can optionally specify a qualifier to further narrow down which files are uploaded.  For example:

```
$ python ~/geffenlab-ephys-pipeline/scripts/upload_data.py

2026-05-12 13:48:03,811 [INFO] Uploading behavior files from: /mnt/c/Users/labuser/Desktop/rig-data
2026-05-12 13:48:03,811 [INFO] Using behavior .txt pattern: <SUBJECT>/**/*_<MM><DD><YY>_*.txt
2026-05-12 13:48:03,811 [INFO] Using behavior .mat pattern: <SUBJECT>/**/*_<MM><DD><YY>_*.mat
2026-05-12 13:48:03,811 [INFO] Using behavior .hdf5 pattern: <SUBJECT>/**/*_<YYYY><MM><DD>_*.hdf5
2026-05-12 13:48:03,811 [INFO] Uploading ephys files from: /mnt/c/Users/labuser/Desktop/rig-data
2026-05-12 13:48:03,812 [INFO] Using SpikeGLX matching pattern(s): ['<SUBJECT>/**/*_<MM><DD><YYYY>_*.nidq.meta', '<SUBJECT>/**/*_<MM><DD><YYYY>_*.obx.bin', '<SUBJECT>/**/*_<YY><MM><DD>_*.nidq.meta', '<SUBJECT>/**/*_<YY><MM><DD>_*.obx.bin']
2026-05-12 13:48:03,812 [INFO] Using Open Ephys .oebin matching pattern: <SUBJECT>/**/<YYYY>-<MM>-<DD>_*/*/*/*/structure.oebin
2026-05-12 13:48:03,812 [INFO] Uploading files to remote host: 128.91.19.199
2026-05-12 13:48:03,812 [INFO] Uploading files to remote raw data root: /cdz/geffenlab/raw_data
Experimenter initials: BH
2026-05-12 13:48:05,943 [INFO] Uploading files for experimenter: BH
Subject ID: AS20-demo
2026-05-12 13:48:11,048 [INFO] Uploading files for subject id: AS20-demo
Session date MMDDYYYY (multiple dates may be separated by spaces): 03112025
2026-05-12 13:48:14,412 [INFO] Uploading files for session date(s): ['2025-03-11']
Qualifier like 'training','ap.bin', 'recording1', etc.  Leave blank to upload all:
2026-05-12 13:48:15,544 [INFO] Uploading all files.
Remote username: ben
```

Based on the subject id, session date(s), and optional qualifier, the script will search local directories for behavior and ecephys files.  It will use [glob](https://docs.python.org/3/library/glob.html) patterns to select specific files of interest.  The defaults are intended to match:
 - behavior `.mat`, `.txt` and/or `.hdf5` files
 - SpikeGlx `nidq.meta` or `obx.bin` files, and their containing run directories
 - OpenEphys `.oebin` files, and their containing session directories

These patterns may match multiple behavior and ecephys sessions, for the same experimenter, subject, and date.
The script will upload data for all matching sessions.

In this example there was just one session with behavioral data as well as neural data for one probe.

```
2026-05-12 13:48:17,200 [INFO] Uploading files as remote user: ben
2026-05-12 13:48:17,200 [INFO] Looking for session date: 2025-03-11 AKA 03112025
2026-05-12 13:48:17,201 [INFO] Searching local behavior_root for .txt like: AS20-demo/**/*_031125_*.txt
2026-05-12 13:48:17,212 [INFO]   AS20-demo/AS20_031125_trainingSingle6Tone2024_0_39.txt
2026-05-12 13:48:17,275 [INFO] Searching local behavior_root for .mat like: AS20-demo/**/*_031125_*.mat
2026-05-12 13:48:17,282 [INFO]   AS20-demo/AS20_031125_trainingSingle6Tone2024_0_39.mat
2026-05-12 13:48:17,296 [INFO] Searching local behavior_root for .hdf5 like: AS20-demo/**/*_20250311_*.hdf5
2026-05-12 13:48:17,306 [INFO] Searching local ephys_root for SpikeGlx files like: AS20-demo/**/*_03112025_*.nidq.meta
2026-05-12 13:48:17,313 [INFO] Found 1 SpikeGlx matches: [PosixPath('/mnt/c/Users/labuser/Desktop/rig-data/AS20-demo/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.meta')]
2026-05-12 13:48:17,314 [INFO] Found spikeglx run dir: /mnt/c/Users/labuser/Desktop/rig-data/AS20-demo/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0
2026-05-12 13:48:17,317 [INFO]   AS20-demo/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.bin
2026-05-12 13:48:17,317 [INFO]   AS20-demo/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.meta
2026-05-12 13:48:17,317 [INFO]   AS20-demo/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.bin
2026-05-12 13:48:17,317 [INFO]   AS20-demo/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.meta
2026-05-12 13:48:17,317 [INFO] Searching local ephys_root for SpikeGlx files like: AS20-demo/**/*_03112025_*.obx.bin
2026-05-12 13:48:17,326 [INFO] Found 0 SpikeGlx matches: []
2026-05-12 13:48:17,326 [INFO] Searching local ephys_root for SpikeGlx files like: AS20-demo/**/*_250311_*.nidq.meta
2026-05-12 13:48:17,335 [INFO] Found 0 SpikeGlx matches: []
2026-05-12 13:48:17,335 [INFO] Searching local ephys_root for SpikeGlx files like: AS20-demo/**/*_250311_*.obx.bin
2026-05-12 13:48:17,344 [INFO] Found 0 SpikeGlx matches: []
2026-05-12 13:48:17,344 [INFO] Searching local ephys_root for .oebin like: AS20-demo/**/2025-03-11_*/*/*/*/structure.oebin
2026-05-12 13:48:17,353 [INFO] Found 0 .oebin matches: []
2026-05-12 13:48:17,353 [INFO] Found 0 run dirs: set()
```

From all the files found, the script can use the optional qualifier to further restrict which files will be uploaded.  When the qualifier is provided, only files that contain the qualifier in their name will be uploaded.  For example, the qualifier "training" could be used to select "training" files but ignore "testing" files.

Before uploading, the script will show which files it plans to create on cortex and prompt for your confirmation.

```
2026-05-12 13:48:17,353 [INFO] Planning to create 6 files in remote dir /cdz/geffenlab/raw_data:
2026-05-12 13:48:17,353 [INFO]   BH/AS20-demo/03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.txt
2026-05-12 13:48:17,353 [INFO]   BH/AS20-demo/03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.mat
2026-05-12 13:48:17,353 [INFO]   BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.bin
2026-05-12 13:48:17,353 [INFO]   BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.meta
2026-05-12 13:48:17,353 [INFO]   BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.bin
2026-05-12 13:48:17,353 [INFO]   BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.meta
Do you want to upload these 6 files?  Type 'yes' to proceed: yes
```

You must type `yes` to proceed.  Otherwise the script will exit before uploading.
If you do type `yes` the script will prompt for your cortex user password, then upload each file to cortex:

```
2026-05-12 13:48:47,109 [WARNING] Proceeding to upload files.
Password for remote user ben:
2026-05-12 13:48:52,096 [INFO] Connecting to remote host: 128.91.19.199.
2026-05-12 13:49:02,065 [INFO] Connected (version 2.0, client OpenSSH_8.9p1)
2026-05-12 13:49:02,261 [INFO] Authentication (password) successful!
2026-05-12 13:49:02,261 [INFO] Uploading to /cdz/geffenlab/raw_data:
2026-05-12 13:49:02,261 [INFO]   BH/AS20-demo/03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.txt
2026-05-12 13:49:09,998 [INFO] [chan 1] Opened sftp connection (server version 3)
2026-05-12 13:49:10,018 [INFO]   BH/AS20-demo/03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.mat
2026-05-12 13:49:10,084 [INFO]   BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.bin
2026-05-12 13:49:30,260 [INFO]   BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.meta
2026-05-12 13:49:30,332 [INFO]   BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.bin
2026-05-12 13:49:52,320 [INFO]   BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.meta
2026-05-12 13:49:52,402 [INFO] Setting 'group' and 'other' permissions for session dir /cdz/geffenlab/raw_data/BH/AS20-demo/03112025:
2026-05-12 13:49:52,472 [INFO] [chan 1] sftp session closed.
2026-05-12 13:49:52,472 [INFO] OK.
```

## Results overview

When the script reports `OK`, then all the matching raw data files should be uploaded to cortex.

The uploaded data will use a standard directory layout based on the experimenter, subject, date, and data modality (`behavior` or `ecephys`):

![Ubuntu Files view of a raw_data/ directory containing behavioral and neural data](./cortex-data.png)


The uploaded data will also have standard permissions set, allowing read and write access, only to members of the `geffenlab` user group on cortex. 


## Options

The example above used several default options like the cortex host address, the local directories to search for behavior and spikeglx files, and the lab's assigned data directory on cortex.
All of these can be modified from the command line as needed.

You can also specify many values like `--experimenter`, `--subject`, `--date`, and `--qualifier` on the command line instead of waiting for the script to prompt you interactively.  The only argument you can not specify on the command line is your cortex user password -- this is to prevent your password from being saved into your terminal command history.

For details of command line options please see:

```
python ~/geffenlab-ephys-pipeline/scripts/upload_data.py --help
```

## Uploading multiple dates at once

For the `--date` command line option, or when prompted interactively for session dates, you can provide one or more session dates separated by spaces for the script to search and upload.

For example with command line args:

```
python ~/geffenlab-ephys-pipeline/scripts/upload_data.py --date 03112025 03122025 03132025
```

Or with the interactive prompt:

```
Session date MMDDYYYY (multiple dates may be separated by spaces): 03112025 03122025 03132025
```

## Pattern matching for finding local files to upload

The script uses pattern matching to locate files to upload.  By default it will look for behavior files that end with `.txt` and `.mat`.  It will look for SpikeGlx run directories that contain files ending like `.nidq.meta` or `.obx.bin`, and with dates formatted like `MMDDYYYY` or `YYMMDD`.

You can supply alternative patterns on the command line.  Here are the relevant parameters and their default values:

| parameter | default value | notes |
|---|---|---|
| `--behavior-root` | `.` (current directory) | searches within for behavior pattern matches |
| `--behavior-txt-pattern` | `<SUBJECT>/**/*_<MM><DD><YY>_*.txt` | upload all matches |
| `--behavior-mat-pattern` | `<SUBJECT>/**/*_<MM><DD><YY>_*.mat` | upload all matches |
| `--behavior-hdf5-pattern` | `<SUBJECT>/**/*_<YYYY><MM><DD>_*.hdf5` | upload all matches |
| `--ephys-root` | `.` (current directory) | searches within for SpikeGlx or OpenEphys pattern matches |
| `--spikeglx-run-patterns` | `<SUBJECT>/**/*_<MM><DD><YYYY>_*.nidq.meta` `<SUBJECT>/**/*_<MM><DD><YYYY>_*.obx.bin` `<SUBJECT>/**/*_<YY><MM><DD>_*.nidq.meta` `<SUBJECT>/**/*_<YY><MM><DD>_*.obx.bin` | upload SpikeGlx run dirs that contain matching files |
| `--openephys-oebin-pattern` | `<SUBJECT>/**/<YYYY>-<MM>-<DD>_*/*/*/*/structure.oebin` | upload OpenEphys session dirs that are four levels above mathcing files |

Each of these matching patterns supports wildcards and replacements for flexibility:
 - `?`: match any single character
 - `*`: match zero or more characters, or any single subdirectory
 - `**`: match zero or more subdirectories
 - `<EXPERIMENTER>`: replaced with the given `--experimenter` (or experimenter entered at prompt)
 - `<SUBJECT>`: replaced with the given `--subject` (or subject entered at prompt)
 - `<YYYY>`: replaced with the four-digit part of the given `--date` (or date entered at prompt)
 - `<YY>`: replaced with the two-digit part of the given `--date` (or date entered at prompt)
 - `<MM>`: replaced with the two-digit month of the given `--date` (or date entered at prompt)
 - `<DD>`: replaced with the two-digit day of the given `--date` (or date entered at prompt)


Here's an example that would match behavior and SpikeGlx files using a different date pattern, `YYYY-MM-DD`:

```
cd /mnt/c/Users/labuser/Desktop/Data/
conda activate geffen-pipelines

python ~/geffenlab-ephys-pipeline/scripts/upload_data.py \
  --behavior-txt-pattern '<SUBJECT>/**/*_<YYYY>-<MM>-<DD>_*.txt' \
  --behavior-mat-pattern '<SUBJECT>/**/*_<YYYY>-<MM>-<DD>_*.mat' \
  --spikeglx-run-patterns '<SUBJECT>/**/*_<YYYY>-<MM>-<DD>_*.obx.bin'
```
