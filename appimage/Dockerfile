FROM ubuntu:16.04

WORKDIR /app
COPY pdfcompare.yml /app

RUN apt update && apt upgrade -y && apt install -y dpkg wget imagemagick file binutils
RUN wget https://github.com/AppImageCommunity/pkg2appimage/releases/download/continuous/pkg2appimage--x86_64.AppImage -O pkg2appimage
RUN chmod a+x pkg2appimage
RUN ./pkg2appimage --appimage-extract-and-run pdfcompare.yml

