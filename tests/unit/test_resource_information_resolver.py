from cloudformation_permissions.adapters.permissions_resolver import ResourceInformationResolver
from pytest import mark

test_data = (
    ("Organization::Service::UseCase::MODULE", True),
    ("AWS:SQS:Queue", False),
)


@mark.parametrize("resource_type_name,result", test_data)
def test_module_detection(resource_type_name, result):
    assert ResourceInformationResolver._is_module(resource_type_name) is result
