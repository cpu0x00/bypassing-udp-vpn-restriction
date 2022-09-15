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

	- you can destroy the openvpn vps and build another one in minutes or even with an automation script so you don't get charged for the vps the time you are not using it ;), but destroying a for-hacking vps and building it again you guessed it, is no fun at all |:



## automation scripts ##

- the python scripts aims to automate the process that i took to create and connect and destroy the droplet which means it only works with digital ocean and the digital ocean api key of your account

- the (automate_connection.py) script only supports (The Second Method) when you run the script it will automate:
	
	- creating and adding ssh-keys to the digitalocean account 
	- creating a vm in the cloud in digitalocean with the created keys
	- downloading and creating an openvpn access server on the created droplet
	- connecting the machine with the created openvpn server 

- once the script connects you with the droplet's vpn you can normally connect the THM network from your local machine `# openvpn thm_vpn.ovpn`


- the (automate_destroy.py) script also takes the digitalocean api and it automates the process of:

	- destroying the created droplet (the droplet that was created using automate_connection.py script)
	- removing the generated ssh-keys from the digitalocean account and deleting them from the disk
	- deleting the openvpn client of the vps


- the (openvpn-automated-install.sh) is just an edited version of (Nyr's) <a href="https://github.com/Nyr/openvpn-install"> openvpn-install</a> script , credit for <a href="https://github.com/Nyr">Nyr</a> for making this amazing script



## costs ##

from digital ocean i used debian-11 with shared cpu and regular with ssd the second cheapest machine (6$/mo) 

my usage is per hour and i destroy it after i finish so it cost per hour:

0.009$/hour = 0.216$/day (even if you gonna go crazy and hack for 24 hours straight it still pretty damn good ;) 

