ActiveCache
===========

We found the need to have a particular kind of in-memory cache to cache the result of an
operation that involved a DB call plus computation. We wanted the cache to:

* be kept fresh, either by refreshing on schedule or on an event
* be thread-safe
* not to block whilst refreshing (an IO-bound operation in our case)

This is purely in-process and probably has a narrow range of use-cases. It is probably
also re-inventing the wheel - we'll surely stumble across another, better implementation
before long!

To use you'll want to sub-class `ActiveCache` and implement `refresh_cache` which computes and
returns the value to cache, and possibly `trigger` which returns only when you wish the cache
to refresh. 

`TimeoutCache` is an implementation which refreshes the cache on a fixed interval. By sub-classing
and implementing `refresh_cache` you will have a cache that refreshes on a periodic basis.

Read the code comments for more info.
