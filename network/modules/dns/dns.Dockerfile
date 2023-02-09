# Image name: test-run/dns
FROM test-run/base:latest

RUN apt-get install -y dnsmasq

COPY start_dns start_dns

RUN chmod u+x start_dns

COPY conf/dnsmasq.conf /etc/dnsmasq.conf

# Start DNS server
ENTRYPOINT [ "./start_dns" ]
