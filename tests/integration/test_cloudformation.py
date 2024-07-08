from pathlib import Path

from boto3 import client
from cloudformation_permissions.adapters import cloudformation
from cloudformation_permissions.domain.model import ShortResourceInfo


def test_resource_provider_permission_resolver():
    cfn = client("cloudformation")
    cfn_adapter = cloudformation.ResourceInformationResolver(cfn)
    permissions = cfn_adapter.permissions_for_resource_type("AWS::IAM::Role")
    assert permissions.ok_value == frozenset(
        [
            "iam:AttachRolePolicy",
            "iam:CreateRole",
            "iam:DeleteRole",
            "iam:DeleteRolePermissionsBoundary",
            "iam:DeleteRolePolicy",
            "iam:DetachRolePolicy",
            "iam:GetRole",
            "iam:GetRolePolicy",
            "iam:ListAttachedRolePolicies",
            "iam:ListRolePolicies",
            "iam:ListRoles",
            "iam:PutRolePermissionsBoundary",
            "iam:PutRolePolicy",
            "iam:TagRole",
            "iam:UntagRole",
            "iam:UpdateAssumeRolePolicy",
            "iam:UpdateRole",
            "iam:UpdateRoleDescription",
        ]
    )


def test_local_template_adapter():
    cfn = client("cloudformation")
    local_template_adapter = cloudformation.LocalAdapter(cfn)
    template_path = Path("tests/integration/data/template.yaml")
    resources = local_template_adapter.get_template_resources(str(template_path))
    assert resources.ok_value == [ShortResourceInfo(TypeName="AWS::IAM::Role", LogicalId="Example")]
