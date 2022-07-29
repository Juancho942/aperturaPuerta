#from ast import For
from mfrc522 import MFRC522
from machine import Pin
from machine import SPI
from machine import I2C
from lcd_api import LcdApi
from machine import Timer
from pico_i2c_lcd import I2cLcd
import os   
import time 
import network
import _thread


I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

targetaMaestra = ("0x1a0d8519",)
uid_card = []
rele = Pin(33,Pin.OUT)
sonido = Pin(32,Pin.OUT)
luzPuertaAbierta = Pin(26, Pin.OUT)
luzPuertaCerrada = Pin(25, Pin.OUT)
aperturarf = Pin(27, Pin.IN)
tiempoEncendido = 0
tiempoExtraerDatos = 0
acceso = False
spi = 0
lcd = 0
conexion = False
puntosConexion = 9
puntos = 0

    
def int_ext(aperturarf):
    global acceso
    acceso = True
    
tim1 = Timer(1)
tim1.init(period=2000, mode=Timer.PERIODIC, callback=lambda t:tiempo())

def escribir():
    global uid_card
    import ufirebase as firebase
    firebase.setURL("https://ccirod-default-rtdb.firebaseio.com/")
    firebase.put("CCI", {"RFID": uid_card[:]}, bg=0)


def extraerDatos():
            
    global uid_card
    import ufirebase as firebase
    firebase.setURL("https://ccirod-default-rtdb.firebaseio.com/")
    firebase.get("CCI/RFID", "var1", bg=0)
    uid_card = firebase.var1
            
            
def Inserta_Nueva_Targeta():
    global spi
    global lcd
    global uid_card
    luzPuertaCerrada.value(0)
    Sonido_ingreso_targeta()
    luzPuertaAbierta.value(1)
    ingresoTargeta = 1
    time.sleep(2)
    cambioLcd = True
    while (ingresoTargeta):
        if cambioLcd:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("acerque targeta")
            lcd.move_to(7,1)
            lcd.putstr("RF")
            cambioLcd = False
        spi.init()
        rdr = MFRC522(spi=spi, gpioRst=4, gpioCs=5)
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                card_id = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                if str(card_id) in uid_card:
                    Sonido_Puerta_Denegada()
                    ingresoTargeta = 0
                    lcd.clear()
                    lcd.move_to(0,0)
                    lcd.putstr("Denegado targeta")
                    lcd.move_to(3,1)
                    lcd.putstr("ingresada")
                    cambioLcd = False
                elif str(card_id) in targetaMaestra:
                    Sonido_Puerta_Denegada()
                    ingresoTargeta = 0
                    lcd.clear()
                    lcd.move_to(0,0)
                    lcd.putstr("Denegado targeta")
                    lcd.move_to(4,1)
                    lcd.putstr("Maestra")
                    cambioLcd = False
                else:
                    Sonido_ingreso_targeta()
                    uid_card.append(str(card_id))
                    escribir()
                    ingresoTargeta = 0
                    lcd.clear()
                    lcd.move_to(1,0)
                    lcd.putstr("nueva targeta")
                    lcd.move_to(3,1)
                    lcd.putstr("ingresada")
                    cambioLcd = False

def Sonido_ingreso_targeta():
    sonido.value(1)
    luzPuertaAbierta.value(1)
    time.sleep(500/1000)
    sonido.value(0)
    luzPuertaAbierta.value(0)
    time.sleep(500/1000)
    sonido.value(1)
    luzPuertaAbierta.value(1)
    time.sleep(200/1000)
    sonido.value(0)
    luzPuertaAbierta.value(0)
    time.sleep(200/1000)
    sonido.value(1)
    luzPuertaAbierta.value(1)
    time.sleep(200/1000)
    sonido.value(0)
    luzPuertaAbierta.value(0)
            
def Abrir_Puerta():
    global acceso
    if acceso is True:
        luzPuertaCerrada.value(0)
        luzPuertaAbierta.value(1)
        Sonido_Abrir_puerta()
        time.sleep(3)
        luzPuertaCerrada.value(1)
        luzPuertaAbierta.value(0)
        acceso = False
    else:
        luzPuertaCerrada.value(0)
        luzPuertaAbierta.value(1)
        rele.value(1)
        Sonido_Abrir_puerta()
        time.sleep(3)
        rele.value(0)
        luzPuertaCerrada.value(1)
        luzPuertaAbierta.value(0)
            
def Sonido_Puerta_Denegada():
    sonido.value(1)
    luzPuertaCerrada.value(1)
    time.sleep(100/1000)
    sonido.value(0)
    luzPuertaCerrada.value(0)
    time.sleep(100/1000)
    sonido.value(1)
    luzPuertaCerrada.value(1)
    time.sleep(100/1000)
    sonido.value(0)
    luzPuertaCerrada.value(0)
    time.sleep(100/1000)
    sonido.value(1)
    luzPuertaCerrada.value(1)
    time.sleep(100/1000)
    sonido.value(0)
    luzPuertaCerrada.value(0)
            
def Sonido_Abrir_puerta():
    sonido.value(1)
    time.sleep(1500/1000)
    sonido.value(0)
            
def tiempo():
    global tiempoEncendido
    tiempoEncendido += 1

def mensajeConectando():
    global puntosConexion
    global puntos
    if (puntosConexion > 16):
        puntosConexion = 9
        for i in range(16, 9, -1):
            lcd.move_to(i,0)
            lcd.putstr(" ")
    lcd.move_to(puntosConexion,0)
    lcd.putstr(".")
    puntos += 1
    if puntos > 10 :
        puntosConexion += 1
        puntos = 0
def conectar():
    global conexion
    GLOB_WLAN=network.WLAN(network.STA_IF)
    GLOB_WLAN.active(True)
    try:
        GLOB_WLAN.connect("Francelly", "25101291")
    
    except OSError:
        lcd.clear()
        lcd.move_to(0,1)
        lcd.putstr("no se pudo")
        lcd.move_to(1,1)
        lcd.putstr("establecer conex")
        print("no se establecio conexion")
        conexion = True
        pass
    while not GLOB_WLAN.isconnected():
        global conexion
        mensajeConectando()
        conexion = False
        pass
    
def main():
    
    global spi
    global lcd
    global uid_card
    global extraerDatos
    
    i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr("connected")
    conectar()
    if conexion is False:
        extraerDatos()
    spi = SPI(2, baudrate=2500000, polarity=0, phase=0)
    pantallaLcd = True
    aperturarf.irq(trigger=Pin.IRQ_RISING, handler=int_ext)

    while True:
        
        if conexion:
            conectar()
            
        global tiempoEncendido
        global acceso
        global uid_card
        
        if tiempoEncendido > 20:
            extraerDatos()
            print("extraer datos")
            tiempoEncendido = 0
        
        if acceso is True:
            lcd.backlight_on()
            lcd.clear()
            lcd.move_to(4,0)
            lcd.putstr("Ingreso")
            lcd.move_to(4,1)
            lcd.putstr("Mando RF")
            pantallaLcd = False
            Abrir_Puerta()
            pantallaLcd = True
            tiempoEncendido = 0
        if (pantallaLcd):
            if(tiempoEncendido >2):
                lcd.clear()
                lcd.move_to(1,0)
                lcd.putstr("Gestion acceso")
                lcd.move_to(0,1)
                lcd.putstr("CCI Rodamientos")
                pantallaLcd = False
            
        if (tiempoEncendido > 4):
            lcd.backlight_off()
            
        luzPuertaCerrada.value(1)
        luzPuertaAbierta.value(0)
        spi.init()
        rdr = MFRC522(spi=spi, gpioRst=4, gpioCs=5)
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                card_id = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                        
                if str(card_id) in targetaMaestra:
                    lcd.backlight_on()
                    Inserta_Nueva_Targeta()
                    pantallaLcd = True
                    tiempoEncendido = 0
                    
                elif str(card_id) in str(uid_card):
                    lcd.backlight_on()
                    lcd.clear()
                    lcd.move_to(4,0)
                    lcd.putstr("Ingreso")
                    lcd.move_to(2,1)
                    lcd.putstr("Targeta RF")
                    pantallaLcd = False
                    Abrir_Puerta()
                    pantallaLcd = True
                    tiempoEncendido = 0
                    acceso = False
                    
                else:
                    lcd.backlight_on()
                    lcd.clear()
                    lcd.move_to(4,0)
                    lcd.putstr("targeta")
                    lcd.move_to(3,1)
                    lcd.putstr("denegada")
                    pantallaLcd = True
                    Sonido_Puerta_Denegada()
                    tiempoEncendido = 0
                
main()