ActiveCache
===========

We found the need to have a particular kind of in-memory cache to cache the
result of an operation that involved an expensive DB call plus some computation.
We wanted the cache to:

* be kept fresh, either by refreshing on schedule or on an event
* be thread-safe
* not to block whilst refreshing (an IO-bound operation in our case)

This is purely in-process and probably has a narrow range of use-cases. It is
probably also re-inventing the wheel - we'll surely stumble across another,
better implementation before long!

To use you'll want to sub-class `ActiveCache` and implement `refresh_cache`
which computes and returns the value to cache, and possibly `trigger` which
blocks and returns only when you wish the cache to refresh. 

`TimeoutCache` is an implementation which refreshes the cache on a fixed
interval. By sub-classing and implementing `refresh_cache` you will have a
cache that refreshes on a periodic basis.

Read the code comments for more info.

Installation
------------

With pip::

 > pip install activecache

From a GIT checkout::

 > python setup.py install


Testing
-------

If you have a GIT checkout of this repository you can run the tests as follows:

* create and activate a virtualenv for the project
* `pip install -r test_requirements`
* `./runtests.sh`

This will run all the unit tests, create a coverage report
(see `htmlcov/index.html`) and also PEP8 check the code (see `pep8.txt`).

Jenkins
-------

If you like to use Jenkins you may like to make use of our build script
`build.sh`. If executed by Jenkins as a build step you can then ingest the
output as follows:

* Cobertura plugin can read `coverage.xml`
* xUnit plugin can read JUnit formatted `nosetests.xml`
* violations plugin: add `pep8.txt` to the pep8 field

.. include:: <isonum.txt>
Copyright |copy| 2012 ReThought Ltd, all rights reserved
