# Cortex User Setup

This doc should help you configure your local lab machine and your cortex user account for running Geffen lab pipelines with [Proceed](https://github.com/benjamin-heasly/proceed).

# Overview

Our workflow has a few steps to it which will run from local lab machines or cortex:
 - Uploading data to cortex runs from a local lab machine, using a Python script, from the local terminal.
 - Pipeline processing runs on cortex using the `proceed` command in the terminal.
 - Manual cluser curation with Phy runs on cortex using the [run_phy.py](../scripts/run_phy.py) Python script.
 - Downloading results runs on a local lab machine, using a Python script, from the local terminal.

The steps below should help you set up both your local lab machine and your Cortex user account.

# Your local lab machine

Let's set up your local lab machine for uploading raw data and downloading pipeline results.
These instructions assume you're using Windows and WSL (Linux that runs within Windows).
Regular Linux and macOS should work too, but might require small adjustments to these steps.

## local WSL

It will be useful to set up [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) on your local Windows machine.
"WSL" stands for "Windows Subsystem for Linux".
It's a Windows feature that provides a full Linux environment running within and alongside Windows.
Working from a Linux environment means the local and cortex environments and command languages will be the same.

To install WSL find Windows Powershell in the Start menu, open a Powershell window, and type:

```
wsl --install
```

This will take a few minutes then prompt you to reboot the machine.  After rebooting, open Powershell again and type:

```
wsl --install Ubuntu-24.04
```

This will make WSL use Ubuntu by default -- similar to cortex.  When prompted, set up a default Linux user for WSL.  Use the same credentials as the Windows machine.  Perhaps:

```
user: labuser
password: *******
```

Going forward, whenever you need to start WSL, open a Powershell window and type:

```
wsl
```

From there you'll be working in Linux environment and you're ready to run all the commands below.

## local Conda

We can use [Conda](https://anaconda.org/anaconda/conda) to manage dependencies on the lab machine and on cortex.
To install Conda in your local WSL environment:

```
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-py311_24.5.0-0-Linux-x86_64.sh -O miniconda.sh
chmod +x ./miniconda.sh 
./miniconda.sh 
# Follow the prompts.
# Choose "yes" to automatically initialize conda for shell.
```

To finish installing conda you'll need to log out from WSL and log in again.

```
# from WSL
exit
```

```
# from Powershell
wsl
```

Verify that conda is installed in your WSL environment.

```
conda --version
# expect conda 24.5.0
```

## local Conda environment

With conda installed we can create our own conda environment for running lab Python scripts.
The environment is defined here in this repo in [geffen-pipelines.yml](../geffen-pipelines.yml).
To create and activate the environment in WSL:

```
cd ~
git clone https://github.com/geffenlab/geffenlab-ephys-pipeline.git

cd ~/geffenlab-ephys-pipeline
conda env create -f geffen-pipelines.yml
```

Check that the environment is active and has the expected versions of Python and Proceed

```
conda activate geffen-pipelines

python --version
# expect Python 3.13.x

proceed --version
# expect Proceed v0.0.11
```

With this environment in place, you'll be set up to upload and dowload from cortex, as in [cortex-moving-data.md](./cortex-moving-data.md).

# Your cortex user account

Let's set up your cortex user account for running pipelines and curating with Phy.

## cortex remote desktop connection

You'll need to already have a cortex user account and be able to log in.
You might find the [Getting started canvas](https://pesaranlab.slack.com/docs/T0481N8KH0A/F09E97B31J7) helpful, on the brainsadmin Slack channel.

In Windows you can find Remote Desktop Connection in the Start menu.
Open this, use `Computer:` `128.91.19.199` for cortex, and press `Connect`.

You should get a window that says `Login to cortex`.
Fill in your cortex user name and password, and press `OK`.

You should get an Ubuntu Desktop!
You might be prompted to do first-time Ubuntu user setup.
You can chose "skip" or "proceed" to move past this.

## cortex remote desktop settings

By default Ubuntu will turn off the remote screen after 5 minutes of inactivity.
This is unhelpful and distracting for remote desktop!
You might be able to disable this:
 - Choose `Settings` from the system meny in the upper right.
 - Choose `Power` on the left side of the settings window.
 - Click on `Screen Blank` and choose `Never`.

## cortex terminal

We have a full desktop, but we'll still need to run commands from a terminal.
You can get a terminal in your desktop session by choosing:
 - Click `Activities` in the upper left.
 - Click `Show Applications` in the bottom right (menu should appear).
 - Choose `Terminal`.

To make this slightly quicker next time, you can:
 - Click `Activities` again.
 - Right-click on the `Terminal` icon.
 - Choose `Pin to dash`.

NOTE: you should be able to cut-and-paste commands into your remote terminal on cortex by right-clicking in the terminal window.

## cortex enable rootless Docker

Our pipelines use Docker to run steps in version-controlled, isolated environments with all their own code and dependencies.
Docker is already installed on Cortex, but you may need to do some one-time steup.

See the brainsadmin Slack channel and find the canvas with instructions for [Rootles Docker](https://pesaranlab.slack.com/docs/T0481N8KH0A/F09JMHTJKA6).
Follow the instructions in this document.

The process will go something like this:
 - Ask ask Bijan or Jarl for admin help setting up rootless docker.
 - Tell them your cortex user name.
 - As admins they will do the first part, adding your user to the system config files `/etc/subuid` and `/etc/subgid`.
 - When they are done, you can run `dockerd-rootless-setuptool.sh install --force` yourself.

The instructions above enable rootless Docker itself.
You must also [configure your Docker data directory](./docker-images.md#change-your-docker-data-directory)!

## cortex test Docker

With rootless Docker all set up, verify you can run Docker containers.

Run this command:

```
docker run --rm hello-world
```

Expect output like this:

```
# Hello from Docker!
# This message shows that your installation appears to be working correctly.
# etc...
```

## cortex test Docker GPU support

Verify that your docker containers will have access to the GPUs on cortex.

Run this command:

```
docker run --rm --gpus all ubuntu nvidia-smi
```

Expect output like this, indicating the existence of several NVIDIA GPUs:

```
Thu Oct 30 20:41:36 2025       
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.274.02             Driver Version: 535.274.02   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA RTX A4500               Off | 00000000:27:00.0 Off |                  Off |
| 30%   27C    P8              21W / 200W |    123MiB / 20470MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
|   1  NVIDIA RTX A4500               Off | 00000000:38:00.0 Off |                  Off |
| 30%   25C    P8              13W / 200W |      9MiB / 20470MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
|   2  NVIDIA RTX A4500               Off | 00000000:A8:00.0 Off |                  Off |
| 30%   22C    P8              17W / 200W |      9MiB / 20470MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
|   3  NVIDIA RTX A4500               Off | 00000000:B8:00.0 Off |                  Off |
| 30%   21C    P8              13W / 200W |      9MiB / 20470MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
                                                                                         
+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
+---------------------------------------------------------------------------------------+
```

## cortex test Docker graphics support

Verify that your Docker containers will be able to run interactive graphical applications (like Phy).

Run this command:

```
docker run --rm --env DISPLAY --volume /tmp/.X11-unix:/tmp/.X11-unix ferri/xeyes:alpine
```

Expect a graphical window to appear with a title like "xeyes".
The window should contain two silly eyeballs that look at the mouse cursor and follow it as it moves.
You can close the window by clicking the `x` any time.

## cortex Conda

We can use [Conda](https://anaconda.org/anaconda/conda) to manage dependencies on cortex, just like we did on your local lab machine.
To install conda for your cortex user run the following in a terminal on your cortex remote desktop:

```
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-py311_24.5.0-0-Linux-x86_64.sh -O miniconda.sh
chmod +x ./miniconda.sh 
./miniconda.sh 
# Follow the prompts.
# Choose "yes" to automatically initialize conda for shell.
```

To finish installing conda you'll need to log out from your terminal, then open a new one.

```
# from cortex terminal
exit
```

Open a new terminal on your cortex remote desktop, via `Activities` in the upper left.

```
# from new cortex terminal
conda --version
# expect conda 24.5.0
```

## cortex Conda environment

With conda installed we can create our environment with Python and Proceed.
The environment is defined here in this repo in [geffen-pipelines.yml](../geffen-pipelines.yml).
It's the same environment we used above, for your local lab machine.

Please note: on cortex we want to store our Conda environment data within `/vol/cortex/nvme-envs/geffenlab`, and not within the lab data directory `/cdz/geffenlab`.  Please see [nvme-envs-policy.md](https://pesaranlab.slack.com/files/U08UK1MFZ7Y/F0B9R1R6AC8/nvme-envs-policy.md) on the `brainsadmin` Slack for details.

Here's how to create and activate our environment on cortex:

```
# Remove any stale environment (It's OK for this to fail, if no environment exists yet).
conda env remove -n geffen-pipelines

# Create your Conda environment storage directory including your username ($USER becomes your username).
mkdir -p /vol/cortex/nvme-envs/geffenlab/$USER/envs

# Get this repo, which contains our environment definition.
cd ~
git clone https://github.com/geffenlab/geffenlab-ephys-pipeline.git

# Create the environment.
cd ~/geffenlab-ephys-pipeline
conda env create -f geffen-pipelines.yml

# Confirm the environment is created and has its path within /vol/cortex/nvme-envs/geffenlab/
conda env list
```

As above, verify expected Python and Proceed versions.

```
conda activate geffen-pipelines

python --version
# expect Python 3.13.x

proceed --version
# expect Proceed v0.0.11
```

After all of this, you should be able to go on to [pipeline-test-run.md](./pipeline-test-run.md) to try a pipeline run with known data.

# Other cortex setup for Geffen lab

In addition to your own user setup above, we had some setup on cortex for the whole lab.
You don't need to run the steps below yourself, but we do want the lab to have this documentation.

## data directories

The Geffen lab is assigned the following storage directory on cortex: `/cdz/geffenlab/`.

We created several subdirectories to organized things:
 - `/cdz/geffenlab/raw_data`: raw nerual and behavioral data uploaded from lab machines
 - `/cdz/geffenlab/processed_data`: intermediate pipeline outputs
 - `/cdz/geffenlab/analysis`: final pipeline outputs to be downloaded for further analysis

## AWS account setup

The Geffen lab has an AWS S3 storage bucket at `s3://upenn-research.geffen-lab-01.us-east-1/`.
We are accessing this bucket from cortex using a Penn AWS account named `cortex-data-transfer-user`.

We created an access key for this account:
 - Visit [cortex-data-transfer-user](https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-1#/users/details/cortex-data-transfer-user?section=security_credentials) credentials page (requires Penn AWS account and permissions).
 - Scroll to "Access keys" and click "Create access key".
 - Choose "Command Line Interface".
 - Use description "Geffen lab data archiving from cortex".
 - Choose create.
 - Use the generated access key and secret access key during `aws configure`, below.

We installed the access key on cortex:
 - On cortex, type `aws configure`.
 - Enter the "AWS Access Key ID" from above.
 - Enter the "AWS Secret Access Key" from above.
 - Use "Default region name" `us-east-1`.
 - Use "Default output format" `json`.
 - Verify this worked with `aws sts get-caller-identity`.

From the last step expect output like this:

```
$ aws sts get-caller-identity
{
    "UserId": "AIDAYIZ4MBX6AGEWBPEQ2",
    "Account": "568672914940",
    "Arn": "arn:aws:iam::568672914940:user/cortex-data-transfer-user"
}
```

We copied the access key to a location on cortex where users in the `geffenlab` group can access it:
 - `cp -r ~/.aws/ /cdz/geffenlab/`
 - `chmod g+r /cdz/geffenlab/.aws/credentials`
 - `chmod g+r /cdz/geffenlab/.aws/config`
