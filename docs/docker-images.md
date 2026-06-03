# Docker Images

Our [proceed](../proceed/) pipelines are based on Docker images.  These images are how we obtain processing code, along with all dependencies, in a versioned and reproducible way.
Some Docker images are large (multiple GB).
Here are some tips for managing them.

# Listing installed images

You can see which images are already installed by running `docker images`.  Here's an example from the cortex server:

```
$ docker images

IMAGE                                                      ID             DISK USAGE   CONTENT SIZE   EXTRA
ghcr.io/benjamin-heasly/geffenlab-bombcell:v0.0.6          9f3b4dc71b37       3.08GB             0B        
ghcr.io/benjamin-heasly/geffenlab-kilosort4:v0.0.3         9a37f2e60c08       10.9GB             0B        
ghcr.io/benjamin-heasly/geffenlab-phy-desktop:v0.0.5       7c679a9d42d6       5.14GB             0B        
ghcr.io/benjamin-heasly/geffenlab-spikeglx-tools:v0.0.16   c84d82023a9a       2.69GB             0B        
ghcr.io/benjamin-heasly/geffenlab-spikeglx-tools:v0.0.17   f6060f4cd4c9       2.69GB             0B        
hello-world:latest                                         1b44b5a3e06a       10.1kB             0B        
```

Each of these would be downloaded by Proceed, the first time it was needed for a pipeline run.
Keeping the images on disk speeds up subsequent pipeline runs.
Otherwise, we'd have wait for the same images to be re-downloaded every time.

# Removing old images

Proceed and Docker will keep images on disk indefinitely.
If you know that you no longer need an image, you must delete it manually.

For example, as we make fixes and improvements to pipeline steps we'll need to download newer versions of our images.
From time to time you can can delete older, stale image versions.

The listing above shows two versions of the same `geffenlab-spikeglx-tools` image -- specifically:

```
IMAGE                                                      ID             DISK USAGE   CONTENT SIZE   EXTRA
ghcr.io/benjamin-heasly/geffenlab-spikeglx-tools:v0.0.16   c84d82023a9a       2.69GB             0B        
ghcr.io/benjamin-heasly/geffenlab-spikeglx-tools:v0.0.17   f6060f4cd4c9       2.69GB             0B        
```

The older version, `v0.0.16`, is stale.  We can remove the image using its `ID` value from the listing, via `docker rmi`:

```
$ docker rmi c84d82023a9a

Untagged: ghcr.io/benjamin-heasly/geffenlab-spikeglx-tools:v0.0.16
Untagged: ghcr.io/benjamin-heasly/geffenlab-spikeglx-tools@sha256:b322b9e36244fb05a34c7cba44d89e191368bf1ae224771af24af34ace4f8404
Deleted: sha256:c84d82023a9a328877c9588d5f163623476327ea8e18dcd27f01a6c89bf762c1
Deleted: sha256:c6d6e6d3cb079806a7a39436d4040359ed3c275b6e8bf9f2dd0d754815264d35
Deleted: sha256:8118f2b754c0d94f330e31759c45412fa039db8fbf78dbcd8df5258b6324dfd5
Deleted: sha256:e8046cfe830b1ff9c2aa85ccdfbd9295c7d65bb68be5b2d1c12382916bc05e0e
Deleted: sha256:24c3deb68747803da56856b336be8269bc306b0c52dd8d859753d89d6b9646b3
Deleted: sha256:7112823b81317067c4f5200b9774f68c6b008d4a0c23fb3aaa3a4000ac9cbf7d
Deleted: sha256:df8e43b47ddc757e1c7e5d5d593936987ff92852e96a4a7a3eb8bd0977f23dd1
Deleted: sha256:c8f2804eb0d487451c15b6fc08c4041cb9dd0151dc0019c119fd9d3b106749b9
Deleted: sha256:ff8778f65c30722571eb009087bba5e2f2d7e33c92c60c3b13e5d4686cf40385
Deleted: sha256:d4141d9bca0603ab194910951dfbfbb1db390eb2fc13f5d9134537752556a71e
Deleted: sha256:a47b3314b3122b475c78b3b432f85389fb713ed5f3c9829c91ed07b72b1eb198
Deleted: sha256:b1fc0638c4930824086805af0841a85291da8b965c16c58e59c8d36426d418a5
Deleted: sha256:5aa4cdbc59b9fb72b8a70445347851624b0a95873a836ab9630d76a7e61d17e8
```

Removing this one image would free up a few GB of disk space.

## acceidentally removing required images

If you accidentally `docker rmi` an image that's needed for a pipeline, don't worry.
Proceed will re-download the image the next time it's needed.

## `docker system prune`

`docker system prune` is another useful command that can free up space.
This tells Docker to find and remove unused containers and image layers.

Depending on what you've been doing with Docker this might free up a lot of space, or no space.
Either way, it should be harmless to run:

```
$ docker system prune

WARNING! This will remove:
  - all stopped containers
  - all networks not used by at least one container
  - all dangling images
  - unused build cache

Are you sure you want to continue? [y/N] y
Total reclaimed space: 0B
```

# Configure your rootless Docker data directory

On the cortex server we use rootles Docker.
This is good because it means you can't use Docker to gain root access and accidentally break the system.

However, by default, rootless Docker will store images and other data within your home directory.
This is currently not supported on cortex (as of writing in June 2026).
The reason has to do with file system types: the `zfs` file system that helps cortex stay performant in general does not support Docker's `overlay2` file system.

So, you must configure your rootless Docker to store data on a separate volume: `/vol/cortex/nvme-infra`.
Here's how you can do that.

## confirm the Docker data directory

First, confirm where Docker is storing data:

```
$ docker info | grep "Docker Root Dir"

Docker Root Dir: /home/ben/.local/share/docker
```

If your Docker system is not running, the command above might return an error.
That's OK, you can move on to the next step.

If your Docker system is running, this can confirm that Docker is saving images and other data within the user's home directory at `/home/ben/.local/share/docker`.
In this example the username is `ben`.
You should see your own username, instead.

## stop Docker

Stop your Docker system process so that we can reconfigure the data directory.
With rootless Docker, this will only affect your cortex user, not anyone else.

```
$ systemctl --user stop docker
```

Confirm that docker is not running.  Try to run `docker images` again and expect an error like the following:

```
$ docker images

failed to connect to the docker API at unix:///run/user/10078/docker.sock; check if the path is correct and if the daemon is running: dial unix /run/user/10078/docker.sock: connect: no such file or directory
```

## change your Docker data directory

Create a new directory to hold your Docker images and other data.
The standard data directory name should fit this pattern:

```
/vol/cortex/nvme-infra/LABNAME/USERNAME/docker-rootless
```

Where `LABNAME` is `geffenlab` and `USERNAME` is your cortex username.
Here's a concrete example for cortex user `ben`:

```
/vol/cortex/nvme-infra/geffenlab/ben/docker-rootless
```

To create your data directory:

```
$ mkdir -p /vol/cortex/nvme-infra/geffenlab/ben/docker-rootless
```

## point your Docker at your data directory

Your Docker system process will look for a configuraiton file in your home directory at `~/.config/docker/daemon.json`.
(It's OK for the configuration file to be located in your home dir.)

Check whether this file already exists:

```
$ cat ~/.config/docker/daemon.json

{
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
```

This file might already exist, with other configuration in it.
If so, you should edit it using your favorite editor:

```
# text-based editor
$ vim ~/.config/docker/daemon.json

# graphical editor
$ gedit ~/.config/docker/daemon.json
```
If the file does not exist yet, you can created it and add the necessary config.

The config we want to add looks like this:

```
{ "data-root": "/vol/cortex/nvme-infra/geffenlab/ben/docker-rootless" }
```

If you're combining with existing config, the end result might look like this:

```
{
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    },
    "data-root": "/vol/cortex/nvme-infra/geffenlab/ben/docker-rootless"
}
```

When you're done creating or editing the file, you can check it again:

```
$ cat ~/.config/docker/daemon.json
```

You should have one `"data-root":` property, pointing to your own data directory within `/vol/cortex/nvme-infra`.

Don't forget to replace `ben` with your own cortex username!

## restart Docker

With that config change, you should be able to restart your Docker system process:

```
$ systemctl --user start docker
```

Confirm that Docker is running and using your new data directory:

```
$ docker info | grep "Docker Root Dir"

Docker Root Dir: /vol/cortex/nvme-infra/geffenlab/ben/docker-rootless
```

## run a container

Confirm that Docker can run a container using the standard `hello-world` image.

```
$ docker run --rm hello-world

Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
17eec7bbc9d7: Pull complete 
Digest: sha256:ef54e839ef541993b4e87f25e752f7cf4238fa55f017957c2eb44077083d7a6a
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

... etc ...
```

Docker should download the `hello-world` image and display a message like "Hello from Docker!".

You should now be able to see the `hello-world` image, as saved in your data directory:

```
$ docker images

IMAGE                                                      ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-world:latest                                         1b44b5a3e06a       10.1kB             0B        
```

At this point we would not expect any other images to be stored in the new data directory.
But next time you run a pipeline, Proced and Docker will download additional images to this directory, as needed.

# Clean up old Docker data directory config

Some of us (maybe just Ben and Anjali) have older config for cortex rootless docker.
Once the above steps are working and Docker is functional on `/vol/cortex/nvme-infra`, we can delete the old config.
This is just removing a symbolic link that we had created.

Check if the link still exists:

```
$ ls -alth ~/.local/share/docker
```

If you see a link here (looks like `source -> destination`, for example `/home/ben/.local/share/docker -> /vol/cortex/cd5/geffenlab/docker-data/ben/docker`) go ahead and remove it:

```
$ rm ~/.local/share/docker
```

As long as you don't add a trailing slash `/`, and you don't add the flags `-rf`, then this `rm` command will only remove the link, not the directory to which the link points.
