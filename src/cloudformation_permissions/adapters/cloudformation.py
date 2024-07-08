from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from mypy_boto3_cloudformation.type_defs import (
        DescribeTypeOutputTypeDef,
        GetTemplateOutputTypeDef,
    )


class CloudFormationClient(Protocol):
    def describe_type(self, Type: str, TypeName: str) -> DescribeTypeOutputTypeDef: ...
    def get_template(self, ChangeSetName: str, TemplateStage: str) -> GetTemplateOutputTypeDef: ...
    def get_paginator(self, operation: str) -> Any: ...
