# Run Phy

This doc should help you run Phy for manual sorting curation.

Before running this you'd need to process a dataset, see [run-proceed.md](./run-proceed.md).

# Phy on cortex remote desktop

You can run Phy on cortex via remote desktop using our [run_phy.py](../scripts/run_phy.py) script.

This script calls `docker run` to start a Docker container with Phy installed in it.
It uses our [geffenlab-phy-desktop](https://github.com/geffenlab/geffenlab-phy-desktop) Docker image.  The script will make the necessary `/cdz/geffenlab/processed_data/` session subdirectory available within the container.

Run the commands below from a terminal on cortex (see [cortex-remote-desktop-connection](./cortex-user-setup.md#cortex-remote-desktop-connection)).

You can tell the script which session to use via the `--experimenter`, `--subject`, and `--date` arguments.

```
conda activate geffen-pipelines
cd ~/geffenlab-ephys-pipeline/scripts

python run_phy.py --experimenter BH --subject AS20-demo --date 03112025
```

## selecting a Phy subdirectory

The script will search within `/cdz/geffenlab/processed_data/`, for Phy `params.py` files, for the specified session.
It might find multiple `params.py`, as from multiple sessions on the same date or multiple probes for a given session.

If so it will prompt you to choose one of them by number.  For example:

```
$ python run_phy.py --experimenter BH --subject AS20-minimal3 --date 03112025

2026-05-13 11:06:43,337 [INFO] Writing logs for this script to stdout and /cdz/geffenlab/processed_data/BH/AS20-minimal3/03112025/run_phy_20260513T150643UTC.log
2026-05-13 11:06:43,337 [INFO] Using Docker image: ghcr.io/geffenlab/geffenlab-phy-desktop:v0.0.6
2026-05-13 11:06:43,337 [INFO] Using 'docker run' args: ['--rm']
2026-05-13 11:06:43,337 [INFO] Using GPU device: 0
2026-05-13 11:06:43,337 [INFO] Configuring X11 display: True
2026-05-13 11:06:43,337 [INFO] Running container as user and group: None
2026-05-13 11:06:43,337 [INFO] Looking for phy/ data in: /cdz/geffenlab/processed_data/BH/AS20-minimal3/03112025
2026-05-13 11:06:43,338 [INFO] Looking for params.py files(s) matchign pattern: **/params.py
2026-05-13 11:06:43,339 [INFO] Found 2 params.py matches within /cdz/geffenlab/processed_data/BH/AS20-minimal3/03112025
2026-05-13 11:06:43,339 [INFO] Please choose one:
2026-05-13 11:06:43,339 [INFO]   0: kilosort4/catgt_AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0_imec0/params.py
2026-05-13 11:06:43,339 [INFO]   1: kilosort4/catgt_another_session_test_g0/another_session_test_g0_imec0/params.py
Choose by number 0-1: 1
2026-05-13 11:07:07,101 [INFO] Using params.py: /cdz/geffenlab/processed_data/BH/AS20-minimal3/03112025/kilosort4/catgt_another_session_test_g0/another_session_test_g0_imec0/params.py
2026-05-13 11:07:07,101 [INFO] Starting Phy run.
```

## the Phy GUI

The script should launch the interactive Phy GUI.
This should appear along with your terminal window, within your cortex remote desktop session.

![Cortex remote desktop with Phy GUI](./phy-desktop.png)

When you're done with Phy, exit the window and the script should also exit.

# Phy on cortex via XPra and web browser

We have found that Phy can be slow to use, when running directly on the cortex remote desktop.
We can use a nice tool called [Xpra](https://github.com/Xpra-org/xpra) to allow the Phy GUI to run on your local machine, while the data are still sitting on cortex (!).

In fact, it's possible to do this using your local web browser (!!).

## start an Xpra session on cortex

Xpra is already installed on cortex.  To use it you must start an Xpra session.  From a cortex terminal run:

```
xpra start --opengl=on --exit-with-children=no --bind-tcp=0.0.0.0:10000 :123
```

The `-bind-tcp=0.0.0.0:10000` part means Xpra will listen for web connections on port `10000`.
We'll use this when connecting from the browser, below.
Port numbers are uniqure system resources, shared by all users.  You might need to choose a different number and substitute it below.
5-digit port numbers from `10000` to `65535` are often free.

The `:123` means this Xpra session will use display number `123`.
Each Xpra session must have a unique display number, across all cortex users, so you might need to choose a different number and substitute it below.

## Launch Phy into your Xpra session

With an Xpra session running, you can launch Phy into display number `123`.  From the same cortex terminal run:

```
conda activate geffen-pipelines
cd ~/geffenlab-ephys-pipeline/scripts

DISPLAY=:123 python run_phy.py --experimenter BH --subject AS20-demo --date 03112025
```

This is the same command we used above, plus the extra `DISPLAY=:123` to specify the display number of your Xpra session.

You should see logging output from Phy, but no GUI window (yet).

## visit Xpra and Phy from your local browser

With Phy running, return to your local machine and launch a web browser.
Visit cortex at its IP address and specify the port number from above, for example: [http://128.91.19.199:10000](http://128.91.19.199:10000)

You should see a desktop running in your browswer window, with an interactive Phy window.

![Xpra and web browser with Phy GUI](./phy-browser-xpra.png)

The Xpra desktop should resize to match your browser window.

When you're done with Phy, you can close its window and exit your browser tab.

## stop Xpra

Finally, when you're all done you can stop Xpra and free up the port, display number, and other resources.  From your original cortex terminal run:

```
xpra stop :123
```
