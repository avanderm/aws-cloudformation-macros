import pytest

from main import Substitutor


class TestSubstitutor:
    @pytest.fixture
    def replications(self):
        return {
            'resource_one': {
                'variable1': 'foo',
                'variable2': 'bar'
            },
            'resource_two': {
                'variable1': 'fuu',
                'variable2': 'bor'
            }
        }

    def test_initialise(self):
        Substitutor('Base', None)

    def test_initialise_with_defaults(self):
        Substitutor('Base', None, {'variable': 'value'})

    def test_derive_name(self):
        """
        Test the naming of a replicated resource. Snake case is converted to camel case and added
        as a suffix to the base name.
        """
        obj = Substitutor('Base', None)
        assert obj.name('resource_one') == 'BaseResourceOne'

    def test_substitute_list_form(self):
        """
        Test substitution of replication variables in a CloudFormation sub function. In this case
        the sub command is given in list form, the first entry the string expression, the second
        entry a dictionary.

        Replication variables are prefixed by repl: in the string expression. Any replication
        variables already present in the dictionary are overwritten if present in the dictionary.
        """
        obj = Substitutor('Base', None)

        variables = {
            'variable1': 'value1',
            'variable2': 'value2'
        }

        cloudformation = [
            '${repl:variable1}-${repl:variable2}-${variable3}',
            {
                'repl:variable2': 'value4',
                'variable3': 'value3'
            }
        ]
        result = obj.substitute(variables, cloudformation)

        assert result == [
            '${repl:variable1}-${repl:variable2}-${variable3}',
            {
                'repl:variable1': 'value1',
                'repl:variable2': 'value2',
                'variable3': 'value3'
            }
        ]

    def test_substitute_string_form(self):
        """
        Test substitution of replication variables in a CloudFormation sub function. In this case
        the sub command is given in string form. It is converted to list form with any replication
        variable added to the dictionary (second list entry).
        """
        obj = Substitutor('Base', None)

        variables = {
            'variable1': 'value1',
            'variable2': 'value2'
        }

        cloudformation = '${repl:variable1}-${repl:variable2}-${variable3}'
        result = obj.substitute(variables, cloudformation)

        assert result == [
            '${repl:variable1}-${repl:variable2}-${variable3}',
            {
                'repl:variable1': 'value1',
                'repl:variable2': 'value2'
            }
        ]

    def test_substitute_nested(self):
        """
        Test substitution of replication variables in a CloudFormation sub function. In this case
        the sub command is given in list form. In addition, one of the entries in the dictionary,
        the second list entry, is itself a CloudFormation expression that needs to be dealt with
        recursively.
        """
        obj = Substitutor('Base', None)

        variables = {
            'variable1': 'value1',
            'variable2': 'value2'
        }

        cloudformation = [
            '${repl:variable1}-${repl:variable2}-${variable3}',
            {
                'repl:variable2': 'value4',
                'variable3': {
                    'Fn::ImportValue': {
                        'Fn::Sub': 'again-${repl:variable1}'
                    }
                }
            }
        ]
        result = obj.substitute(variables, cloudformation)

        assert result == [
            '${repl:variable1}-${repl:variable2}-${variable3}',
            {
                'repl:variable1': 'value1',
                'repl:variable2': 'value2',
                'variable3': {
                    'Fn::ImportValue': {
                        'Fn::Sub': [
                            'again-${repl:variable1}',
                            {
                                'repl:variable1': 'value1'
                            }
                        ]
                    }
                }
            }
        ]

    def test_traverse_list(self):
        obj = Substitutor('Base', None)

        result = obj.traverse_list(replications['resource_one'], [
            {
                'Fn::Sub': '${repl:variable1}-${repl:variable2}'
            },
            {
                'Fn::Sub': '${repl:variable2}-${repl:variable1}'
            }
        ])

        assert base == {
            'Type': 'AWS::Service::Resource',
            'Properties': {
                'Property1': [
                    {
                        'Fn::Sub': [
                            '${repl:variable1}-${repl:variable2}',
                            {
                                'repl:variable1': 'foo',
                                'repl:variable2': 'bar'
                            }
                        ]
                    },
                    {
                        'Fn::Sub': [
                            '${repl:variable2}-${repl:variable1}',
                            {
                                'repl:variable1': 'foo',
                                'repl:variable2': 'bar'
                            }
                        ]
                    }
                ]
            }
        }

    def test_traverse(self, replications):
        base = {
            'Type': 'AWS::Service::Resource',
            'Properties': {
                'Property1': {
                    'Fn::Sub': '${repl:variable1}-${repl:variable2}'
                }
            }
        }

        obj = Substitutor('Base', base)

        obj.traverse(replications['resource_one'], base)

        assert base == {
            'Type': 'AWS::Service::Resource',
            'Properties': {
                'Property1': {
                    'Fn::Sub': [
                        '${repl:variable1}-${repl:variable2}',
                        {
                            'repl:variable1': 'foo',
                            'repl:variable2': 'bar'
                        }
                    ]
                }
            }
        }

    def test_process(self, replications):
        base = {
            'Type': 'AWS::Service::Resource',
            'Properties': {
                'Property1': {
                    'Fn::Sub': [
                        '${repl:variable1}-${repl:variable2}',
                        {
                            'repl:variable2': 'test'
                        }
                    ]
                }
            }
        }

        obj = Substitutor('Base', base)

        resources = obj.process(replications)

        assert resources == {
            'BaseResourceOne': {
                'Type': 'AWS::Service::Resource',
                'Properties': {
                    'Property1': {
                        'Fn::Sub': [
                            '${repl:variable1}-${repl:variable2}',
                            {
                                'repl:variable1': 'foo',
                                'repl:variable2': 'bar'
                            }
                        ]
                    }
                }
            },
            'BaseResourceTwo': {
                'Type': 'AWS::Service::Resource',
                'Properties': {
                    'Property1': {
                        'Fn::Sub': [
                            '${repl:variable1}-${repl:variable2}',
                            {
                                'repl:variable1': 'fuu',
                                'repl:variable2': 'bor'
                            }
                        ]
                    }
                }
            }
        }
