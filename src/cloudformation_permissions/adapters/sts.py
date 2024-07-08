from typing import Protocol

import botocore.exceptions
from attrs import frozen
from result import Err, Ok, Result, as_result

from ..domain.model import ARN


class STSClient(Protocol):
    def get_caller_identity(self) -> dict: ...


class STSProtocol(Protocol):
    client: STSClient

    def __call__(self) -> Result[ARN, str]: ...


@frozen
class STS(STSProtocol):
    client: STSClient

    @staticmethod
    def _get_role_name_from_session(resource: str) -> str:
        return resource.split("/")[1]

    def __build_role_from_session(self, session_arn: ARN) -> ARN:
        role_name = self._get_role_name_from_session(session_arn.resource)
        return ARN(
            partition=session_arn.partition,
            service="iam",
            region=session_arn.region,
            account_id=session_arn.account_id,
            resource=f"role/{role_name}",
        )

    def __get_current_role(self) -> Result[ARN, str]:
        identity_result = as_result(botocore.exceptions.NoCredentialsError)(self.client.get_caller_identity)()
        match identity_result:
            case Ok(identity):
                arn = ARN.from_str(identity["Arn"])
                return Ok(self.__build_role_from_session(arn))
            case Err(error):
                return Err(str(error))

    def __call__(self) -> Result[ARN, str]:
        return self.__get_current_role()
