FROM golang:1.24.8-bookworm AS build
ARG MINIO_REF=RELEASE.2025-10-15T17-29-55Z
RUN CGO_ENABLED=0 go install github.com/minio/minio@${MINIO_REF}
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=build /go/bin/minio /usr/local/bin/minio
USER 10001:10001
ENTRYPOINT ["minio"]
CMD ["server", "/data", "--console-address", ":9001"]
