
import pkg_resources as pkg

from vk_bot import version


def get_file_path(path):
    return pkg.resource_filename(
        version.version_info.package,
        path
    )