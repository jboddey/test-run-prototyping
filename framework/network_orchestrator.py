#!/usr/bin/env python3

import docker
import ipaddress
import json
import logger
import os
import util

LOGGER = logger.get_logger('net_orc')
CONFIG_FILE = "conf/system.json"
NETWORK_MODULES_DIR = "network/modules"
NETWORK_MODULE_METADATA = "metadata.json"
DEVICE_BRIDGE = "tr-d"
INTERNET_BRIDGE = "tr-c"

class NetworkOrchestrator:

    def __init__(self):
        self._int_intf = None
        self._dev_intf = None
        self._net_modules = []

        self._load_config()
        self.network_config = NetworkConfig()
        
        self._load_network_modules()
        self._build_network_modules()
        
        self._create_net()
        self._start_network_services()

    def _load_config(self):
        config_json = json.load(open(CONFIG_FILE, 'r'))
        self._int_intf = config_json['internet_intf']
        self._dev_intf = config_json['device_intf']

    def _create_net(self):
        LOGGER.info("Creating baseline network")

        # Create data plane
        util.run_command("ovs-vsctl add-br " + DEVICE_BRIDGE)

        # Create control plane
        util.run_command("ovs-vsctl add-br " + INTERNET_BRIDGE)

        # Remove IP from internet adapter
        util.run_command("ifconfig " + self._int_intf + " 0.0.0.0")

        # Add external interfaces to data and control plane
        util.run_command("ovs-vsctl add-port " + DEVICE_BRIDGE + " " + self._dev_intf)
        util.run_command("ovs-vsctl add-port " + INTERNET_BRIDGE + " " + self._int_intf)

        # Set ports up
        util.run_command("ip link set dev " + DEVICE_BRIDGE + " up")
        util.run_command("ip link set dev " + INTERNET_BRIDGE + " up")

    def _load_network_modules(self):
        LOGGER.debug("Loading network modules from /" + NETWORK_MODULES_DIR)

        loaded_modules = "Loaded the following network modules: "

        for module_dir in os.listdir(NETWORK_MODULES_DIR):

            net_module = NetworkModule()

            net_module_json = json.load(open(os.path.join(NETWORK_MODULES_DIR, module_dir, NETWORK_MODULE_METADATA)))
            net_module.name = net_module_json['name']
            net_module.description = net_module_json['description']
            net_module.dir_name = module_dir
            net_module.build_file = module_dir + ".Dockerfile"
            net_module.container_name = "tr-ct-" + net_module.dir_name
            net_module.image_name = "test-run/" + net_module.dir_name

            if "enable_container" in net_module_json:
                net_module.enable_container = net_module_json['enable_container']


            if net_module.enable_container:

                net_module.net_config.enable_wan = net_module_json['network']['enable_wan']
                net_module.net_config.ipv4_index = net_module_json['network']['ip_index']
                net_module.net_config.ipv4_address = self.network_config.ipv4_network[net_module.net_config.ipv4_index]
                net_module.net_config.ipv4_network = self.network_config.ipv4_network

            self._net_modules.append(net_module)

            loaded_modules += net_module.dir_name + " "

        LOGGER.info(loaded_modules)

    def _build_network_modules(self):
        for net_module in self._net_modules:
            self._build_module(net_module)

    def _build_module(self, net_module):
        LOGGER.debug("Building network module " + net_module.dir_name)
        client = docker.from_env()
        client.images.build(
            dockerfile=net_module.build_file,
            path= NETWORK_MODULES_DIR + "/" + net_module.dir_name,
            tag="test-run/" + net_module.dir_name
        )

    def _start_network_services(self):
        LOGGER.info("Starting network services")

        client = docker.from_env()

        for net_module in self._net_modules:

            # Network modules may just be Docker images, so we do not want to start them as containers
            if not net_module.enable_container:
                continue

            net_module.container = client.containers.run(
                net_module.image_name,
                remove=True,
                cap_add=["NET_ADMIN"],
                name=net_module.container_name,
                network_mode="none",
                privileged=True,
                detach=True
            )
            
            self._attach_service_to_network(net_module)

    def _attach_service_to_network(self, net_module):
        LOGGER.debug("Attaching net service " + net_module.name + " to device bridge")

        # Device bridge interface example: tr-di-dhcp (Test Run Device Interface for DHCP container)
        bridge_intf = DEVICE_BRIDGE + "i-" + net_module.dir_name

        # Container interface example: tr-cti-dhcp (Test Run Container Interface for DHCP container)
        container_intf = "tr-cti-" + net_module.dir_name

        # Container network namespace name
        container_net_ns = "tr-ctns-" + net_module.dir_name

        # Create interface pair
        util.run_command("ip link add " + bridge_intf + " type veth peer name " + container_intf)

        # Add bridge interface to device bridge
        util.run_command("ovs-vsctl add-port " + DEVICE_BRIDGE + " " + bridge_intf)

        # Get PID for running container
        # TODO: Some error checking around missing PIDs might be required
        container_pid, stderr = util.run_command("docker inspect -f {{.State.Pid}} " + net_module.container_name)
        
        # Create symlink for container network namespace
        util.run_command("ln -sf /proc/" + container_pid + "/ns/net /var/run/netns/" + container_net_ns)

        # Attach container interface to container network namespace
        util.run_command("ip link set " + container_intf + " netns " + container_net_ns)

        # Rename container interface name to eth0
        util.run_command("ip netns exec " + container_net_ns + " ip link set dev " + container_intf + " name eth0")

        # Set IP address of container interface
        util.run_command("ip netns exec " + container_net_ns + " ip addr add " + net_module.net_config.get_ipv4_addr_with_prefix() + " dev eth0")

        # Set interfaces up
        util.run_command("ip link set dev " + bridge_intf + " up")
        util.run_command("ip netns exec " + container_net_ns + " ip link set dev eth0 up")

        if net_module.net_config.enable_wan:
            LOGGER.info("Attaching net service " + net_module.name + " to internet bridge")

            # Internet bridge interface example: tr-ci-dhcp (Test Run Control (Internet) Interface for DHCP container)
            bridge_intf = INTERNET_BRIDGE + "i-" + net_module.dir_name

            # Container interface example: tr-cti-dhcp (Test Run Container Interface for DHCP container)
            container_intf = "tr-cti-" + net_module.dir_name

            # Create interface pair
            util.run_command("ip link add " + bridge_intf + " type veth peer name " + container_intf)

            # Attach bridge interface to internet bridge
            util.run_command("ovs-vsctl add-port " + INTERNET_BRIDGE + " " + bridge_intf)

            # Attach container interface to container network namespace
            util.run_command("ip link set " + container_intf + " netns " + container_net_ns)

            # Rename container interface name to eth1
            util.run_command("ip netns exec " + container_net_ns + " ip link set dev " + container_intf + " name eth1")

            # Set MAC address of container interface
            util.run_command("ip netns exec " + container_net_ns + " ip link set dev eth1 address 9a:02:57:1e:8f:0" + str(net_module.net_config.ipv4_index))

            # Set interfaces up
            util.run_command("ip link set dev " + bridge_intf + " up")
            util.run_command("ip netns exec " + container_net_ns + " ip link set dev eth1 up")

    def restore_net(self):

        client = docker.from_env()

        # Stop all network containers if still running
        for net_module in self._net_modules:
            try:
                container = client.containers.get("tr-ct-" + net_module.dir_name)
                container.kill()
            except: 
                pass
            

        # Delete data plane
        util.run_command("ovs-vsctl del-br tr-d")

        # Delete control plane
        util.run_command("ovs-vsctl del-br tr-c")

        LOGGER.info("Network is restored")

class NetworkModule:

    def __init__(self):
        self.name = None
        self.description = None

        self.container = None
        self.container_name = None
        self.image_name = None

        self.dir_name = None
        self.build_file = None

        self.enable_container = True

        self.net_config = NetworkModuleNetConfig()

# The networking configuration for a network module
class NetworkModuleNetConfig:

        def __init__(self):

            self.enable_wan = False

            self.ipv4_index = 0
            self.ipv4_address = None
            self.ipv4_network = None

        def get_ipv4_addr_with_prefix(self):
            return format(self.ipv4_address) + "/" + str(self.ipv4_network.prefixlen)

# Represents the current configuration of the network for the device bridge
class NetworkConfig:

    def __init__(self):
        self.ipv4_network = ipaddress.ip_network('10.10.10.0/24')
        # TODO: IPv6 prefix etc...