# How to run
Tested in `x86_64` & `aarch64` arch.

First, pull the submodule to build the docker image:

```sh
git submodule update --init --recursive
```

Then, just:
```sh
docker-compose up
```

The `src/` folder is mounted as a docker volume, so you don't have to rebuild the image when is changed.