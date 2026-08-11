FROM ubuntu:26.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libboost-dev=1.90.0.1ubuntu3 \
    libboost-url1.90-dev=1.90.0-6ubuntu1 \
    libmuparserx-dev=4.0.12-2.1 \
    libopencv-dev=4.10.0+dfsg-7ubuntu5 \
    libomp-dev=1:21.1.6-71 \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY . .

RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
 && cmake --build build -j"$(nproc)"

FROM ubuntu:26.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libboost-url1.90.0=1.90.0-6ubuntu1 \
    libmuparserx4.0.12=4.0.12-2.1 \
    libopencv-core410=4.10.0+dfsg-7ubuntu5 \
    libopencv-imgproc410=4.10.0+dfsg-7ubuntu5 \
    libopencv-imgcodecs410=4.10.0+dfsg-7ubuntu5 \
    libomp5=1:22.1.2-1ubuntu1 \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

EXPOSE 7854

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app/build/conformal_canvas /app/conformal_canvas

ENTRYPOINT ["/app/conformal_canvas"]
