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

The listing above shows two versions of the same `geffenlab-spikeglx-tools` image:

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

# Docker data in your home directory

On the cortex server, we use rootles Docker.
This is good because it means you can't use Docker to gain root access and accidentally break the system.

But, this also means that by default Docker stores image data within your home directory.
The images can consume much of your cortex home directory disk quota.
As of writing, the default quota was about 50GB and the Docker images listed above took up about 20GB -- clost to half of the quota.

The default location for Docker image cache is in your home directory at `~/.local/share/docker`.
You can check the size of this directory (or any directory!) with the `du` command.

You might see disk usage like this:

```
$ du -d1 -h ~/.local/share/docker

4.0K    /home/ben/.local/share/docker/runtimes
21G     /home/ben/.local/share/docker/overlay2      <--- large
37M     /home/ben/.local/share/docker/image
8.0K    /home/ben/.local/share/docker/plugins
4.0K    /home/ben/.local/share/docker/containers
64K     /home/ben/.local/share/docker/network
4.0K    /home/ben/.local/share/docker/swarm
28K     /home/ben/.local/share/docker/volumes
4.0K    /home/ben/.local/share/docker/tmp
392K    /home/ben/.local/share/docker/containerd
108K    /home/ben/.local/share/docker/buildkit
22G     /home/ben/.local/share/docker
```

Note `21G` of images stored in `/home/ben/.local/share/docker/overlay2`.
Those are the file system snapshots that make up our Docker images and provide reproducible environments for our processing steps.

# Moving the Docker data directory

You can configure your rootless Docker to save images and other data to a different location, outside of your home directory.
On cortex you can choose a location within `/vol/cortex/cd5/geffenlab/`.

## confirm the Docker data directory

First, confirm where Docker is storing data:

```
$ docker info | grep "Docker Root Dir"

Docker Root Dir: /home/ben/.local/share/docker
```

This confirms that Docker is saving images and other data within the user's home directory at `/home/ben/.local/share/docker`.

In this example the username is `ben`.
You must use your own username, instead.

## clean up existing images

Before moving to a new Docker data directory it can be helpful to clean up the current data directory.
You can do this with `docker system prune`.
Adding the `--all` flag asks Docker to clean up completely, instead of keeping some images.

```
$ docker system prune --all

WARNING! This will remove:
  - all stopped containers
  - all networks not used by at least one container
  - all images without at least one container associated to them
  - all build cache

Are you sure you want to continue? [y/N] y
Total reclaimed space: 21GB
```

The first time you run this, it might free up a lot of space.
It will remove images that we want to use for pipelines, but Proceed will automatically download these again as needed.
It will also remove any cruft that we don't need to move -- or can't move due to Docker-managed file permissions.

## stop Docker

Stop your Docker system process while the data move is happening.
With rootless Docker, this will only affect your cortex user, not anyone else.

```
$ systemctl --user stop docker
```

Confirm that docker is not running.  Try to run `docker images` again and expect an error like the following:

```
$ docker images

failed to connect to the docker API at unix:///run/user/10078/docker.sock; check if the path is correct and if the daemon is running: dial unix /run/user/10078/docker.sock: connect: no such file or directory
```

## move your Docker data directory

Create a new directory to hold your Docker images and other data.
A directory within `/vol/cortex/cd5/geffenlab/` won't count against your home directory quota.

Replace the username `ben` with your own cortex username.

```
$ mkdir -p /vol/cortex/cd5/geffenlab/docker-data/ben
```

Move your existing Docker data to the new location.

```
$ mv ~/.local/share/docker /vol/cortex/cd5/geffenlab/docker-data/ben/docker
```

## create a link from old location to new

Create a file system link from the old Docker data location to the new location.

```
$ ln -s /vol/cortex/cd5/geffenlab/docker-data/ben/docker ~/.local/share/docker
```

Docker will still look for `~/.local/share/docker` when it wants to store data.  But now, it will find that this is a link to the new location within `/vol/cortex/cd5/geffenlab`.

You can confirm the link with `ls`:

```
$ ls -alth ~/.local/share/docker

lrwxrwxrwx 1 ben geffenlab 48 Feb 27 15:29 /home/ben/.local/share/docker -> /vol/cortex/cd5/geffenlab/docker-data/ben/docker
```

## restart Docker

With the data moved and a link to the new location, Docker should be able to run again.
Restart your Docker system process.

```
$ systemctl --user start docker
```

Confirm that Docker can run its `hello-world` example.

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

Docker should download its `hello-world` image and display a message like "Hello from Docker!".

## Confirm the new Docker data location

Finally, confirm that Docker is storing data in the new location:

```
$ docker info | grep "Docker Root Dir"
Docker Root Dir: /vol/cortex/cd5/geffenlab/docker-data/ben/docker
```

This confirms that Docker found the link from the old location to the new location, and is now saving images and other data within `/vol/cortex/cd5/geffenlab/docker-data/ben/docker`.

You should be able to list the image(s) in the new location:

```
$ docker images
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-world:latest   1b44b5a3e06a       10.1kB             0B        
```

At first `hello-world` might be the only image present.

But now you should be ready to run pipelines again, and see those larger images saved outside of your home directory.

# Un-moving the Docker data directory

Our Docker images may change over time, and so may the storage situation on cortex!
In case you want to undo moving the Docker data directory, here are some comands:

Undo the alternative data directory:

```
# clean up cached images to make the move faster
$ docker system prune --all

# stop Docker
$ systemctl --user stop docker

# un-link to the alternative data directory
rm ~/.local/share/docker

# move docker data back to home
$ mv /vol/cortex/cd5/geffenlab/docker-data/ben/docker ~/.local/share/docker

# restart docker
$ systemctl --user start docker
```

Verify docker works from default data directory within home:

```
# Confirm you can run containers
$ docker run --rm hello-world

# Confirm data directory
$ docker info | grep "Docker Root Dir"
```

If all looks good, clean up the alternative data directory:

```
$ rm -rf /vol/cortex/cd5/geffenlab/docker-data/ben
```
