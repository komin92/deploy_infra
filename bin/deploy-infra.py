from deploy_infra.bin.client_locate import EC2Client
from deploy_infra.ec2.vpc import VPC
from deploy_infra.config.config import LOG
import time

profile_name = "Your aws profile name"  # first need to setup aws cli config with profile name
#eg profile_name = "uat"


def aws_route_call():
    call_vpc = EC2Client(profile_name).get_client()
    route = VPC(call_vpc)
    return route


def create_private_subnet(vpc_id, ip_address, za, subnet_name):
    response_subnet = aws_route_call().create_subnet(vpc_id, ip_address, za)
    private_subnet_id = response_subnet['Subnet']['SubnetId']
    aws_route_call().add_tag_name(private_subnet_id, subnet_name)
    return private_subnet_id


def create_public_subnet(vpc_id, ip_address, za, subnet_name):
    response_subnet = aws_route_call().create_subnet(vpc_id, ip_address, za)
    public_subnet_id = response_subnet['Subnet']['SubnetId']
    aws_route_call().allow_public_ip_into_subnet(public_subnet_id)
    aws_route_call().add_tag_name(public_subnet_id, subnet_name)
    return public_subnet_id


def create_route_table(vpc_id):
    response = aws_route_call().create_route_table(vpc_id)
    rt_id = response['RouteTable']['RouteTableId']
    LOG.logger.info(f"Already Created this {rt_id} Route Table from this {vpc_id} VPC ")
    return rt_id


def main():
    # Crate VPC
    cidr = "10.217.0.0/16"  # you can replace this cidr ip address 
    vpc_ru = aws_route_call().vpc_create(cidr)
    vpc_id = vpc_ru['Vpc']['VpcId']
    aws_route_call().add_tag_name(vpc_id, 'devops')

    if vpc_id is not None:
        # Create Private Subnet
        Private_AZs = {"ap-southeast-1a": "10.217.1.0/24", "ap-southeast-1b": "10.217.2.0/24"}
        private_subnetIDs = []
        for private_az in Private_AZs:
            az = private_az
            name = az.split("-")
            z = name[2].split("1")[1]
            private_subnet_name = f"devops_private_subnet_Z{z}"
            ip_address = Private_AZs[az]
            private_subnetA_id = create_private_subnet(vpc_id, ip_address, az, private_subnet_name)
            private_subnetIDs.append(private_subnetA_id)
        # Create public Subnet
        # subnet  Zone A
        Public_AZs = {"ap-southeast-1a": "10.217.11.0/24", "ap-southeast-1b": "10.217.12.0/24"}
        public_subnetIDs = []
        for public_az in Public_AZs:
            az = public_az
            name = az.split("-")
            z = name[2].split("1")[1]
            public_subnet_name = f"devops_public_subnet_Z{z}"
            ip_address = Public_AZs[az]
            public_subnet_id = create_private_subnet(vpc_id, ip_address, az, public_subnet_name)
            public_subnetIDs.append(public_subnet_id)

        # Create Internet Gateway
        response_igw = aws_route_call().create_internet_gateway()
        igw_id = response_igw['InternetGateway']['InternetGatewayId']
        aws_route_call().add_tag_name(igw_id, 'devops_igw')
        aws_route_call().attach_igw_to_vpc(igw_id, vpc_id)

        # Create NAT Gateway
        public_ip_allocation_id = aws_route_call().allocate_address()
        ngw_subnet_id = public_subnetIDs[0]
        response_ngw = aws_route_call().create_nat_gateway(ngw_subnet_id, "devops_ngw", public_ip_allocation_id)
        ngw_id = response_ngw['NatGateway']['NatGatewayId']
        time.sleep(60)

        # Create Public Route Tables
        public_route_id = create_route_table(vpc_id)
        aws_route_call().add_tag_igw_name(public_route_id, "devops_public_route")

        # Create Private Route Tables
        private_route_id = create_route_table(vpc_id)
        aws_route_call().add_tag_igw_name(private_route_id, "devops_private_route")

        # ADD Route Records
        aws_route_call().add_route_to_igw_vgw(igw_id, public_route_id, "0.0.0.0/0")


        aws_route_call().add_route_to_nat(ngw_id, private_route_id, "0.0.0.0/0")

        # Route Table Subnet Associate
        for public_subnet_id in public_subnetIDs:
            aws_route_call().route_table_associate_with_subnet(public_route_id, public_subnet_id)
        for private_subnet_id in private_subnetIDs:
            aws_route_call().route_table_associate_with_subnet(private_route_id, private_subnet_id)

    else:
        LOG.logger.error(".....VPC Not found.....")


if __name__ == '__main__':
    main()
