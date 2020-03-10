import os
import unittest

from cglue import cglue
from cglue.plugins.BuiltinDataTypes import builtin_data_types
from cglue.plugins.RuntimeEvents import runtime_events
from cglue.plugins.ProjectConfigCompactor import project_config_compactor


def _create_generator(path):
    generator = cglue.CGlue(path)

    generator.add_plugin(project_config_compactor())
    generator.add_plugin(builtin_data_types())
    generator.add_plugin(runtime_events())

    generator.load()
    return generator


class TestComponentGeneration(unittest.TestCase):

    def _test_generated_files(self, project_file, component, expectations):
        os.chdir(os.path.dirname(__file__))

        root = os.path.dirname(project_file)
        generator = _create_generator(project_file)

        files = generator.update_component(component)

        self.maxDiff = None

        for generated_file, expected_file in expectations.items():
            with open(f'{root}/{expected_file}', 'r') as f:
                file_contents = f.read()

            self.assertEqual(file_contents, files[root + '/components/' + component + '/' + generated_file])

    def test_component_generation_does_not_raise_error(self):
        self._test_generated_files('../fixtures/00-demo-test/project_consumer_list.json', 'foo', {})

    def test_typedefs_of_required_component_are_generated(self):
        self._test_generated_files('../fixtures/01-component-dependency/project.json', 'foo', {
            'foo.h': 'foo.expected.h'
        })

    def test_runnables_can_implement_func_ptrs(self):
        self._test_generated_files('../fixtures/02-funcptr-runnable/project.json', 'foo', {
            'foo.h': 'foo.expected.h'
        })

    def test_multiple_component_instances(self):
        self._test_generated_files('../fixtures/03-multiple-instance/project.json', 'foo', {
            'foo.h': 'foo.expected.h'
        })
