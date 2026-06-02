# Archiving Data to S3

This doc should help you archive session raw data from cortex to the lab's S3 bucket.

First, you'll need to do the one-time [cortex user setup](./cortex-user-setup.md).

## Archive raw data to S3

This repo has a Python script [archive_data.py](../scripts/archive_data.py) that should help archiving data from cortex to the lab's S3 bucket.

You can run this script from a terminal on cortex:

```
# Use our conda environment with Python, etc.
conda activate geffen-pipelines

cd ~/geffenlab-ephys-pipeline/scripts
python archive_data.py --delete
```

The `--delete` flag means raw data files will be deleted from cortex after being succesfully archived to S3.  If you don't supply this flag, the files will be kept on cortex even after archiving.

You can also use the `--dry-run` flag to see what the script would do, without committing data to S3 or deleting anything.

The script will prompt you for the experimenter initials, subject id, and session date(s) that you want to archive.
You can provide an optional qualifier to filter which files will be archived.

Finally the script will prompt you for a project name, for tagging the data objects in S3.  For example:

```
$ python archive_data.py --delete

2026-05-14 12:46:14,842 [INFO] Archiving files within raw data root: /cdz/geffenlab/raw_data
Experimenter initials: BH
2026-05-14 12:46:17,835 [INFO] Archiving files for experimenter: BH
Subject ID: AS20-demo
2026-05-14 12:46:21,563 [INFO] Archiving files for subject id: AS20-demo
Session date MMDDYYYY (multiple dates may be separated by spaces): 03112025
2026-05-14 12:46:25,093 [INFO] Archiving files for session date(s): ['2025-03-11']
Qualifier like 'training','ap.bin', 'recording1', etc.  Leave blank to upload all: 
2026-05-14 12:46:26,588 [INFO] Archiving all files
Project name (for tag 'project_name' on stored objects): demo
2026-05-14 12:46:29,163 [INFO] Adding stored object tag project_name=demo.
2026-05-14 12:46:29,163 [INFO] Using S3 bucket: upenn-research.geffen-lab-01.us-east-1
2026-05-14 12:46:29,163 [INFO] Using S3 bucket path prefix: cortex/raw_data
2026-05-14 12:46:29,163 [INFO] Using S3 storage class: DEEP_ARCHIVE
2026-05-14 12:46:29,163 [INFO] Using AWS credentials from: /cdz/geffenlab/.aws/credentials
2026-05-14 12:46:29,163 [INFO] Using AWS config from: /cdz/geffenlab/.aws/config
2026-05-14 12:46:29,163 [WARNING] Deleting local files after archiving.
```

Based on the experimenter initials, subject id, session date(s) the script will search the local `raw_data` directory for files to archive.

From all the files found, the script can use the optional qualifier to further restrict which files will be uploaded.  When the qualifier is provided, only files that contain the qualifier in their name will be uploaded.  For example, the qualifier "training" could be used to select "training" files but ignore "testing" files.

Before archiving, the script will show which files it plans to archive to S3, along with several tags, and prompt for your confirmation.

```
2026-05-14 12:46:29,163 [INFO] Looking for session date: 2025-03-11 AKA 03112025
2026-05-14 12:46:29,163 [INFO] Using these tags for this date: {'experimenter': 'BH', 'subject': 'AS20-demo', 'year': '2025', 'month': '03', 'day': '11', 'project_name': 'demo'}
2026-05-14 12:46:29,164 [INFO] Found 6 files within: /cdz/geffenlab/raw_data/BH/AS20-demo/03112025
2026-05-14 12:46:29,164 [INFO] Planning to archive 6 files within /cdz/geffenlab/raw_data/BH/AS20-demo:
2026-05-14 12:46:29,164 [INFO]   03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.txt
2026-05-14 12:46:29,164 [INFO]   03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.mat
2026-05-14 12:46:29,164 [INFO]   03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.bin
2026-05-14 12:46:29,164 [INFO]   03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.meta
2026-05-14 12:46:29,164 [INFO]   03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.bin
2026-05-14 12:46:29,164 [INFO]   03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.meta
Do you want to archive these 6 files?  Type 'yes' to proceed: yes
```

You must type `yes` to proceed.  Otherwise the script will exit before archiving.
If you do type `yes` the script will upload files to S3.:


```
2026-05-14 12:46:31,091 [WARNING] Proceeding to archive files.
2026-05-14 12:46:31,200 [INFO] Found credentials in shared credentials file: /cdz/geffenlab/.aws/credentials
2026-05-14 12:46:31,311 [INFO] Archiving s3://upenn-research.geffen-lab-01.us-east-1/cortex/raw_data/BH/AS20-demo/03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.txt
2026-05-14 12:46:31,485 [INFO] Archiving s3://upenn-research.geffen-lab-01.us-east-1/cortex/raw_data/BH/AS20-demo/03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.mat
2026-05-14 12:46:31,597 [INFO] Archiving s3://upenn-research.geffen-lab-01.us-east-1/cortex/raw_data/BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.bin
2026-05-14 12:46:36,470 [INFO] Archiving s3://upenn-research.geffen-lab-01.us-east-1/cortex/raw_data/BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.meta
2026-05-14 12:46:36,587 [INFO] Archiving s3://upenn-research.geffen-lab-01.us-east-1/cortex/raw_data/BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.bin
2026-05-14 12:46:40,845 [INFO] Archiving s3://upenn-research.geffen-lab-01.us-east-1/cortex/raw_data/BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.meta
2026-05-14 12:46:41,039 [INFO] Archived 6 files
```

If you provided the `--delete` flag, the script will then delete the archived files from cortex.

```
2026-05-14 12:46:41,039 [WARNING] Proceeding to delete local files.
2026-05-14 12:46:41,039 [INFO] Deleting BH/AS20-demo/03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.txt
2026-05-14 12:46:41,040 [INFO] Deleting BH/AS20-demo/03112025/behavior/AS20_031125_trainingSingle6Tone2024_0_39.mat
2026-05-14 12:46:41,040 [INFO] Deleting BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.bin
2026-05-14 12:46:41,155 [INFO] Deleting BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.nidq.meta
2026-05-14 12:46:41,155 [INFO] Deleting BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.bin
2026-05-14 12:46:41,362 [INFO] Deleting BH/AS20-demo/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_t0.imec0.ap.meta
```

![Web broswer screen shot of tags added to an S3 storage object](./s3-object-tags.png)
