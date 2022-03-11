FROM ubuntu:latest
LABEL ovecjoe <ovecjoe123@gmail.com>
RUN apt-get update && \
    apt-get install -y python3 nodejs npm && \
    npm install -g ganache-cli && \
    pip install vyper eth-brownie
WORKDIR /home/ubuntu/chattyToken/
