# CloudFormation Permissions

Check if your CloudFormation Template can be deployed by a Role.

## Use Me

To generate reports, cloudformation-permissions makes AWS API requests. The
following statement includes the Actions required to make this work with you
IAM Principal

```json
{
    "Effect": "Allow",
    "Action": [
        "sts:GetCallerIdentity"
    ],
    "Resource": "*"
},
{
    "Effect": "Allow",
    "Action": [
        "iam:GetContextKeysForPrincipalPolicy",
        "iam:SimulatePrincipalPolicy"
    ],
    "Resource": "*"
},
{
    "Effect": "Allow",
    "Action": [
        "cloudformation:GetTemplate",
        "cloudformation:ListStackResources"
    ],
    "Resource": "*"
}
```

### GitHub Action

### Locally

```sh
$ pipx run cloudformation-permissions resource 'AWS::IAM::Role' permissions
iam:CreateRole
iam:UpdateRole
iam:DeleteRole
iam:PutRolePermissionsBoundary
iam:DeleteRolePermissionsBoundary
iam:TagRole
iam:GetRole
iam:ListRoles
iam:UpdateRoleDescription
iam:DeleteRolePolicy
iam:ListRolePolicies
iam:AttachRolePolicy
iam:DetachRolePolicy
iam:UpdateAssumeRolePolicy
iam:PutRolePolicy
iam:GetRolePolicy
iam:ListAttachedRolePolicies
iam:UntagRole
```

```sh
$ pipx run cloudformation-permissions resource 'AWS::IAM::Role' permissions --output tree
AWS::IAM::Role
├── iam:CreateRole
├── iam:UpdateRole
├── iam:DeleteRole
├── iam:PutRolePermissionsBoundary
├── iam:DeleteRolePermissionsBoundary
├── iam:TagRole
├── iam:GetRole
├── iam:ListRoles
├── iam:UpdateRoleDescription
├── iam:DeleteRolePolicy
├── iam:ListRolePolicies
├── iam:AttachRolePolicy
├── iam:DetachRolePolicy
├── iam:UpdateAssumeRolePolicy
├── iam:PutRolePolicy
├── iam:GetRolePolicy
├── iam:ListAttachedRolePolicies
└── iam:UntagRole
```

```sh
$ pipx run cloudformation-permissions template 'tests/data/template.cfn.yaml' permissions --output tree
tests/integration/data/template.yaml
└── Example
    └── AWS::IAM::Role
        ├── iam:AttachRolePolicy
        ├── iam:CreateRole
        ├── iam:DeleteRole
        ├── iam:DeleteRolePermissionsBoundary
        ├── iam:DeleteRolePolicy
        ├── iam:DetachRolePolicy
        ├── iam:GetRole
        ├── iam:GetRolePolicy
        ├── iam:ListAttachedRolePolicies
        ├── iam:ListRolePolicies
        ├── iam:ListRoles
        ├── iam:PutRolePermissionsBoundary
        ├── iam:PutRolePolicy
        ├── iam:TagRole
        ├── iam:UntagRole
        ├── iam:UpdateAssumeRolePolicy
        ├── iam:UpdateRole
        └── iam:UpdateRoleDescription
```

```sh
pipx run cloudformation-permissions template 'tests/data/template.cfn.yaml' verify 'arn:aws:iam:::role/example'
```
## Limitations

### Modules are not supported

### Simulation of resource-based policies isn't supported for IAM roles.

This tool won't be able to tell you if there is Resource Policy 

