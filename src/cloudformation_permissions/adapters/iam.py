from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Literal, Protocol, TypedDict, Unpack

from attrs import frozen

if TYPE_CHECKING:
    from mypy_boto3_iam.type_defs import (
        SimulatePolicyResponseTypeDef,
        SimulatePrincipalPolicyRequestRequestTypeDef,
    )

from ..domain.model import Action, ActionPermission, Authorized

type EvalDecision = Literal["allowed", "implicitDeny", "explicitDeny"]


class IAMEvaluationResult(TypedDict):
    EvalActionName: str
    EvalDecision: EvalDecision


class Paginator[P: TypedDict, R](Protocol):
    def paginate(self, **kwargs: Unpack[P]) -> Iterable[R]: ...


class IAMClient(Protocol):
    def get_paginator(
        self, operation: Literal["simulate_principal_policy"]
    ) -> Paginator[
        SimulatePrincipalPolicyRequestRequestTypeDef,
        SimulatePolicyResponseTypeDef,
    ]: ...


class IAMProtocol(Protocol):
    def simulate(self, role: str, actions: Iterable[str]) -> Iterable[ActionPermission]: ...


@frozen
class IAM(IAMProtocol):
    client: IAMClient

    def simulate(self, role: str, actions: Iterable[str]) -> Iterable[ActionPermission]:
        paginator = self.client.get_paginator("simulate_principal_policy")
        for page in paginator.paginate(PolicySourceArn=role, ActionNames=list(actions)):
            for result in page["EvaluationResults"]:
                evaluation_result = IAMEvaluationResult(result)
                action = Action(evaluation_result["EvalActionName"])

                match evaluation_result["EvalDecision"]:
                    case "allowed":
                        permission = Authorized.ALLOWED
                    case "implicitDeny" | "explicitDeny":
                        permission = Authorized.DENIED

                yield ActionPermission(action=action, authorization=permission)
