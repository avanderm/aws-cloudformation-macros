import os

import botocore
import boto3
import cfn_flip
import pytest


class TestMacro:
    @pytest.fixture
    def client(self):
        session = boto3.session.Session(profile_name=os.getenv('AWS_PROFILE', 'default'))
        client = session.client('cloudformation')

        return client

    def load_template(self, name):
        with open(name) as f:
            template = cfn_flip.load_yaml(f)
            template['Transform'] = os.getenv('MACRO_NAME')

        return cfn_flip.dump_yaml(template)

    def create_stack(self, client, stack_name, template_file):
        response = client.create_stack(
            StackName=stack_name,
            TemplateBody=self.load_template(template_file),
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_AUTO_EXPAND'
            ]
        )

        waiter = client.get_waiter('stack_create_complete')
        waiter.wait(StackName=response['StackId'])

    def delete_stack(self, client, stack_name):
        client.delete_stack(StackName=stack_name)

        waiter = client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name)

    @pytest.mark.parametrize('stack_name,template_file', [
        (
            f'integration-test-substitution-replicate',
            'tests/integration/templates/global_level.yml'
        ),
        (
            f'integration-test-substitution-replicate',
            'tests/integration/templates/global_level_with_mappings.yml'
        )
    ])
    def test_stack(self, client, stack_name, template_file):
        try:
            self.create_stack(client, stack_name, template_file)

            response = client.describe_stack_resources(StackName=stack_name)

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
            self.delete_stack(client, stack_name)

    def test_stack_empty(self, client):
        stack_name = f'integration-test-substitution-replicate'
        template_file = 'tests/integration/templates/global_level_empty.yml'

        try:
            self.create_stack(client, stack_name, template_file)

            response = client.describe_stack_resources(StackName=stack_name)

            resources_names = [
                resource['LogicalResourceId'] for resource in response['StackResources']
            ]

            assert len(resources_names) == 1
            assert 'StaticRole' in resources_names
        except botocore.exceptions.WaiterError as error:
            assert False
        finally:
            self.delete_stack(client, stack_name)
