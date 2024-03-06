FROM alpine:3.19.1 as media-server-lite
RUN apk add --no-cache git meson curl
RUN apk add --no-cache pkgconfig ninja-build cmake

RUN git clone --depth 1 --branch 1.23.90 https://gitlab.freedesktop.org/gstreamer/gstreamer.git /app/gstreamer
WORKDIR /app/gstreamer
RUN meson subprojects download vpx

# Dev 
RUN apk add --no-cache g++ musl-dev gcompat libstdc++ libffi-dev flex bison nasm
# RUN meson subprojects download glib
# RUN meson subprojects download libffi



# FROM ubuntu:24.04 as media-server-deps
#
# RUN apt update
# RUN apt install -y git meson
#
# RUN git clone --depth 1 --branch 1.23.90 https://gitlab.freedesktop.org/gstreamer/gstreamer.git /app/gstreamer
# WORKDIR /app/gstreamer
# RUN meson subprojects download vpx
# RUN meson subprojects download glib
# RUN meson subprojects download libffi
#
# RUN apt install -y pkg-config autoconf automake libtool ninja-build cmake
# # RUN apt install -y python3.12-venv python3.12-dev python3-pip
# # RUN apt install -y libcairo2-dev libgirepository1.0-dev
# # RUN apt install -y python-gi-dev python3-gst-1.0 
# # Gstreamer build deps
# RUN apt install -y flex bison
# # vpx deps
# RUN apt install -y nasm
# RUN apt install -y neovim
#
# # ENV PYTHONUNBUFFERED 1
# #
# # RUN python3 -m venv --system-site-packages /opt/venv
# # ENV PATH="/opt/venv/bin:$PATH"
#
# COPY ./requirements.txt /app/requirements.txt
#
# # RUN --mount=type=cache,target=/root/.cache \
# #     pip install -Ur /app/requirements.txt
#
# # RUN apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x 
#
# # How to build with meson
# # https://blogs.igalia.com/scerveau/discover-gstreamer-full-static-mode/
#
#     # -Dgst-full-plugins=coreelements;staticelements;typefindfunction;matroska;vpx;pbtypes;good;base \
#
# # --mount=type=cache,target=/app/gstreamer/builddir \
# RUN --mount=type=cache,target=/app/gstreamer/builddir \
#     meson setup -Dauto_features=disabled --default-library=static \
#     -Dgst-full-target-type=static_library \
#     --wipe builddir && meson compile -C builddir && meson install -C builddir
#
#     # coreelements,typefindfunctions,alsa,pbtypes
#     # -Dgst-full-plugins=coreelements,typefindfunctions,alsa,pbtypes \
#     # -Dgst-full-libraries=app,video \
#
#     # -Dgpl=enabled -Dlibav=disabled \
#     # -Dgstreamer:tools=enabled \
#
# # RUN --mount=type=cache,target=/app/gstreamer/builddir \
# #     meson setup -Dauto_features=disabled --default-library=static \
# #     -Dgst-full-target-type=static_library \
# #     -Dgst-full-plugins=coreelements,staticelements,typefindfunction,matroska,vpx,pbtypes,good,base \
# #     -Dgood=enabled -Dbase=enabled \
# #     -Dgpl=enabled -Dlibav=disabled \
# #     -Dgstreamer:tools=enabled \
# #     -Dgst-full-libraries=app,video \
# #     -Dpython=disabled \
# #     -Dgst-plugins-good:vpx=enabled \
# #     -Dgst-plugins-good:matroska=enabled \
# #     -Dgst-plugins-good:autodetect=enabled \
# #     -Dgst-plugin-base:compositor=enabled \
# #     -Dgst-plugin-base:videoconvertscale=enabled \
# #     -Dgst-plugins-base:audioresample=enabled \
# #     -Dvpx:vp8=enabled \
# #     -Dvpx:vp9=enabled \
# #     -Dvpx:vp8_encoder=enabled \ 
# #     -Dvpx:vp8_decoder=enabled \
# #     -Dvpx:vp9_encoder=enabled \ 
# #     -Dvpx:vp9_decoder=enabled \
# #     --reconfigure --wipe builddir && meson compile -C builddir && meson install -C builddir
#
# # WORKDIR /app/gstreamer/subprojects/gst-python
# # RUN meson setup builddir && meson compile -C builddir && meson install -C builddir
#
# EXPOSE 3478
# # RUN apt install -y curl
# # RUN curl -LO https://github.com/neovim/neovim/releases/download/v0.9.4/nvim-linux64.tar.gz
# # RUN export PATH="$PATH:/opt/nvim-linux64/bin"
# # RUN tar -C /opt -xzf nvim-linux64.tar.gz
# #
# # WORKDIR /opt/nvim-linux64
# # RUN cp bin/nvim /usr/bin/nvim && cp -r lib/nvim /usr/lib && cp -r share/nvim /usr/share/
# #
# # RUN git clone --branch no-auto-install https://github.com/romashorodok/dotfiles.git ~/.config/nvim
# # RUN apt install -y fzf npm
# # RUN apt install -y golang
# #
# # RUN git clone https://github.com/jesseduffield/lazygit.git --depth 1
# # RUN cd lazygit && go build -o /usr/bin/lazygit main.go
# #
# # RUN pip install git+https://github.com/romashorodok/gstreamer-stubs.git
#
# WORKDIR /app
#
# FROM alpine:3.19.1 as vp8-rtp
# RUN apk add --no-cache ffmpeg
#
# CMD [ "ffmpeg", "-re", "-f", "lavfi", "-i", "testsrc=size=640x480:rate=30", "-c:v", "libvpx", "-b:v", "1M", "-an", "-f", "rtp", "-buffer_size", "1024", "-pkt_size", "1024", "-payload_type", "111", "rtp://localhost:34788" ]
#
# # /usr/lib/python3/dist-packages/gi/overrides/
# # /lib/x86_64-linux-gnu/gstreamer-1.0/
