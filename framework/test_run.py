#!/usr/bin/env python3

import logger
import signal
import time 

from network_orchestrator import NetworkOrchestrator
from test_orchestrator import TestOrchestrator

LOGGER = logger.get_logger('test_run')

class TestRun:

    def __init__(self):

        signal.signal(signal.SIGINT, self.handler)

        LOGGER.info("Starting Test Run")

        # Get all components ready
        self._test_orchestrator = TestOrchestrator()
        self._net_orchestrator = NetworkOrchestrator()

        # Get network ready (via Network orchestrator)
        LOGGER.info("Network is ready. Waiting for device information...")

        # TODO: This time should be configurable (How long to hold before exiting, this could be infinite too)
        time.sleep(300)

        # This method would be called by the service worker (need to make it static?)
        self.test_device()

        LOGGER.info("Test Run is finished")

        # Tear down network
        self._net_orchestrator.restore_net()

    def test_device(self):
        # Perform startup checks
        # Run test modules against device
        self._test_orchestrator.run_tests()

    def handler(self, signum, frame):
        if (signum == 2):
            LOGGER.info("Exit signal received. Restoring network...")
            self._net_orchestrator.restore_net()
            exit(1)

test_run = TestRun()