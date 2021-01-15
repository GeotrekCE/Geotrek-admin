tests_settings_file = os.path.join(os.path.dirname(__file__), 'env_tests.py')
with open(tests_settings_file, 'r') as f:
    exec(f.read())

TREKKING_TOPOLOGY_ENABLED = False
