from flask import Flask, render_template, jsonify, request, make_response, json, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import s3troposphere
import ec2troposphere

class Config(object):
    SECRET_KEY = '\xf5\xd4\x90sd\xed\xa8\xf6\x867B\n\xd0\xdcR\xb1'
    SQLALCHEMY_DATABASE_URI='mysql://root:AmazingTheory62@localhost:3306/cloud_formation'
    DEBUG = True


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:AmazingTheory62@localhost:3306/cloud_formation'
app.config.from_object(Config)
db = SQLAlchemy(app)


class s3_table(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    description = db.Column(db.String(80), nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<s3_table %r>' % self.username


class ec2_table(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    region = db.Column(db.String(80))
    instance = db.Column(db.String(80))
    vpc = db.Column(db.String(80))
    subnet = db.Column(db.String(80))

    def __init__(self, name, region, instance, vpc, subnet):
        self.name = name
        self.region = region
        self.instance = instance
        self.vpc = vpc
        self.subnet = subnet

    def __repr__(self):
        return '<ec2_table %r>' % self.username


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/s3')
def s3_render():
    return render_template('s3.html')


@app.route('/create_s3_bucket', methods=['GET', 'POST'])
def s3():
    if request.method == 'POST':
        if not request.form['bucket_name'] or not request.form['description']:
            flash('Please enter all the fields', 'error')
        else:
            s3dbs = s3_table(request.form['bucket_name'], request.form['description'])
            db.session.add(s3dbs)
            db.session.commit()
            flash('Record was successfully added')
            s3troposphere.create()
            s3troposphere.syscommand()
            return redirect(url_for('s3success'))

    return render_template('s3.html')


@app.route('/s3success')
def s3success():
    return render_template('s3success.html')


@app.route('/ec2')
def ec2_render():
    return render_template('ec2.html')


@app.route('/ec2_instance', methods=['GET', 'POST'])
def ec2():
    if request.method == 'POST':
        if not request.form['instance_name'] or not request.form['region'] or not request.form['instance'] or not request.form['vpc'] or not request.form['subnet']:
            flash('Please enter all the fields', 'error')
        else:
            ec2dbs = ec2_table(request.form['instance_name'], request.form['region'], request.form['instance'], request.form['vpc'], request.form['subnet'])
            db.session.add(ec2dbs)
            db.session.commit()
            flash('Record was successfully added')
            ec2troposphere.create()
            ec2troposphere.syscommand()
            return redirect(url_for('ec2success'))
    return render_template('ec2.html')


@app.route('/ec2success')
def ec2success():
    return render_template('ec2success.html')


@app.route('/rds')
def rds():
    return render_template('rds.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/vpc')
def vpc():
    return render_template('vpc.html')


if __name__ == "__main__":
    app.run(port=8080, debug=True)