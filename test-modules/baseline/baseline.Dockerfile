# Image name: test-run/baseline

# This will eventually be a lightweight base image
FROM ubuntu:jammy

RUN apt-get update

RUN chmod u+x test_baseline

ENTRYPOINT ["./test_baseline"]
