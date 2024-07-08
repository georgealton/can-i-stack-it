import pytest
from boto3 import client
from cloudformation_permissions.adapters import iam
from cloudformation_permissions.domain.model import (
    Action,
    ActionPermission,
    Authorized,
)


@pytest.mark.parametrize(
    "role, actions, result",
    [
        (
            "arn:aws:iam::737710810646:role/PlanGitHubRoles",
            [
                "sts:GetCallerIdentity",
            ],
            [
                ActionPermission(Action("sts:GetCallerIdentity"), Authorized.ALLOWED),
            ],
        ),
        (
            "arn:aws:iam::737710810646:role/PlanGitHubRoles",
            [
                "ec2:RunInstances",
            ],
            [
                ActionPermission(Action("ec2:RunInstances"), Authorized.DENIED),
            ],
        ),
        (
            "arn:aws:iam::737710810646:role/PlanGitHubRoles",
            [
                "sts:GetCallerIdentity",
                "ec2:RunInstances",
            ],
            [
                ActionPermission(Action("sts:GetCallerIdentity"), Authorized.ALLOWED),
                ActionPermission(Action("ec2:RunInstances"), Authorized.DENIED),
            ],
        ),
    ],
    ids=[
        "Allowed",
        "Denied",
        "AllowedAndDenied",
    ],
)
def test_simulate(role, actions, result):
    iam_client = client("iam")
    adapter = iam.IAM(iam_client)
    assert result == list(adapter.simulate(role, actions))
