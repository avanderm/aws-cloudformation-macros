import collections
import copy
import logging
import re

import logger


class Substitutor:
    def __init__(self, base_name, base_resource, defaults={}):
        self.base_name = base_name
        self.base_resource = base_resource
        self.repl_defaults = defaults

    def name(self, replication_name):
        """
        Supply a name for the replicated resource.
        """
        tokens = re.split('[-_]', replication_name)

        return self.base_name + ''.join(map(lambda x: x.capitalize(), tokens))

    def __parse_cf_substitution(self, cloudformation):
        """
        Extract the expression, its variables and variables values of a Fn::Sub function.

        "Fn::Sub": [
            expression,
            {
                "variable1": ...,
                "variable2": ...
            }
        ]

        The variables are derived from the expression and AWS variables are omitted. Example:

        "${AWS::Region}-${variable1}-${variable2}-{variable3}"

        will result in the variables list

        [
            "variable1",
            "variable2",
            "variable3"
        ]
        """
        if isinstance(cloudformation, list):
            expression, supplied = cloudformation
        else:
            expression, supplied = cloudformation, {}

        variables = re.findall(r'\${repl:(.+?)}', expression)

        return expression, variables, supplied

    def substitute(self, replication_variables, cloudformation):
        """
        Modifies the CloudFormation substitution function by looking up values in the replication
        variables for variables mentioned in the substitution expression.
        """
        expression, variables, supplied = self.__parse_cf_substitution(cloudformation)

        # recursive calls
        for variable_name, variable_expression in supplied.items():
            self.traverse(replication_variables, variable_expression)

        for variable in variables:
            if variable in replication_variables:
                supplied[f'repl:{variable}'] = replication_variables[variable]

        return [ expression, supplied ]

    def traverse_list(self, replication_variables, cf_list):
        return list(
            self.traverse(replication_variables, entry) for entry in cf_list
        )

    def traverse_dict(self, replication_variables, cf_dict):
        """
        Modifies the dictionary recursively. If a key indicates a substitution function, its value
        is merged with the replication variables.
        """
        for k, v in cf_dict.items():
            if k == 'Fn::Sub':
                cf_dict[k] = self.substitute(replication_variables, v)
            elif k == 'Ref' and isinstance(v, dict):
                cf_dict[k] = self.traverse(replication_variables, v)
            elif k == 'Ref':
                search = re.search('^repl:(.+)$', v)

                if search and search.group(1) in replication_variables:
                    return replication_variables[search.group(1)]
                else:
                    cf_dict[k] = 'AWS::NoValue'
            else:
                cf_dict[k] = self.traverse(replication_variables, v)

        return cf_dict

    def traverse(self, replication_variables, cloudformation):
        if isinstance(cloudformation, dict):
            return self.traverse_dict(replication_variables, cloudformation)
        elif isinstance(cloudformation, list):
            return self.traverse_list(replication_variables, cloudformation)
        else:
            return cloudformation

    def process(self, replications):
        resources = {}

        if not replications:
            return resources

        for replication_name, substitutions in replications.items():
            name = self.name(replication_name)
            replication_variables = collections.ChainMap(substitutions, self.repl_defaults)

            resource = self.substitute(replication_variables, copy.deepcopy(self.base_resource))

            resources[name] = resource

        return resources


def is_tagged(resource : tuple):
    return 'SubReplicate' in resource[1]


def lambda_handler(event, context):
    fragment = event['fragment']
    logger.log_message(logging.INFO, fragment)

    resources = fragment['Resources'].copy()

    for name, resource in filter(is_tagged, resources.items()):
        params = resource.pop('SubReplicate')
        replications = params['Replications']
        defaults = params.get('Defaults', {})

        # check if we need to get data from the Mappings section
        if isinstance(replications, str):
            replications = fragment['Mappings'][replications]

        resources = Substitutor(name, resource, defaults).process(replications)

        # add replicated resources
        fragment['Resources'].update(resources)

        # remove the replicating resource
        del fragment['Resources'][name]

    logger.log_message(logging.INFO, fragment)

    return {
        'requestId': event['requestId'],
        'status': 'success',
        'fragment': fragment
    }


if __name__ == '__main__':
    template = {
        'fragment': {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Resources': {
                'BaseStack': {
                    'Type': 'AWS::CloudFormation::Stack',
                    'Replicate': {
                        'accommodation': {
                            'Parameters': {
                                'Variable1': 'foo',
                                'Variable2': 'bar'
                            }
                        },
                        'destination': {
                            'Parameters': {
                                'Variable1': 'fuu',
                                'Variable2': 'bor'
                            }
                        }
                    },
                    'Properties': {
                        'TemplateURL': 'stack.yml',
                        'Parameters': {
                            'PropertyOne': {
                                'Fn::Sub': '${Variable1}-${Variable2}'
                            }
                        }
                    }
                }
            }
        },
        'requestId': '1'
    }

    test = lambda_handler(template, None)
    print(test)
