from netmiko import Netmiko
from getpass import getpass
import datetime
import os
import socket

def get_credentials(secondary_credentials):		#Appends "secondary_credentials" dictionary (containing 2 items: username & password) and 2 other dictionaries to list named "credentials"
    credentials = []
    credentials.append(secondary_credentials)
    credentials.append({'username': 'eylogin', 'password':'ey$ecure'})
    credentials.append({'username': 'eylogin', 'password':'cisco2'})
    return credentials   #returns full list containing 3 dictionaries


def get_image(net_connect):		#Retrieves IOS running in the device
    output = net_connect.send_command('show version | i image')
    image = output[output.find(":") + 1 : output.rfind("\"")]

    if 'packages.conf' in image:
        output = net_connect.send_command('show version | i Cisco')
        start = output.find('Version')+8
        end = output.find('\n')
        image = output.splitlines()[0][start:end]

    return image

def get_model(net_connect):		#Retrieves device model
    output = net_connect.send_command("show version | i cisco")

    for line in output.splitlines():
        if "WS" in line:
            start = line.find('W')
            end = line.find(')')
            model = line[start:end+1]
            
            if "C45" in model and 'X' not in model:
                supervisor = net_connect.send_command('show ver | i Supervisor')
                ref = supervisor.find('L-E')
                model = model + ' - Supervisor ' + supervisor[ref-1:ref+3]

    return model


def servers_list_concatenated(filename):		#Returns a concatenated list of servers separated by "|"
    servers_list = open(filename, "r").readlines()
    servers_list = list(map(lambda s: s.strip("\r\n"),servers_list))
    return '|'.join(servers_list).strip("\r\n")

def check_servers(device, show_command):		#Returns the result of issuing a command on provided device
    output=device.send_command(show_command)
    return output

def check_routing(device):		#Checks if OSPF or static routing configuration is found in the running config
    if 'ospf' in device.send_command("show run | i ospf"):
        return ('OSPF configured')
    elif device.send_command('show run | i 0.0.0.0'):
        return('Static routing configured')
    else:
        return('No OSPF and no Static routing detected')

def cred_list_concatenated(filename):		#Returns a string: '|username' concatenated with each line of the file 
    cred_list = open(filename, "r").readlines()
    cred_list = list(map(lambda s: s.strip("\r\n"),cred_list))
    return '|username '.join(cred_list).strip("\r\n")


def check_credentials(device, credentials_file):		#Returns the result of checking if the usernames provided in CredentialsFile in the running-config
    output=device.send_command('show running-config | i username '+cred_list_concatenated(credentials_file))
    return output


def get_running_conf(device, hostname, folder):		#Creates a .txt file with the output of the running configuration
    
    run = device.send_command("show run")

    if run:
        f = open(folder + hostname +' running config.txt', "w")
        f.write(run)
        f.close()
        output = 'Yes'
    else:
        output='No'

    return output

def cls():		#Clears the CMD window. Command returns nothing
    os.system('CLS')

def print_status(string, output_file):		#Prints in CMD whatever receives under "string". Also prints the content of "string" to the "output_file"
    print(string)
    output_file.write(string+'\n')

def save_result(k):		#Checks if "k" variable has something and return yes if it does
    if k:
        res = 'Yes'
    else:
        res = 'No'
    return res


def create_folder(name):		#Checks if folder named "name"\ exists in current directory and creates it if it doesn´t. Returns complete path to inside the "name" folder
    directory = os.getcwd()+'\\'+ name + '\\'
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except Exception as err:
        print(err)
    else:
        return directory

def get_data_source_path():		#Returns full path to "DataSources\" folder located in the directory that the current script is located
    directory = os.getcwd()+'\\' + 'DataSources\\'
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except Exception as err:
        print(err)
    else:
        return directory


def checkDNS(device):
	result = {'NAME': '', 'IP': ''}
	if 'R' in device.upper(): #If device.upper() contains 'R' it means that contains a hostname
		try: #If hostname is resolved to an IP address, saves result to result['IP']
			result['IP'] = socket.gethostbyname(device)
		except Exception as e:
			print('\nAn error occurred while resolving name: ',str(e))
		try:
			name = socket.gethostbyaddr(result['IP'])#If PTR is retrieved from the ip, saves it to result['NAME']
			result['NAME'] = name[0]
		except Exception as e:
			print('\nAn error occurred while getting PTR for IP: ',str(e))	
		return result
	else:#If device contains an IP address
		try:#If PTR is retrieved from the ip, saves it to result['NAME']
			name = socket.gethostbyaddr(device)
			result['NAME'] = name[0]
		except Exception as e:
			print('\nAn error occurred while getting PTR for the IP address: ',str(e))
		try:#If hostname is resolved to an IP address, saves result to result['IP']
			result['IP'] = socket.gethostbyname(result['NAME'])
		except Exception as e:
			print('\nAn error occurred while resolving name: ',str(e))
		return result


def banner(device):

	output = device.send_command('show run | i banner')
	result = ''
	
	if output:
		for line in output.splitlines():
			start = line.find('r')+2
			end = line.find('^C')-1
			if result:
				result += ' - '
			result+= line[start:end]

	return result

	
def tacacs(device):
	run = device.send_command('show run | i tacacs-server host')
	servers = []
	if run:
		for line in run.splitlines():
			start = line.find('host') + 5
			end = line.find('\r\n')
			servers.append({'tacacs':line[start:end]})
	return servers

def ssh(device):
	output = device.send_command('show run | i ssh version')

	if output:
		start = output.find('n')+2
		output = output[start]
		return output

	return 'Not configured'


def run():

#Asks for TACACS username and password

	print('\nEnter your TACACS credentials')
	secondary_username = 'A2135864-3'
	secondary_password = 'U=VREt@5d7wT4Jz'
	
#Next writes the provided credentials to the "credentials" variable and appends local creds defined in the get_credentials function
	credentials = get_credentials({'username':secondary_username, 'password':secondary_password})
#Asks for site name
	site_name = input('\nEnter name of the site: ')

	devices_file = open("Devices.txt", "r")
	devices_c = open("Devices.txt", "r")
#Gets full path to DataSources folder
	input_folder = get_data_source_path()
#Creates folder in the location of the script with string provided to siteName
	output_folder = create_folder(site_name)
	results_file = open (output_folder+'results.csv',"w")

	output_file = open (output_folder + 'output.txt',"w")

	current_dt = datetime.datetime.now()

	headers = 'Device;Connection status;A record created;PTR created;Device model;Running image;CAPC servers configured?;Netbrain servers configured?;Splunk servers configured?;TACACs servers;Configured routing;Standard credentials;Banners;SSH version;Running configuration retrieved?'
	results_file.write(headers)

	results_file.write('\n')
    
	output_file.write('Running script...'+'\n')
	output_file.write('Start time: '+current_dt.strftime("%Y-%m-%d %H:%M:%S")+'\n')

	device_total=0
	device_count=0
	
	for line in devices_c:
		device_total+=1
	for d  in devices_file.readlines():
		cls()
		device_count+=1
		device = d.strip("\r\n")
		device_result = {'name':device, 'status':'','ARecord':'','PTR':'','model':'N/A', 'image':'N/A', 'CAPC':'N/A', 'NETBRAIN':'N/A', 'SPLUNK':'N/A','TACACS':'', 'ROUTING':'N/A', 'BANNER':'N/A' , 'SSH' : 'N/A', 'CREDENTIALS':'N/A','RUNNINGCONFIG':'N/A'}

		print_status("**************************************************************************** - " + site_name, output_file)
		print_status('Device '+str(device_count)+' of '+str(device_total)+': '+device , output_file)
		#print_status(device , output_file)

#Tries to login with any of the provided credentials. If every cred fails, script marks device status as 'Inactive' and jumps to next device
		for cred in credentials: 
			try:
				print_status('\nAttempting connection...', output_file)

				net_connect = Netmiko(
                    host=device,
                    username=cred.get('username'),
                    password=cred.get('password'),
                    device_type="cisco_ios",
                )

				print_status('----> Connection successful\n', output_file)
				device_result['status']='Active'
#Checks if DNS records created
				dns = checkDNS(device) ############################################################################################
				device_result['ARecord'] = dns['IP']
				device_result['PTR'] = dns['NAME']

				print_status('\nA Record lookup result: '+ device_result['ARecord'], output_file)
				print_status('\nPTR lookup result: '+ device_result['PTR'], output_file)
#Checks device model
				print_status("\nChecking device model...", output_file)
				device_result['model'] = get_model(net_connect)
				print_status("Device model is "+device_result['model'], output_file)
#Checks device running ios
				print_status("\nChecking image...", output_file)
				device_result['image'] = get_image(net_connect)
				print_status("Image is "+device_result['image'], output_file)
#Checking SSH version
				print_status('\nChecking SSH version in config...', output_file)
				SSHV = ssh(net_connect)
				print_status('\nSSH version: '+ SSHV, output_file)
				device_result['SSH'] = SSHV
#Checks for BANNERS
				print_status('\nChecking banners in config...', output_file)
				ban = banner(net_connect)
				print_status('Banners found in config: ' + ban, output_file)
				device_result['BANNER'] = ban
#Checks if OSPF or Static route is configured
				print_status("\nChecking routing configuration...", output_file)
				routing = check_routing(net_connect)
				device_result['ROUTING'] = routing
				print_status(routing, output_file)
#Checks configured CAPC servers in running
				print_status("\nChecking CAPC servers...", output_file)
				ACL_check_command = 'show running-config | i '+servers_list_concatenated(input_folder +"CAPC servers.txt")
				CAPC = check_servers(net_connect, ACL_check_command)
				device_result['CAPC'] = save_result(CAPC)
				print_status("\nCAPC servers found in configuration?: "+device_result['CAPC'] +'\n'+CAPC, output_file)
#Checks configured NETBRAIN servers in running
				ACL_check_command = 'show running-config | i '+servers_list_concatenated(input_folder +"NETBRAIN servers.txt")
				NETBRAIN = check_servers(net_connect, ACL_check_command)
				device_result['NETBRAIN'] = save_result(NETBRAIN)
				print_status("\nNETBRAIN servers found in configuration?: "+device_result['NETBRAIN'] +'\n'+NETBRAIN, output_file)
#Checks configured SPLUNK servers in running
				ACL_check_command = 'show running-config | i '+servers_list_concatenated(input_folder +"SPLUNK servers.txt")
				SPLUNK = check_servers(net_connect, ACL_check_command)
				device_result['SPLUNK'] = save_result(SPLUNK)
				print_status("\nSPLUNK servers found in configuration?: "+device_result['SPLUNK'] +'\n'+SPLUNK, output_file)
#Checks configured TACACS servers in running
				ACL_check_command = 'show running-config | i '+servers_list_concatenated(input_folder +"TACACS servers.txt")
				TACACS = check_servers(net_connect, ACL_check_command)
				device_result['TACACS'] = save_result(SPLUNK)
				print_status("\nTACACS servers found in configuration?: "+device_result['TACACS'] +'\n'+TACACS, output_file)

#Checks if local credentials indicated in "Standard Credentials.txt" are found in running config
				print_status("\nChecking local credentials...", output_file)
				configuredCreds = check_credentials(net_connect, input_folder +'Standard Credentials.txt')
				if configuredCreds:
				    cred = 'Yes'
				    print_status('Credentials found in configuration:\n'+configuredCreds, output_file)
				else:
				    cred = 'No'
				    print_status('No credentials found in config:\n', output_file)
                
				device_result['CREDENTIALS'] = cred

#Retrieves running config and saves to file named as "device" variable
				print_status("\nRetriving running configuration...", output_file)
				runconf = get_running_conf(net_connect, device, output_folder)
				if runconf:
				    device_result['RUNNINGCONFIG'] = runconf
				    print_status("\nRunning configuration retrieved succesfully.", output_file)
				else:
				    print_status("\nUnable to retrieve running configuration", output_file)


				net_connect.disconnect()
				break

			except Exception as err:
				print_status('----> Connection ERROR\n', output_file)
				print_status(str(err), output_file)
				device_result['status']='Inactive'

#Writes results
		results_file.write(device_result['name']+';'+device_result['status']+';'+device_result['ARecord']+';'+device_result['PTR']+';'+device_result['model']+';'+device_result['image']+';'+device_result['CAPC']+';'+device_result['NETBRAIN']+';'+device_result['SPLUNK']+';'+device_result['TACACS']+';'+device_result['ROUTING']+';'+device_result['CREDENTIALS']+';'+device_result['BANNER']+';'+device_result['SSH']+';'+device_result['RUNNINGCONFIG']+'\n')

	cls()
	print_status('\n'+'Script ended!',output_file)
	devices_file.close()
	devices_c.close()
	results_file.close()
	output_file.close()



run()