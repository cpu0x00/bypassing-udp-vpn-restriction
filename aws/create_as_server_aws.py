'''
Author: Karim (github.com/cpu0x00) (twitter.com/fsociety_py00)

automation script to automate the process of:
	
	- creating and adding ssh-keys to the digitalocean account 
	- creating a vm in the cloud in digitalocean with the created keys
	- downloading and creating an openvpn access server on the created droplet
	- connecting the machine with the created openvpn server 
	- destroying everything once the script is closed by user

'''
import boto3
from os import system
from os import getcwd
from time import sleep
import argparse
import threading
import paramiko

parser = argparse.ArgumentParser()
parser.add_argument('--setup', action='store_true', help='sets up the account to be ready for usage')


args = parser.parse_args()


ec2_ak = 'YOUR_ACCESS_KEY_HERE'
ec2_sak = 'YOUR_SECRET_ACCESS_KEY_HERE' 

image_id = "ami-0bf166b48bbe2bf7c" # debian

ec2 = boto3.client('ec2', 'us-west-1', aws_access_key_id=ec2_ak, aws_secret_access_key=ec2_sak)

def create_keys():
	print('[*] generating ssh keypair (aws_rsa)')
	system(f"ssh-keygen -f {getcwd()}/aws_rsa -N '' ")
	print('[*] done')
	
def importsshkey():
	SSH_PUBKEYFILE = f'{getcwd()}/aws_rsa.pub'
	readfile = open(SSH_PUBKEYFILE, 'r').readlines()
	b64encoded_pubkey = base64.b64encode(readfile[0].strip().encode())
	# print(b64encoded_pubkey)
	ec2.import_key_pair(KeyName='aws_rsa', PublicKeyMaterial=readfile[0].strip())
	print('[*] imported the generated keys into the account')

def setup_secgroups():
	print('[*] creating security group (AllowAll_group)')
	sec_group = ec2.create_security_group(GroupName='AllowAll_group', Description='Allow all traffic')
	print('[*] created security group')
	
	print('[*] configuring in-bound and out-bound traffic to AllowAll ')
	ec2.authorize_security_group_ingress(GroupId=sec_group['GroupId'], IpPermissions=[{'IpProtocol': '-1', 'FromPort': 0, 'ToPort': 65535, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}], 'Ipv6Ranges': [{'CidrIpv6': '::/0'}]}])
	print('[*] done')
  
def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = f'{mins}:{secs}              '
        print(timer, end="\r")
        sleep(1)
        t -= 1


def create_ec2_instance():
	global InstanceId
	global public_ip_address

	sec_group_name = "AllowAll_group"
	sec_group_info = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [sec_group_name]}])
	sec_groud_id = sec_group_info['SecurityGroups'][0]['GroupId'] 

	print('[*] creating ec2 instance....')
	created_instance = ec2.run_instances(InstanceType="t2.nano", MaxCount=1, MinCount=1, ImageId=image_id, KeyName='aws_rsa', SecurityGroupIds=[sec_groud_id])
	InstanceId = created_instance['Instances'][0]['InstanceId']
	print(f'[*] created instance id: {InstanceId}')
	
	print(f'[*] sleeping 30 seconds waiting for initialization....')
	countdown(30)
	instance_info = ec2.describe_instances(InstanceIds=[InstanceId])
	public_ip_address = instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress']
	print(f'[*] created instance public ip: {public_ip_address} (your ip once connected)')



def terminate_instance():
	print(f'\nterminating the instance')
	terminate = ec2.terminate_instances(InstanceIds=[InstanceId])
	print('[*] instance terminated')


def create_openvpn_as(): # creates openvpn access server on the droplet and retrieve the client profile to the local machine
	print('[*] creating openvpn access server on the vps (be patient...)')

	ssh_client = paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


	# ssh_idrsa = f'{getcwd()}/{args.ssh_key}' 
	ssh_client.connect(public_ip_address, port=22 ,username='admin', key_filename=f'{getcwd()}/aws_rsa')

	OPENVPN_SETUP_SCRIPT = 'https://raw.githubusercontent.com/cpu0x00/bypassing-udp-vpn-restriction/main/openvpn-automated-install.sh'

	stdin, stdout, stderr = ssh_client.exec_command(f'wget {OPENVPN_SETUP_SCRIPT} -O ~/openvpn-automated-install.sh')

	print('[*] downloaded the (openvpn-automated-install.sh) script to the vps')

	while not stdout.readlines() or stderr.readlines():
		sleep(0.2)
		if stdout.readlines() or stderr.readlines():
			break


	stdin, stdout, stderr = ssh_client.exec_command(f'chmod +x ~/openvpn-automated-install.sh')


	while not stdout.readlines() or stderr.readlines():
		sleep(0.1)
		if str(stdout.readlines()) == '[]' or str(stderr.readlines()) == '[]':
			break

	print('[*] executing the setup script in the vps...')

	stdin, stdout, stderr =  ssh_client.exec_command('sudo /bin/bash ~/openvpn-automated-install.sh')


	while not stdout.readlines() or not stderr.readlines():
		sleep(0.1)
		if stdout.readlines() or stderr.readlines():
			break



	stdin, stdout, stderr = ssh_client.exec_command(f'sudo cp /root/vps-openvpn-client.ovpn /home/admin/vps-openvpn-client.ovpn')

	stdin, stdout, stderr = ssh_client.exec_command(f'sudo chmod 777 /home/admin/vps-openvpn-client.ovpn')

	sftp_client = ssh_client.open_sftp()

	localpath = f'{getcwd()}/vps-openvpn-client.ovpn'

	remotepath = f'/home/admin/vps-openvpn-client.ovpn'

	print('[*] retrieving the (vps-openvpn-client.ovpn) client file')

	if sftp_client.get(remotepath,localpath):

		print('[*] done!')
	
	sftp_client.close()
	ssh_client.close()


def connect_openvpn(): # connects the local machine to vps openvpn server
	new_file = []
	new_remote = f'remote {public_ip_address} 443'
	file = open('vps-openvpn-client.ovpn', 'r').readlines()
	lines = [l.strip() for l in file]

	for line in lines:
		if 'remote' and '443' in line:
			new_file.append(new_remote)
		else:
			new_file.append(line)

	open('vps-openvpn-client.ovpn', 'w').write('\n'.join(new_file))

	print('[*] re-wrote the openvpn client file (AWS specific)')

	print('[*] connecting to the openvpn of the vps...')

	# input('Press Enter to close')
	system('openvpn vps-openvpn-client.ovpn')


def main():

	if args.setup:
		print('[*] initializating the one time setup...')
		create_keys()
		importsshkey()
		setup_secgroups()


	if not args.setup:
		try:
			create_ec2_instance()
			create_openvpn_as()
			connect_openvpn()

			terminate_thread = threading.Thread(target=terminate_instance)
			terminate_thread.start()
		except KeyboardInterrupt:
			terminate_instance()

main()

# 255.170