from requests.auth import HTTPBasicAuth
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from io import open

def objeto(urly,usernamey,passwy,headersy):
	json_data = requests.get(urly, auth=HTTPBasicAuth(usernamey, passwy), verify=False, data={"id":1}, headers=headersy)
	return json_data

def genera_devices(urlx,usernamex,passwx,headersx):	
	json_data=objeto(urlx,usernamex,passwx,headersx)	
	if (json_data.status_code == 200):  	
		out=json_data.json()
		filtro1=out['versanms.ApplianceStatusResult']
		lista_appliance=[]
		nuevaintro=[]
		appliances=filtro1['appliances']
		for i in appliances:
			nuevaintro=i['name']
			lista_appliance.append(nuevaintro)
		return lista_appliance
	else:
		raise ApiError('GET / {}'.format(resp.status_code))


def main():
	url2='https://1.1.1.1:9352/appliance/appliance?offset=0&limit=5000' 
	print('')
	print('**SDWAN Workflows-Service Templates Script**')	
	print('')
	username = input('User: ' )
	passw = input('Pass: ' )
	headers={'accept':'application/json', 'content-Type':'application/json'}
	archivo_texto=open("Workflows_ServiceTeamplates_output.txt","w")	
	cont=0
	lista_devices=[]	
	lista_devices=genera_devices(url2,username,passw,headers) 
	total=len(lista_devices)		
	for z in lista_devices:		
		url='https://1.1.1.1:7777/next/template/'+z+'/associations'
		lista=[]
		try:
			json_data=objeto(url,username,passw,headers) 
			if (json_data.status_code == 200):					
				output=json_data.json()				
				if output:
					cont+=1
					print('\n--Ok:   '+str(z))
					archivo_texto.write('\n')
					archivo_texto.write('\nDevice: '+str(z)+'\n')
					for i in output:					
						if i['category'] not in lista:
							archivo_texto.write('\n>Category: ' + i['category'])
							lista.append(i['category'])
							for u in output:		
								if i['category']==u['category']:
									archivo_texto.write('\n'+' '+u['serviceTemplate'])
				else:
					print('\n-Not found: '+str(z))	
					archivo_texto.write('\n')
					archivo_texto.write('\n-->Not found: '+str(z)+'\n') 					
			else:
				raise ApiError('GET / {}'.format(resp.status_code))				
		except Exception as err:				
				print('\n-Fail '+ str(z))
				
	archivo_texto.write('\n')	
	archivo_texto.write('\n********************************')
	archivo_texto.write('\n> '+str(cont)+' out of '+str(total)+' were retrieved')
	print('\n_________________________________')
	print('\n> '+str(cont)+' out of '+str(total)+' were retrieved <')	
	print('\n> Workflows_ServiceTemplates_output.txt')	
	print('')		
	archivo_texto.close()	
	input('\nSCRIPT ended. ' )


main()

