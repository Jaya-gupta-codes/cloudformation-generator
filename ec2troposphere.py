#works
from troposphere import FindInMap, GetAtt, Join
from troposphere import Parameter, Output, Ref, Select, Tags, Template
import troposphere.ec2 as ec2
import mysql.connector
import os


def create():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="AmazingTheory62",
        database="cloud_formation"
    )


    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ec2_table")
    myresult = (mycursor.fetchone())
    name = myresult[0]
    region = myresult[1]
    itype = myresult[2]
    vpc1 = myresult[3]
    subnet1 = myresult[4]

    #print(type(vpc1))

    template = Template()

    keyname_param = template.add_parameter(Parameter(
        "KeyName",
        Description="Name of an existing EC2 KeyPair to enable SSH "
                    "access to the instance",
        Type="String",
        Default="jayaincentiuskey"
    ))

    vpcid_param = template.add_parameter(Parameter(
        "VpcId",
        Description="VpcId of your existing Virtual Private Cloud (VPC)",
        Type="String",
        Default=vpc1
    ))

    subnetid_param = template.add_parameter(Parameter(
        "SubnetId",
        Description="SubnetId of an existing subnet (for the primary network) in "
                    "your Virtual Private Cloud (VPC)" "access to the instance",
        Type="String",
        Default=subnet1
    ))

    secondary_ip_param = template.add_parameter(Parameter(
        "SecondaryIPAddressCount",
        Description="Number of secondary IP addresses to assign to the network "
                    "interface (1-5)",
        ConstraintDescription="must be a number from 1 to 5.",
        Type="Number",
        Default="1",
        MinValue="1",
        MaxValue="5",
    ))

    sshlocation_param = template.add_parameter(Parameter(
        "SSHLocation",
        Description="The IP address range that can be used to SSH to the "
                    "EC2 instances",
        Type="String",
        MinLength="9",
        MaxLength="18",
        Default="0.0.0.0/0",
        AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})"
                       "/(\\d{1,2})",
        ConstraintDescription="must be a valid IP CIDR range of the "
                              "form x.x.x.x/x."
    ))

    template.add_mapping('RegionMap', {
        "us-west-2": {"AMI": region}
    })

    eip1 = template.add_resource(ec2.EIP(
        "EIP1",
        Domain="vpc",
    ))

    ssh_sg = template.add_resource(ec2.SecurityGroup(
        "SSHSecurityGroup",
        VpcId=Ref(vpcid_param),
        GroupDescription="Enable SSH access via port 22",
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="22",
                ToPort="22",
                CidrIp=Ref(sshlocation_param),
            ),
        ],
    ))

    eth0 = template.add_resource(ec2.NetworkInterface(
        "Eth0",
        Description="eth0",
        GroupSet=[Ref(ssh_sg), ],
        SourceDestCheck=True,
        SubnetId=Ref(subnetid_param),
        Tags=Tags(
            Name="Interface 0",
            Interface="eth0",
        ),
        SecondaryPrivateIpAddressCount=Ref(secondary_ip_param),
    ))

    # eipassoc1 = template.add_resource(ec2.EIPAssociation(
    #     "EIPAssoc1",
    #     NetworkInterfaceId=Ref(eth0),
    #     AllocationId=GetAtt("EIP1", "AllocationId"),
    #     PrivateIpAddress=GetAtt("Eth0", "PrimaryPrivateIpAddress"),
    # ))

    ec2_instance = template.add_resource(ec2.Instance(
        "EC2Instance",
        ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
        InstanceType=itype,
        KeyName=Ref(keyname_param),
        NetworkInterfaces=[
            ec2.NetworkInterfaceProperty(
                NetworkInterfaceId=Ref(eth0),
                DeviceIndex="0",
            ),
        ],
        Tags=Tags(Name=name, )
    ))

    template.add_output([
        Output(
            "InstanceId",
            Description="InstanceId of the newly created EC2 instance",
            Value=Ref(ec2_instance),
        ),
        Output(
            "EIP1",
            Description="Primary public IP address for Eth0",
            Value=Join(" ", [
                "IP address", Ref(eip1), "on subnet", Ref(subnetid_param)
            ]),
        ),
        Output(
            "PrimaryPrivateIPAddress",
            Description="Primary private IP address of Eth0",
            Value=Join(" ", [
                "IP address", GetAtt("Eth0", "PrimaryPrivateIpAddress"),
                "on subnet", Ref(subnetid_param)
            ]),
        ),
        Output(
            "FirstSecondaryPrivateIPAddress",
            Description="First secondary private IP address of Eth0",
            Value=Join(" ", [
                "IP address",
                Select("0", GetAtt("Eth0", "SecondaryPrivateIpAddresses")),
                "on subnet", Ref(subnetid_param)
            ]),
        ),
    ])

    print(template.to_json())
    file = open('ec2json.json', 'w')
    file.write(template.to_json())
    file.close()


def syscommand():
    os.system('aws cloudformation create-stack --stack-name ec2example --template-body file://ec2json.json')