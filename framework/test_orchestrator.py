#!/usr/bin/env python3

import json
import logger
import os

TEST_MODULES_DIR = "test-modules"
TEST_MODULE_METADATA = "metadata.json"
LOGGER = logger.get_logger('test_orc')

class TestOrchestrator:

    def __init__(self):
        self._test_modules = []
        self._load_modules()

    def _build_modules(self):
        LOGGER.info("Building test modules")
        # TODO: 

    # Load module and test information from each metadata.json file
    def _load_modules(self):
        LOGGER.debug("Loading test modules from /" + TEST_MODULES_DIR)

        loaded_modules = "Loaded the following modules: "

        for module_dir in os.listdir(TEST_MODULES_DIR):
            module_metadata = json.load(open(os.path.join(TEST_MODULES_DIR, module_dir, TEST_MODULE_METADATA), 'r'))

            test_module = TestModule()
            test_module.name = module_metadata['name']
            test_module.description = module_metadata['description']

            self._test_modules.append(test_module)

            num_module_tests = 0

            for module_test in module_metadata['tests']:
                test_case = Test()
                test_case.id = module_test['id']
                test_case.name = module_test['name']
                test_case.category = module_test['category']
                test_case.description = module_test['description']

                test_module.tests.append(test_case)

                num_module_tests += 1

            loaded_modules += test_module.name + " (" + str(num_module_tests) + "), "

        LOGGER.info(loaded_modules)

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
        self.tests = []

