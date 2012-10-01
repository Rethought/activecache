from Queue import Queue
import threading
import time

import logging
logger = logging.getLogger()


class ActiveCache(object):
    """
    Abstract class (requires an implementation of `refresh_cache`) that
    caches the result of `refresh_cache` and actively refreshes it whenever a
    trigger occurs (as managed by the implementation of `trigger`).

    The regeneration happens off thread and when complete the cache reference
    is updated. Thus there is never a block whilst a referesh happens.

    The trigger to refresh comes from a call to the blocking method
    `trigger` returning. This is called from a dedicated thread.

    It is important for thread safety that code using the cached object
    understands the reference can change at any time, so it should be
    bound to a name in the local namespace and then used, rather than
    referenced multiple times from the cahce in one routine.

    To make concrete, subclass and implement:

    * refresh_cache(self)
    * trigger(self)
    """
    __cached_value__ = None
    __initialised__ = False  # set after first refresh

    def __init__(self, start_immediate=False):
        """
        This base implementation starts the watcher thread which blocks
        on `trigger`, calling `refresh_cache` each time the trigger returns.

        `start_immediate` means that the monitor thread will start on
        instantiation. If set True (the default), the monitor thread will start
        when `start()` is called or upon first request for the data value
        whereupon it will autostart.

        This is threadsafe - all callers during first refresh will be queued up
        and block until a first response is ready.
        """
        # queues held by requesters waiting for first result post
        # startup
        self.running = False
        self.notify_queues = []
        if start_immediate:
            self.start()

# left for the reader to get the gist, but not implemented to facilitate
# creating concrete instances composed of multiple base classes.
#
#    def refresh_cache(self):
#        """ Implement this to refresh the cached value. """
#        raise NotImplementedError()
#
#    def trigger(self):
#        """ Implement this to block and return whenever the cache needs to
#be refreshed. """
#        raise NotImplementedError()

    def start(self, notify_queue=None):
        """
        If notify_queue is set to a Queue.Queue object it will be
        sent a value when first refresh complete to signify that a response to
        client can be made.
        """
        if not self.initialised:
            logger.debug("Active Cache initialising")
            if notify_queue:
                self.notify_queues.append(notify_queue)
        if not self.running:
            logger.debug("Active cache set to RUNNING")
            self.running = True
            trigger_thread = threading.Thread(target=self.__monitor)
            trigger_thread.setDaemon(True)
            trigger_thread.start()

    def stop(self):
        """
        Stop monitoring the trigger
        """
        logger.debug("Active cache STOPPING")
        self.run = False

    def __monitor(self):
        """
        The loop which runs in a thread, monitoring the trigger and
        refreshing the cache.
        """
        while self.running:
            self.refresh_cache()
            if not self.initialised:
                self.initialised = True
                while self.notify_queues:
                    self.notify_queues.pop().put(0)
            self.trigger()

    def _set_value(self, x):
        """
        Set the cached value on the class
        """
        self.__cached_value__ = x

    def _get_value(self):
        """
        Get the cached value on the class. If not yet initialised, ensure the
        refresh loop is started and wait on first refresh before returing.
        """
        if not self.initialised:
            # Start the monitor. This is the auto-start on first
            # request behaviour and the request thread returns only when
            # first refresh has happened.
            q = Queue()
            self.start(q)
            # block until signalled we're ready
            q.get()

        return self.__cached_value__

    value = property(_get_value, _set_value)

    def _set_initialised(self, b):
        self.__initialised__ = b

    def _get_initialised(self):
        return self.__initialised__

    initialised = property(_get_initialised, _set_initialised)


class TimeoutCache(ActiveCache):
    """
    ActiveCache that refreshes every `timeout` seconds. Still abstract - you
    need to implement `refesh_cache`
    """
    def __init__(self, timeout=60, start_immediate=False):
        self.timeout = timeout
        super(TimeoutCache, self).__init__(start_immediate=start_immediate)

    def trigger(self):
        time.sleep(self.timeout)


class TestTimeoutCache(TimeoutCache):
    """
    Example implementation of a TimeoutCache to demonstrate the point.
    """
    def refresh_cache(self):
        logger.debug("Refreshing...")
        time.sleep(3)
        cv = self.__cached_value__
        if cv is None:
            cv = 0
        self.value = cv + 1
        logger.debug("refreshed.")

    def trigger(self):
        logger.debug("Waiting")
        super(TestTimeoutCache, self).trigger()


class TriggeredCache(ActiveCache):
    """
    An ActiveCache that is triggered by calling the `refresh` method. Handy for
    testing. Sub-class and implement refresh_cache to implement
    """
    def __init__(self, start_immediate=False):
        self.trigger_q = Queue()
        super(TriggeredCache, self).__init__(start_immediate=start_immediate)

    def trigger(self):
        """ Wait on a Queue to trigger """
        self.trigger_q.get()

    def refresh(self):
        self.trigger_q.put(0)

    def stop(self):
        """
        Call stop then unblock the trigger so the monitor loop can close.
        """
        super(TriggeredCache, self).stop()
        self.refresh()
