FROM ubuntu:24.04 as media-server-deps

RUN apt update
RUN apt install -y git meson

RUN git clone --depth 1 --branch 1.23.90 https://gitlab.freedesktop.org/gstreamer/gstreamer.git /app/gstreamer
WORKDIR /app/gstreamer
RUN meson subprojects download vpx

RUN apt install -y pkg-config autoconf automake libtool ninja-build cmake
RUN apt install -y python3.12-venv python3.12-dev python3-pip
RUN apt install -y libcairo2-dev libgirepository1.0-dev
RUN apt install -y python-gi-dev python3-gst-1.0 
# Gstreamer build deps
RUN apt install -y flex bison
# vpx deps
RUN apt install -y nasm
RUN apt install -y neovim

ENV PYTHONUNBUFFERED 1

RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt

RUN --mount=type=cache,target=/root/.cache \
    pip install -Ur /app/requirements.txt

RUN --mount=type=cache,target=/app/gstreamer/builddir \
    meson setup -Dauto_features=disabled --default-library=static \
    -Dgst-full-libraries=app,video \
    -Dgst-plugins-good:vpx=enabled \
    -Dvpx:vp8_encoder=enabled \ 
    -Dvpx:vp8_decoder=enabled \
    -Dvpx:vp9_encoder=enabled \ 
    -Dvpx:vp9_decoder=enabled \
    --reconfigure builddir && meson compile -C builddir && meson install -C builddir

# /usr/lib/python3/dist-packages/

WORKDIR /app/gstreamer/subprojects/gst-python
RUN meson setup builddir
RUN meson compile -C builddir
RUN meson install -C builddir
