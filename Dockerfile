FROM ubuntu:22.04

RUN sudo add-apt-repository ppa:deadsnakes/ppa
RUN sudo apt update
RUN sudo apt install python3.7 python3.7-dev python3.7-distutils

RUN sudo apt-get install -y libgmp10 libgmp-dev
RUN sudo apt-get install -y openssl
RUN python3.7 -m pip install -r charm/requirements.txt

RUN charm/configure.sh
RUN cd charm/deps/pbc && make && sudo ldconfig && cd -
RUN cd charm && make
RUN cd charm && make install && sudo ldconfig
