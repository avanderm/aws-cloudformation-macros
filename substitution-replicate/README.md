# Substitution Replicate

__The substitution replicate macro combines a base resource with an arbitrary number of parameter dictionaries, replicating the base resource into multiple new ones. The parameter dictionary is used to substitute in parameters needed by the !Sub or !Ref command in the base resource.__

This documentation covers the latest version. For documentation of earlier versions, see [V1](./README-v1.md).

## Example

CloudFormation stack using the substitution replicate to replicate an `AWS::CloudFormation::Stack` resource. The `Replicate` field indicates you want to replicate with the subfield `Replicates`. Defaults can be specified in the subfield `Defaults`. Any replication variables for which there is no value in either the defaults or the replicates will be substituted with `AWS::NoValue`. Variables marked for replication are prefixed with `repl:`.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform:
    - SubReplicate

Mappings:
    stacks:
        stack_one:
            Variable1: foo
            Variable3: 1
        stack_two:
            Variable1: fuu
            Variable2: bor

Resources:
    BaseStack:
        Type: AWS::CloudFormation::Stack
        SubReplicate:
            Replicates: stacks
            Defaults:
                Variable2: bar
        Properties:
            Property1: !Ref repl:Variable1
            Property2: !Sub ${repl:Variable1}-${repl:Variable2}
            Property3: !Ref repl:Variable3
```

In the example above, the `BaseStack` resource will be replicated into two new resources:

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform:
    - SubReplicate

Resources:
    BaseStackStackOne:
        Type: AWS::CloudFormation::Stack
        Properties:
            Property1: foo
            Property2: foobar
            Property3: 1

    BaseStackStackTwo:
        Type: AWS::CloudFormation::Stack
        Properties:
            Property1: fuu
            Property2: fuubor
            Property3: !Ref AWS::NoValue
```

Parameters defined in the `Mappings` section will be substituted into the base resource where needed. The Replicate field determines which subsection from `Mappings` is used. The replication parameters can also be defined in the `Replicate` field itself.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform:
    - SubReplicate

Resources:
    BaseStack:
        Type: AWS::CloudFormation::Stack
        SubReplicate:
            Replicates:
                stack_one:
                    Variable1: foo
                    Variable3: 1
                stack_two:
                    Variable1: fuu
                    Variable2: bor
            Defaults:
                Variable2: bar
        Properties:
            Property1: !Ref repl:Variable1
            Property2: !Sub ${repl:Variable1}-${repl:Variable2}
            Property2: !Ref repl:Variable3
```
 Or with the `AWS::Include` macro:

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform:
    - SubReplicate

Resources:
    BaseStack:
        Type: AWS::CloudFormation::Stack
        SubReplicate:
            Replicates:
                Fn::Transform:
                    Name: AWS::Include
                    Parameters:
                        Location: configuration.yml
            Defaults:
                Variable2: bar
        Properties:
            Property1: !Ref repl:Variable1
            Property2: !Sub ${repl:Variable1}-${repl:Variable2}
            Property3: !Ref repl:Variable3
```

The referenced file `configuration.yml` will be of the form

```yaml
stack_one:
    Variable1: foo
    Variable3: 1
stack_two:
    Variable1: fuu
    Variable2: bor
```

## Scope

The scope of the substitute replicator is at the global level. Since it replicates resources it must be able to add and remove resources from the `Resources` section in CloudFormation. To declare it, one can use

```yml
Transform:
    - SubReplicate
```

## Tests

After deploying a macro for an environment, run the tests

```bash
PYTHONPATH=src:.. MACRO_ENVIRONMENT=<environment> python -m pytest tests
```

This will run both unit and integration tests.