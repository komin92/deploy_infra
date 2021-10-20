from src.bin.client_locate import EC2Client
from collections import defaultdict
from src.config.config import *
from pathlib import Path
import re


class Var:
    def __init__(self, client):
        self._client = client
        """ :type : pyboto3.ec2 """

    def convert_list_to_dict(self, list1, list2):
        result = defaultdict(list)
        for key, value in zip(list1, list2):
            result[key].append(value)
        return dict(result)

    def export_route_table_info_to_file(self):
        result = self._client.describe_route_tables()
        try:
            file_write_handler(efile_name, result, output, 'w')
            LOG.logger.info("Querying Route Table Information ......")
            LOG.logger.info(f"Export data and input to this file {efile_name}.{output} ")
        except Exception as e:
            LOG.logger.error(e)

    def get_data_from_route_table_info_file(self):
        my_file = Path(f"../{efile_name}.{output}")
        i = 1
        while i < 3:
            if my_file.is_file():
                if os.stat(f'../{efile_name}.{output}').st_size > 0:
                    result = file_read_handler(efile_name, output)
                    return result
                else:
                    LOG.logger.info("Querying Route Table Information ......")
                    self.export_route_table_info_to_file()
            else:
                LOG.logger.info("Querying Route Table Information ......")
                self.export_route_table_info_to_file()

    def geers(self, *args, **kwargs):
        response = self.get_data_from_route_table_info_file()
        for x in range(len(response['RouteTables'])):
            if kwargs['rtbid'] in response['RouteTables'][x]['RouteTableId']:
                result = response['RouteTables'][x]
                return result

    def get_replace_gateway_id(self, current_route_id, to_gw, on_premise_ip):
        routes, route_name = self.get_route_list(current_route_id)
        route_list = dict(routes)
        replace_route = []
        tgw_id = []
        cidr_ips = []

        def export_replace_gw_cidr_ip(rgw_id, cidr_ip):
            for x in range(len(cidr_ip)):
                tgw_id.append(rgw_id)
                cidr_ips.append(cidr_ip[x])

        for key in route_list:
            if re.search("^tgw", key):
                export_replace_gw_cidr_ip(key, route_list[key])
            elif re.search("^igw", key):
                export_replace_gw_cidr_ip(key, route_list[key])
            elif re.search("^vgw", key):
                cidr_ip = on_premise_ip
                export_replace_gw_cidr_ip(to_gw, cidr_ip)
            elif re.search("^nat", key):
                export_replace_gw_cidr_ip(key, route_list[key])
            elif re.search("^pcx", key):
                export_replace_gw_cidr_ip(key, route_list[key])
            elif re.search("^vpce", key):
                export_replace_gw_cidr_ip(key, route_list[key])

        tgw_ip = self.convert_list_to_dict(tgw_id, cidr_ips)
        return tgw_ip, route_name

    def get_replace_tgw_only_id(self, current_route_id, to_gw,):
        routes, route_name = self.get_route_list(current_route_id)
        route_list = dict(routes)
        replace_route = []
        tgw_id = []
        cidr_ips = []

        def export_replace_gw_cidr_ip(rgw_id, cidr_ip):
            for x in range(len(cidr_ip)):
                tgw_id.append(rgw_id)
                cidr_ips.append(cidr_ip[x])

        for key in route_list:
            if re.search("^tgw", key):
                export_replace_gw_cidr_ip(to_gw, route_list[key])

        tgw_ip = self.convert_list_to_dict(tgw_id, cidr_ips)
        return tgw_ip, route_name

    # Current Not used
    def get_route_table_id_lists_via_vpc_id(self, u_vpc_id):
        response = self.get_data_from_route_table_info_file()
        routeid_lists = []
        vpcid_lists = []
        for x in range(len(response['RouteTables'])):
            # route_id = ([response['RouteTables'][x]['RouteTableId']])
            route_id = response['RouteTables'][x]['RouteTableId']
            routeid_lists.append(route_id)
            vpc_id = response['RouteTables'][x]['VpcId']
            vpcid_lists.append(vpc_id)

        vgw_route_id = self.convert_list_to_dict(vpcid_lists, routeid_lists)
        for key in vgw_route_id:
            if u_vpc_id in key:
                r_route_id = (vgw_route_id[key])
        return r_route_id

    def get_all_route_table_id_via_each_account(self):
        response = self.get_data_from_route_table_info_file()
        routeid_lists = []
        vpcid_lists = []
        r_route_id_lists = []
        for x in range(len(response['RouteTables'])):
            # route_id = ([response['RouteTables'][x]['RouteTableId']])
            route_id = response['RouteTables'][x]['RouteTableId']
            routeid_lists.append(route_id)
            vpc_id = response['RouteTables'][x]['VpcId']
            vpcid_lists.append(vpc_id)

        vgw_route_id = Var.convert_list_to_dict(self, vpcid_lists, routeid_lists)
        return vgw_route_id

    def get_route_list(self, route_id):
        get_route_role_lists = []
        gateway_id = []
        cidr_ip = []
        # response = self._client.describe_route_tables(Filters=[{'Name': 'route-table-id', 'Values':
        # [route_id]}])["RouteTables"]
        response = self.geers(rtbid=route_id)
        route_name = response["Tags"][0]['Value']
        # for result in response:
        for i in range(len(response['Routes'])):
            ip = response['Routes'][i]
            get_route_role_lists.append(ip)

        for x in range(len(get_route_role_lists)):
            get_route_role = get_route_role_lists[x]
            get_values_of_route_list = []
            for key in get_route_role:
                route_value = get_route_role[key]
                get_values_of_route_list.append(route_value)
            cidr_ip.append(get_values_of_route_list[0])
            if re.search("^pcx", get_values_of_route_list[3]):
                gateway_id.append(get_values_of_route_list[3])
            else:
                gateway_id.append(get_values_of_route_list[1])
        routes = self.convert_list_to_dict(gateway_id, cidr_ip)
        return routes, route_name

    def get_propagation_id(self, route_id):
        response = self.geers(rtbid=route_id)
        propage_id = response['PropagatingVgws'][0]['GatewayId']
        print(propage_id)
        return propage_id

    def get_route_table_associate_subnet_lists(self, current_route_id):
        # response = self._client.describe_route_tables(
        #     Filters=[{'Name': 'route-table-id', 'Values': [current_route_id]}])
        response = self.geers(rtbid=current_route_id)
        assocate_lists = []
        route_table_ids = []
        Mains = response['Associations']
        # for x in range(len(response["RouteTables"])):
        route_table_name = response["Tags"][0]['Value']
        association = response['Associations']
        route_table_id = response['RouteTableId']
        route_table_ids.append(route_table_id)
        subnet_ids = []
        route_ids = []
        dis_associate_id = []
        for i in range(len(association)):
            if 'RouteTableAssociationId' in association[i]:
                dis_associate_id.append(association[i]['RouteTableAssociationId'])
            else:
                print("no association")
            if 'SubnetId' in association[i]:
                subnet_id = response['Associations'][i]['SubnetId']
                subnet_ids.append(subnet_id)

            elif 'SubnetId' not in association[i]:
                LOG.logger.warning(f"This Route Table {route_table_id} don't have any associated subnet")
        for y in range(len(subnet_ids)):
            route_ids.append(route_table_id)

        assocate_list = self.convert_list_to_dict(route_ids, subnet_ids)
        assocate_lists.append(assocate_list)
        for main in Mains:
            if main['Main']:
                assocate_list.clear()
                dis_associate_id.clear()
            else:
                LOG.logger.info(f'Continue association this route {route_table_id}')

        return assocate_list, dis_associate_id

    def get_vpc_id_of_route_table(self, route_id):  # Need to clear ----------------------
        response = self.geers(rtbid=route_id)
        rvpc_id = response['VpcId']
        return rvpc_id

    def check_route_table_ids(self, route_id):
        return self._client.describe_route_tables(Filters=[{'Name': 'route-table-id', 'Values': [route_id]}])
