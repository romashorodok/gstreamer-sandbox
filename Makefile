run:
	docker run \
		--mount "type=volume,source=nvim,target=/root/.local/share/nvim" \
		--mount "type=bind,source=./,target=/app/cython" \
		--rm --name media-server-deps -it media-server-deps bash

build:
	docker build -t media-server-deps --target media-server-deps . && docker build -t media-server --target media-server .

gen:
	ffmpeg -f lavfi -i testsrc=duration=5:size=640x480:rate=30 -c:v libvpx -b:v 1M -an output.mkv
