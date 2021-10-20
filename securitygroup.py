import boto3
import json


class Security:

    def __init__(self):
        session = boto3.session.Session(profile_name='your aws_profilename')
        self._client = session.client('ec2', region_name='ap-southeast-1')
        """ :type : pyboto3.ec2 """

    def create_security_group(self, description, group_name, vpc_id):
        return self._client.create_security_group(Description=description, GroupName=group_name, VpcId=vpc_id)

    def add_security_role_ingress(self, sg_id, protocol, from_ports, to_ports, ip):
        print(" Adding ingress role allow port " + from_ports + " to this ip " + ip + " from " + sg_id)
        return self._client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[{
                'IpProtocol': protocol,
                'FromPort': int(from_ports),
                'ToPort': int(to_ports),
                'IpRanges': [{'CidrIp': ip}]
            }]
        )

    def add_security_role_egress(self, sg_id, protocol, from_ports, to_ports, ip):
        print(
            " Adding egress role allow port " + from_ports + " | " + to_ports + "to this ip " + ip + " from " + security_id)
        return self._client.authorize_security_group_egress(
            GroupId=security_id,
            IpPermissions=[{
                'IpProtocol': service,
                'FromPort': int(from_ports),
                'ToPort': int(to_ports),
                'CidrIp': [{'CidrIp': ip}],
            }]

        )


# added Single Port and Multi Port
sg = Security()
ports = {"8080": "8080", "8081": "8081", "9990": "9990", "9997": "9997"} #simple record
ip_address = ['10.11.76.41/32', '10.11.76.43/32', '10.11.204.41/32', '10.11.204.43/32']  # simple record
service = "tcp"
security_id = "sg-0d90d06ce41b21d50" #simple record
for port in ports:
    for ip in ip_address:
        from_port = port
        to_port = ports[port]
        response = sg.add_security_role_ingress(security_id, service, from_port, to_port,
                                                ip)  # can replace add_security_role_egress
        print(str(str(response)))


