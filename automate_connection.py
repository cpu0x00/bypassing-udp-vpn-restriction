''' 
Author: Karim (github.com/mr-nobody20) (twitter.com/fsociety_py00)

automation script to automate the process of:

	- creating and adding ssh-keys to the digitalocean account 
	- creating a vm in the cloud in digitalocean with the created keys
	- downloading and creating an openvpn access server
	- connecting the machine with the created openvpn server


# this script only supports the explained method 2 to connect to THM-Network #
'''


import digitalocean
from os import getcwd
from os import system
import re
import paramiko 
import requests
from time import sleep


API_TOKEN = 'YOUR_DIGITALOCEAN_API_HERE' # the personal access token
SSH_PUB_KEY = f'{getcwd()}/tmp_idrsa.pub'
DROPLET_ID = []
PUBLIC_V4 = []
OPENVPN_SETUP_SCRIPT = 'https://raw.githubusercontent.com/mr-nobody20/bypassing-udp-vpn-restriction/main/openvpn-automated-install.sh'

#-------------- droplet specifications section --------------#

name= "openvpn-droplet"
region= "fra1"
size= "s-1vcpu-1gb"
image= "debian-11-x64"
backups= False
ipv6= False
user_data= None
private_networking= None
volumes= None

#-------------- END droplet specifications section --------------#


def generate_sshkeys(): # generates ssh key pairs

	system(f"ssh-keygen -f {getcwd()}/tmp_idrsa -P '' ")
	print('[*] generated ssh-key pair for the droplet !')


def add_sshkey_to_user_account(): # adds the ssh public key to the digitalocean account to use it with the vps

	user_sshpub_key = open(SSH_PUB_KEY).read()
	key = digitalocean.SSHKey(token=API_TOKEN,name='tmp_idrsa',public_key=user_sshpub_key)
	key.create()
	print('[*] added the ssh-key to the digitalocean account')


def create_droplet(): # creates the openvpn droplet

	manager = digitalocean.Manager(token=API_TOKEN)
	keys = manager.get_all_sshkeys()

	if not 'tmp_idrsa' in str(keys):
		print('[FATAL] the tmp_idrsa is not found !') 
		exit()

	if 'tmp_idrsa' in str(keys):

		print('[*] creating (openvpn-droplet) with the generated ssh-key !')
		tmp_key = keys[0]
		pattern = re.compile(r'\d.*\d')
		key_id = pattern.findall(str(tmp_key))
		int_keyid = int(''.join(key_id))

		url = f"https://api.digitalocean.com/v2/droplets"

		headers = {
	
			'Authorization': f'Bearer {API_TOKEN}'

		}

		data = {
			"name":name,
			'region':region,
			'size':size,
			'image':image,
			'backups':False,
			'ipv6':ipv6,
			'user_data':None,
			'private_networking':None,
			'volumes':None,
			'ssh_keys':[int_keyid],
			'tags':[
				"uniq-openvpn-droplet-tag"
			]
		
		}

		response = requests.post(url, data=data, headers=headers)

		droplet_id = response.json()['droplet']['id']

		DROPLET_ID.append(droplet_id)

		print(f'[*] created droplet id: {droplet_id}')



		print("[i] sleeping for 1 minute for the droplet to finish creation...")

		sleep(60)

		droplet_url = f"{url}/{droplet_id}"

		droplet_response = requests.get(droplet_url, headers=headers)
		# print(droplet_response.json())
		public_ip_address = droplet_response.json()['droplet']['networks']['v4'][0]['ip_address']

		PUBLIC_V4.append(public_ip_address)
		
		print(f"[*] created droplet's public ip: {public_ip_address}")




def create_openvpn_as(): # creates openvpn access server on the droplet and retrieve the client profile to the local machine
	print('[*] creating openvpn access server on the vps (be patient...)')

	ssh_client = paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	ssh_idrsa = f'{getcwd()}/tmp_idrsa' 

	ssh_client.connect(PUBLIC_V4[0], port=22 ,username='root', key_filename=ssh_idrsa)

	stdin, stdout, stderr = ssh_client.exec_command(f'wget {OPENVPN_SETUP_SCRIPT} -O /root/openvpn-automated-install.sh')

	print('[*] downloaded the (openvpn-automated-install.sh) script to the vps')

	while not stdout.readlines() or stderr.readlines():
		sleep(0.2)
		if stdout.readlines() or stderr.readlines():
			break


	stdin, stdout, stderr = ssh_client.exec_command('chmod +x /root/openvpn-automated-install.sh')


	while not stdout.readlines() or stderr.readlines():
		sleep(0.1)
		if str(stdout.readlines()) == '[]' or str(stderr.readlines()) == '[]':
			break

	print('[*] executing the setup script in the vps...')

	stdin, stdout, stderr =  ssh_client.exec_command('/bin/bash /root/openvpn-automated-install.sh')


	while not stdout.readlines() or not stderr.readlines():
		sleep(0.1)
		if stdout.readlines() or stderr.readlines():
			break

	sftp_client = ssh_client.open_sftp()

	localpath = f'{getcwd()}/vps-openvpn-client.ovpn'

	remotepath = '/root/vps-openvpn-client.ovpn'

	print('[*] retrieving the (vps-openvpn-client.ovpn) client file')

	sftp_client.get(remotepath,localpath)

	print('[*] done!')

	sftp_client.close()
	ssh_client.close()






def destroy_droplet(): # destroys the created vps (on closing the script)

	droplet_object = digitalocean.Droplet(token=API_TOKEN, id=int(DROPLET_ID[0]))
	print('[*] destroying the openvpn-droplet...')
	droplet_object.destroy()

def destroy_sshkey(): # destroys the ssh keys from the account and deletes them from the disk (on closing the script)

	manager = digitalocean.Manager(token=API_TOKEN)
	keys = manager.get_all_sshkeys()

	tmp_key = keys[0]
	pattern = re.compile(r'\d.*\d')
	key_id = pattern.findall(str(tmp_key))
	int_keyid = int(''.join(key_id))

	key = digitalocean.SSHKey(token=API_TOKEN,id=int_keyid)
	key.destroy()
	print('[*] destroyed the ssh-key from the digitalocean account')

	system('rm tmp_idrsa tmp_idrsa.pub')
	print('[*] deleted the ssh-keys from the desk')


def connect_openvpn(): # connects the local machine to vps openvpn server
	print('[*] connecting to the openvpn of the vps...')
	system('openvpn vps-openvpn-client.ovpn')
	
def main():
	try:

		generate_sshkeys()
		add_sshkey_to_user_account()
		create_droplet()
		create_openvpn_as()
		
		connect_thread = threading.Thread(target=connect_openvpn)
		connect_thread.start()



	except KeyboardInterrupt: # in case script execution cancelled before its finished 
		destroy_droplet()
		destroy_sshkey()
		system(f'rm {getcwd()}/vps-openvpn-client.ovpn')


if __name__ == "__main__":
	main()