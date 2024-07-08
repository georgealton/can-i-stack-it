import sys
from logging import getLogger
from pathlib import Path
from typing import Literal

import click
from result import Err, Ok
from rich.console import Console

from ..bootstrap import bootstrap
from ..domain import queries
from ..domain.model import ARN

logger = getLogger(__name__)

OUTPUT_FORMATS = ("list", "tree")
PERMISSION_LEVELS = ("read", "modify", "full")


@click.group()
def cli():
    """Get Permissions for CloudFormation Stacks and Resources"""


@cli.group()
@click.argument("resource_type", required=True)
@click.pass_context
def resource(ctx, resource_type: str) -> None:
    """Perform Operations on CloudFormation Resource Types.

    RESOURCE_TYPE is an CloudFormation Resource Type, eg 'AWS::IAM::Role'
    """
    ctx.obj = resource_type


@resource.command("permissions")
@click.option("--output", default="list", type=click.Choice(OUTPUT_FORMATS))
@click.option("--permission-level", default="full", type=click.Choice(PERMISSION_LEVELS))
@click.pass_obj
def resource_permissions(
    resource_type: str, output: Literal["list", "tree"], permission_level: Literal["read", "modify", "full"]
) -> None:
    """List of IAM Permissons required to manage this RESOURCE_TYPE"""
    query = queries.ListResourceTypePermissions(ResourceType=resource_type, PermissionLevel=permission_level)

    handlers = bootstrap(output_format=output)
    handler = handlers[type(query)]

    report_result = handler(query)

    match report_result:
        case Ok(report):
            Console().print(report)
        case Err(e):
            logger.error(e)
            sys.exit(1)


@resource.command("verify")
@click.argument("role-arn", required=False)
@click.option("--permission-level", default="full", type=click.Choice(PERMISSION_LEVELS))
@click.pass_obj
def resource_verify(resource_type: str, role_arn: str | None):
    """Verify ROLE_ARN can manage this RESOURCE_TYPE"""
    _role_arn = ARN.from_str(role_arn) if role_arn is not None else role_arn
    query = queries.VerifyResourceTypePermissions(ResourceType=resource_type, Role=_role_arn)

    handlers = bootstrap()
    handler = handlers[type(query)]

    report_result = handler(query)

    match report_result:
        case Ok(report):
            Console().print(report)
        case Err(e):
            logger.error(e)
            sys.exit(1)


@cli.group()
@click.argument("template", required=True)
@click.option("--permission-level", default="full", type=click.Choice(PERMISSION_LEVELS))
@click.pass_context
def template(ctx, template: str) -> None:
    """Perform Operations on a CloudFormation Template.

    TEMPLATE may be a Path to a local file, the ARN of a CloudFormation Stack
    or ChangeSet
    """
    ctx.obj = template


@template.command("permissions")
@click.option("--output", default="list", type=click.Choice(OUTPUT_FORMATS))
@click.option("--permission-level", default="full", type=click.Choice(PERMISSION_LEVELS))
@click.pass_obj
def template_permissions(
    template_source: str, output: Literal["list", "tree"], permission_level: Literal["read", "modify", "full"]
) -> None:
    """List permissions required to manage Stacks of this Template"""
    _template_source = (
        ARN.from_str(template_source) if template_source.startswith(f"{ARN.domain}:") else Path(template_source)
    )

    query = queries.ListTemplatePermissions(TemplateSource=_template_source, PermissionLevel=permission_level)

    handlers = bootstrap(template_source=query.TemplateSource, output_format=output)
    handler = handlers[type(query)]

    report_result = handler(query)
    match report_result:
        case Ok(report):
            Console().print(report)
        case Err(e):
            logger.error(e)
            sys.exit(1)


@template.command("verify")
@click.argument("role-arn", required=False)
@click.option("--permission-level", default="full", type=click.Choice(PERMISSION_LEVELS))
@click.pass_obj
def template_verify(template_source: str, role_arn: str | None = None) -> None:
    """Verify ROLE_ARN

    ROLE_ARN the ARN of an AWS::IAM::Role
    """
    _role_arn = ARN.from_str(role_arn) if role_arn is not None else role_arn
    _template_source = (
        ARN.from_str(template_source) if template_source.startswith(f"{ARN.domain}:") else Path(template_source)
    )

    query = queries.VerifyTemplatePermissions(TemplateSource=_template_source, Role=_role_arn)

    handlers = bootstrap(template_source=query.TemplateSource)
    handler = handlers[type(query)]

    report_result = handler(query)
    match report_result:
        case Ok(report):
            Console().print(report)
        case Err(e):
            logger.error(e)
            sys.exit(1)
