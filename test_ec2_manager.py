import pytest
import boto3
import json
import os
import sys
from launch_instance import launch_instance
from setup_cloudwatch import install_cloudwatch, configure_cloudwatch
from ec2_manager_gui import EC2Manager

# Mock data
INSTANCE_ID_FILE = 'instance_id.json'


@pytest.fixture(scope='module')
def ec2_setup():
    ec2 = boto3.resource('ec2', region_name='eu-west-3')
    instance = ec2.create_instances(
        ImageId='ami-045a8ab02aadf4f88',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro'
    )[0]
    instance.wait_until_running()
    yield instance
    instance.terminate()


@pytest.fixture
def create_instance_id_file(ec2_setup):
    with open(INSTANCE_ID_FILE, 'w') as f:
        json.dump({'instance_id': ec2_setup.id}, f)
    yield
    os.remove(INSTANCE_ID_FILE)


def test_launch_instance(ec2_setup):
    launch_instance()
    ec2 = boto3.resource('ec2', region_name='eu-west-3')
    instances = list(ec2.instances.all())
    assert len(instances) == 1
    assert instances[0].state['Name'] == 'running'
    with open(INSTANCE_ID_FILE, 'r') as f:
        data = json.load(f)
        assert data['instance_id'] == instances[0].id


def test_load_instance_id(create_instance_id_file):
    manager = EC2Manager()
    assert manager.instance_id == create_instance_id_file.id


@pytest.mark.parametrize("method", ["start_instance", "stop_instance", "reboot_instance"])
def test_instance_methods(create_instance_id_file, method):
    manager = EC2Manager()
    ec2 = boto3.client('ec2', region_name='eu-west-3')
    getattr(manager, method)()
    response = ec2.describe_instances(InstanceIds=[manager.instance_id])
    assert response['Reservations'][0]['Instances'][0]['InstanceId'] == manager.instance_id


def test_install_cloudwatch(create_instance_id_file):
    response = install_cloudwatch(create_instance_id_file.id)
    assert response['Command']['CommandId'] is not None


def test_configure_cloudwatch(create_instance_id_file):
    response = configure_cloudwatch(create_instance_id_file.id)
    assert response['Command']['CommandId'] is not None
