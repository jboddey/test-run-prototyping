# Image name: test-run/ntp
FROM test-run/base:latest

COPY network/modules/ntp/start_ntp start_ntp

RUN chmod u+x start_ntp

# Start NTP server
ENTRYPOINT [ "./start_ntp" ]
