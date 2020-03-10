from collections import OrderedDict

from cglue.utils.version import Version, VersionConstraint


class Component:
    @staticmethod
    def create_empty_config(name):
        return Component.normalize_config({
            'name':         name,
            'source_files': [f'{name}.c']
        })

    @staticmethod
    def normalize_config(config):
        defaults = OrderedDict({
            'name': 'ComponentName',
            'version': '1.0.0',
            'requires': {},
            'source_files': [],
            'multiple_instances': False,
            'instance_variables': {},
            'types': {},
            'runnables': {},
            'ports': {}
        })
        defaults.update(config)
        return defaults

    def __init__(self, name, config, types):
        self._name = name
        self.types = types
        self._config = self.normalize_config(config)

        self._version = Version(self._config['version'])
        self._dependencies = {component: VersionConstraint(constraint)
                              for component, constraint in self._config['requires'].items()}

        if self._config['instance_variables'] and not self._config['multiple_instances']:
            raise ValueError(f'Component {name} has instance variables but does not support multiple instances')

    @property
    def version(self):
        return self._version

    @property
    def name(self):
        return self._name

    @property
    def config(self):
        return self._config

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def instance_type(self):
        assert self._config['multiple_instances'], 'Component has no instance variable'
        return f'{self._name}_Instance_t'


class ComponentCollection:
    def __init__(self):
        self._components = {}

    def add(self, component: Component):
        self._components[component.name] = component

    def __getitem__(self, item):
        return self._components[item]

    def items(self):
        return self._components.items()

    def check_dependencies(self):
        failures = []
        for component in self._components.values():
            for required_component_name, version_constraint in component.dependencies.items():
                required_component = self._components[required_component_name]
                if not version_constraint.check(required_component.version):
                    failures.append(f'Component {component.name} failed to meet requirement'
                                    f' of {component.name} ({version_constraint})')

        if failures:
            message = '\n'.join(failures)
            raise Exception('Component dependency check failed:\n' + message)


class ComponentInstance:
    def __init__(self, component: Component, name):
        self._name = name
        self._prototype = component

        if name != component.name:
            assert component.config['multiple_instances']

    @property
    def component_name(self):
        return self._prototype.name

    @property
    def component(self):
        return self._prototype

    @property
    def instance_var_name(self):
        assert self._prototype.config['multiple_instances'], 'Component has no instance variable'
        return f'{self._prototype.name}_instance_{self._name}'
