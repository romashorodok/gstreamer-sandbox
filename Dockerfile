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

# --mount=type=cache,target=/app/gstreamer/builddir \
RUN meson setup -Dauto_features=disabled --default-library=static \
    -Dgst-full-libraries=app,video \
    -Dgst-plugins-good:vpx=enabled \
    -Dvpx:vp8_encoder=enabled \ 
    -Dvpx:vp8_decoder=enabled \
    -Dvpx:vp9_encoder=enabled \ 
    -Dvpx:vp9_decoder=enabled \
    -Dgst-plugins-base:audioresample=enabled \
    -Dgst-plugins-good:autodetect=enabled \
    -Dgst-plugin-base:compositor=enabled \
    -Dgst-plugin-base:videoconvertscale=enabled \
    --reconfigure builddir && meson compile -C builddir && meson install -C builddir

WORKDIR /app/gstreamer/subprojects/gst-python
# --mount=type=cache,target=/app/gstreamer/subprojects/gst-python/builddir \
RUN meson setup builddir && meson compile -C builddir && meson install -C builddir

RUN apt install -y curl
RUN curl -LO https://github.com/neovim/neovim/releases/download/v0.9.4/nvim-linux64.tar.gz
RUN export PATH="$PATH:/opt/nvim-linux64/bin"
RUN tar -C /opt -xzf nvim-linux64.tar.gz

WORKDIR /opt/nvim-linux64
RUN cp bin/nvim /usr/bin/nvim && cp -r lib/nvim /usr/lib && cp -r share/nvim /usr/share/

RUN git clone --branch no-auto-install https://github.com/romashorodok/dotfiles.git ~/.config/nvim
RUN apt install -y fzf npm
RUN apt install -y golang

RUN git clone https://github.com/jesseduffield/lazygit.git --depth 1
RUN cd lazygit && go build -o /usr/bin/lazygit main.go

RUN pip install git+https://github.com/romashorodok/gstreamer-stubs.git

WORKDIR /app

# /usr/lib/python3/dist-packages/gi/overrides/
# /lib/x86_64-linux-gnu/gstreamer-1.0/

# FROM ubuntu:24.04 as media-server
# RUN apt update
# RUN apt install -y curl git
#
# RUN apt install -y musl-dev pkg-config python3-dev golang meson npm
#
# COPY . /app
# WORKDIR /app
# RUN apk add meson
# RUN apk add --no-cache neovim git curl
# RUN git clone --branch no-auto-install https://github.com/romashorodok/dotfiles.git ~/.config/nvim
# RUN apk add musl-dev pkgconfig python3-dev go bash npm
# RUN apk add meson
# COPY . /app
# WORKDIR /app

