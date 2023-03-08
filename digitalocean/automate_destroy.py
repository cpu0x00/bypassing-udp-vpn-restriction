''' 
Author: Karim (github.com/cpu0x00) (twitter.com/fsociety_py00)

automation script to automate the process of:

	- destroying the created droplet (the droplet that was created using automate_connection.py script)
	- removing the generated ssh-keys from the digitalocean account and from the disk
	- deleting the openvpn client of the vps

'''


import digitalocean
import requests
from os import system
import re
from os import getcwd
from os import environ

API_TOKEN = 'ACCESS_TOKEN_HERE' # personal access token 


def destroy_droplet(): # destroys the created vps 
	print('[*] destroying the openvpn-droplet...')
	headers = {

		'Authorization': f'Bearer {API_TOKEN}'

	}


	DELETE_URL = f'https://api.digitalocean.com/v2/droplets?tag_name=uniq-openvpn-droplet-tag'

	api_response = requests.delete(DELETE_URL, headers=headers)
	
	if api_response.status_code == 204:
		print('[*] destroyed the openvpn-droplet !')





def destroy_sshkey(): # destroys the ssh keys from the account and deletes them from the disk 

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


destroy_droplet()
destroy_sshkey()
system(f'rm {getcwd()}/vps-openvpn-client.ovpn')
print('[*] deleted the (vps-openvpn-client.ovpn) file')
