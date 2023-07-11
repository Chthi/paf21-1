# snippet source: https://git.rz.uni-augsburg.de/luttkule/psaf-utils/-/blob/master/docker/carla-build/Dockerfile
# this fixes the 'xdg-user-dir not found' error message, preventing the official CARLA image from crashing

ARG CARLA_VERSION=0.9.10.1
FROM carlasim/carla:$CARLA_VERSION

USER root

# Fix Nvidia installation
# because of a nvidia bug
# https://github.com/NVIDIA/nvidia-docker/issues/1631 
# https://developer.nvidia.com/blog/updating-the-cuda-linux-gpg-repository-key/
WORKDIR /tmp
RUN sed -i '/developer\.download\.nvidia\.com\/compute\/cuda\/repos/d' /etc/apt/sources.list && \
    rm /etc/apt/sources.list.d/cuda*.list && \
    rm /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-key del 7fa2af80 && \
    apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb

WORKDIR /home/carla

RUN apt-get update && apt-get install -y xdg-user-dirs xdg-utils && apt-get clean

ARG ADD_ASSETS_URL=https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/AdditionalMaps_0.9.10.tar.gz
RUN echo 'downloading additional assets (for towns 6, 7 and 10) ...' && \
    cd Import && wget -q $ADD_ASSETS_URL && cd .. && \
    echo 'download successful!' && \
    echo 'importing additional assets ...' && \
    ./ImportAssets.sh > /dev/null 2>&1 && rm -rf Import/*.tar.gz && \
    echo 'import successful!'
USER carla

ENTRYPOINT ["/bin/bash", "./CarlaUE4.sh"]
CMD ["-carla-server"]
