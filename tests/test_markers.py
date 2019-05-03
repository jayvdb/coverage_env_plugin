import os

from distutils.version import LooseVersion
from unittest import TestCase

from unittest_mixins import TempDirMixin

import coverage_env_plugin

from coverage import __version__ as coverage_version
from coverage.backward import StringIO
from coverage.control import Coverage


class ConfigMarkersPluginTest(TempDirMixin, TestCase):
    """Test plugin through the Coverage class."""

    def _reset_env(self):
        if 'OS_NAME' in os.environ:
            del os.environ['OS_NAME']
        assert 'OS_NAME' not in os.environ
        coverage_env_plugin.DEFAULT_ENVIRONMENT = {}

    def test_plugin_init(self):
        self._reset_env()

        self.make_file('.coveragerc', """\
            [run]
            plugins = coverage_env_plugin

            [coverage_env_plugin]
            markers = True

            [report]
            exclude_lines =
              foobar: no cover
            """)

        cov = Coverage()
        assert cov.config.get_option('report:exclude_lines') == ['foobar: no cover']

        cov.start()
        cov.stop()

        assert cov.config.plugins == ['coverage_env_plugin']
        assert cov.config.plugin_options =={'coverage_env_plugin': {'markers': 'True'}}

        assert 'OS_NAME' in coverage_env_plugin.DEFAULT_ENVIRONMENT
        assert 'OS_NAME' in os.environ

    def test_reload_plugin_init(self):
        self._reset_env()

        self.make_file('.coveragerc', """\
            [run]
            plugins = coverage_env_plugin, coverage_config_reload_plugin
            [coverage_env_plugin]
            markers = True
            [report]
            exclude_lines =
              pragma ${OS_NAME}: no cover
            """)

        debug_out = StringIO()
        cov = Coverage(config_file='.coveragerc', debug=['sys'])
        cov._debug_file = debug_out
        cov.set_option('run:plugins', ['coverage_env_plugin', 'coverage_config_reload_plugin'])
        cov.start()
        cov.stop()

        assert cov.config.get_option('coverage_env_plugin:markers') == 'True'

        out_lines = [line.strip() for line in debug_out.getvalue().splitlines()]
        self.assertIn('plugins.file_tracers: -none-', out_lines)

        expected_end = [
            '-- sys: coverage_config_reload_plugin.ConfigReloadPlugin -----',
            'configreload: True',
            '-- end -------------------------------------------------------',
        ]
        self.assertEqual(expected_end, out_lines[-len(expected_end):])

        if LooseVersion(coverage_version) >= LooseVersion('4.6'):
            self.assertIn('plugins.configurers: coverage_config_reload_plugin.ConfigReloadPlugin', out_lines)

    def test_os_name(self):
        self._reset_env()

        self.make_file('.coveragerc', """\
            [run]
            plugins = coverage_env_plugin, coverage_config_reload_plugin
            [coverage_env_plugin]
            markers = True
            [report]
            exclude_lines =
              pragma ${OS_NAME}: no cover
            """)

        debug_out = StringIO()
        cov = Coverage(config_file='.coveragerc')

        assert cov.config.get_option('report:exclude_lines') == ['pragma : no cover']
        assert cov.config.exclude_list == ['pragma : no cover']

        assert cov.config.get_option('coverage_env_plugin:markers') == 'True'

        cov.start()
        cov.stop()

        assert 'OS_NAME' in coverage_env_plugin.DEFAULT_ENVIRONMENT

        os_name = coverage_env_plugin.DEFAULT_ENVIRONMENT['OS_NAME']
        os_name_pragma = 'pragma {}: no cover'.format(os_name)


        assert cov.config.get_option('report:exclude_lines') == [os_name_pragma]
        assert cov.config.exclude_list == [os_name_pragma]

    def __test_os_name_without_reload(self):
        self._reset_env()

        self.make_file('.coveragerc', """\
            [run]
            plugins = coverage_env_plugin
            [coverage_env_plugin]
            markers = True
            [report]
            exclude_lines =
              pragma ${OS_NAME}: no cover
            """)

        debug_out = StringIO()
        cov = Coverage(config_file='.coveragerc')

        assert cov.config.get_option('report:exclude_lines') == ['pragma : no cover']
        assert cov.config.exclude_list == ['pragma : no cover']

        assert cov.config.get_option('coverage_env_plugin:markers') == 'True'

        cov.start()
        cov.stop()

        assert 'OS_NAME' in coverage_env_plugin.DEFAULT_ENVIRONMENT

        os_name = coverage_env_plugin.DEFAULT_ENVIRONMENT['OS_NAME']
        os_name_pragma = 'pragma {}: no cover'.format(os_name)


        assert cov.config.get_option('report:exclude_lines') == [os_name_pragma]
        assert cov.config.exclude_list == [os_name_pragma]
