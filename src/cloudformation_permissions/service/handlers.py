from __future__ import annotations

from typing import assert_never

from attrs import frozen
from result import Err, Ok, Result

from cloudformation_permissions.adapters.iam import IAMProtocol
from cloudformation_permissions.adapters.permissions_resolver import ResourceInformationResolverProtocol
from cloudformation_permissions.adapters.reporter import Reporter, ResourceReporterTree
from cloudformation_permissions.adapters.sts import STSProtocol
from cloudformation_permissions.adapters.template_loader import TemplateResourceLoaderProtocol
from cloudformation_permissions.domain.model import (
    ResourcePermissionSummary,
    TemplateSummary,
)
from cloudformation_permissions.domain.queries import (
    ListResourceTypePermissions,
    ListTemplatePermissions,
    VerifyResourceTypePermissions,
    VerifyTemplatePermissions,
)
from cloudformation_permissions.service import QueryHandler


@frozen
class HandleListResourceTypePermissions(QueryHandler):
    permission_resolver: ResourceInformationResolverProtocol
    reporter: Reporter

    def __call__(self, query: ListResourceTypePermissions) -> Result[ResourcePermissionSummary, str]:
        result = self.permission_resolver.resolve(query.ResourceType, query.PermissionLevel)

        match result:
            case Ok(permissions):
                summary = ResourcePermissionSummary(resource_type=query.ResourceType, permissions=permissions)
                report = self.reporter.add_summary(summary)
                return Ok(report)

            case Err():
                return result.map_err(str)

            case _:
                assert_never(result)


@frozen
class HandleVerifyResourceTypePermissions(QueryHandler):
    permission_resolver: ResourceInformationResolverProtocol
    iam: IAMProtocol
    sts: STSProtocol
    reporter: Reporter

    def __call__(self, query: VerifyResourceTypePermissions) -> Result[ResourcePermissionSummary, str]:
        result = self.permission_resolver.resolve(query.ResourceType, permission_level=query.PermissionLevel)

        match result:
            case Ok(permissions):
                summary = ResourcePermissionSummary(resource_type=query.ResourceType, permissions=permissions)
                role = query.Role or self.sts()
                print(list(self.iam.simulate(str(role), [str(p) for p in summary.permissions])))
                return None

            case Err(e):
                return Err(str(e))

            case _:
                assert_never(result)


@frozen
class HandleTemplateListPermissions(QueryHandler):
    template_loader: TemplateResourceLoaderProtocol
    permission_resolver: ResourceInformationResolverProtocol
    reporter: Reporter

    def __call__(self, query: ListTemplatePermissions) -> Result[ResourceReporterTree, str]:
        resources_result = self.template_loader.get_template_resources(query.TemplateSource)
        resource_summaries = dict[str, ResourcePermissionSummary]()

        match resources_result:
            case Ok(resources):
                for resource in resources:
                    resource_type = resource.TypeName
                    match self.permission_resolver.resolve(resource_type, permission_level=query.PermissionLevel):
                        case Ok(permissions):
                            resource_summaries[resource.LogicalId] = ResourcePermissionSummary(
                                resource_type=resource_type, permissions=permissions
                            )
                        case Err(e):
                            return e
                report = self.reporter.add_summary(
                    TemplateSummary(source=query.TemplateSource, resources=resource_summaries)
                )
                return Ok(report)

            case Err():
                return resources_result

            case _:
                assert_never(resources_result)


@frozen
class HandleVerifyPermissions(QueryHandler):
    template_loader: TemplateResourceLoaderProtocol
    iam: IAMProtocol
    sts: STSProtocol
    reporter: Reporter

    def __call__(self, query: VerifyTemplatePermissions) -> Result[TemplateSummary, str]:
        role = query.Role or self.sts()

        resources = self.template_loader.get_template_resources(query.template_source)
        collected_permissions = frozenset(resource.permissions for resource in resources)
        self.iam.simulate(str(role), collected_permissions)
