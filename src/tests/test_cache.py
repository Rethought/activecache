import threading
import time
from unittest import TestCase
from activecache import TriggeredCache


class TestingCache(TriggeredCache):
    def __init__(self):
        super(TestingCache, self).__init__()
        #self.value = None

    def refresh_cache(self):
        time.sleep(1)
        cv = self.__cached_value__
        if cv is None:
            cv = 0
        self.value = cv + 1


class TestActiveCache(TestCase):
    """ Some basic test cases. """
    def setUp(self):
        self.cache = TestingCache()

    def tearDown(self):
        self.cache.stop()
        self.cache = None

    def test_auto_start(self):
        self.assertEquals(self.cache.__cached_value__, None)
        self.assertEquals(self.cache.value, 1)
        self.assertEquals(self.cache.__cached_value__, 1)

    def test_trigger_behaviour(self):
        self.assertEquals(self.cache.value, 1)
        self.cache.refresh()
        self.assertEquals(self.cache.value, 1)
        time.sleep(1.5)
        self.assertEquals(self.cache.value, 2)

    def test_multiple_listeners_waiting_for_value(self):
        responses = []

        def listener():
            responses.append(self.cache.value)

        # start 20 threads all latching onto the cache. ensure each returns
        # the answer 1 only (ie the cache correctly blocked and refreshed only
        # once on start)
        threads = [threading.Thread(target=listener) for x in xrange(20)]
        [t.start() for t in threads]
        time.sleep(1.2)
        self.assertEquals(responses, [1] * 20)


class TestMultipleCache(TestCase):
    """ Ensure that the caches are independent """
    def setUp(self):
        self.cache_a = TestingCache()
        self.cache_b = TestingCache()

    def test_multi_cache(self):
        self.assertEquals(self.cache_a.value, 1)
        self.assertEquals(self.cache_b.value, 1)
        self.cache_b.refresh()
        time.sleep(1.2)
        self.assertEquals(self.cache_a.value, 1)
        self.assertEquals(self.cache_b.value, 2)
