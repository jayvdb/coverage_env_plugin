# coverage_env_plugin

Set environment variables of the environment markers

Enable by adding the following to coverage configuration file such as `setup.cfg`:

```
[coverage:coverage_env_plugin]
markers = True

[coverage:run]
markers = True

plugins =
    coverage_env_plugin
    coverage_config_reload_plugin
```

Depends on [`coverage_config_reload_plugin`](https://github.com/jayvdb/coverage_config_reload_plugin).
