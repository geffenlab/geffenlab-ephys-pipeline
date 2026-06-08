# Download Analysis

This doc should help you download pipelines analysis results from cortex to your local machine.

First you'll need to do initial [cortex user setup](./cortex-user-setup.md) and [process a dataset](./run-proceed.md).

# Download analysis results from cortex

Our [download_analysis.py](../scripts/download_analysis.py) script will search on cortex within `/cdz/geffenlab/analysis` for a session that you specify.  It will download the session's `analysis/` subdirectory to your local machine.

Internally this uses `ssh` to connect to cortex using your own user credentials.

You can run this script from the WSL environment of your local lab machine:

```
# Use our conda environment with Python, etc.
conda activate geffen-pipelines

# Go to the directory that will contain your pipeline-analysis/ folder, for example:
cd /mnt/c/Users/labuser/Desktop

# Run our download script.
python ~/geffenlab-ephys-pipeline/scripts/download_analysis.py
```

This will prompt you for the experimenter initials, subject id, and session date you want to download.  It will also ask for your cortex credentials.  For example:

```
2026-05-14 12:00:32,024 [INFO] Downloading files to local root: /mnt/c/Users/labuser/Desktop/pipeline-results
2026-05-14 12:00:32,024 [INFO] Downloading files from remote host: 128.91.19.199
2026-05-14 12:00:32,024 [INFO] Downloading files from remote analysis root: /cdz/geffenlab/analysis
Experimenter initials: BH
2026-05-14 12:00:34,018 [INFO] Downloading files for experimenter: BH
Subject ID: AS20-demo
2026-05-14 12:00:37,135 [INFO] Downloading files for subject id: AS20-demo
Session date MMDDYYYY: 03112025
2026-05-14 12:00:41,105 [INFO] Downloading files for session date: 03112025 (2025-03-11)
Remote username: ben
2026-05-14 12:00:45,858 [INFO] Downloading files as remote user: ben
Password for remote user ben:
2026-05-14 12:00:52,989 [INFO] Connecting to remote host: 128.91.19.199.
2026-05-14 12:01:03,058 [INFO] Connected (version 2.0, client OpenSSH_8.9p1)
2026-05-14 12:01:03,186 [INFO] Authentication (password) successful!
```

It will summarize what it finds in the session's `analysis/` subdirectory on cortex, and download all of these files:

```
2026-05-14 12:01:03,186 [INFO] Checking for remote analysis session directory /cdz/geffenlab/analysis/BH/AS20-demo/03112025:
catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0
summary
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/neuronal_plus_behavioral.pkl
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_2.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_5.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_12.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_1.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_11.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_13.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_8.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_10.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_3.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_14.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_7.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_9.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_4.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_6.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/multiplot/AS20-demo-03112025_neurons_15.png
/cdz/geffenlab/analysis/BH/AS20-demo/03112025/summary/progress.txt.done
2026-05-14 12:01:09,905 [INFO] Downloading files to: /mnt/c/Users/labuser/Desktop/pipeline-results
2026-05-14 12:01:09,946 [INFO] [chan 2] Opened sftp connection (server version 3)
2026-05-14 12:01:11,677 [INFO] [chan 2] sftp session closed.
2026-05-14 12:01:11,678 [INFO] OK.
```

The files on cortex would be in a subfolder of `/cdz/geffenlab/analysis`, for the session you specified.  For example, this demo session has a data [Pickle](https://docs.python.org/3/library/pickle.html) and a folder of summary plots.

![Ubuntu Files view of a session analysis/ subdirectory containing behavioral and neural data](./cortex-analysis.png)

When the script finishes you should have the same files locally in `pipeline-analysis/` folder.

![Windows Explorer view of a pipeline-analysis/ directory containing a Pickle file and folder of figures](./local-analysis.png)

## Options

The example above used several default options like the cortex host address, the local directory to receive results, and which subfolders to download for the given session.
All of these can be modified from the command line as needed.  For details please see:

```
python ~/geffenlab-ephys-pipeline/scripts/download_analysis.py --help
```
