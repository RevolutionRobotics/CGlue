from collections import OrderedDict
from typing import Dict, Any

from cglue.function import FunctionPrototype
from cglue.data_types import TypeCollection
from cglue.utils.dict_processor import DictProcessor


class PortType:
    def __init__(self, types: TypeCollection, config: Dict[str, Any]):
        self._types = types
        self.config = config
        self._data_processor = DictProcessor(
            required_keys=config['def_attributes'].get('required', set()),
            optional_keys=config['def_attributes'].get('optional', {})
        )

        self.get = config.get

    def __getitem__(self, item):
        return self.config[item]

    @property
    def is_consumer(self) -> bool:
        return self.config.get('consumes', False)

    @property
    def is_provider(self) -> bool:
        return self.config.get('provides', False)

    def declare_functions(self, port):
        raise NotImplementedError

    def create_component_functions(self, port):
        raise NotImplementedError

    def create_runtime_functions(self, port):
        raise NotImplementedError

    def process_port(self, component, pn, port_data):

        attributes = self.config['def_attributes']
        port_data = port_data.copy()
        port_type = port_data['port_type']
        del port_data['port_type']
        return Port(component, pn, {
            'port_type': port_type,
            **attributes['static'],
            **self._data_processor.process(port_data)
        }, self)


class Port:
    functions: Dict[str, FunctionPrototype]

    def __init__(self, component, port_name, port_data, port_type: PortType):
        self.port_name = port_name
        self.component_name = component.name
        self.port_type = port_type
        self.port_data = port_data
        self._owner = component

        self._full_name = f'{component.name}/{port_name}'

        self.functions = port_type.declare_functions(self)

        self.get = self.port_data.get

    def declare_function(self, function_name, return_type, arguments=None):
        args = OrderedDict()
        if self._owner.config['multiple_instances']:
            args['instance'] = {'direction': 'inout', 'data_type': self._owner.types.get(self._owner.instance_type)}
        if arguments:
            args.update(arguments)
        return FunctionPrototype(function_name, return_type, args)

    @property
    def full_name(self):
        return self._full_name

    @property
    def is_consumer(self) -> bool:
        return self.port_type.is_consumer

    @property
    def is_provider(self) -> bool:
        return self.port_type.is_consumer

    def __getitem__(self, item):
        return self.port_data[item]

    def __contains__(self, item):
        return item in self.port_data

    def create_runtime_functions(self):
        return self.port_type.create_runtime_functions(self)

    def create_component_functions(self):
        return self.port_type.create_component_functions(self)
