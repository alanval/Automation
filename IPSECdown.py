from requests.auth import HTTPBasicAuth
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from API import *
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

print("▒▒▒▒▒▒▒█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█")
print("▒▒▒▒▒▒▒█░▒▒▒▒▒▒▒▓▒▒▓▒▒▒▒▒▒▒░█")
print("▒▒▒▒▒▒▒█░▒▒▓▒▒▒▒▒▒▒▒▒▄▄▒▓▒▒░█░▄▄")
print("▒▒▄▀▀▄▄█░▒▒▒▒▒▒▓▒▒▒▒█░░▀▄▄▄▄▄▀░░█")
print("▒▒█░░░░█░▒▒▒▒▒▒▒▒▒▒▒█░░░░░░░░░░░█")
print("▒▒▒▀▀▄▄█░▒▒▒▒▓▒▒▒▓▒█░░░█▒░░░░█▒░░█")
print("▒▒▒▒▒▒▒█░▒▓▒▒▒▒▓▒▒▒█░░░░░░░▀░░░░░█")
print("▒▒▒▒▒▄▄█░▒▒▒▓▒▒▒▒▒▒▒█░░█▄▄█▄▄█░░█")
print("▒▒▒▒█░░░█▄▄▄▄▄▄▄▄▄▄█░█▄▄▄▄▄▄▄▄▄█")
print("▒▒▒▒█▄▄█░░█▄▄█░░░░░░█▄▄█░░█▄▄█")
print("")

username = input("User: ")
passw = input("Pass: ")
print("")
ip=input("IP: ")   #INICIO DEL PROGRAMA
print("____________________")

while (ip!="exit") and (ip!="Exit"):
	cont=0
	par=""
	par2=""
	device=""
	url=""
	out=""

	for h in ip:
		if (h=="."): #BUSCA PUNTOS
			cont=cont+1		
		if (cont==2) and (h!="."):	
			par=par+h #SACA TERCER OCTETO
		else:
			if (cont==3) and (h=="."): 
				par=int(par)+64 #SUMA 64 AL 3er OCTETO
				device=str(device)+str(par)
			device=device+h #CONCATENA EL RESULTADO

	#print(device)
	
	print("") 
	headers={'accept':'application/json', 'content-Type':'application/json'}

	dicc_uuid=main()
	#print("EL DICCIONARIO UUID ES: " + str(dicc_uuid))

	url='https://10.150.112.209:9182/vnms/appliance/filter/EY-Global?filterString=' + device + '&offset=0&limit=25'

	json_data = requests.get(url, auth=HTTPBasicAuth(username, passw), verify=False, data={"id":1}, headers=headers)


	#if json_data.status_code != 200:
	    # This mens something went wrong.
	#   


	if (json_data.status_code == 200):  
		out=json_data.json() #TRAE INFO
	else:
		raise ApiError('GET / {}'.format(resp.status_code))
	
	filtro1=out['versanms.ApplianceStatusResult']
	filtro2=filtro1['appliances']

	for i in filtro2:
		filtro4=i['ping-status']
		filtro5=i['sync-status']
		filtro6=i['services-status']
		filtro7=i['ipAddress']
		filtro3=i['applianceLocation']
		print("")
	 	
		print("SDWAN Router: " + str(filtro3['applianceName']) + "    Ip:" + str(filtro7))	
		print("Location: " + filtro3['locationId'])
		print("Type: " + filtro3['type'])	
		print("Ping-status: " + str(filtro4))
		print("Sync-status: " + str(filtro5))
		print("Services-status: " + str(filtro6))
	print("")
	print(">>>exit to terminate program")
	print("")
	ip=input("IP: ")
	print("____________________")   

else:
	print("")
	print("BYE")
	exit()
		





