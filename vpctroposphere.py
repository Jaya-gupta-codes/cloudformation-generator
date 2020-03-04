from troposphere import Parameter, Ref, Tags, Template
from troposphere.ec2 import Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
    VPC,  \
    InternetGateway
import mysql.connector
import os

def create():
    from troposphere.ec2 import Route, \
        VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
        VPC \

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="AmazingTheory62",
        database="cloud_formation"
    )

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vpc_table")
    myresult = (mycursor.fetchone())
    sname = myresult[0]
    vpcname = myresult[1]
    vpccidr = myresult[2]
    subnetname = myresult[3]
    subnetcidr = myresult[4]
    rname = myresult[5]
    igwname = myresult[6]

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


    ref_stack_id = Ref('AWS::StackId')
    ref_region = Ref('AWS::Region')
    ref_stack_name = Ref('AWS::StackName')

    VPC = t.add_resource(
        VPC(
            'VPC',
            CidrBlock='10.0.0.0/16',
            Tags=Tags(Name=vpcname,
                Application=ref_stack_id)))

    subnet = t.add_resource(
        Subnet(
            'Subnet',
            CidrBlock='10.0.0.0/24',
            VpcId=Ref(VPC),
            Tags=Tags(
                Name=subnetname,
                Application=ref_stack_id)))

    internetGateway = t.add_resource(
        InternetGateway(
            'InternetGateway',
            Tags=Tags(
                Name=igwname,
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
                Name=rname,
                Application=ref_stack_id)))

    route = t.add_resource(
        Route(
            'Route',
            DependsOn='AttachGateway',
            GatewayId=Ref('InternetGateway'),
            DestinationCidrBlock='0.0.0.0/0',
            RouteTableId=Ref(routeTable),
        ))

    subnetRouteTableAssociation = t.add_resource(
        SubnetRouteTableAssociation(
            'SubnetRouteTableAssociation',
            SubnetId=Ref(subnet),
            RouteTableId=Ref(routeTable),
        ))


    print(t.to_json())
    file = open('vpcjson.json', 'w')
    file.write(t.to_json())
    file.close()
    os.system('aws cloudformation create-stack --stack-name ' + sname + ' --template-body file://vpcjson.json')