# Substitution Replicate V1

__The substitution replicate macro combines a base resource with an arbitrary number of parameter dictionaries, replicating the base resource into multiple new ones. The parameter dictionary is used to substitute in parameters needed by the !Sub command in the base resource.__

## Example

CloudFormation stack using the substitution replicate to replicate an `AWS::CloudFormation::Stack` resource.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform:
    - SubReplicate-production

Mappings:
    stacks:
        stack_one:
            Variable1: foo
            Variable2: bar
        stack_two:
            Variable1: fuu
            Variable2: bor

Resources:
    BaseStack:
        Type: AWS::CloudFormation::Stack
        SubReplicate: stack
        Properties:
            Property1: !Sub ${Variable1}
            Property2: !Sub ${Variable1}-${Variable2}
```

In the example above, the `BaseStack` resource will be replicated into two new resources:

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform:
    - SubReplicate-production

Resources:
    BaseStackStackOne:
        Type: AWS::CloudFormation::Stack
        Properties:
            Property1: foo
            Property2: foobar

    BaseStackStackTwo:
        Type: AWS::CloudFormation::Stack
        Properties:
            Property1: fuu
            Property2: fuubor
```

Parameters defined in the `Mappings` section will be substituted into the base resource where needed. The Replicate field determines which subsection from `Mappings` is used. The replication parameters can also be defined in the `Replicate` field itself.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform:
    - SubReplicate-production

Resources:
    BaseStack:
        Type: AWS::CloudFormation::Stack
        SubReplicate:
            stack_one:
                Variable1: foo
                Variable2: bar
            stack_two:
                Variable1: fuu
                Variable2: bor
        Properties:
            Property1: !Sub ${Variable1}
            Property2: !Sub ${Variable1}-${Variable2}
```
 Or with the `AWS::Include` macro:

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform:
    - SubReplicate-production

Resources:
    BaseStack:
        Type: AWS::CloudFormation::Stack
        SubReplicate:
            Fn::Transform:
                Name: AWS::Include
                Parameters:
                    Location: configuration.yml
        Properties:
            Property1: !Sub ${Variable1}
            Property2: !Sub ${Variable1}-${Variable2}
```

The referenced file `configuration.yml` will be of the form

```yaml
stack_one:
    Variable1: foo
    Variable2: bar
stack_two:
    Variable1: fuu
    Variable2: bor
```

## Scope

The scope of the substitute replicator is at the global level. Since it replicates resources it must be able to add and remove resources from the `Resources` section in CloudFormation. To declare it, one can use

```yml
Transform:
    - SubReplicate-production
```

## Tests

After deploying a macro for an environment, run the tests

```bash
PYTHONPATH=src:.. MACRO_ENVIRONMENT=<environment> python -m pytest tests
```

This will run both unit and integration tests.