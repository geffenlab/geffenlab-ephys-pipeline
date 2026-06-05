# Pipeline configurations

Our ['proceed/'](../proceed/) pipelines can be customized and configured in a few different ways.  This doc should introduce four ways:

 - creating a new pipeline YAML file
 - passing arguments to a pipeline via `proceed run` on the command line
 - providing probe-specific Kilosort 4 settings in a JSON file
 - providing probe-specific Bombcell parameters in a JSON file

# Creating a new pipeline YAML file

The biggest way to change a pipeline is by writing a new Proceed pipeline definition YAML file!
This might be necessary when setting up a new rig, especially if the rig uses unique hardware or software, or if you want to run different processign steps.

As of writing we have two pipeline definitions:

 - [as-nidq.yaml](../proceed/as-nidq.yaml) is intended for SpikeGLX-with-NIDQ recordings.  It has steps for `catgt`, `kilosort4`, `tprime`, and `bombcell`.
 - [ad-onebox.yaml](../proceed/ad-onebox.yaml) is intended for SpikeGLX-with-OneBox recordings with a continuous treadmill signal.  It has steps for `catgt`, `kilosort4`, `tprime`, `signal-alignment`, and `bombcell`.

`as-nidq.yaml` was the first, and `ad-onebox.yaml` is a copied-then-modified version.
To create your own pipeline YAML you might do the same -- start with a know working YAML, then make small changes for your situation.

Proceed is a fairly general tool for choosing Docker images and running commands in containers.
If you need to make large pipeline changes this would also be possible, but might take some doing and revalidation.

# Passing arguments to a pipeline via `proceed run` on the command line

Once you've chosen a pipeline YAML, you can run it on the command line via `proceed run`.
The pipelines are parameterized to allow passing arguments like `experimenter`, `subject`, and `date`, as on the command line.

Taking [as-nidq.yaml](../proceed/as-nidq.yaml) as an example, the pipeline has an `args:` section that declares available parameters:

```
args:
  user: "0:0"
  gpus: [3]
  raw_data_root: /vol/cortex/cd5/geffenlab/raw_data
  processed_data_root: /vol/cortex/cd5/geffenlab/processed_data
  experimenter: AS
  subject: AS20
  date: "03112025"
  catgt_args: "-prb_fld -out_prb_fld -ni -ap -apfilter=butter,12,300,10000 -lffilter=butter,12,1,500 -gblcar -gfix=0.4,0.1,0.02 -xa=0,0,0,1,3,500 -xia=0,0,1,3,3,0 -xd=0,0,8,3,0 -xid=0,0,-1,2,1.7 -xid=0,0,-1,3,5"
  tprime_to_sync_pattern: "*/*.imec0.ap.*.txt"
  tprime_events_sync_pattern: "*.nidq.xd_8_4_500.txt"
  tprime_events_pattern: "*.nidq.*.txt"
```

Each parameter has a name, like `user`, `experimenter`, `subject`, `date`, `catgt_args`, etc.
Each parameter also has a default value.
If you don't specify a value on the command line, the default will be used.
Many of the parameters don't need to change very often and for these default is the way to go.

Parameters like `experimenter`, `subject`, `date` will change depending on the dataset being processed.
To override the defaults on the command line, pass these as `name=value` pairs following the `--args` option.

```
conda activate geffen-pipelines
cd ~/geffenlab-ephys-pipeline

proceed run proceed/as-nidq.yaml --args experimenter=BH subject=AS20-minimal3 date="03112025"
```

Some parameters will change infrequently depending on situations like server load.
For example, `gpus: [3]` tells Proceed to select the 4th (index 3) GPU device for running Kilosort 4.
If this device is busy, you can choose a different device on the command line.

```
conda activate geffen-pipelines
cd ~/geffenlab-ephys-pipeline

proceed run proceed/as-nidq.yaml --args gpus="[2]"
```

The command `nvidia-smi` can tell you which GPU devices are under more or less load.

# Providing probe-specific Kilosort 4 settings in a JSON file

Kilosort 4 has [many settings](https://github.com/MouseLand/Kilosort/blob/9f8e7052f43fbe12b3462bd185f2de05fceef33a/kilosort/parameters.py) that can be specified at runtime.
In principle we could encode these as part of the pipeline YAML, possibly using `args:` for flexibility.
However, given the number of available settings, this seems cumbersome.

Instead our [kilosort4](https://github.com/geffenlab/geffenlab-kilosort4) step allows reading Kilosort 4 settings from a JSON file.

As configured in [as-nidq.yaml](../proceed/as-nidq.yaml), the step will look in the session's `raw_data` directory for any JSON files with names that end with `-kilosort4-settings.json`.
As the step looks for potential probes to sort, like `imec0` or `imec1`, it will choose a JSON file that contains the probe name, for example `my-imec0-kilosort4-settings.json`.
Settings in this file will be loaded from JSON and used to override the Kilosort 4's baked-in default settings.  If there is no probe-specific match, the step will use default, baked-in settings.

A working file layout with Kilosort 4 settings for two probes might look like this:

```
/vol/cortex/cd5/geffenlab/
└── raw_data/
    └── BH/
        └── AS20-minimal3/
            └── 03112025/
                ├── ecephys/
                ├── behavior/
                ├── my-imec0-kilosort4-settings.json
                └── my-imec1-kilosort4-settings.json
```

When sorting probe `imec0`, the step should find `my-imec0-kilosort4-settings.json` and use those settings for Kilosort 4.  Likewise for `imec1`.

## Kilosort 4 settings JSON format

What is the expected format for a Kilosort 4 settings JSON file?
It's a single JSON object of many `"name": value` pairs.
This repo has an example at [my-imec0-kilosort4-settings.json](./my-imec0-kilosort4-settings.json).

We can also get examples from previous pipeline runs.
When our [kilosort4](https://github.com/geffenlab/geffenlab-kilosort4) step runs, it writes out a JSON file of effective settings that were used, in the expected format.  Even when the default, baked-in settings are used the effective settings file will be complete and explicit.

For example, the pipeline run above with `experimenter=BH subject=AS20-minimal3 date="03112025"` would have produced an effective settings file within our `processed_data` directory:

```
/vol/cortex/cd5/geffenlab/processed_data/
└── BH/
    └── AS20-minimal3/
        └── 03112025/
            └── kilosort4/
                └── catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/
                    └── AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/
                        └── imec0-kilosort4-effective-settings.json
```

You can copy an `effective-settings.json` file like this, or the example settings file in this repo, into the `raw_data` subdirectory of another session.
You could make multiple copies as needed, for multiple sessions, or for multiple probes within each session.

You can also remove name-value pairs that you don't need to specify, allowing defaults for these.

# Providing probe-specific Bombell parameters in a JSON file

Bombcell also has [many parameters](https://github.com/Julie-Fabre/bombcell/blob/main/py_bombcell/bombcell/default_parameters.py) that can be specified at runtime.
Again, in principle we could encode these as part of the pipeline YAML and use `args:` for flexibility.
And again, given the number of available parameters, this seems cumbersome.

Instead our [bombcell](https://github.com/geffenlab/geffenlab-bombcell) step allows reading Bombcell parameters from a JSON file.

As configured in [as-nidq.yaml](../proceed/as-nidq.yaml), the step will look in the session's `raw_data` directory for any JSON files with names that end with `-bombcell-parameters.json`.
As the step looks for potential probes to curate, like `imec0` or `imec1`, it will choose a JSON file that contains the probe name, for example `my-imec0-bombcell-parameters.json`.
Settings in this file will be loaded from JSON and used to override the Bombcell baked-in default settings.  If there is no probe-specific match, the step will use default, baked-in parameters.

A working file layout with Bombcell parameters for two probes might look like this:

```
/vol/cortex/cd5/geffenlab/
└── raw_data/
    └── BH/
        └── AS20-minimal3/
            └── 03112025/
                ├── ecephys/
                ├── behavior/
                ├── my-imec0-bombcell-parameters.json
                └── my-imec1-bombcell-parameters.json
```

When curating for probe `imec0`, the step should find `my-imec0-bombcell-parameters.json` and use those settings for Bombcell.  Likewise for `imec1`.

## Bombcell parameters JSON format

What is the expected format for a Bombcell parameters JSON file?
It's a single JSON object of many `"name": value` pairs.
This repo has an example at [my-imec0-bombcell-parameters.json](./my-imec0-bombcell-parameters.json).

We can also get examples from previous pipeline runs.
When our [bombcell](https://github.com/geffenlab/geffenlab-bombcell) step runs, it writes out a JSON file of effective parameters that were used, in the expected format.  Even when the default, baked-in settings are used the file of effective parameters will be complete and explicit.

For example, the pipeline run above with `experimenter=BH subject=AS20-minimal3 date="03112025"` would have produced an effective parameters file within our `processed_data` directory:

```
/vol/cortex/cd5/geffenlab/processed_data/
└── BH/
    └── AS20-minimal3/
        └── 03112025/
            └── kilosort4/
                └── catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/
                    └── AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/
                        └── imec0-bombcell-effective-parameters.json
```

You can copy an `effective-parameters.json` file like this, or the example in this repo, into the `raw_data` subdirectory of another session.
You could make multiple copies as needed, for multiple sessions, or for multiple probes within each session.

You can also remove name-value pairs that you don't need to specify, allowing defaults for these.

Several Bombcell parameters will be filled in automatically at runtime, based on the actual session data.  You should omit these from your parameters JSON file unless you need to force their values:
 - `plotsSaveDir`
 - `ephysKilosortPath`
 - `ephys_meta_file`
 - `raw_data_file`
 - `ephys_sample_rate`
 - `nChannels`
 - `nSyncChannels`
 - `gain_to_uV`
