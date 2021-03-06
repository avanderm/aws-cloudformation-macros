# AWS CloudFormation macros

- [substitution replicate](substitution-replicate): eliminate nearly identical resources in a template by replicating a base resource and substituting in variables wherever the intrinsic substitution function to CloudFormation is used.

## Deploying macros

The Makefile can be reused for any macro; specify the environment, the folder containing the macro and the macro name to deploy:

```bash
MACRO_PATH=<dir_to_macro> MACRO_NAME=<macro_name> make deploy
```

This will deploy the macro under the naming convention `<macro_name>`. For example, the substitution replicator macro is deployed as follows:

```bash
MACRO_PATH=resource-replicate MACRO_NAME=ResourceReplicate make deploy
```

and is used in any CloudFormation template with

```yaml
AWSTemplateVersion: 2010-09-09
Transform:
    - SubReplicate
```

## Versioning

A `versions.yml` file can be used in each macro folder to specify macro versions. The file is of the form:

```yaml
V1:
    version_name: V1
V2:
    version_name: V2
```

Versions can be added and removed (if no CloudFormation stack needs it anymore). These versioned macros will be available under the convention `<macro_name>-<version_name>`. Once a macro version is made it is static, unlike the `<macro_name>` macro. This will ensure that existing stacks relying on a versioned macro will not break due to code changes.