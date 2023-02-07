# Image name: test-run/gateway
FROM test-run/base:latest

# Install dnsmasq
RUN apt-get install -y iptables

COPY start_gateway start_gateway

RUN chmod u+x start_gateway

# Start networking
ENTRYPOINT ["./start_gateway"]
