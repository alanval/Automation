from requests.auth import HTTPBasicAuth
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from io import open

def objeto(urly,usernamey,passwy,headersy):
	json_data = requests.get(urly, auth=HTTPBasicAuth(usernamey, passwy), verify=False, data={"id":1}, headers=headersy)
	return json_data	

def filtro(outa,name,tota,conta):	
	templa=[]
	filtro1=outa['sdwan-policy-group']	
	for i in filtro1:
		filtro2=i['rules']
	filtro3=filtro2['rule']	
	print('\n-ok   '+str(conta)+'/'+str(tota)+': ' + str(name))	
	for j in filtro3:		
		templa.append(j['name'])	
	return templa

def genera_devices(urlx,usernamex,passwx,headersx):	
	json_data=objeto(urlx,usernamex,passwx,headersx)	
	if (json_data.status_code == 200):  	
		out=json_data.json()
		filtro1=out['versanms.ApplianceStatusResult']
		diccionario=[]
		nuevaintro=[]
		appliances=filtro1['appliances']
		for i in appliances:
			nuevaintro=i['name']
			diccionario.append(nuevaintro)
		return diccionario
	else:
		raise ApiError('GET / {}'.format(resp.status_code))


def main():
	url2='https://10.150.0.230:9182/vnms/appliance/appliance?offset=0&limit=5000' 
	print('')
	print('**SDWAN Policies Script**')	
	username = input('User: ' )
	passw = input('Pass: ' )
	print('')
	headers={'accept':'application/json', 'content-Type':'application/json'}

	archivo_texto=open("Policies_output.txt","w")	
	cont=0
	lista_devices=[]
	template=[]
	lista_devices=genera_devices(url2,username,passw,headers) 
	total=len(lista_devices)
	archivo_texto.write('Total Appliances:  ' +str(total)+'\n')	
	for z in lista_devices:
		cont=cont+1
		url='https://1.1.1.1:7777/api/config/devices/device/' + z + '/config/orgs/org-services/XZS'
		try:
			json_data=objeto(url,username,passw,headers) 

			if (json_data.status_code == 200):  
					
				output=json_data.json()				
				template=filtro(output,z,total,cont)
				archivo_texto.write('\nDevice: '+str(z)+'\n') 
				for v in template:
					archivo_texto.write(' '+v+'\n')
			else:
				raise ApiError('GET / {}'.format(resp.status_code))
		except Exception as err:
				
				print('\n-Fail '+str(cont)+'/'+str(total)+': ' + str(z))
				archivo_texto.write('\n---->DEVICE ERROR: '+str(z)+'\n') 	
	print('\n'+'________________')
	print('\nExport-> Policies_output.txt')	
	print('')		
	archivo_texto.close()	
	input('\nSCRIPT ended. ' )


main()

