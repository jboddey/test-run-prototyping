# Image name: test-run/base
FROM ubuntu:jammy

# Install common software
RUN apt-get update && apt-get install -y net-tools iputils-ping tcpdump iproute2 jq python3
