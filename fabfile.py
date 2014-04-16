import json
import time
import os
import socket
import boto
import boto.ec2
import datetime

from fabric.api import *
from fabric.contrib.project import upload_project
from profilehooks import timecall
from fabric.operations import reboot


env.applications = []
env.angular_applications = ['WebClient', 'WebClientNew']
env.node_applications = ['NameServerAPI', 'Dashboard']
env.java_applications = ['BoastfulFingerprint', 'Bucket', 'CEO', 'CIK', 'Controller', 'DeluxeLabeler', 'FancyNLP', 'Feeder', 'FoxyCEOUpdater', 'LavishClassifier', 'PlayfulStatistician', 'SIC', 'TIC', 'VisDataProvider']
env.colorize_errors = True
env.edition_directory = ''
env.deployment_directory = '/opt/phrTranslation'


@task
def ngserver():
    """
    Connect to the Ngramatic laptop from the host machine
    """
    env.user = 'ngramatic'
    env.hosts = ['{0}:{1}'.format('136.206.48.255', 22)]
    key_filename = os.path.join(os.getcwd(), 'syncResources', 'Keys', 'JLevelingNG')
    env.key_filename = (key_filename)


@task
def check_status():
    """
    Run a curl against the Dashboard
    """
    run('curl -isS http://localhost:3002/status')


@task
def check_logs():
    """
    Every server should be on, and answer status
    """
    run('less /opt/finalytics/BoastfulFingerprint/logs/commandserver.log')
    run('less /opt/finalytics/Bucket/logs/commandserver.log')
    run('less /opt/finalytics/CEO/logs/commandserver.log')
    run('less /opt/finalytics/CIK/logs/commandserver.log')
    run('less /opt/finalytics/Controller/logs/commandserver.log')
    run('less /opt/finalytics/Bucket/logs/queryserver.log')
    run('less /opt/finalytics/DeluxeLabeler/logs/commandserver.log')
    run('less /opt/finalytics/FancyNLP/logs/commandserver.log')
    run('less /opt/finalytics/Feeder/logs/commandserver.log')
    run('less /opt/finalytics/FoxyCEOUpdater/logs/commandserver.log')
    run('less /opt/finalytics/LavishClassifier/logs/commandserver.log')
    run('less /opt/finalytics/PlayfulStatistician/logs/commandserver.log')
    run('less /opt/finalytics/SIC/logs/commandserver.log')
    run('less /opt/finalytics/TIC/logs/commandserver.log')
    run('less /opt/finalytics/VisDataProvider/logs/queryserver.log')


@task
def check_output():
    """
    Every nohup.out should be empty
    """
    run('less /opt/finalytics/BoastfulFingerprint/bin/nohup.out')
    run('less /opt/finalytics/Bucket/bin/nohup.out')
    run('less /opt/finalytics/CEO/bin/nohup.out')
    run('less /opt/finalytics/CIK/bin/nohup.out')
    run('less /opt/finalytics/Controller/bin/nohup.out')
    run('less /opt/finalytics/DeluxeLabeler/bin/nohup.out')
    run('less /opt/finalytics/FancyNLP/bin/nohup.out')
    run('less /opt/finalytics/Feeder/bin/nohup.out')
    run('less /opt/finalytics/FoxyCEOUpdater/bin/nohup.out')
    run('less /opt/finalytics/LavishClassifier/bin/nohup.out')
    run('less /opt/finalytics/PlayfulStatistician/bin/nohup.out')
    run('less /opt/finalytics/SIC/bin/nohup.out')
    run('less /opt/finalytics/TIC/bin/nohup.out')
    run('less /opt/finalytics/VisDataProvider/bin/nohup.out')
    run('less /opt/finalytics/Dashboard/bin/nohup.out')

@task
def upload_mongo():
    """
    Send dump from Mongo database
    """
    sudo('mkdir -p /NGRAMATIC')
    local('tar -zcvf /NGRAMATIC/mongo.dump.tar.gz /NGRAMATIC/mongo_dump/dump/ngramatic')
    put('/NGRAMATIC/mongo.dump.tar.gz', '/NGRAMATIC', use_sudo=True)
    sudo('tar -zxvf /NGRAMATIC/mongo.dump.tar.gz -C /')


@task
def restore_mongo():
    """
    Restore the dump from Maria's machine
    """
    run('mongorestore /NGRAMATIC/mongo_dump/dump/ngramatic/')


@task
def remove_mongo_dump():
    """
    Release the disk space
    """
    sudo('rm -r /NGRAMATIC/mongo_dump')
    sudo('rm -rf /NGRAMATIC/mongo')


@task
def configure_nginx():
    '''
    Create the config file to host the application
    '''
    sudo('touch /opt/nginx/conf/nginx.conf')
    sudo('mkdir -p /opt/nginx/conf/backup')
    sudo('mv --backup=numbered /opt/nginx/conf/nginx.conf /opt/nginx/conf/backup')
    put('../nginx.conf', '/opt/nginx/conf/nginx.conf', use_sudo=True)
    sudo('service nginx stop')
    sudo('service nginx start')


@task
def upload_source_code():
    '''
    Take the build files and send them under a version directory
    '''
    print('build is at %s'.format(env.edition_directory))
    sudo('rm -rf {0}'.format(env.deployment_directory))
    sudo('mkdir -p {0}'.format(env.deployment_directory))
    with lcd(env.edition_directory):
        put('*', env.deployment_directory, use_sudo=True)
        sudo('chown -R {0}:{1} {2}/*'.format(env.user, env.user, env.deployment_directory))


@task
def run_npm():
    '''
    Do an npm install in each directory
    '''
    for application in env.node_applications:
        directory = os.path.join(env.deployment_directory, application, 'bin')
        with cd(directory):
            sudo('npm install')


@task
def upload_resources():
    """
    Get data from the local machine
    """
    sudo('mkdir -p /NGRAMATIC/contentgrader/Resources/en')
    put('/NGRAMATIC/contentgrader/Resources/en', '/NGRAMATIC/contentgrader/Resources', use_sudo=True)
    sudo('mkdir -p /NGRAMATIC/contentgrader/Resources/general')
    put('/NGRAMATIC/contentgrader/Resources/general', '/NGRAMATIC/contentgrader/Resources', use_sudo=True)
    sudo('mkdir -p /SEC')
    put('/SEC/CEO_index', '/SEC', use_sudo=True)
    put('/SEC/CompanyName_index', '/SEC', use_sudo=True)
    put('/SEC/SECFilings_index', '/SEC', use_sudo=True)
    put('/SEC/SIC_index', '/SEC', use_sudo=True)
    put('/SEC/TIC_index', '/SEC', use_sudo=True)
    sudo('mkdir -p /SEC/Training_Set/train_sets_for_service/')
    put('/SEC/Training_Set/train_sets_for_service/train.concatenate.arff', '/SEC/Training_Set/train_sets_for_service/train.concatenate.arff', use_sudo=True)
    sudo('mkdir -p /SEC/Training_Set/model')
    put('/SEC/Training_Set/model/data.model', '/SEC/Training_Set/model/data.model', use_sudo=True)

@task
def build():
    '''
    Prepare an application for deployment
    '''
    base = os.getcwd()
    edition = 'edition-{0}'.format(
        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M'))
    env.edition_directory = os.path.join(base, '../Build', edition)
    local('mkdir -p {0}'.format(env.edition_directory))

    _build_all_python()
    _build_all_java()

def _build_all_python():
    """
    Traverse the list and build each Python application
    """
    for application in env.python_applications:
        _build_python(application)

def _build_all_angular():
    """
    Traverse the list and build each Angular application
    """
    for application in env.angular_applications:
        _build_angular(application)


def _build_all_node():
    """
    Traverse the list and build each NodeJS application
    """
    for application in env.node_applications:
        _build_nodejs(application)


def _build_all_java():
    """
    Traverse the list and build each Java application
    """
    for application in env.java_applications:
        _build_java(application)


def _build_python(application_name):
    """
    Move the code to the right place
    """
    env.applications.append(application_name)
    base = os.getcwd()
    parent = os.path.dirname(os.path.dirname(base))
    source_directory = os.path.join(parent, application_name)
    with lcd(source_directory):
        application_directory = create_directory(env.edition_directory, application_name)
        bin_directory = create_directory(application_directory, 'bin')
        local('cp *.py {0}'.format(bin_directory))

def _build_nodejs(application_name):
    """
    Move the code to the right place
    """
    env.applications.append(application_name)
    base = os.getcwd()
    parent = os.path.dirname(os.path.dirname(base))
    source_directory = os.path.join(parent, application_name)
    with lcd(source_directory):
        application_directory = create_directory(env.edition_directory, application_name)
        bin_directory = create_directory(application_directory, 'bin')
        local('cp package.json {0}'.format(bin_directory))
        local('cp *.js {0}'.format(bin_directory))


def _build_angular(application_name):
    '''
    Move the code to the right place
    '''
    env.applications.append(application_name)
    base = os.getcwd()
    parent = os.path.dirname(os.path.dirname(base))
    source_directory = os.path.join(parent, application_name)
    with lcd(source_directory):
        local('grunt --force')
        application_directory = create_directory(env.edition_directory, application_name)
        www_directory = create_directory(application_directory, 'www')
        local('cp -r ./dist/* {0}'.format(www_directory))


def _build_java(application_name):
    """
    Create jar and copy dist directory
    """
    env.applications.append(application_name)
    base = os.getcwd()
    parent = os.path.dirname(os.path.dirname(base))
    source_directory = os.path.join(parent, application_name)
    with lcd(source_directory):
        local('ant jar')
        application_directory = create_directory(env.edition_directory, application_name)
        log_directory = create_directory(application_directory, 'logs')
        bin_directory = create_directory(application_directory, 'bin')
        local('cp -r ./dist/* {0}'.format(bin_directory))
    with lcd(base):
        conf_directory = create_directory(application_directory, 'conf')
        local('cp ../log4j.properties {0}'.format(conf_directory))


def create_directory(path, name):
    """
    Make a directory joining  path and name
    """
    result = os.path.join(path, name)
    local('mkdir -p {0}'.format(result))
    return result

@task
def start_servers():
    """
    Servers, engage!
    """
    with cd(env.deployment_directory):
        for python_application in env.python_applications:
            directory = os.path.join(python_application, 'bin')
            with cd(directory):
                runbg('nohup node --harmony server.js')
        java_options = '-Djava.library.path=/usr/local/lib'
        for java_application in env.java_applications:
            name = java_application
            lower_name = name.lower()
            jar_location = os.path.join(java_application, 'bin')
            with cd(jar_location):
                runbg('nohup java {0} -cp {1}.jar ngramatic.{2}.query.Server'.format(java_options, name, lower_name))


def runbg(cmd, socket_name="dtach"):
    return run('dtach -n `mktemp -u /tmp/{0}.XXXX` {1}'.format(socket_name, cmd))


@task
def fix_vagrant_guest_additions():
    """
    Version 4.3 of Virtual Box makes Vagrant bomb
    fab host_vagrant fix_vagrant_guest_additions
    """
    local('vagrant plugin install vagrant-vbguest')
    local('vagrant up --no-provision')
    sudo('apt-get -y -q purge virtualbox-guest-dkms')
    sudo('apt-get -y -q purge virtualbox-guest-utils')
    sudo('apt-get -y -q purge virtualbox-guest-x11')
    local('vagrant halt')
    local('vagrant up --provision')


@task
def ec2():
    """
    Connect to EC2
    """
    env.user = 'ubuntu'


@task
def vagrant():
    """
    Connect to Vagrant from the host machine
    """
    env.user = 'vagrant'
    result = dict(line.split() for line in local(
        'vagrant ssh-config', capture=True).splitlines())
    env.hosts = ['{0}:{1}'.format(result['HostName'], result['Port'])]
    env.key_filename = result['IdentityFile'].replace('"', '')


@task
def install_tools():
    """
    pip, dtach, curl, ant, nginx, nodejs, zeromq, oraclejdk
    """
    install_pip()
    install_dtach()
    install_build_tools()
    install_curl()
    install_python()
    install_nodejs()
    install_oraclejdk()
    install_ant()
    install_zeromq()
    install_jzmq()


@task
def server_update():
    """
    Ubuntu full update
    """
    run('mkdir -p ~/tmp')
    sudo('apt-get clean')
    sudo('rm -rf /var/lib/apt/lists/*')
    sudo('apt-get clean')
    sudo('apt-get update')
    sudo('apt-get install python-software-properties -y ')
    sudo(('DEBIAN_FRONTEND=noninteractive apt-get -y '
          '-o Dpkg::Options::="--force-confdef" '
          '-o Dpkg::Options::="--force-confold" dist-upgrade'))


@task
def server_reboot():
    """
    Restart Ubuntu
    """
    reboot(120)


@task
def identify_os():
    """
    Identify the operating system
    """
    run('uname -s')


@task
def update_virtualbox():
    """
    Fix Vagrant in Virtual Box after an update in Ubuntu
    """
    sudo('/etc/init.d/vboxadd setup')


@task
def install_yeoman():
    """
    Get tools for front end
    """
    sudo('npm install -g yo')

@task
def install_build_tools():
    """
    make from package
    """
    sudo('apt-get install -y autoconf')
    sudo('apt-get install -y automake')


@task
def install_dtach():
    """
    dtach from package
    """
    sudo('apt-get install -y dtach')


@task
def install_pip():
    """
    Pip from package
    """
    sudo('apt-get install -y python-pip')
    sudo('apt-get install -y python-dev')
    sudo('apt-get install -y build-essential')
    sudo('pip install --upgrade pip')


@task
def install_curl():
    """
    curl from package
    """
    sudo('apt-get install -y curl')


@task
def install_ant():
    """
    Ant from package
    """
    sudo('apt-get install -y ant')


@task
def install_python():
    """
    Python 2.7 from package
    """
    sudo('pip install docopt')
    sudo('pip install pyzmq')


@task
def install_nginx():
    """
    Nginx from source
    """
    version = '1.4.1'
    url = 'http://nginx.org/download/nginx-{0}.tar.gz'.format(version)
    sudo('apt-get install -y libpcre3')
    sudo('apt-get install -y libpcre3-dev')
    sudo('apt-get install -y libssl-dev')
    sudo('apt-get install -y zlib1g')
    sudo(('adduser --system --no-create-home --disabled-login '
          '--disabled-password --group nginx'))
    sudo('mkdir -p /var/www')
    run('mkdir -p ~/tmp')
    run('wget -P ~/tmp {0}'.format(url))
    with cd('~/tmp'):
        run('tar xvzf nginx-{0}.tar.gz'.format(version))
    with cd('~/tmp/nginx-{0}'.format(version)):
        run(('./configure --prefix=/opt/nginx --user=nginx '
             '--group=nginx --with-http_ssl_module '
             '--without-http_scgi_module '
             '--without-http_uwsgi_module '
             '--without-http_fastcgi_module'))
        run('make')
        sudo('make install')
    run('rm -rf ~/tmp')
    put('../etc-init.d-nginx', '/etc/init.d/nginx', use_sudo=True)
    sudo('chmod +x /etc/init.d/nginx')
    sudo('update-rc.d nginx defaults')
    sudo('service nginx start')


@task
def install_nodejs():
    """
    NodeJS from external package
    """
    run('mkdir -p ~/tmp')
    sudo('apt-get install -y python-software-properties')
    sudo('apt-get install -y software-properties-common')
    sudo('add-apt-repository -y ppa:chris-lea/node.js')
    sudo('apt-get update')
    sudo('apt-get install -y nodejs')
    run('rm -rf ~/tmp')


@task
def install_zeromq():
    """
    ZeroMQ from source
    """
    version = '3.2.4' # 4.0.4 is bombing at build on jzmq
    url = 'http://download.zeromq.org/zeromq-{0}.tar.gz' \
        .format(version)
    sudo('apt-get install -y libtool')
    sudo('apt-get install -y uuid-dev')
    run('mkdir -p ~/tmp')
    run('wget -P ~/tmp {0}'.format(url))
    with cd('~/tmp'):
        run('tar xvzf zeromq-{0}.tar.gz'.format(version))
    with cd('~/tmp/zeromq-{0}'.format(version)):
        run('./autogen.sh')
        run('./configure')
        run('make')
        sudo('make install')
        sudo('ldconfig')
    run('rm -rf ~/tmp')


@task
def install_jzmq():
    """
    Java bindings for ZeroMQ
    """
    url = 'https://github.com/zeromq/jzmq/archive/master.zip'
    sudo('apt-get install -y unzip')
    sudo('apt-get install -y pkg-config')
    run('mkdir -p ~/tmp')
    run('wget -P ~/tmp {0}'.format(url))
    with cd('~/tmp'):
        run('unzip master.zip')
    with cd('~/tmp/jzmq-master'):
        run('./autogen.sh')
        run('./configure')
        run('make')
        sudo('make install')
        sudo('ldconfig')
    run('rm -rf ~/tmp')
    sudo(('echo export LD_LIBRARY_PATH=/usr/local/lib'
          ' > /etc/profile.d/ldlibrarypath.sh'))


@task
def install_oraclejdk():
    """
    Oracle JDK from package
    """
    sudo('apt-get install -y python-software-properties')
    sudo('add-apt-repository -y ppa:webupd8team/java')
    sudo('apt-get update')
    sudo(('echo debconf shared/accepted-oracle-license-v1-1 '
          'select true | sudo debconf-set-selections'))
    sudo(('echo debconf shared/accepted-oracle-license-v1-1 '
          'seen true | sudo debconf-set-selections'))
    sudo('apt-get install -y oracle-java8-installer')


@task
def install_mongo():
    """
    Mongo from package
    """
    sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
    sudo("echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/mongodb.list")
    sudo('apt-get update')
    sudo('apt-get install -y mongodb-10gen')


def load_ec2():
    """
    Make sure env.ec2 exists and has valid credentials
    """
    if 'aws' not in env:
        env.aws = {}
        if 'credentials' not in env.aws:
            with open('../aws_credentials.json') as credentials:
                env.aws['credentials'] = json.load(credentials)
        if 'ec2' not in env.aws:
            with open('../ec2_details.json') as ec2new:
                env.aws['ec2'] = json.load(ec2new)
    if 'ec2' not in env:
        env.ec2 = {}


@task
def load_ec2_region(region_name=''):
    """
    AWS region
    """
    load_ec2()
    if region_name not in env.aws['ec2']['regions']:
        region_name = env.aws['ec2']['defaults']['region']
        print ('Region unknown, selecting default')
    env.ec2['region_name'] = region_name
    env.ec2['region'] = env.aws['ec2']['regions'][region_name]
    print('Region selected: {0} - {1}'.format(env.ec2['region_name'],
                                              env.ec2['region']))


@task
def connect_ec2(region_name=''):
    """
    Create a connection to AWS
    """
    load_ec2()
    if 'region' not in env.ec2:
        load_ec2_region(region_name)

    print('Access Key {0}'.format(
        env.aws['credentials']['aws_access_key_id']))
    print('Secret Access Key {0}'.format(
        env.aws['credentials']['aws_secret_access_key']))

    env.ec2['connection'] = boto.ec2.connect_to_region(
        env.ec2['region'],
        aws_access_key_id=env.aws['credentials']['aws_access_key_id'],
        aws_secret_access_key=env.aws['credentials'][
            'aws_secret_access_key'])

    if env.ec2['connection'] is None:
        raise Exception(
            'Cannot connect to AWS region {0} using {1} and {2} '
            .format(env.ec2.region_name, env.ec2.aws_access_key_id,
                    env.ec2.aws_secret_access_key))

    print('Connection {0}'.format(env.ec2['connection']))


@task
def load_ec2_ami_name(image_name='', region_name=''):
    """
    Select an image available to the region
    """
    load_ec2()
    if 'region' not in env.ec2:
        load_ec2_region(region_name)
    region_name = env.ec2['region_name']
    if image_name not in env.aws['ec2']['images'][region_name]:
        image_name = env.aws['ec2']['defaults']['imageName']
        print ('Image unknown, selecting default')
    env.ec2['ami_name'] = env.aws['ec2']['images'][region_name][
        image_name]
    print('Image selected: {0}'.format(image_name))
    print ('AMI selected: {0}'.format(env.ec2['ami_name']))


@task
def load_ec2_image(image_name='', region_name=''):
    """
    Grab an image from AWS
    """
    load_ec2()
    if 'connection' not in env.ec2:
        connect_ec2(region_name)
    if 'ami_name' not in env.ec2:
        load_ec2_ami_name(image_name, region_name)
    print(env.ec2['connection'])
    env.ec2['image'] = env.ec2['connection'].get_image(
        env.ec2['ami_name'])
    print('Image selected: {0}'.format(env.ec2['image']))


@task
def load_ec2_instance_type(instance_type=''):
    """
    Select instance type for EC2
    """
    load_ec2()
    if instance_type not in env.aws['ec2']['instanceTypes']:
        instance_type = env.aws['ec2']['defaults']['instanceType']
        print ('Instance type unknown, selecting default')
    env.ec2['instance_type'] = instance_type
    print ('Instance type selected: {0}'.format(instance_type))


@task
def ensure_key_name(key_name=''):
    """
    Grab a key from AWS
    """
    load_ec2()
    if env.key_filename is None:
        if key_name == '':
            key_name = env.aws['ec2']['defaults']['key_name']
            print ('Key name unspecified, selecting default')
        env.ec2['key_name'] = key_name
    else:
        key_filename = env.key_filename[0]
        filename = os.path.basename(key_filename)
        keyname = os.path.splitext(filename)[0]
        env.ec2['key_name'] = keyname


@task
def ensure_ec2_key(key_name='', region_name=''):
    """
    Create a key in AWS and store it locally
    """
    load_ec2()
    if 'key' not in env.ec2:
        if 'connection' not in env.ec2:
            connect_ec2(region_name)
        ensure_key_name(key_name)
        key = env.ec2['connection'].get_key_pair(env.ec2['key_name'])
        if key is None:
            key = env.ec2['connection'].create_key_pair(
                env.ec2['key_name'])
            save_key_pairs_local(key, env.ec2['region_name'])
        else:
            print ('Key already exists')
        env.ec2['key'] = key

    key_filename = get_local_key_filename_from_ec2()
    print('Key filename is {0}'.format(key_filename))


def get_local_key_filename_from_ec2():
    working_directory = os.getcwd()
    keys_directory = os.path.join(working_directory, 'synchResources',
                                  'Keys', env.ec2['region_name'])
    key_filename = os.path.join(keys_directory,
                                env.ec2['key'].name + '.pem')
    return key_filename


def save_key_pairs_local(key_pair, region_name):
    """
    Keep a copy of the key
    """
    working_directory = os.getcwd()
    keys_directory = os.path.join(working_directory, 'synchResources',
                                  'Keys', region_name)
    save_key_pair_on_disk(key_pair, keys_directory)


def save_key_pair_on_disk(key_pair, directory):
    """
    Drop the key in disk
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    key_pair.save(directory)


@task
def load_ec2_security_groups(security_groups_name='', region_name=''):
    """
    Select the security_groups for EC2
    """
    load_ec2()
    if security_groups_name not in env.aws['ec2']['securityGroups']:
        security_groups_name = env.aws['ec2']['defaults'][
            'securityGroupsName']
        print ('Security groups unknown, selecting default')

    env.ec2['security_groups'] = env.aws['ec2']['securityGroups'][
        security_groups_name]
    print (
        'Security groups selected: {0} - {1}'.format(
            security_groups_name,
            env.ec2[
                'security_groups']))

    if 'connection' not in env.ec2:
        connect_ec2(region_name)

    existing_groups_names = [x.name.encode('utf-8') for x in env.ec2[
        'connection'].get_all_security_groups()]
    print (
        'Existing group names are {0}'.format(existing_groups_names))

    missing_groups_names = [x for x in env.ec2['security_groups'] if
                            x not in existing_groups_names]

    if len(missing_groups_names) > 0:
        print (
            'Groups {0} are not in AWS, will be created empty'.format(
                missing_groups_names))
        description = 'Empty group created as part of deployment'
        create_group = (
            lambda g: env.ec2['connection']
            .create_security_group(g, description))
        [create_group(x) for x in missing_groups_names]


@task
def load_ec2_block_device_map(disk_size=''):
    """
    Get a block device map with a given disk size
    """
    load_ec2()
    if disk_size not in env.aws['ec2']['diskSizes']:
        disk_size = env.aws['ec2']['defaults']['diskSize']
        print ('Disk size unknown, selecting default')

    dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
    dev_sda1.size = disk_size
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/sda1'] = dev_sda1

    env.ec2['block_device_map'] = bdm
    print ('Disk size selected: {0}'.format(disk_size))


@task
def get_reservation(image_name='', instance_type='', key_name='',
                    security_groups_name='', region_name='', disk_size=''):
    """
    Grab an instance to run
    """
    load_ec2()
    if 'reservation' not in env.ec2:
        if 'image' not in env.ec2:
            load_ec2_image(image_name, region_name)
        if 'instance_type' not in env.ec2:
            load_ec2_instance_type(instance_type)
        if 'key' not in env.ec2:
            ensure_ec2_key(key_name)
        if 'security_groups' not in env.ec2:
            load_ec2_security_groups(security_groups_name,
                                     region_name)
        if 'disk_size' not in env.ec2:
            load_ec2_block_device_map(disk_size)
        env.ec2['reservation'] = env.ec2['image'].run(
            instance_type=env.ec2['instance_type'],
            key_name=env.ec2['key_name'],
            security_groups=env.ec2['security_groups'],
            block_device_map=env.ec2['block_device_map'])
    print ('Reservation is {0}'.format(env.ec2['reservation']))


@task
def create_ec2_instance(machine_name='', image_name='',
                        instance_type='', key_name='',
                        security_groups_name='', region_name='', disk_size=''):
    """
    Fire a server
    """
    load_ec2()
    if 'reservation' not in env.ec2:
        get_reservation(image_name, instance_type, key_name,
                        security_groups_name, region_name, disk_size)
    if machine_name == '':
        machine_name = env.aws['ec2']['defaults']['machineName']
    env.ec2['instance'] = env.ec2['reservation'].instances[0]
    env.ec2['connection'].create_tags([env.ec2['instance'].id],
                                      {'Name': machine_name})
    print ('Waiting for the instance to be ready...')
    while env.ec2['instance'].state != u'running':
        time.sleep(5)
        env.ec2['instance'].update()
    print ('Public address {0} - {1} at {2} with key {3}'.format(
        env.ec2['instance'].ip_address,
        env.ec2['instance'].public_dns_name, env.ec2['region_name'],
        env.ec2['key'].name))

    remaining_attempts = 20

    while remaining_attempts > 0:
        try:
            check_ssh(env.ec2['instance'].public_dns_name)
            remaining_attempts = 0
        except Exception, e:
            remaining_attempts -= 1

    print ('Server ready to fly and accessible by port 22')


def check_ssh(hostname, port_number=22):
    """
    Try to connect to ssh port
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remaining_attempts = 30

        while remaining_attempts > 0:
            try:
                s.connect((hostname, port_number))
                print ('Port {0} reachable'.format(port_number))
                remaining_attempts = 0
            except Exception, e:
                remaining_attempts -= 1
                time.sleep(6)
    except socket.error as e:
        print 'Error on connect: {0}'.format(e)
    s.close()


@task
def create_ec2_deploy_fresh_server(machine_name='', image_name='',
                                   instance_type='', key_name='',
                                   security_groups_name='',
                                   region_name='', disk_size=''):
    """
    USE FOR EC2 - Make an instance in EC2
    and have it ready to deploy code
    """
    create_ec2_instance(machine_name, image_name, instance_type,
                        key_name, security_groups_name, region_name, disk_size)
    env.user = 'ubuntu'
    env.hosts = [env.ec2['instance'].public_dns_name.encode('utf-8')]
    env.key_filename = [
        get_local_key_filename_from_ec2().encode('utf-8')]
    time.sleep(60)
    print ('Machine created, trying to identify')
    remaining_attempts = 20

    worked = False
    while remaining_attempts > 0:
        try:
            time.sleep(6)
            execute(identify_os)
            remaining_attempts = 0
            worked = True
        except Exception, e:
            remaining_attempts -= 1
            print('Bombed, {0} more attempts to try'.format(
                remaining_attempts))

    if worked:
        execute('server_update')
