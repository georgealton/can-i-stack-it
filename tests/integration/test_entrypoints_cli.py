from textwrap import dedent

from click.testing import CliRunner
from cloudformation_permissions.entrypoints import cli


def test_resource_permissions():
    runner = CliRunner()
    result = runner.invoke(
        cli.resource,
        ["AWS::IAM::Role", "permissions"],
    )
    assert result.exit_code == 0
    assert result.stdout == dedent("""\
    iam:AttachRolePolicy
    iam:CreateRole
    iam:DeleteRole
    iam:DeleteRolePermissionsBoundary
    iam:DeleteRolePolicy
    iam:DetachRolePolicy
    iam:GetRole
    iam:GetRolePolicy
    iam:ListAttachedRolePolicies
    iam:ListRolePolicies
    iam:ListRoles
    iam:PutRolePermissionsBoundary
    iam:PutRolePolicy
    iam:TagRole
    iam:UntagRole
    iam:UpdateAssumeRolePolicy
    iam:UpdateRole
    iam:UpdateRoleDescription
    """)


def test_resource_permissions_output_tree():
    runner = CliRunner()
    result = runner.invoke(
        cli.resource,
        ["AWS::IAM::Role", "permissions", "--output", "tree"],
    )
    assert result.exit_code == 0
    assert result.stdout == dedent("""\
    AWS::IAM::Role
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
    """)


def test_template_local_path_permissions():
    runner = CliRunner()
    result = runner.invoke(
        cli.template,
        ["tests/integration/data/template.yaml", "permissions"],
    )
    assert result.exit_code == 0
    assert result.stdout == dedent("""\
    iam:AttachRolePolicy
    iam:CreateRole
    iam:DeleteRole
    iam:DeleteRolePermissionsBoundary
    iam:DeleteRolePolicy
    iam:DetachRolePolicy
    iam:GetRole
    iam:GetRolePolicy
    iam:ListAttachedRolePolicies
    iam:ListRolePolicies
    iam:ListRoles
    iam:PutRolePermissionsBoundary
    iam:PutRolePolicy
    iam:TagRole
    iam:UntagRole
    iam:UpdateAssumeRolePolicy
    iam:UpdateRole
    iam:UpdateRoleDescription
    """)


def test_template_local_path_permissions_output_tree():
    runner = CliRunner()
    result = runner.invoke(
        cli.template,
        ["tests/integration/data/template.yaml", "permissions", "--output", "tree"],
    )
    assert result.exit_code == 0
    assert result.stdout == dedent("""\
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
    """)
