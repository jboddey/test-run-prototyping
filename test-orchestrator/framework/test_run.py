#!/usr/bin/env python3

import logger
from device import Device
from test_orchestrator import TestOrchestrator

LOGGER = logger.get_logger('test_run')

class TestRun:

    def __init__(self):
        LOGGER.info("Starting Test Run")

        # Get all components ready
        self._test_orchestrator = TestOrchestrator()
        #self._net_orchestrator = NetworkOrchestrator()

        # Get network ready (via Network orchestrator)
        LOGGER.info("Network is ready. Awaiting command from user interface...")
        LOGGER.info("Test Run will idle until a test attempt is started by the user")

        # This method would be called by the service worker (need to make it static?)
        self.test_device()

        LOGGER.info("Test Run is finished")

        # Tear down network
        LOGGER.info("Network is restored")

    def test_device(self):
        # Perform startup checks
        # Run test modules against device
        self._test_orchestrator.run_tests()

test_run = TestRun()