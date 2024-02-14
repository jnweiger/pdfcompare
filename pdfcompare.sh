#! /bin/bash
#
# (C) 2024 jnweiger@gmail.com - pdfcompare
#
# My old pdfcompare DEB package runs on nothing newer than Ubuntu 16.04
# This script has instructions to ceate a docker image from that.
#
# As a docker image, it runs on any Linux.
# TODO: Create a Dockerfile from this. Create an AppImage from this.
#------
#
# docker run -ti --name u1604pdfcompare ubuntu:16.04 bash
# apt update; apt upgrade; apt install -y wget
# wget https://github.com/jnweiger/pdfcompare/releases/download/v1.6.5/pdfcompare_1.6.5-24.1_amd64.deb
# apt install -y ./pdfcompare_1.6.5-24.1_amd64.deb
# exit
# docker commit u1604pdfcompare pdfcompare
# docker rm u1604pdf
#

docker run --rm pdfcompare pdfcompare "$@"

