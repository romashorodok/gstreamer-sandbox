run:
	docker run \
		-p 34788:34788 \
		--net host \
		--mount "type=volume,source=nvim,target=/root/.local/share/nvim" \
		--mount "type=bind,source=./,target=/app/cython" \
		--rm --name media-server-lite -it media-server-lite sh 

	# docker run \
	# 	-p 34788:34788 \
	# 	--net host \
	# 	--mount "type=volume,source=nvim,target=/root/.local/share/nvim" \
	# 	--mount "type=bind,source=./,target=/app/cython" \
	# 	--rm --name media-server-deps -it media-server-deps bash

test:
	docker build -t vp8-rtp --target vp8-rtp . && docker run --rm --net host vp8-rtp 

build:
	docker build -t media-server-lite . 
	# && docker build -t media-server-deps --target media-server-deps . && 

gen:
	ffmpeg -f lavfi -i testsrc=duration=5:size=640x480:rate=30 -c:v libvpx -b:v 1M -an output.mkv

arena:
	go env -w GOEXPERIMENT=arenas
