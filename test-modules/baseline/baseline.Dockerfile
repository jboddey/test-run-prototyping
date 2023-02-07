# Image name: test-run/baseline

FROM test-run/base

RUN apt-get update

COPY test_baseline test_baseline

RUN chmod u+x test_baseline

ENTRYPOINT ["./test_baseline"]
