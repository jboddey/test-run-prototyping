#!/usr/bin/env python3

import docker
import json
import logger
import os
import time

TEST_MODULES_DIR = "test-modules"
TEST_MODULE_METADATA = "metadata.json"
LOGGER = logger.get_logger('test_orc')

class TestOrchestrator:

    def __init__(self):
        self._test_modules = []
        self.test_results = []
        self._load_modules()
        self._build_modules()

    def _build_modules(self):
        LOGGER.info("Building test modules")

        for test_module in self._test_modules:
            self._build_module(test_module)

    def _build_module(self, test_module):
        LOGGER.info("Building test module " + test_module.name)
        client = docker.from_env()
        client.images.build(
            dockerfile=test_module.build_file,
            path="test-modules/" + test_module.module_dir,
            tag="test-run/" + test_module.module_dir
        )

    # Load module and test information from each metadata.json file
    def _load_modules(self):
        LOGGER.debug("Loading test modules from /" + TEST_MODULES_DIR)

        loaded_modules = "Loaded the following test modules: "

        for module_dir in os.listdir(TEST_MODULES_DIR):
            module_metadata = json.load(open(os.path.join(TEST_MODULES_DIR, module_dir, TEST_MODULE_METADATA), 'r'))

            test_module = TestModule()
            test_module.name = module_metadata['name']
            test_module.description = module_metadata['description']
            test_module.build_file = module_metadata['build_file']
            test_module.module_dir = module_dir

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

            loaded_modules += test_module.name + " (" + str(num_module_tests) + ") "

        LOGGER.info(loaded_modules)

    # Device initialisation has been completed
    # The orchestrator must now cycle through all enabled test modules
    def run_tests(self):
        LOGGER.info("Beginning test run")
        while len(self._test_modules) > 0:
            next_module = self._test_modules.pop()
            container = self._run_test_module(next_module)

            # Extract results from test module

    def _run_test_module(self, test_module):
        LOGGER.info("Starting test module " + test_module.name)

        module_logger = logger.get_logger(test_module.module_dir)

        client = docker.from_env()
        container = client.containers.run(
            "test-run/" + test_module.module_dir,
            remove=True,
            cap_add=["NET_ADMIN"],
            name="tr-ct-" + test_module.module_dir,
            network_mode="none",
            detach=True,
            volumes=[
                os.getcwd() + "/runtime/" + test_module.module_dir + ":/runtime"
            ]
        )

        stream = container.logs(stream=True)
        for log in stream:
            module_logger.info(log.strip().decode('utf-8'))

        LOGGER.info("Test module " + test_module.name + " has finished. Collecting results...")

        # TODO: If results file does not exist, then report module failed
        results = json.load(open('runtime/module_' + test_module.module_dir + "/output/result.json", 'r'))
        self.test_results.extend(results['results'])


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
        self.build_file = None
        self.module_dir = None
        self.tests = []

