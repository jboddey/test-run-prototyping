#!/usr/bin/env python3

import docker
import json
import logger
import os
import util

LOGGER = logger.get_logger('net_orc')
CONFIG_FILE = "conf/system.json"
NETWORK_MODULES_DIR = "network/modules"
DEVICE_BRIDGE = "tr-d"
INTERNET_BRIDGE = "tr-c"

class NetworkOrchestrator:

    def __init__(self):
        self._int_intf = None
        self._dev_intf = None
        self._load_config()
        self._net_modules = []
        self._load_network_modules()
        self._build_network_modules()
        self.create_net()

    def _load_config(self):
        config_json = json.load(open(CONFIG_FILE, 'r'))
        self._int_intf = config_json['internet_intf']
        self._dev_intf = config_json['device_intf']

    def create_net(self):
        LOGGER.info("Creating baseline network")

        # Create data plane
        util.run_command("ovs-vsctl add-br " + DEVICE_BRIDGE)

        # Create control plane
        util.run_command("ovs-vsctl add-br " + INTERNET_BRIDGE)

        # Add external interfaces to data and control plane
        util.run_command("ovs-vsctl add-port " + DEVICE_BRIDGE + " " + self._dev_intf)
        util.run_command("ovs-vsctl add-port " + INTERNET_BRIDGE + " " + self._int_intf)

        # Set ports up
        util.run_command("ip link set " + DEVICE_BRIDGE + " up")
        util.run_command("ip link set " + INTERNET_BRIDGE + " up")

    def _load_network_modules(self):
        LOGGER.debug("Loading network modules from /" + NETWORK_MODULES_DIR)

        loaded_modules = "Loaded the following network modules: "

        for module_dir in os.listdir(NETWORK_MODULES_DIR):
            net_module = NetworkModule()
            net_module.dir_name = module_dir
            net_module.build_file = module_dir + ".Dockerfile"
            self._net_modules.append(net_module)
            loaded_modules += net_module.dir_name + " "

        LOGGER.info(loaded_modules)

    def _build_network_modules(self):
        for net_module in self._net_modules:
            self._build_module(net_module)

    def _build_module(self, net_module):
        LOGGER.info("Building network module " + net_module.dir_name)
        client = docker.from_env()
        client.images.build(
            dockerfile=net_module.build_file,
            path= NETWORK_MODULES_DIR + "/" + net_module.dir_name,
            tag="test-run/" + net_module.dir_name
        )

    def _start_network_services(self):
        LOGGER.info("Starting network services")

        # TODO: We need to load a list of network services (and image tags) from JSON to start them

    def restore_net(self):

        # Delete data plane
        util.run_command("ovs-vsctl del-br tr-d")

        # Delete control plane
        util.run_command("ovs-vsctl del-br tr-c")

        LOGGER.info("Network is restored")

class NetworkModule:

    def __init__(self):
        self.dir_name = None
        self.build_file = None