#!/usr/bin/env python3

import logger
import signal
import time 

from network_orchestrator import NetworkOrchestrator
from test_orchestrator import TestOrchestrator

LOGGER = logger.get_logger('test_run')

class TestRun:

    def __init__(self):
        LOGGER.info("Starting Test Run")

        # Get all components ready
        self._test_orchestrator = TestOrchestrator()
        self._net_orchestrator = NetworkOrchestrator()

        # Get network ready (via Network orchestrator)
        LOGGER.info("Network is ready. Waiting for device information...")

        time.sleep(20)

        # This method would be called by the service worker (need to make it static?)
        self.test_device()

        LOGGER.info("Test Run is finished")

        # Tear down network
        self._net_orchestrator.restore_net()

    def test_device(self):
        # Perform startup checks
        # Run test modules against device
        self._test_orchestrator.run_tests()

def handler(signum, frame):
    if (signum == 2):
        exit(1)

signal.signal(signal.SIGINT, handler)

test_run = TestRun()