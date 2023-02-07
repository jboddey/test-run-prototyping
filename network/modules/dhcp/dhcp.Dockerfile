# Image name: test-run/dhcp
FROM test-run/base:latest

# Install dnsmasq
RUN apt-get install -y dnsmasq iptables

COPY start_dhcp start_dhcp

RUN chmod u+x start_dhcp

# Start DHCP server
ENTRYPOINT [ "./start_dhcp" ]
