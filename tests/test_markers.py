from distutils.version import LooseVersion
from unittest import TestCase

from unittest_mixins import TempDirMixin

import coverage_env_plugin

from coverage import __version__ as coverage_version
from coverage.backward import StringIO
from coverage.control import Coverage


class ConfigMarkersPluginTest(TempDirMixin, TestCase):
    """Test plugin through the Coverage class."""

    def test_init(self):
        coverage_env_plugin.DEFAULT_ENVIRONMENT = {}
        cov = Coverage()
        cov.set_option('run:plugins', ['coverage_env_plugin'])
        cov.start()
        cov.stop()

        assert 'OS_NAME' in coverage_env_plugin.DEFAULT_ENVIRONMENT

    def test_os_name(self):
        self.make_file('.coveragerc', """\
            [report]
            exclude_lines =
              pragma ${OS_NAME}: no cover
            """)

        debug_out = StringIO()
        cov = Coverage()
        assert cov.config.get_option('report:exclude_lines') == ['pragma : no cover']

        cov.set_option('run:plugins', ['coverage_env_plugin', 'coverage_config_reload_plugin'])
        cov.start()
        cov.stop()

        assert 'OS_NAME' in coverage_env_plugin.DEFAULT_ENVIRONMENT

        os_name = coverage_env_plugin.DEFAULT_ENVIRONMENT['OS_NAME']

        assert cov.config.get_option('report:exclude_lines') == ['pragma {}: no cover'.format(os_name)]
