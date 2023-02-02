#!/usr/bin/env python3

import logger

TEST_MODULES_DIR = "test-modules"
LOGGER = logger.get_logger('test_orc')

class TestOrchestrator:

    def __init__(self):
        self._test_modules = {}
        self._load_modules()
        LOGGER.info("Test modules loaded")

    # Load module and test information from each metadata.json file
    def _load_modules(self):
        LOGGER.debug("Loading test modules from /" + TEST_MODULES_DIR)

    # Device initialisation has been completed
    # The orchestrator must now cycle through all enabled test modules
    def run_tests(self):
        LOGGER.info("Beginning test run")

class Test:

    def __init__(self):
        self.id = None
        self.name = None
        self.description = None
        self.category = None

class TestModule:

    def __init__(self):
        self.name = None
        self.description = None
        self.tests = {}