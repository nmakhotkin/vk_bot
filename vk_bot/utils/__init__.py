
import logging
import pkg_resources as pkg
import shutil
import time
import urllib

from vk_bot import version


LOG = logging.getLogger(__name__)


def get_file_path(path):
    return pkg.resource_filename(
        version.version_info.package,
        path
    )


def with_retry(count=3, delay=1, accept_none=False):
    def decorator(func):
        def wrapped(*args, **kwargs):
            counter = 0

            while counter <= count:
                try:
                    result = func(*args, **kwargs)
                    if not accept_none and not result:
                        raise Exception("The function returns None.")

                    return result
                except Exception as e:
                    LOG.warn("Retry got error: %s" % e)

                    counter += 1
                    time.sleep(delay)
        return wrapped
    return decorator


def download_picture(url):
    file_path, _ = urllib.urlretrieve(url)

    if '.' not in file_path:
        shutil.move(file_path, '%s.png' % file_path)
        file_path += '.png'

    return file_path
