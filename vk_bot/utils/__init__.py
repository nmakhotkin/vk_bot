
import logging
import time
import pkg_resources as pkg

from vk_bot import version


LOG = logging.getLogger(__name__)


def get_file_path(path):
    return pkg.resource_filename(
        version.version_info.package,
        path
    )


def with_retry(count=3, delay=1):
    def decorator(func):
        def wrapped(*args, **kwargs):
            counter = 0

            while counter <= count:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    LOG.warn("Retry got error: %s" % e)

                    counter += 1
                    time.sleep(delay)
        return wrapped
    return decorator

