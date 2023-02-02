#!/usr/bin/env python3

TEST_MODULES_DIR = "test-modules"

class TestOrchestrator:

    def __init__(self):
        self._test_modules = {}
        self._load_modules()
        print("Finished loading test modules")

    # Load module and test information from each metadata.json file
    def _load_modules(self):
        print("Loading test modules")

    # Device initialisation has been completed
    # The orchestrator must now cycle through all enabled test modules
    def run_tests(self):
        print("Running test modules")

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
    