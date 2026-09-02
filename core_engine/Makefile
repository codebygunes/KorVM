.PHONY: test test-e2e test-doomsday clean

test:
    python tests/unit/test_interpreter.py
    python tests/unit/test_jit.py

test-e2e:
    python tests/integration/test_impossible_e2e.py

test-doomsday:
    python tests/security/test_doomsday.py

clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
