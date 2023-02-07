#!/usr/bin/env python3

import logger
import util

LOGGER = logger.get_logger('net_orc')

class NetworkOrchestrator:

    def __init__(self):
        self.create_net()

    def create_net(self):
        LOGGER.info("Creating baseline network")

        # Create data plane
        util.run_command("ovs-vsctl add-br tr-d")

        # Create control plane
        util.run_command("ovs-vsctl add-br tr-c")

        # Add external interfaces to data and control plane
        # TODO: Load interfaces from config file

    def restore_net(self):

        # Delete data plane
        util.run_command("ovs-vsctl del-br tr-d")

        # Delete control plane
        util.run_command("ovs-vsctl del-br tr-c")

        LOGGER.info("Network is restored")