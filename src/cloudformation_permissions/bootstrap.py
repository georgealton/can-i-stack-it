from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Literal

import punq
from boto3 import session

from .adapters import cloudformation, iam, permissions_resolver, sts, template_loader
from .adapters.reporter import ListReporter, Reporter, ResourceReporterTree
from .adapters.sar import ServiceAuthorizationReferenceLocal, ServiceAuthorizationReferenceProcotol
from .domain.model import ARN
from .domain.queries import Query
from .service.handlers import QueryHandler


def bootstrap(
    *,
    template_source: Path | ARN | None = None,
    output_format: Literal["tree", "list"] | None = "list",
) -> Mapping[type[Query], QueryHandler]:
    container = punq.Container()

    _session = session.Session()
    container.register(cloudformation.CloudFormationClient, instance=_session.client("cloudformation"))
    container.register(iam.IAMClient, instance=_session.client("iam"))
    container.register(sts.STSClient, instance=_session.client("sts"))

    container.register(iam.IAMProtocol, iam.IAM)
    container.register(sts.STSProtocol, sts.STS)

    container.register(ServiceAuthorizationReferenceProcotol, ServiceAuthorizationReferenceLocal)

    match template_source:
        case ARN() as stack if stack.resource.startswith("stack/"):
            container.register(template_loader.TemplateResourceLoaderProtocol, template_loader.StackAdapter)
        case ARN() as changeset if changeset.resource.startswith("changeSet/"):
            container.register(template_loader.TemplateResourceLoaderProtocol, template_loader.ChangeSetAdapter)
        case Path():
            container.register(template_loader.TemplateResourceLoaderProtocol, template_loader.LocalAdapter)
        case _:
            container.register(template_loader.TemplateResourceLoaderProtocol, template_loader.LocalAdapter)

    container.register(
        permissions_resolver.ResourceInformationResolverProtocol, permissions_resolver.ResourceInformationResolver
    )

    match output_format:
        case "list":
            container.register(Reporter, ListReporter)
        case "tree":
            container.register(Reporter, ResourceReporterTree)
        case _:
            container.register(Reporter, ListReporter)

    return {Query: container.instantiate(Handler) for Query, Handler in QueryHandler.registry.items()}
