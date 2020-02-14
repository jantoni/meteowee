#!/bin/bash

#####################################################################################################
# Variables a declarar. Modifica estas variables. De lo contrario utilizará los valores por defecto #
#####################################################################################################

DIR='/home/pi'			# Directorio de instalación por defecto (Weewx se instalará en los directorios definidos en el paquete Debian)
WEELOGPER='daily'		# Periodicidad de rotación del log de Weewx. Por defecto es daily (diario), puedes establecer weekly (semanal)
WEELOGMAX=2				# Numero máximo de rotaciones del log de Weewx. Por defecto 2.
APACHE2LOGSIZE='20m'	# Tamaño máximo en Megabytes del log para Apache en RAM. Tras el número debe seguir la m minuscula. Por defecto 20m
WEEWXLOGSIZE='20m'		# Tamaño máximo en Megabytes del log para Weewx en RAM. Tras el número debe seguir la m minuscula. Por defecto 20m
UPDATEOS=0				# Actualizar todo el sistema operativo. 0=NO   1=SI . Esto alarga mucho el tiempo de ejecución del script. Por defecto 0


METEOCLIMATIC_COD='ESMAD2800000028522A'			# Código de estación en Meteoclimatic
METEOCLIMATIC_SIG='12345647890abcdefghijklmn'	# Password de Meteoclimatic
METEOCLIMATIC_TMPL_URL='https://drive.google.com/file/d/0B3z9VwkcZjjWaHNFQzNBUmZCRHc/view?usp=sharing' 		# Enlace a la ubicación de la plantilla


###################################
# FIN DE DECLARACION DE VARIABLES #
###################################


clear
echo "Empezamos"
date


#####################################################################
# Vamos al directorio de instalación establecido en la variable DIR #
#####################################################################

cd $DIR


#############################################
# DESCARGA DE LA PLANTILLA DE METEOCLIMATIC #
#############################################

# echo "Descargando plantilla Meteoclimatic"
# echo "==================================="
# wget


##############################
# Cambiamos la zona horaria. #
##############################

echo "Cambiando la zona horaria"
echo "========================="
# Esta linea es para hora UTC
sudo ln -fs /usr/share/zoneinfo/UTC /etc/localtime
# Esta linea para para hora CET (Central Europe Time)
#sudo ln -fs /usr/share/zoneinfo/CET /etc/localtime
# Esta linea para hora oficial de España Peninsular
#sudo ln -fs /usr/share/zoneinfo/Europe/Madrid /etc/localtime
# Esta linea para hora oficial de Canarias y Portugal
#sudo ln -fs /usr/share/zoneinfo/Portugal /etc/localtime
dpkg-reconfigure -f noninteractive tzdata





############################################################################################################################
# Mejoramos la supervivencia de la tarjeta SD mediante log en RAM y suprimiendo control de acceso a ficheros y directorios #
############################################################################################################################

echo "Creando un disco de 20 MBytes en RAM para hacer el log en la RAM"
echo "================================================================"
echo " " >> /etc/fstab
echo "tmpfs   /var/log    tmpfs    defaults,noatime,nosuid,mode=0755,size=$WEEWXLOGSIZE    0 0" >> /etc/fstab
echo "tmpfs   /var/log/apache2    tmpfs    defaults,noatime,nosuid,mode=0755,size=$APACHE2LOGSIZE    0 0" >> /etc/fstab
echo "Eliminando el registro de acceso a ficheros y directorios. Esto alagará mucho la vida de la SD"
echo "=============================================================================================="
sed -i 's/noatime/noatime,nodiratime/g' "/etc/fstab"


###############################################################
# Eliminamos el swaping para alargar la vida de la tarjeta SD #
###############################################################

echo
echo "Inhabilitando el swaping para alargar la vida de la SD"
echo "======================================================"
swapoff --all


########################################################
# Desinstalamos el falso reloj y el sistema de swaping #
########################################################

echo
date
echo
echo "Eliminando el falso reloj y el sistema de swaping"
echo "================================================="
apt-get purge --yes fake-hwclock dphys-swapfile >> /dev/null


#################################################################
# Mas dificil todavia. Generamos el locale spanish si no existe #
#################################################################

echo
date
echo "Generamos el locale spanish si no existe"
echo "========================================"
sed -i 's/# es_ES.UTF-8/es_ES.UTF-8/g' /etc/locale.gen
/usr/sbin/locale-gen
echo -e "LANG=\"es_ES.UTF-8\"\nLANGUAGE=\"es_ES.UTF-8\"\nLC_ALL=\"es_ES.UTF-8\"" | sudo tee -a /etc/environment > /dev/null
echo
date
echo


###################################################################################
# Definimos los repositorios de Weewx para instalación con apt en sistemas Debian #
###################################################################################

wget -qO - http://weewx.com/keys.html | sudo apt-key add -
wget -qO - http://weewx.com/apt/weewx.list | sudo tee /etc/apt/sources.list.d/weewx.list


###############################################
# Actualizamos el sistema. Un dolor de muelas #
###############################################

echo
date
echo
echo "Actualizamos la lista de paquetes"
echo "================================="
apt-get update >> /dev/null
date

if [ $UPDATEOS = 1 ]
	then
    echo "Actualizando los paquetes del sistema operativo"
	echo "==============================================="
	apt-get upgrade --yes >> /dev/null
	date
fi


############################################
# Instalamos el software adicional a Weewx #
############################################

echo
date
echo
echo "Antes de instalar WeeWX, instalamos el sofware adicional que nos hace falta"
echo "==========================================================================="
echo
echo "Instalando librerias necesarias"
echo "==============================="
apt-get install --yes libimagequant0 libjbig0 liblcms2-2 libtiff5 libwebp6 libwebpdemux2 libwebpmux3 python-cheetah python-configobj python-olefile python-pil python-serial python-six python-usb >> /dev/null
echo
date
echo
echo "Instalando software que vamos a necesitar antes o después. Sqlite, Apache2, ftp, PHP7.3 y otras librerias de python"
echo
echo "Este paso puede tardar, en función de la placa que utilices, hasta 15 minutos. ¡¡Paciencia!!"
echo "==================================================================================================================="
echo
apt-get install --yes sqlite apache2 ftp rsync python-dev php7.3 >> /dev/null


######################################################
# Instalamos Weewx mediante el repositorio de Debian #
######################################################

echo
date
echo
echo "Instalamos WeeWX desde el repositorio oficial"
echo "============================================="
apt-get install weewx


########################################################################################
# Descargamos e instalamos la version disponible en Weewx.com para su descarga directa #
########################################################################################

#echo "Descargando la ultima version disponible de Weewx"
#echo "================================================="
#wget -A '*.deb' -r -l 1 -nd http://weewx.com/downloads/
#echo "Instalando WeeWX"
#echo "================"
#dpkg -i wee*.deb


###############################################################################################################################
# Paramos Weewx para realizar modificaciones en la configuración                                                              #
# Este paso no es necesario puesto que se puede modificar /etc/weewx/weewx.conf y luego recargar con /etc/init.d/weewx reload #
###############################################################################################################################

echo
date
echo
echo "Parando el servidor de WeeWX"
echo "============================"
/etc/init.d/weewx stop
echo


###########################################################################################################
# Modificamos el sistema de log para que Weewx tenga su propio log y no mezclado con el resto del sistema #
###########################################################################################################

echo
date
echo
echo "Modificando el sistema de Log para que WeeWX tenga su propio log diferenciado"
echo "============================================================================="
echo ":programname,startswith,\"weewx\"" /var/log/weewx.log | sudo tee -a /etc/rsyslog.d/99-weewx.conf > /dev/null
echo ":programname,startswith,\"weewx\"" \~\ | sudo tee -a /etc/rsyslog.d/99-weewx.conf > /dev/null


################################################################################################################
# Establecemos que Weewx tenga un log dentro de logrotate para evitar ficheros que nos consuman la RAM o la SD #
# Se estable rotacion diaria y el numero maximo de rotaciones en 2
################################################################################################################

echo
echo "Estableciendo la rotación de log para WeeWX"
echo "==========================================="
echo -e "/var/log/weewx.log {\n  $WEELOGPER\n  missingok\n  rotate $WEELOGMAX\n  compress\n  delaycompress\n  notifempty\n  sharedscripts\n  postrotate\n  /etc/init.d/rsyslog stop\n  /etc/init.d/rsyslog start\n  endscript\n}" | sudo tee -a /etc/logrotate.d/weewx > /dev/null
echo "reiniciando el sistema de log"
echo "============================="
service rsyslog restart


########################################################################################
# Cambiamos en Weewx el dia de comienzo de semana. Ponemos lunes                       #
# Buscamos week_start = 6 y lo sustituimos por week_start = 0 en /etc/weewx/weewx.conf #
########################################################################################

echo
echo "Estableciendo el Lunes como primer dia de la semana en WeeWX"
echo "============================================================"
sed -i 's/week_start = 6/week_start = 0/g' "/etc/weewx/weewx.conf"


#############################################################################################################
# Cambiamos Weewx.conf para que las unidades sean en metrica y ademas mm en lugar de cm y km/h en lugar m/s #
#############################################################################################################

echo
echo "Estableciendo unidades en métrica, milimetros en lugar de centimetros y Kmh en lugar de ms/s"
echo "Esto no modifica la base de datos. La base de datos seguirá en unidades imperiales"
echo "============================================================================================"
sed -i 's/group_speed = meter_per_second/group_speed = km_per_hour/g' "/etc/weewx/weewx.conf"
sed -i 's/group_speed2 = meter_per_second2/group_speed2 = km_per_hour2/g' "/etc/weewx/weewx.conf"
sed -i 's/group_pressure = mbar/group_pressure = hPa/g' "/etc/weewx/weewx.conf"
sed -i 's/group_rain = cm/group_rain = mm/g' "/etc/weewx/weewx.conf"
sed -i 's/group_rainrate = cm_per_hour/group_rainrate = mm_per_hour/g' "/etc/weewx/weewx.conf"


##################################################
# Cambiamos el formato de las horas y las fechas #
##################################################

echo
echo "Cambiando el formato de fechas y horas"
echo "======================================"
sed -i 's/day        = %X/day        = %H:%M/g' "/etc/weewx/skins/Standard/skin.conf"
sed -i 's/week       = %X (%A)/week       = %H:%M on %A/g' "/etc/weewx/skins/Standard/skin.conf"
sed -i 's/month      = %x %X/month      = %d-%b-%Y %H:%M/g' "/etc/weewx/skins/Standard/skin.conf"
sed -i 's/year       = %x %X/year       = %d-%b-%Y %H:%M/g' "/etc/weewx/skins/Standard/skin.conf"
sed -i 's/rainyear   = %x %X/rainyear   = %d-%b-%Y %H:%M/g' "/etc/weewx/skins/Standard/skin.conf"
sed -i 's/current    = %x %X/current    = %d-%b-%Y %H:%M/g' "/etc/weewx/skins/Standard/skin.conf"
sed -i 's/ephem_day  = %X/ephem_day  = %H:%M/g' "/etc/weewx/skins/Standard/skin.conf"
sed -i 's/ephem_year = %x %X/ephem_year = %d-%b-%Y %H:%M/g' "/etc/weewx/skins/Standard/skin.conf"


###############################################################################################
# Cambiamos el formato de viento para que cuando la velocidad sea Cero no aparezca N/A sino N #
###############################################################################################

echo
echo "Realizando modificaciones para que viento igual a cero no aparezca N/A sino N"
echo "============================================================================="
sed -i 's/NNW, N\/A/NNW, N/g' "/etc/weewx/skins/Standard/skin.conf"
sed -i 's/NNW, N\/A/NNW, N/g' "/etc/weewx/weewx.conf"




#############################################################################
# ToDo insertar las variables de lenguaje en el script de arranque de weewx #
#############################################################################



#################
# Meteoclimatic #
#################


# Descargar una plantilla de algún sitio
#wget http://www.googledrive.com/host/0B3z9VwkcZjjWaHNFQzNBUmZCRHc
#mv 0B3z9VwkcZjjWaHNFQzNBUmZCRHc weewx.plantilla
# Editar la plantilla con los datos incorporados anteriormente
#
# Descargar skin Meteoclimatic que aún no existe
#
# Descomprimir skin en /etc/weewx/skins/Meteoclimatic
#
# Descargar rutina de envío de datos a Meteoclimatic
#
# Configuración de la rutina con los datos introducidos
# 
# Modificar /etc/crontab para envío de datos con la rutina
#
#
# Incluir las modificaciones en StdRESTful
# Envio a diferentes redes meteorológicas



#############################
# Para desarrollo posterior #
#############################



#################################################################################
# Identificar o preguntar por la plataforma Raspberry Pi, Orange Pi, Odroid, PC #
#################################################################################








###############################################################################################
# Esto es todo. Reiniciamos, haciendo antes un sync de los datos al disco. Malas experiencias #
###############################################################################################
echo "Proceso finalizado"
echo "=================="
date
echo "Reiniciando"
echo "==========="
sync
reboot