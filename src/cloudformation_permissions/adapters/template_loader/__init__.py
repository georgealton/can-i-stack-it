from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Protocol, TypedDict

from attrs import frozen
from botocore.exceptions import ClientError
from cfnlint.decode import cfn_json, cfn_yaml
from cfnlint.template import Template
from result import Err, Ok, Result, as_result, is_ok

from ...domain.model import ARN, ShortResourceInfo
from ..cloudformation import CloudFormationClient

if TYPE_CHECKING:
    from mypy_boto3_cloudformation.type_defs import GetTemplateOutputTypeDef



class TemplateResourceLoaderProtocol(Protocol):
    client: CloudFormationClient

    def get_template_resources(self, template_source: ARN | Path) -> Result[Iterable[ShortResourceInfo], str]: ...


class CloudFormationTemplate(TypedDict):
    Resources: dict[str, Any]


@frozen
class StackAdapter(TemplateResourceLoaderProtocol):
    client: CloudFormationClient

    def get_template_resources(self, template_source: ARN) -> Result[Iterable[ShortResourceInfo], str]:
        paginator = self.client.get_paginator("list_stack_resources")
        resources = []
        for stack_resource in paginator.paginate(StackName=str(template_source)):
            for resource_summary in stack_resource["StackResourceSummaries"]:
                info = ShortResourceInfo(
                    TypeName=resource_summary["ResourceType"],
                    LogicalId=resource_summary["LogicalResourceId"],
                )
                resources.append(info)
        return Ok(resources)


@frozen
class ChangeSetAdapter(TemplateResourceLoaderProtocol):
    client: CloudFormationClient

    def _load_template(self, template_str: GetTemplateOutputTypeDef) -> Result[Template, str]:
        return as_result(json.JSONDecodeError)(cfn_json.loads)(template_str["TemplateBody"]).map_err(str)

    def _get_template(self, template_source: ARN) -> Result[GetTemplateOutputTypeDef, str]:
        return as_result(ClientError)(self.client.get_template)(
            ChangeSetName=str(template_source), TemplateStage="Processed"
        ).map_err(str)

    def get_template_resources(self, template_source: ARN) -> Result[Iterable[ShortResourceInfo], str]:
        template_result = self._get_template(template_source).and_then(self._load_template)

        match template_result:
            case Ok(template):
                resources = template.get_resources()
                r = []
                for logical_id, properties in resources.items():
                    type_name = properties["Type"]
                    info = ShortResourceInfo(LogicalId=logical_id, TypeName=type_name)
                    r.append(info)
                return Ok(r)
            case Err(e):
                return Err(f"Failed to get CloudFormation Resources for {template_source}: {e}")


@frozen
class LocalAdapter(TemplateResourceLoaderProtocol):
    client: CloudFormationClient

    def _get_template(self, template_source: Path) -> Result[Template, str]:
        load_result = as_result(OSError)(cfn_yaml.load)(template_source)
        if is_ok(load_result):
            return Ok(Template(str(template_source), template=load_result.ok_value))
        return Err(str(load_result))

    def get_template_resources(self, template_source: Path) -> Result[Iterable[ShortResourceInfo], str]:
        get_template_result = self._get_template(template_source)

        match get_template_result:
            case Ok(_template):
                resources = _template.get_resources()
                resource_information_collection = list[ShortResourceInfo]()
                for logical_id, properties in resources.items():
                    resource_information_collection.append(
                        ShortResourceInfo(LogicalId=logical_id, TypeName=properties["Type"])
                    )
                return Ok(resource_information_collection)
            case Err(e):
                return Err(str(e))
