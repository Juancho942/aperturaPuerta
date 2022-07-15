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
tiempoEncendido = 0
spi = 0
lcd = 0

def tiempo():
    #global tiempoEncendido
    tiempoEncendido = 1 + tiempoEncendido
    
tim1 = Timer(1)
tim1.init(period=2000, mode=Timer.PERIODIC, callback=lambda t:
            tiempo()
            )

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
    print(uid_card)
    print(type(uid_card))
            
            
def Inserta_Nueva_Targeta():
    global spi
    global lcd
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
                print(uid_card[:])
                uid_card.append(str(card_id))
                print(uid_card[:])
                escribir()
                ingresoTargeta = 0
                lcd.clear()
                lcd.move_to(1,0)
                lcd.putstr("nueva targeta")
                lcd.move_to(3,1)
                lcd.putstr("ingresada")
                cambioLcd = False
                Sonido_ingreso_targeta()

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

def main():
    
    global spi
    global lcd
    
    i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)    
    GLOB_WLAN=network.WLAN(network.STA_IF)
    GLOB_WLAN.active(True)
    GLOB_WLAN.connect("Francelly", "25101291")
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr("connected....")          

    while not GLOB_WLAN.isconnected():
        pass

    lcd.move_to(2,0)
    lcd.putstr("conect wifi")
    lcd.move_to(0,1)
    lcd.putstr("obteniendo datos")
    extraerDatos()
    print(uid_card)
    longitudDiccionario = len(uid_card)
    print(longitudDiccionario)
    spi = SPI(2, baudrate=2500000, polarity=0, phase=0)
    pantallaLcd = True

    while True:
        global tiempoEncendido
        print(tiempoEncendido)
        if (pantallaLcd):
            if(tiempoEncendido >2):
                lcd.clear()
                lcd.move_to(1,0)
                lcd.putstr("Gestion acceso")
                lcd.move_to(0,1)
                lcd.putstr("CCI Rodaminetos")
                pantallaLcd = False
            
        if (tiempoEncendido > 4):
            lcd.backlight_off()
            
        luzPuertaCerrada.value(1)
        luzPuertaAbierta.value(0)
        spi.init()
        rdr = MFRC522(spi=spi, gpioRst=4, gpioCs=5)
        print("Place card")
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                card_id = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                print(card_id)
                        
                if str(card_id) in str(uid_card):
                    lcd.backlight_on()
                    lcd.clear()
                    lcd.move_to(4,0)
                    lcd.putstr("ingreso")
                    lcd.move_to(2,1)
                    lcd.putstr("targeta RF")
                    pantallaLcd = False
                    print("abrir puerta")
                    Abrir_Puerta()
                    pantallaLcd = True
                    tiempoEncendido = 0
                    
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
                if str(card_id) in targetaMaestra:
                    print("inserta nueva targeta")
                    Inserta_Nueva_Targeta()
                    pantallaLcd = True
                    tiempoEncendido = 0
main()