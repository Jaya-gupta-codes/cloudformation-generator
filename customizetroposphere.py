from troposphere import Base64, FindInMap, GetAtt, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.ec2 import PortRange, NetworkAcl, Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
    VPC, NetworkInterfaceProperty, NetworkAclEntry, \
    SubnetNetworkAclAssociation, EIP, Instance, InternetGateway, \
    SecurityGroupRule, SecurityGroup
from troposphere.rds import DBInstance, DBSubnetGroup
import mysql.connector
import os


def create():
    from troposphere.ec2 import PortRange, NetworkAcl, Route, \
        VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
        VPC, NetworkInterfaceProperty


    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="AmazingTheory62",
        database="cloud_formation"
    )

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM customize_table")
    myresult = (mycursor.fetchone())
    sname = myresult[0]
    instance1 = myresult[1]
    instancetype1 = myresult[2]
    instance2 = myresult[3]
    instancetype2 = myresult[4]
    dbname = myresult[5]
    dbuser = myresult[6]
    dbpassword = myresult[7]
    dbstorage = myresult[8]
    dbinstance = myresult[9]
    vpcname = myresult[10]
    subnetname = myresult[11]

    t = Template()

    t.add_version('2010-09-09')

    t.set_description("""\
    AWS CloudFormation Sample Template VPC_Single_Instance_In_Subnet: Sample \
    template showing how to create a VPC and add an EC2 instance with an Elastic \
    IP address and a security group. \
    **WARNING** This template creates an Amazon EC2 instance. You will be billed \
    for the AWS resources used if you create a stack from this template.""")

    keyname_param = t.add_parameter(
        Parameter(
            'KeyName',
            ConstraintDescription='must be the name of an existing EC2 KeyPair.',
            Description='Name of an existing EC2 KeyPair to enable SSH access to \
    the instance',
            Type='AWS::EC2::KeyPair::KeyName',
            Default='jayaincentiuskey',
        ))

    sshlocation_param = t.add_parameter(
        Parameter(
            'SSHLocation',
            Description=' The IP address range that can be used to SSH to the EC2 \
    instances',
            Type='String',
            MinLength='9',
            MaxLength='18',
            Default='0.0.0.0/0',
            AllowedPattern=r"(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})",
            ConstraintDescription=(
                "must be a valid IP CIDR range of the form x.x.x.x/x."),
        ))

    instanceType_param = t.add_parameter(Parameter(
        'InstanceType',
        Type='String',
        Description='WebServer EC2 instance type',
        Default=instancetype1,
        AllowedValues=[
            't1.micro',
            't2.micro', 't2.small', 't2.medium',
            'm1.small', 'm1.medium', 'm1.large', 'm1.xlarge',
            'm2.xlarge', 'm2.2xlarge', 'm2.4xlarge',
            'm3.medium', 'm3.large', 'm3.xlarge', 'm3.2xlarge',
            'c1.medium', 'c1.xlarge',
            'c3.large', 'c3.xlarge', 'c3.2xlarge', 'c3.4xlarge', 'c3.8xlarge',
            'g2.2xlarge',
            'r3.large', 'r3.xlarge', 'r3.2xlarge', 'r3.4xlarge', 'r3.8xlarge',
            'i2.xlarge', 'i2.2xlarge', 'i2.4xlarge', 'i2.8xlarge',
            'hi1.4xlarge',
            'hs1.8xlarge',
            'cr1.8xlarge',
            'cc2.8xlarge',
            'cg1.4xlarge',
        ],
        ConstraintDescription='must be a valid EC2 instance type.',
    ))

    instanceType_param1 = t.add_parameter(Parameter(
        'SecindInstanceType',
        Type='String',
        Description='WebServer EC2 instance type',
        Default=instancetype2,
        AllowedValues=[
            't1.micro',
            't2.micro', 't2.small', 't2.medium',
            'm1.small', 'm1.medium', 'm1.large', 'm1.xlarge',
            'm2.xlarge', 'm2.2xlarge', 'm2.4xlarge',
            'm3.medium', 'm3.large', 'm3.xlarge', 'm3.2xlarge',
            'c1.medium', 'c1.xlarge',
            'c3.large', 'c3.xlarge', 'c3.2xlarge', 'c3.4xlarge', 'c3.8xlarge',
            'g2.2xlarge',
            'r3.large', 'r3.xlarge', 'r3.2xlarge', 'r3.4xlarge', 'r3.8xlarge',
            'i2.xlarge', 'i2.2xlarge', 'i2.4xlarge', 'i2.8xlarge',
            'hi1.4xlarge',
            'hs1.8xlarge',
            'cr1.8xlarge',
            'cc2.8xlarge',
            'cg1.4xlarge',
        ],
        ConstraintDescription='must be a valid EC2 instance type.',
    ))

    t.add_mapping('AWSInstanceType2Arch', {
        't1.micro': {'Arch': 'PV64'},
        't2.micro': {'Arch': 'HVM64'},
        't2.small': {'Arch': 'HVM64'},
        't2.medium': {'Arch': 'HVM64'},
        'm1.small': {'Arch': 'PV64'},
        'm1.medium': {'Arch': 'PV64'},
        'm1.large': {'Arch': 'PV64'},
        'm1.xlarge': {'Arch': 'PV64'},
        'm2.xlarge': {'Arch': 'PV64'},
        'm2.2xlarge': {'Arch': 'PV64'},
        'm2.4xlarge': {'Arch': 'PV64'},
        'm3.medium': {'Arch': 'HVM64'},
        'm3.large': {'Arch': 'HVM64'},
        'm3.xlarge': {'Arch': 'HVM64'},
        'm3.2xlarge': {'Arch': 'HVM64'},
        'c1.medium': {'Arch': 'PV64'},
        'c1.xlarge': {'Arch': 'PV64'},
        'c3.large': {'Arch': 'HVM64'},
        'c3.xlarge': {'Arch': 'HVM64'},
        'c3.2xlarge': {'Arch': 'HVM64'},
        'c3.4xlarge': {'Arch': 'HVM64'},
        'c3.8xlarge': {'Arch': 'HVM64'},
        'g2.2xlarge': {'Arch': 'HVMG2'},
        'r3.large': {'Arch': 'HVM64'},
        'r3.xlarge': {'Arch': 'HVM64'},
        'r3.2xlarge': {'Arch': 'HVM64'},
        'r3.4xlarge': {'Arch': 'HVM64'},
        'r3.8xlarge': {'Arch': 'HVM64'},
        'i2.xlarge': {'Arch': 'HVM64'},
        'i2.2xlarge': {'Arch': 'HVM64'},
        'i2.4xlarge': {'Arch': 'HVM64'},
        'i2.8xlarge': {'Arch': 'HVM64'},
        'hi1.4xlarge': {'Arch': 'HVM64'},
        'hs1.8xlarge': {'Arch': 'HVM64'},
        'cr1.8xlarge': {'Arch': 'HVM64'},
        'cc2.8xlarge': {'Arch': 'HVM64'},
    })

    t.add_mapping('AWSRegionArch2AMI', {
        'us-east-1': {'PV64': 'ami-50842d38', 'HVM64': 'ami-08842d60',
                      'HVMG2': 'ami-3a329952'},
        'us-west-2': {'PV64': 'ami-af86c69f', 'HVM64': 'ami-8786c6b7',
                      'HVMG2': 'ami-47296a77'},
        'us-west-1': {'PV64': 'ami-c7a8a182', 'HVM64': 'ami-cfa8a18a',
                      'HVMG2': 'ami-331b1376'},
        'eu-west-1': {'PV64': 'ami-aa8f28dd', 'HVM64': 'ami-748e2903',
                      'HVMG2': 'ami-00913777'},
        'ap-southeast-1': {'PV64': 'ami-20e1c572', 'HVM64': 'ami-d6e1c584',
                           'HVMG2': 'ami-fabe9aa8'},
        'ap-northeast-1': {'PV64': 'ami-21072820', 'HVM64': 'ami-35072834',
                           'HVMG2': 'ami-5dd1ff5c'},
        'ap-southeast-2': {'PV64': 'ami-8b4724b1', 'HVM64': 'ami-fd4724c7',
                           'HVMG2': 'ami-e98ae9d3'},
        'sa-east-1': {'PV64': 'ami-9d6cc680', 'HVM64': 'ami-956cc688',
                      'HVMG2': 'NOT_SUPPORTED'},
        'cn-north-1': {'PV64': 'ami-a857c591', 'HVM64': 'ami-ac57c595',
                       'HVMG2': 'NOT_SUPPORTED'},
        'eu-central-1': {'PV64': 'ami-a03503bd', 'HVM64': 'ami-b43503a9',
                         'HVMG2': 'ami-b03503ad'},
    })

    ref_stack_id = Ref('AWS::StackId')
    ref_region = Ref('AWS::Region')
    ref_stack_name = Ref('AWS::StackName')

    VPC = t.add_resource(
        VPC(
            'VPC',
            CidrBlock='10.0.0.0/16',
            Tags=Tags(
                Name=vpcname,
                Application=ref_stack_id)))

    subnet = t.add_resource(
        Subnet(
            'publicSubnet',
            CidrBlock='10.0.1.0/24',
            AvailabilityZone='us-west-2b',
            VpcId=Ref(VPC),
            Tags=Tags(
                Name=subnetname,
                Application=ref_stack_id)))

    subnet1 = t.add_resource(
         Subnet(
             'publicSubnet1',
             CidrBlock='10.0.3.0/24',
             AvailabilityZone='us-west-2a',
             VpcId=Ref(VPC),
             Tags=Tags(
                 Name=subnetname,
                 Application=ref_stack_id)))

    publicsubnet = t.add_resource(
         Subnet(
             'PrivateSubnet',
             CidrBlock='10.0.0.0/24',
             AvailabilityZone='us-west-2a',
             VpcId=Ref(VPC),
             Tags=Tags(
                 Name=subnetname,
                 Application=ref_stack_id)))

    publicsubnet1 = t.add_resource(
         Subnet(
             'PrivateSubnet1',
             CidrBlock='10.0.2.0/24',
             AvailabilityZone='us-west-2b',
             VpcId=Ref(VPC),
             Tags=Tags(
                 Name=subnetname,
                 Application=ref_stack_id)))

    internetGateway = t.add_resource(
        InternetGateway(
            'InternetGateway',
            Tags=Tags(
                Application=ref_stack_id)))

    gatewayAttachment = t.add_resource(
        VPCGatewayAttachment(
            'AttachGateway',
            VpcId=Ref(VPC),
            InternetGatewayId=Ref(internetGateway)))

    routeTable = t.add_resource(
        RouteTable(
            'RouteTable',
            VpcId=Ref(VPC),
            Tags=Tags(
                Application=ref_stack_id)))

    route = t.add_resource(
        Route(
            'Route',
            DependsOn='AttachGateway',
            GatewayId=Ref('InternetGateway'),
            DestinationCidrBlock='0.0.0.0/0',
            RouteTableId=Ref(routeTable),
        ))

    routeTable1 = t.add_resource(
        RouteTable(
            'PrivateRouteTable',
            VpcId=Ref(VPC),
            Tags=Tags(
                Application=ref_stack_id)))

    # route1 = t.add_resource(
    #     Route(
    #         'PublicRoute',
    #         DependsOn='AttachGateway',
    #         GatewayId=Ref('InternetGateway'),
    #         DestinationCidrBlock='0.0.0.0/0',
    #         RouteTableId=Ref(routeTable1),
    #     ))

    subnetRouteTableAssociation = t.add_resource(
        SubnetRouteTableAssociation(
            'SubnetRouteTableAssociation',
            SubnetId=Ref(subnet),
            RouteTableId=Ref(routeTable),
        ))

    subnetRouteTableAssociation1 = t.add_resource(
        SubnetRouteTableAssociation(
            'SubnetRouteTableAssociation1',
            SubnetId=Ref(subnet1),
            RouteTableId=Ref(routeTable),
        ))

    subnetRouteTableAssociation2 = t.add_resource(
        SubnetRouteTableAssociation(
            'SubnetRouteTable1Association2',
            SubnetId=Ref(publicsubnet),
            RouteTableId=Ref(routeTable1),
        ))

    subnetRouteTableAssociation3 = t.add_resource(
        SubnetRouteTableAssociation(
            'SubnetRouteTable1Association3',
            SubnetId=Ref(publicsubnet1),
            RouteTableId=Ref(routeTable1),
        ))
    #
    # subnetRouteTableAssociation4= t.add_resource(
    #     SubnetRouteTableAssociation(
    #         'SubnetRouteTable1Association4',
    #         SubnetId=Ref(subnet1),
    #         RouteTableId=Ref(routeTable1),
    #     ))

    instanceSecurityGroup = t.add_resource(
        SecurityGroup(
            'InstanceSecurityGroup',
            GroupDescription='Enable SSH access via port 22',
            SecurityGroupIngress=[
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort='22',
                    ToPort='22',
                    CidrIp=Ref(sshlocation_param)),
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort='80',
                    ToPort='80',
                    CidrIp='0.0.0.0/0')],
            VpcId=Ref(VPC),
        ))


    instance = t.add_resource(
        Instance(
            'WebServerInstance',
            #Metadata=instance_metadata,
            ImageId=FindInMap(
                'AWSRegionArch2AMI',
                Ref('AWS::Region'),
                FindInMap(
                    'AWSInstanceType2Arch',
                    Ref(instanceType_param),
                    'Arch')),
            InstanceType=Ref(instanceType_param),
            KeyName=Ref(keyname_param),
            NetworkInterfaces=[
                NetworkInterfaceProperty(
                    GroupSet=[
                        Ref(instanceSecurityGroup)],
                    AssociatePublicIpAddress='true',
                    DeviceIndex='0',
                    DeleteOnTermination='true',
                    SubnetId=Ref(subnet))],
            Tags=Tags(
                Name=instance1,
                Application=ref_stack_id),
        ))

    instance1 = t.add_resource(
        Instance(
            'WebServerInstance1',
            #Metadata=instance_metadata,
            ImageId=FindInMap(
                'AWSRegionArch2AMI',
                Ref('AWS::Region'),
                FindInMap(
                    'AWSInstanceType2Arch',
                    Ref(instanceType_param1),
                    'Arch')),
            InstanceType=Ref(instanceType_param1),
            KeyName=Ref(keyname_param),
            NetworkInterfaces=[
                NetworkInterfaceProperty(
                    GroupSet=[
                        Ref(instanceSecurityGroup)],
                    AssociatePublicIpAddress='true',
                    DeviceIndex='0',
                    DeleteOnTermination='true',
                    SubnetId=Ref(subnet1))],
            Tags=Tags(
                Name=instance2,
                Application=ref_stack_id),
        ))


    # rdssubnet = t.add_parameter(Parameter(
    #     "Subnets",
    #     Type="CommaDelimitedList",
    #     Default=Ref(publicsubnet1),
    #     Description=(
    #         "The list of SubnetIds, for at least two Availability Zones in the "
    #         "region in your Virtual Private Cloud (VPC)")
    # ))


    mydbsubnetgroup = t.add_resource(DBSubnetGroup(
        "MyDBSubnetGroup",
        DBSubnetGroupDescription="Subnets available for the RDS DB Instance",
        # Type="CommaDelimitedList",
        SubnetIds=[Ref(publicsubnet) ,Ref(publicsubnet1)],
    ))


    mydb = t.add_resource(DBInstance(
        "MyDB",
        DBName=dbname,
        AllocatedStorage=dbstorage,
        DBInstanceClass=dbinstance,
        Engine="MySQL",
        EngineVersion="5.5",
        MasterUsername=dbuser,
        MasterUserPassword=dbpassword,
        DBSubnetGroupName=Ref(mydbsubnetgroup),
    ))

    t.add_output(Output(
        "JDBCConnectionString",
        Description="JDBC connection string for database",
        Value=Join("", [
            "jdbc:mysql://",
            GetAtt("MyDB", "Endpoint.Address"),
            GetAtt("MyDB", "Endpoint.Port"),
            "/",
            "customizedb"
        ])
    ))


    # print(t.to_json())
    file = open('customizejson.json', 'w')
    file.write(t.to_json())
    file.close()
    os.system('aws cloudformation create-stack --stack-name ' + sname + ' --template-body file://customizejson.json')

# create()