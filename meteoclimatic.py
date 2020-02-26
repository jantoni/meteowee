#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------------------------------------------------------------------------------------
OPCIONES DE CONFIGURACIÓN DE CORREO

Activar la opción y rellenar los diferentes campos

"""
MANDAR_CORREO = False # ACTIVAR PONIENDO True DESACTIVAR PONIENDO False 

servidor_smtp = "smtpqueenvía"  # Colocar aquí el servidor SMTP que envía el correo, por ejemplo smtp.office365.com para outlook y smtp.gmail.com para gmail
puerto = "587" # Puerto del servidor SMTP, por defecto usar 587 para STARTTLS (smtp explícito) y 465 para smtp implícito
direccion_de_envio = "emailqueenvia"  # Dirección de email que envía el correo
password = "contraseña"  # Contraseña
direccion_a_enviar = "emailalqueseenvía"  # Dirección de correo al que llegará el correo, puede ser la misma que envía
fallos_envio = 5 # Número de plantillas no actualizadas al día en el cual se enviará un correo
test_correo = False  # Poner a True para probar el correo ejecutando el script manualmente

"""
----------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

import os
import math, re
import socket
import hashlib
from datetime import date, datetime
import time

if MANDAR_CORREO:
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText
	import smtplib

utc = 0

if time.daylight:
	fec = time.localtime().tm_isdst
	if fec: utc = time.altzone
	else: utc = time.timezone

os.environ['TZ'] = 'UTC'
time.tzset()

meses = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

def BaseConvert(number, fromdigits, todigits):
	neg = ""
	if number[:1] == "-":
		number = number[1:]
		neg = "-"
	x = 0
	for n in range(0, len(number), 1):
		digit = number[n]
		x = (x * len(fromdigits)) + fromdigits.find(digit)
	
	res = ""
	while x > 0:
		digit = x % len(todigits)
		res = todigits[int(digit)] + res
		x = math.floor(x / len(todigits))
	if neg:
		res = neg + res
	return res

def intorfloat(number):
	number = str(number)
	if "." in number:
		return float(number)
	elif number.isdigit(): 
		return int(number)
	else:
		return 0

def rsentit(winddir): 
	sentit = winddir	
	if winddir.isdigit(): 
		if winddir == "0": winddir = 360
		return winddir
	elif winddir == "N": sentit="360"
	elif winddir == "NNE": sentit="23"
	elif winddir == "NE": sentit="45"
	elif winddir == "ENE": sentit="68"
	elif winddir == "E": sentit="90"
	elif winddir == "ESE": sentit="113"
	elif winddir == "SE": sentit="135"
	elif winddir == "SSE": sentit="158"
	elif winddir == "S": sentit="180"
	elif winddir == "SSW": sentit="203"
	elif winddir == "SW": sentit="225"
	elif winddir == "WSW": sentit="248"
	elif winddir == "W": sentit="270"
	elif winddir == "WNW": sentit="293"
	elif winddir == "NW": sentit="315"
	elif winddir == "NNW": sentit="338"
	elif winddir == "SSO": sentit="203"
	elif winddir == "SO": sentit="225"
	elif winddir == "OSO": sentit="248"
	elif winddir == "O": sentit="270"
	elif winddir == "ONO": sentit="293"
	elif winddir == "NO": sentit="315"
	elif winddir == "NNO": sentit="338"
	elif winddir == "N/A": sentit="0"
	return sentit

def enviar_correo(mensaje, contenido):
	
	msg = MIMEMultipart()
	
	msg['From'] = direccion_de_envio
	msg['To'] = direccion_a_enviar
	msg['Subject'] = mensaje
	
	msg.attach(MIMEText(contenido))
	
	if puerto == "465":
		server = smtplib.SMTP_SSL(servidor_smtp + ": " + puerto)
	else: 
		server = smtplib.SMTP(servidor_smtp + ": " + puerto)
		server.starttls()
	
	server.login(msg['From'], password)
	
	server.sendmail(msg['From'], msg['To'], msg.as_string())
	
	server.quit()
	
	print("Email enviado a %s" % (msg['To']))

if test_correo: 
	enviar_correo('Esto es una prueba del correo python de meteoclimatic','')
	quit()

pwd = os.path.dirname(os.path.abspath(__file__))

try:

	with open(pwd + '/meteoclimatic.ini', 'r') as ini:

		inicont = ini.readlines()

except IOError:
	
	quit('\nFalta meteoclimatic.ini\n')
	
values = {}

for i in inicont:
	if '=' in i:
		valor = i.strip().split('=')
		values[valor[0]] = valor[1]

ruta = values['Path']

if not os.path.isfile(ruta):
	quit('\nRuta o nombre de la plantilla incorrectos\n')

if values["Password"]:
	passwd = values["Password"]
else:
	quit('\nFalta poner la contraseña en meteoclimatic.ini\n')

conex = open(ruta, 'r')

plantilla = conex.readlines()

conex.close()

BASE10 = "0123456789"
BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

valores = {}

for i in plantilla:
	i = i[1:]
	if '=' in i:
		valor = i.strip().replace(',','.').split('=')
		valores[valor[0]] = valor[1]

fecha = valores['UPD']

fecha.replace('/', '-')

fechaanho = (fecha.split(' ')[0]).split('-')[2]

if len(fechaanho) == 4: anho = '%Y'
else: anho = '%y'

fechaformat = time.mktime(time.strptime(fecha, '%d-%m-' + anho + ' %H:%M'))

tiempodesac = time.time() - fechaformat

if  tiempodesac > 1800 + utc: 
	if MANDAR_CORREO:
		if tiempodesac > 1800 + utc and tiempodesac < 2700 + utc:	
			enviar_correo("Plantilla no actualizada", '\n'.join(plantilla))
	quit('\nPlantilla no actualizada\n')

OTP = hashlib.md5(passwd.encode('utf-8')).hexdigest()[:10]

T = BaseConvert(str(int(intorfloat(valores['TMP']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['DHTM']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['DLTM']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MHTM']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MLTM']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YHTM']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YLTM']) * 10)), BASE10, BASE62)
H = BaseConvert(str(int(intorfloat(valores['HUM']))), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['DHHM']))), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['DLHM']))), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MHHM']))), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MLHM']))), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YHHM']))), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YLHM']))), BASE10, BASE62)
B = BaseConvert(str(int(intorfloat(valores['BAR']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['DHBR']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['DLBR']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MHBR']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MLBR']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YHBR']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YLBR']) * 10)), BASE10, BASE62)
W = BaseConvert(str(int(intorfloat(rsentit(valores['AZI'])))), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['WND']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['WRUN']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['DGST']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MGST']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YGST']) * 10)), BASE10, BASE62)
P = BaseConvert(str(int(intorfloat(valores['DPCP']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MPCP']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YPCP']) * 10)), BASE10, BASE62)
S = BaseConvert(str(int(intorfloat(valores['SUN']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['DSUN']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MSUN']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YSUN']) * 10)), BASE10, BASE62)
V = BaseConvert(str(int(intorfloat(valores['UVI']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['DHUV']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['MHUV']) * 10)), BASE10, BASE62) + ';' + \
    BaseConvert(str(int(intorfloat(valores['YHUV']) * 10)), BASE10, BASE62)
U = "3a;" + valores['COD'] + ";" + OTP


query = "T=" + T + "&H=" + H + "&B=" + B + "&W=" + W + "&P=" + P + "&S=" + S + "&V=" + V + "&U=" + U

print(query)

buenos = 0
mal = 0
data = ""
caido = 0

HOST = 'pool.meteoclimatic.com'  
PORT = 80        

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	s.send(("GET /?" + query + " HTTP/1.0\r\nHOST: pool.meteoclimatic.com\r\nUser-Agent: Meteoclimatic_HTTP/1.0\r\n\r\n").encode())
	s.settimeout(20)
	s.send(("Connection: close\r\n\r\n").encode())
	data = s.recv(1024)
	s.close()
except:
	print("Conexión no establecida")
	mal = 1
	caido = 1
	

data = data.decode('utf-8')

datos = data.splitlines()

error = ""

for valor in datos:
	if re.search('^\*ERR', valor): 
		error = str(valor)


if "202 Accepted" in data:
	resul = str(datetime.now()).split('.')[0] + '\nEnvío aceptado\n' + error + '\n\n'
	buenos = 1
	print("Envio aceptado")
else: 
	resul = str(datetime.now()).split('.')[0] + '\nEnvío no aceptado\n\n'
	mal = 1
	print("Envio no aceptado")

print(error)

try:
	if values['Log'] == "1": 
		fecha = pwd + '/log/' + str(date.today().year) + '/' + meses[date.today().month]
		if not os.path.isdir(fecha):
			os.makedirs(fecha)
		log = open(fecha + "/" + str(date.today()) + '.log', 'a+')
		log.seek(0)
		cont = log.read()
		log.write(resul)
		log.close()
		buenos = str(cont.count("Envío aceptado") + buenos)
		malos = str(cont.count("Envío no aceptado") + mal)
		errores = str(cont.count("ERR"))
		if MANDAR_CORREO:
			if mal and int(malos) % int(fallos_envio) == 0: 
				if caido: enviar_correo(malos + " fallos de envío plantilla meteoclimatic", "No se puede conectar con meteoclimatic.")
				else: enviar_correo(malos + " fallos de envío plantilla meteoclimatic", "")
		
		logmes = open(pwd + "/log/" + str(date.today().year) + "/" + meses[date.today().month] + ".log", "a+")
		logmes.seek(0)
		res = logmes.readlines()
		if error: 
			error = "   Errores: " + error 
			if MANDAR_CORREO:
				
				if error and int(errores) % 8 == 0: 
					
					enviar_correo("Errores en la plantilla a meteoclimatic", error + "\n\n" + "\n".join(plantilla))
		cad = "Día " + str(date.today().day) + "   Totales: " + str(int(buenos) + int(malos)) + "   Aceptados: " + str(buenos) + "   No Aceptados: " + str(malos) + error + "\n"
		if len(res) > 0:	
			ultima = res[-1]
			
			if ultima.split(' ')[1].strip() == str(date.today().day): 
				logmes.seek(0)
				logmes.truncate()
				res[-1] = cad
				logmes.writelines(res)
			else: logmes.write(cad)
		else: logmes.write(cad)
		logmes.close()
		

except KeyError:
	with open(pwd + "/meteoclimatic.ini", 'r+') as fp:
		lineas = fp.readlines()    
		lineas.insert(0, "Log=0\n") 
		fp.seek(0)                
		fp.writelines(lineas)
		
