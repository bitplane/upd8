"""
Tests for thread-safety and concurrency in the upd8 package.
"""

import threading
import time

from upd8 import Versioned, changes, field


class ConcurrentTest(Versioned):
    """Test class for concurrency"""

    value = field(0)

    @changes
    def increment(self):
        current = self.value
        # Small sleep to increase the chance of race conditions
        time.sleep(0.001)
        self.value = current + 1
        return self.value


def test_thread_safety():
    """Test that Versioned objects are thread-safe"""
    obj = ConcurrentTest()
    iterations = 50
    threads = 10

    def increment_version():
        for _ in range(iterations):
            obj.change()

    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=increment_version)
        threads_list.append(t)
        t.start()

    for t in threads_list:
        t.join()

    # Each thread increments the version 'iterations' times
    assert obj.version == iterations * threads


def test_concurrent_field_updates():
    """Test concurrent access to fields is thread-safe"""
    obj = ConcurrentTest()
    iterations = 50
    threads = 10

    def update_field():
        for _ in range(iterations):
            obj.value += 1

    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=update_field)
        threads_list.append(t)
        t.start()

    for t in threads_list:
        t.join()

    # Each thread increments the value 'iterations' times
    assert obj.value == iterations * threads


def test_concurrent_method_calls():
    """Test that concurrent method calls are thread-safe"""
    obj = ConcurrentTest()
    iterations = 50
    threads = 10

    def call_method():
        for _ in range(iterations):
            obj.increment()

    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=call_method)
        threads_list.append(t)
        t.start()

    for t in threads_list:
        t.join()

    # Each thread increments the value 'iterations' times
    assert obj.value == iterations * threads
