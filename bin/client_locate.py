import boto3


class ClientLocator:
    def __init__(self, client, get_profile):
        session = boto3.session.Session(profile_name=get_profile)
        self._client = session.client(client, region_name='ap-southeast-1')

    def get_client(self):
        return self._client

    @staticmethod
    def get_profiles():
        pro = boto3.session.Session().available_profiles
        return pro


class EC2Client(ClientLocator):
    def __init__(self, profile):
        get_profile = profile
        super().__init__('ec2', get_profile)
