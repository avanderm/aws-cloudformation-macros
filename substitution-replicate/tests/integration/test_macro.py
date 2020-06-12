import os

import botocore
import boto3
import cfn_flip
import pytest


class TestMacro:
    client = boto3.client('cloudformation')

    def load_template(self, name):
        with open(name) as f:
            template = cfn_flip.load_yaml(f)
            template['Transform'] = f'SubReplicate-{os.getenv("MACRO_ENVIRONMENT")}'

        return cfn_flip.dump_yaml(template)

    @property
    def tags(self):
        return [
            {
                'Key': 'Pillar',
                'Value': os.getenv('PILLAR')
            },
            {
                'Key': 'Domain',
                'Value': os.getenv('DOMAIN')
            },
            {
                'Key': 'Team',
                'Value': os.getenv('DOMAIN')
            },
            {
                'Key': 'Environment',
                'Value': os.getenv('MACRO_ENVIRONMENT')
            },
            {
                'Key': 'Owner',
                'Value': os.getenv('USER')
            },
            {
                'Key': 'Project',
                'Value': 'cloudformation'
            }
        ]

    def create_stack(self, stack_name, template_file):
        response = self.client.create_stack(
            StackName=stack_name,
            TemplateBody=self.load_template(template_file),
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_AUTO_EXPAND'
            ],
            Tags=self.tags
        )

        waiter = self.client.get_waiter('stack_create_complete')
        waiter.wait(StackName=response['StackId'])

    def delete_stack(self, stack_name):
        self.client.delete_stack(StackName=stack_name)

        waiter = self.client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name)

    @pytest.mark.parametrize('stack_name,template_file', [
        (
            f'{os.getenv("DOMAIN")}-macro-resource-replicate-integration-{os.getenv("MACRO_ENVIRONMENT")}',
            'tests/integration/templates/global_level.yml'
        ),
        (
            f'{os.getenv("DOMAIN")}-macro-resource-replicate-integration-{os.getenv("MACRO_ENVIRONMENT")}',
            'tests/integration/templates/global_level_with_mappings.yml'
        )
    ])
    def test_stack(self, stack_name, template_file):
        try:
            self.create_stack(stack_name, template_file)

            response = self.client.describe_stack_resources(StackName=stack_name)

            resources_names = [
                resource['LogicalResourceId'] for resource in response['StackResources']
            ]

            assert len(resources_names) == 3
            assert 'RoleStepFunction' in resources_names
            assert 'RoleFargate' in resources_names
            assert 'StaticRole' in resources_names
        except botocore.exceptions.WaiterError as error:
            assert False
        finally:
            self.delete_stack(stack_name)

    def test_stack_empty(self):
        stack_name = f'{os.getenv("DOMAIN")}-macro-resource-replicate-integration-{os.getenv("MACRO_ENVIRONMENT")}'
        template_file = 'tests/integration/templates/global_level_empty.yml'

        try:
            self.create_stack(stack_name, template_file)

            response = self.client.describe_stack_resources(StackName=stack_name)

            resources_names = [
                resource['LogicalResourceId'] for resource in response['StackResources']
            ]

            assert len(resources_names) == 1
            assert 'StaticRole' in resources_names
        except botocore.exceptions.WaiterError as error:
            assert False
        finally:
            self.delete_stack(stack_name)
