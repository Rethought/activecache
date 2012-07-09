from Queue import Queue
import threading
import time


class ActiveCache(object):
    """ Abstract class (requires an implementation of `refresh_cache`) that
caches the result of `refresh_cache` and actively refreshes it whenever a
trigger occurs (as managed by the implementation of `trigger`).

The regeneration happens off thread and when complete the cache reference
is updated. Thus there is never a block whilst a referesh happens.

The trigger to refresh comes from a call to the blocking method 
`trigger` returning. This is called from a dedicated thread.

It is important for thread safety that code using the cached object
understands the reference can change at any time, so it should be 
bound to a name in the local namespace and then used, rather than 
referenced multiple times from the cahce in one routine. """
    __cached_value__ = None
    __initialised__ = False # set after first refresh
    
    def __init__(self, start_immediate=False):
        """ This base implementation starts the watcher thread which blocks
on `trigger`, calling `refresh_cache` each time the trigger returns.

start_immediate means that the monitor thread will start on instantiation.
If set True (the default), the monitor thread will start when `start()`
is called or upon first request for the data value whereupon it will autostart.

This is threadsafe - all callers during first refresh will be queued up and
block until a first response is ready.
"""
        # queues held by requestors waiting for first result post
        # startup
        self.running = False
        self.notify_queues = []
        if start_immediate:
            self.start()
        
    def refresh_cache(self):
        """ Implement this to refresh the cached value. """
        raise NotImplementedError()

    def trigger(self):
        """ Implement this to block and return whenever the cache needs to 
be refreshed. """        
        raise NotImplementedError()

    def start(self, notify_queue=None):
        """ If notify_queue is set to a Queue.Queue object it will be 
sent a value when first refresh complete to signify that a response to 
client can be made. """
        if not self.initialised:
            if notify_queue:
                self.notify_queues.append(notify_queue)
        if not self.running:
            self.running = True
            trigger_thread = threading.Thread(target=self.__monitor)
            trigger_thread.setDaemon(True)
            trigger_thread.start()

    def stop(self):
        """ Stop monitoring the trigger """
        self.run = False

    def __monitor(self):
        """ The loop which runs in a thread, monitoring the trigger and
refreshing the cache."""
        while self.running:
            self.refresh_cache()
            if not self.initialised:
                self.initialised = True
                while self.notify_queues:
                    self.notify_queues.pop().put(0)
            self.trigger()

    def _set_value(self, x):
        """ Set the cached value on the class """
        self.__class__.__cached_value__ = x

    def _get_value(self):
        """ Get the cached value on the class. If not yet initialised, ensure the refresh 
loop is started and wait on first refresh before returing."""
        if not self.initialised:
            # Start the monitor. This is the auto-start on first
            # request behaviour and the request thread returns only when 
            # first refresh has happened.
            q = Queue()
            self.start(q)
            # block until signalled we're ready
            q.get()

        return self.__class__.__cached_value__ 

    value = property(_get_value, _set_value)

    def _set_initialised(self, b):
        self.__class__.__initialised__ = b

    def _get_initialised(self):
        return self.__class__.__initialised__

    initialised = property(_get_initialised, _set_initialised)


class TimeoutCache(ActiveCache):
    """ ActiveCache that refreshes every `timeout` seconds. Still abstract - you need to
implement `refesh_cache`"""
    def __init__(self, timeout=60, start_immediate=False):
        self.timeout = timeout
        super(TimeoutCache, self).__init__(start_immediate=start_immediate)

    def trigger(self):
        time.sleep(self.timeout)


class TestTimeoutCache(TimeoutCache):
    """ Test implementation of a TimeoutCache """
    def refresh_cache(self):
        print("Refreshing...")
        time.sleep(3)
        cv = self.__class__.__cached_value__
        if cv is None:
            cv = 0
        self.value = cv + 1
        print("refreshed.")

    def trigger(self):
        print("Waiting")
        super(TestTimeoutCache, self).trigger()
