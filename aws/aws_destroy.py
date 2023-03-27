import boto3
import argparse

ec2_ak = 'YOUR_ACCESS_KEY'
ec2_sak = 'YOUR_SECRET_ACCESS_KEY' 

parser = argparse.ArgumentParser()
parser.add_argument('--region', help='region to use (default=eu-central-1 [Frankfurt - Germany])')

arg = parser.parse_args()


REGION = 'eu-central-1'

if arg.region:
	REGION = arg.region

ec2 = boto3.client('ec2', REGION, aws_access_key_id=ec2_ak, aws_secret_access_key=ec2_sak)

try:

	InstanceId = open('instance_id.latest', 'r').readline()
	InstanceId = str(InstanceId.strip())

except FileNotFoundError:
	exit('[-] file (instance_id.latest) was not found, exiting...')


print(f'[*] terminating the instance')
terminate = ec2.terminate_instances(InstanceIds=[InstanceId])
if terminate:
	print('[*] instance terminated')

	
