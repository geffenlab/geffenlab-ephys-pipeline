# geffenlab-ephys-pipeline

This repository contains [Proceed](https://geffenlab.github.io/proceed/) [pipelines](./proceed/) and Python [scripts](./scripts/) for processing Geffen lab ephys data.

This repository goes with several other repositories that define inividual processing steps and Docker images:

 - [geffenlab-spikeglx-tools](https://github.com/geffenlab/geffenlab-spikeglx-tools): CatGT, TPrime, Python scripts
 - [geffenlab-kilosort4](https://github.com/geffenlab/geffenlab-kilosort4): Kilosort4, NVIDIA and CUDA dependencies, ProbeInterface
 - [geffenlab-bombcell](https://github.com/geffenlab/geffenlab-bombcell): Bombcell
 - [geffenlab-phy-desktop](https://github.com/geffenlab/geffenlab-phy-desktop): interactive Phy environment
 - [geffenlab-data-summary](https://github.com/geffenlab/geffenlab-data-summary): population analysis data summary and plots

# Getting started

To set up your local and cortex environments for running pipelines, see [cortex-user-setup.md](./docs/cortex-user-setup.md).

# Running pipelines

Here's the general, intended workflow along with relevant [docs/](./docs/).

## Intended workflow

### upload data to cortex
See [upload-data.md](./docs/upload-data.md) to locate behavioral and neural data on a rig machine, for a given subject and date, and upload to cortex using standardized directory structure and file permissions.

### run a pipeline on cortex
Process data for each session using the `proceed` command and one of our [pipeline YAML files](./proceed/).  See [run-proceed.md](./docs/run-proceed.md).

### configure Kilosort4 and Bombcell with JSON
Both Kilosort4 and Bombcell accept dozens of configuration options / parameters that guide their behavior.  You can specify these, per probe, using JSON files and a naming convention.  See [pipeline-config.md](./docs/pipeline-config.md).

### run Phy on cortex
The pipieline will run Kilosort 4 and Bombcell.  You can do interactive review and curation with Phy, see [run-phy.md](./docs/run-phy.md).

### re-run pipeline steps on cortex
You might need to re-run one or more pipeline steps, for example after manual curation.  See [reprocessing-a-datset](./docs/run-proceed.md#reprocessing-a-datset).

### download `analysis` results locally
Pipelines deal with large raw data files and intermediate processing results.  They should produce relatively small results into an `analysis` subdirectory.  See [download-analysis.md](./docs/download-analysis.md) to download the `analysis` subdirectory for a subject and date.

### archive data from cortex
If you decide to archive a dataset, you can copy the raw behavioral and neural data to Amazon S3.  You can optionally delete these from cortex as well.  See [archive-data.md](./docs/archive-data.md).

# Docker images

Our pipeline steps are based on [Docker images](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/).  Each image contains custom Python code along with the Python runtime and other dependencies, bundled into a portable, reproducible environment.

The repositories mentioned at the top of this page are responsible for defining and producing these Docker images.  See the readme for each repository for details like where to find the Docker images on Github, and how to create new versions.

When running pipelines we download relevant Docker images and run commands within Docker containers.  Some Docker images are large, multiple GB.  See [docker-images.md](./docs/docker-images.md) for tips on how to manage Docker images and disk usage.

# Minimal testing data

We have one more repository related Geffen lab pipelines:

 - [geffenlab-minimal-data](https://github.com/benjamin-heasly/geffenlab-minimal-data): utilities for preparing small test datasets

This repository has scripts for creating reduced-size test data, by extracting a few trials from a larger, real dataset.
Having a smaller dataset speeds up testing, debugging, and interating on code changes.
