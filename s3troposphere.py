from troposphere import Output, Ref, Template
from troposphere.s3 import Bucket, PublicRead
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
    mycursor.execute("SELECT * FROM s3_table")
    myresult = (mycursor.fetchone())
    bname = myresult[0]
    desc = myresult[1]

    t = Template()
    t.set_description(desc)
    s3bucket = t.add_resource(Bucket(bname))
    t.add_output(Output(
        "BucketName",
        Value=Ref(s3bucket),
        Description=desc
    ))
    print(t.to_json())
    file = open('s3json.json', 'w')
    file.write(t.to_json())
    file.close()


def syscommand():
    os.system('aws cloudformation create-stack --stack-name s3example --template-body file://s3json.json')
