FROM ubuntu:22.04

RUN apt update
RUN apt install -y sudo
RUN apt install -y software-properties-common python3-pip wget
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.7 python3.7-dev python3.7-distutils
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --set python /usr/bin/python3.7

RUN apt-get install -y libgmp10 libgmp-dev
RUN apt-get install -y openssl

RUN apt install -y libssl-dev flex bison

COPY charm/ charm

RUN cd charm && python3.7 -m pip install -r requirements.txt

RUN cd charm && ./configure.sh
RUN cd charm/deps/pbc && make && ldconfig && cd -
RUN cd charm && make
RUN cd charm && make install && ldconfig

#RUN cd charm && make test
RUN python3.7 -m pip install numpy lark

COPY src/ src
WORKDIR /src

#ENTRYPOINT ["tail", "-f", "/dev/null"]
