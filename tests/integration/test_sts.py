from boto3 import client
from cloudformation_permissions.adapters import sts


def test_sts():
    c = client("sts")
    s = sts.STS(c)
    role = "arn:aws:iam::737710810646:role/AWSReservedSSO_EvertzIOAdmin_e2e5cb6ac866872e"
    assert str(s()) == role
