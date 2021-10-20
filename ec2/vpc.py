from infra.config.config import LOG


class VPC:
    def __init__(self, client):
        self._client = client
        """ :type : pyboto3.ec2 """

    def vpc_create(self, ip_address):
        LOG.logger.info("Creating VPC .....")
        return self._client.create_vpc(
            CidrBlock=ip_address
        )

    def get_vpcs(self):
        return self._client.describe_vpcs()

    def add_tag_name(self, resource_id, resource_name):
        LOG.logger.info(" Adding " + resource_name + " tag to the " + resource_id)
        return self._client.create_tags(
            Resources=[resource_id],
            Tags=[{
                "Key": "Name",
                "Value": resource_name

            }]
        )

    # Create Internet Gateway
    def create_internet_gateway(self):
        LOG.logger.info("Creating Internet Gateway ......")
        return self._client.create_internet_gateway()

    def attach_igw_to_vpc(self, igw_id, vpc_id):
        LOG.logger.info("Adding VPC ID: " + vpc_id + " to InternetGateway ID: " + igw_id)
        return self._client.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )

    # Create NAT GateWay
    def allocate_address(self):
        LOG.logger.info("Get Allocate_address")
        response = self._client.allocate_address(Domain='vpc')
        return response['AllocationId']

    def create_nat_gateway(self, subnetId, ngw_name, public_ip_allocation_id):
        LOG.logger.info("Creating NAT Gateway")
        if public_ip_allocation_id is not None:
            return self._client.create_nat_gateway(
                AllocationId=public_ip_allocation_id,
                SubnetId=subnetId,
                TagSpecifications=[{
                    'ResourceType':
                        'natgateway',
                    'Tags': [{
                        'Key': 'Name',
                        'Value': ngw_name
                    }]
                }]
            )
        else:
            LOG.logger.error("Not Found public_ip_allocation_id ")

    # Create Virtual Gateway
    def create_virtual_gateway(self):
        LOG.logger.info("Creating Virtual Gateway......")
        return self._client.create_vpn_gateway(Type="ipsec.1")

    def attach_vgw_to_vpc(self, vpc_id, vgw_id):
        LOG.logger.info("Adding VPC ID: " + vpc_id + " to VirtualGateway ID: " + vgw_id)
        return self._client.attach_vpn_gateway(VpcId=vpc_id, VpnGatewayId=vgw_id)

    # Tagging
    def add_tag_igw_name(self, resource_igw_id, resource_igw_name):
        LOG.logger.info("Adding " + resource_igw_name + " to the " + resource_igw_id)
        return self._client.create_tags(
            Resources=[resource_igw_id],
            Tags=[{
                "Key": "Name",
                "Value": resource_igw_name

            }]
        )

    # Create Subnet
    def create_subnet(self, vpc_id, ip, az):
        LOG.logger.info("Creating Subnet ... " + ip + " into this vpc " + vpc_id + " on " + az)
        return self._client.create_subnet(
            VpcId=vpc_id,
            CidrBlock=ip,
            AvailabilityZone=az
        )

    def delete_subnet(self, subnet_id):
        LOG.logger.info(f"Deleting Subnet ... {subnet_id}")
        return self._client.delete_subnet(SubnetId=subnet_id)

    def allow_public_ip_into_subnet(self, subnet_id):
        LOG.logger.info("Allow Public IP into subnet " + subnet_id)
        return self._client.modify_subnet_attribute(
            SubnetId=subnet_id,
            MapPublicIpOnLaunch={'Value': True}
        )

    # Create Route
    def create_route_table(self, vpc_id):
        LOG.logger.info("Creating Route Table .... ")
        return self._client.create_route_table(VpcId=vpc_id)

    def describe_route_table(self, rtble_id):
        return self._client.describe_route_tables(
            Filters=[
                {
                    'Name': 'route-table-id',
                    'Values': [rtble_id]
                },
            ],
        )

    def enable_route_propagation(self, vgw_id, route_id):
        LOG.logger.info("Enabling Propagation .... " + route_id)
        return self._client.enable_vgw_route_propagation(GatewayId=vgw_id, RouteTableId=route_id)

    def disable_route_propagation(self, vgw_id, route_id):
        LOG.logger.info("Disabling Propagation .... " + route_id)
        return self._client.disable_vgw_route_propagation(GatewayId=vgw_id, RouteTableId=route_id)

    def add_route_to_igw_vgw(self, gw_id, rt_id, cidirip):
        LOG.logger.info(f"Adding IP Address {cidirip} and Gateway {gw_id} to  this Route Table {rt_id} ")
        return self._client.create_route(
            DestinationCidrBlock=cidirip,
            GatewayId=gw_id,
            RouteTableId=rt_id
        )

    def add_route_to_nat(self, ngw_id, rt_id, cidirip):
        LOG.logger.info(f"Adding IP Address {cidirip} and Gateway {ngw_id} to  this Route Table {rt_id} ")
        return self._client.create_route(
            DestinationCidrBlock=cidirip,
            NatGatewayId=ngw_id,
            RouteTableId=rt_id

        )

    def add_route_to_tgw(self, tgw_id, rt_id, cidirip):
        LOG.logger.info(f"Adding IP Address {cidirip} and Gateway {tgw_id} to  this Route Table {rt_id} ")
        return self._client.create_route(
            DestinationCidrBlock=cidirip,
            TransitGatewayId=tgw_id,
            RouteTableId=rt_id
        )

    def add_route_to_vpc_peering(self, peer_id, rt_id, cidirip):
        LOG.logger.info(f"Adding IP Address {cidirip} and Gateway {peer_id} to  this Route Table {rt_id} ")
        return self._client.create_route(
            DestinationCidrBlock=cidirip,
            VpcPeeringConnectionId=peer_id,
            RouteTableId=rt_id
        )

    def add_route_to_endpoint_gw(self, vpce_id, rm_rt, add_rt):
        LOG.logger.info("Adding Endpoint " + vpce_id + " Remove Route Table " + rm_rt + " Add Route table " + add_rt)
        return self._client.modify_vpc_endpoint(
            VpcEndpointId=vpce_id,
            RemoveRouteTableIds=[rm_rt],
            AddRouteTableIds=[add_rt],

        )

    def delete_route_record(self, rt_id, cidirip):
        LOG.logger.info("delete IP Address to " + cidirip + " This Route Table " + rt_id)
        return self._client.delete_route(
            DestinationCidrBlock=cidirip,
            RouteTableId=rt_id,
        )

    def enable_propagation_route_table(self, vgw_id, rt_id):
        LOG.logger.info(f"Enable Propagation This Route Table {rt_id}")
        return self._client.enable_vgw_route_propagation(
            GatewayId=vgw_id,
            RouteTableId=rt_id,
        )

    def disable_propagation_route_table(self, vgw_id, rt_id):
        LOG.logger.info(f"Disabling Propagation This Route Table {rt_id}")
        return self._client.disable_vgw_route_propagation(
            GatewayId=vgw_id,
            RouteTableId=rt_id,
        )

    def route_table_associate_with_subnet(self, route_id, subnet_id):
        LOG.logger.info("Associating Route Table " + route_id + " to Subnet " + subnet_id)
        return self._client.associate_route_table(RouteTableId=route_id, SubnetId=subnet_id)

    def route_table_disassociate_with_subnet(self, disassocate_id):
        LOG.logger.info("Disassociating Route " + disassocate_id)
        self._client.disassociate_route_table(AssociationId=disassocate_id)

    # Delete Route Table
    def delete_route_tables(self, route_id):
        LOG.logger.info("Deleting This Route Table - " + route_id)
        return self._client.delete_route_table(RouteTableId=route_id)
