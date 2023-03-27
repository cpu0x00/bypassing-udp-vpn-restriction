# 2 ways of bypassing the udp vpn restriction and connecting to the THM network #

- openvpn is used in both in methods

- requirments for the both methods:
	- a vps located outside the country of restriction (a digital ocean droplet in san fransisco used in this project)
	
	- resources is not an issue here (use the cheapest possible machine ;) )



## installing openvpn in the vps ##

- I used debian 11 machine, all openvpn supported linux distros is <a href="https://openvpn.net/vpn-software-packages/"> here </a>

- for debian:

```
# apt update && apt -y install ca-certificates wget net-tools gnupg

# wget -qO - https://as-repository.openvpn.net/as-repo-public.gpg | apt-key add -

# echo "deb http://as-repository.openvpn.net/as/debian bullseye main">/etc/apt/sources.list.d/openvpn-as-repo.list

# apt update && apt -y install openvpn-as
```

- for ubuntu:

```
# apt update && apt -y install ca-certificates wget net-tools gnupg

# wget -qO - https://as-repository.openvpn.net/as-repo-public.gpg | apt-key add -

# echo "deb http://as-repository.openvpn.net/as/debian jammy main">/etc/apt/sources.list.d/openvpn-as-repo.list

# apt update && apt -y install openvpn-as
```

- once installed it will prompt with the login panel for the admin and the client which by default located in: https://vps_ip:943/admin, https://vps_ip:943/ and the randomly generated password for the (openvpn) user


- openvpn access server is now installed !. 


## configuring the openvpn access server ##

- once logged-in in the admin panel using the random password navigate to the (Network Settings) tab under the (configuration) section and make 
sure that:

	- (Listen on all interfaces) option is enabled
	- tcp is enabled in the protocol section


- then save the settings from the very buttom of the page and click on (update the running server) after saving


- navigate to (User Permissions) under the (USER MANAGMENT) section and create a new user and make sure that the auto-login box is checked and again save and update the running server once the username appears click on the more settings icon next to the username and set a password for the new user and make sure that the (allow access to all interfaces) box under the (Access Control) section is selected and save the setting


- once the user settings is saved navigate to the client url and log-in with created username and password and download the (auto-login profile)


## First Method ##

- upload the (THM ovpn) file to your vps/openvpn-server and use the openvpn client to connect to THM network from the vps which will create a tun0 interface on the vps (the listen on all interfaces option is useful here)


- once the vps is connected to the THM network connect your local machine to the vpn client of (YOUR) vpn/vps server  


- now you have access the THM network over the connection you have to your vps through the vpn server !


- simple visuallization of how it works:

``` 

------------                          ------------
|  YOUR	   |    VPN TO YOUR VPS    	  |	  YOUR   |	 TO THM NETWORK
|  LOCAL   |   =================>     |	  VPS    |   ===============>   THM-NETWORK
|  MACHINE |						  |          |
|----------|		   				  |----------|
```

## Second Method ##  


- connect your local machine to your vps/vpn server through the openvpn client you downloaded from the client panel


- use openvpn again on your local machine to connect to the THM Network normally `# openvpn THM.ovpn`


- now you have access the THM tunnelled through the vpn connection of your vps 


- simple visuallization of how it works:


```

FIRST:

------------                          ------------
|  YOUR	   |    VPN TO YOUR VPS    	  |	  YOUR   |	
|  LOCAL   |   =================>     |	  VPS    |  
|  MACHINE |						  |          |
|----------|		   				  |----------|


SECOND:

------------                                
|  YOUR	   |   VPN TO THM NETWORK THROUGH THE TUNNELLED TRAFFIC           	 
|  LOCAL   |   ===================================================>    THM-NETWORK   
|  MACHINE |						        
|----------|		   				        

```



- try both and see which one is more network efficient for you


- the main goal from this whole project is to get access to the THM network and do machines from my local machine using my own tools instead of using the attack box or an external vps to hack from and , It Worked !

- using a vps to hack from, is no good for me bec. :
	
	- way more resources than the cheapest vps would have and costs much more  
	
	- it doesn't have my tools and configurations that i have on my own machine, setting it up would require exceptionally long time

	- you can destroy the openvpn vps and build another one in minutes or even with an automation script so you don't get charged for the vps the time you are not using it ;), but destroying a for-hacking vps and building it again you guessed it, is no fun at all |:,  thats why we have automation right?!




## automation scripts ##

- requirments `python3 -m pip install digitalocean paramiko requests boto3`


### DigitalOcean

- the (create_as_server.py) script only supports (The Second Method) when you run the script it will automate:
		
	- creating and adding ssh-keys to the digitalocean account 
	- creating a vm in the cloud in digitalocean with the created keys
	- downloading and creating an openvpn access server on the created droplet
	- connecting the machine with the created openvpn server 
	- destroying everything once the script is closed by user

- once the script connects you with the droplet's vpn you can normally connect the THM network from your local machine `# openvpn thm_vpn.ovpn`


- the (automate_destroy.py) script also takes the digitalocean api and it automates the process of:

	- destroying the created droplet (the droplet that was created using automate_connection.py script)
	- removing the generated ssh-keys from the digitalocean account and deleting them from the disk
	- deleting the openvpn client of the vps

	- its there in case something gone wrong with the automate script so destroying the stuff wouldn't take much time


- the (create_as_server.py) script does it all in one time don't use the (automate_destroy.py) unless needed  


- the (openvpn-automated-install.sh) is just an edited version of (Nyr's) <a href="https://github.com/Nyr/openvpn-install"> openvpn-install</a> script , credit for <a href="https://github.com/Nyr">Nyr</a> for making this amazing script


- change this variable to your digitalocean api key in both python scripts: (API_TOKEN)  in the digitalocean folder


### AWS

- the (create_as_server_aws.py) supports two modes, the first one which is probably gonna be ran once which is the --setup `python3 create_as_server_aws.py --setup` this mode does 3 things:
	- creates ssh keys that will be used in the future
	- imports the keys into your aws account
	- creates the needed security groups for the machine to work
- OR `python3 create_as_server_aws.py --setup --region [AWS_REGION]` to setup a specific region, but you will have to the add region arg every time you run the script or just change the REGION variable in the script to your favorite region

- if you have an existing ssh key you can run `python3 create_as_server_aws.py --setup --sshkey [YOUR_KEY.pub]` this will skip creating keys and will add your own keys to the region specified for future use

- once done you don't need to run the setup again (unless for a new aws account or you want to set up a new region) 

- the script automates the following (normal mode `python3 create_as_server_aws.py`):
	- creates an aws t2.nano instance and configures it with the imported ssh-keys and the created security groups
	- downloads the (openvpn-automated-install.sh) to the machine
	- sets up the openvpn server 
	- downloads the openvpn client to your localmachine
	- re-writes the openvpn client to make it usable
	- connects with the downloaded openvpn client to the created OpenVpn access server
	- terminates the EC2 instance once pressed CTRL-C

- you need to replace those variables with your own keys from your aws account: (ec2_ak, ec2_sak) 
	- ec2_ak = AccessKey
	- ec2_sak = SecurityAccessKeys 
- how to get the keys?!  <a href="https://www.geeksforgeeks.org/launching-aws-ec2-instance-using-python/"> Geek For Geeks</a> have you covered ;) (AWS account with privileges) part

- the aws script supports the second method described by an SSH dynamic tunnel SOCKS, here is how to configure:
	- run `# python3 create_as_server_aws.py --socks_server` this will open a socks tunnel on (127.0.0.1:1080), now add this line to your (.ovpn) `socks 127.0.0.1 1080` and run the vpn 	 

- the aws method doesn't have an (automate_destroy) so if something gone wrong you gonna need to log-in to your aws and terminate the instance yourself 



## costs ##

### DigitalOcean

-from digital ocean i used debian-11 with shared cpu and regular with ssd the second cheapest machine (6$/mo) 

- my usage is per hour and i destroy it after i finish so it cost per hour:
	
- 0.009$/hour = 0.216$/day (even if you gonna go crazy and hack for 24 hours straight it still pretty damn good ;) 

### AWS

- FREE for 12 MONTH
- 0.0069$/h after the first year 
