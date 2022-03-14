from requests.auth import HTTPBasicAuth
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from io import open

def objeto(urly,usernamey,passwy,headersy):
	json_data = requests.get(urly, auth=HTTPBasicAuth(usernamey, passwy), verify=False, data={"id":1}, headers=headersy)
	return json_data	

def filtro(outa,devicex,keyx):		
	filtro1=outa['sdwan-policy-group']	
	for i in filtro1:
		filtro2=i['rules']
	filtro3=filtro2['rule']			
	for j in filtro3:
		if j['name']==keyx:
			print('\n-ok   ' + str(devicex))								
			return devicex	

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
	url2='https://1.1.1.1:7777/appliance/appliance?offset=0&limit=5000' 
	print('')
	print('**SDWAN Policies Search Script**')	
	username = input('User: ' )
	passw = input('Pass: ' )
	clave=input('Search Key: ' )
	print('')
	headers={'accept':'application/json', 'content-Type':'application/json'}
	archivo_texto=open("Policies_output_search.txt","w")	
	cont=0
	lista_devices=[]	
	lista_devices=genera_devices(url2,username,passw,headers) 
	total=len(lista_devices)
	archivo_texto.write('Search Key:  ' +str(clave)+'\n')	
	for z in lista_devices:
		
		url='https://1.1.1.1:7772/api/config/devices/device/' + z + '/config/orgs/XYZ'
		try:
			json_data=objeto(url,username,passw,headers) 

			if (json_data.status_code == 200):					
				output=json_data.json()				
				devi=filtro(output,z,clave)
				if devi:					
					archivo_texto.write('\n'+str(z)) 	
					cont=cont+1				
			else:
				raise ApiError('GET / {}'.format(resp.status_code))
		except Exception as err:
				pass					
	
	archivo_texto.write('\n'+'________________')			
	archivo_texto.write('\n## '+str(cont)+' of '+ str(total) + ' devices found ##')		
	archivo_texto.close()
	print('')	
	print('\n## '+str(cont)+ ' devices found ##')
	print('\nExport-> Policies_output_search.txt')
	print('')		
	input('\nSCRIPT ended. ' )


main()

