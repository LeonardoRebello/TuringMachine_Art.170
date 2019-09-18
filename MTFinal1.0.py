#************************ MAQUINA DE TURING VERSÃO 1.0 ************************
# Esse programa deve ser usado em conjunto da Máquina de Turing feita em arduino para funcionar como o esperado.
# Lógica de Programação - Leonardo Rebello (acadêmico de Engenharia de Computação)
# Interface e Correção de Bugs - Gustavo Henrique Stahl Müller (acadêmico de Ciência da Computação)
# UNIVALI - UNIVERSIDADE DO VALE DO ITAJAÍ - 09/2019

import os
import time
import xml.etree.ElementTree as ET
from tkinter import filedialog
from tkinter import *

import serial
from serial.tools import list_ports

Version = "1.0"

# Código que roda ao pressionar o botão executar

def RunTuringMachine():

    LabelComplete["text"] = "Running..."
    root.update()

    tree = ET.parse(machinefile)
    Root = tree.getroot()

    for child in Root:
        Root = child

    NumLines = len(Root.findall('transition'))

    States = []

    for i in range(NumLines):

        lines = []

        for j in range(5):
            lines.append('0')

        States.append(lines)

    i = 0

    for transition in Root.findall('transition'):
        States[i][0] = transition.find('from').text
        States[i][1] = transition.find('to').text
        States[i][2] = transition.find('read').text
        States[i][3] = transition.find('write').text
        States[i][4] = transition.find('move').text
        i += 1

    InitialState = ''
    Terminals = []

    if Root.findall('block') != []:

        for block in Root.findall('block'):

            if block.find('final') != None:
                Terminals.append(block.get('id'))

            if block.find('initial') != None:
                InitialState = block.get('id')
    else:

        for block in Root.findall('state'):

            if block.find('final') != None:
                Terminals.append(block.get('id'))

            if block.find('initial') != None:
                InitialState = block.get('id')

        States.sort()

    tape = str(EntryTape.get())

    # Checks whether the input tape is binary
    for i in range(len(tape)):

        if tape[i] != '1' and tape[i] != '0':
            LabelComplete["fg"] = "red"
            LabelComplete["text"] = "The input tape must be binary only."

            return

    i = 0
    counter = 0
    ValueAux = ''
    signal = False
    Terminal = 'N'
    Door = serial.Serial(port = variablePort.get(), baudrate = 9600)

    while Terminal == 'N':

        if InitialState == States[i][0]:

            Door.write(b'W')
            time.sleep(1)

            ValueAux = Door.readline()
            time.sleep(1)

            if ValueAux == bytes(b'1\r\n'):

                ValueAux = '1'

            else:

                ValueAux = '0'

            if ValueAux == States[i][2]:

                InitialState = States[i][1]

                Door.write(bytes(int(States[i][3])))
                time.sleep(1)

                Door.write(bytes(counter))
                time.sleep(1)

                signal = True

                if States[i][4] == 'R':

                    counter = counter + 1
                    Door.write(b'R')
                    time.sleep(1)

                elif States[i][4] == 'L':

                    counter = counter - 1
                    Door.write(b'L')
                    time.sleep(1)

                else:

                    Door.write(b'S')
                    time.sleep(1)

            elif (i + 1) == NumLines:

                for j in range(len(Terminals)):

                    if InitialState == Terminals[j]:

                        Terminal = 'T'
                        LabelComplete["fg"] = "green"
                        LabelComplete["text"] = "The tape belongs to the language."
                        Door.write(b'T')
                        time.sleep(1)
                        break

                    elif (j + 1) == len(Terminals):

                        Terminal = 'T'
                        LabelComplete["fg"] = "red"
                        LabelComplete["text"] = "The tape does not belong to the language."
                        Door.write(b'F')
                        time.sleep(1)
                        break

                    j += 1

        elif (i + 1) == NumLines:

            for j in range(len(Terminals)):

                if InitialState == Terminals[j]:

                    Terminal = 'T'
                    LabelComplete["fg"] = "green"
                    LabelComplete["text"] = "The tape belongs to the language."
                    Door.write(b'T')
                    time.sleep(1)
                    break

                elif (j + 1) == len(Terminals):

                    Terminal = 'T'
                    LabelComplete["fg"] = "red"
                    LabelComplete["text"] = "The tape does not belong to the language."
                    Door.write(b'F')
                    time.sleep(1)
                    break

                j += 1

        if i == (NumLines + 1):
            Terminal = 'T'
            LabelComplete["fg"] = "red"
            LabelComplete["text"] = "The tape does not belong to the language."

        if signal == True:

            i = 0
            signal = False

        else:

            i += 1

    Door.close()

# Declaração da raiz da interface gráfica

root = Tk()
root.title("TuringMachine v" + Version)
root.resizable(0,0)

# Declaração de funcoes e variaveis da interface grafica

updateFrequency = 100 # Frequência de atualização do botão de executar
hasfile = False
hasport = False
hastape = False

def getfile():
    global machinefile
    global hasfile
    machinefile =  filedialog.askopenfilename(initialdir = "/",title = "Select Automata (.jff)",filetypes = (("Jff files","*.jff"),("All files","*.*")))
    if (machinefile != ""):
        temp = os.path.split(machinefile)
        temp = os.path.split(machinefile)[1]
        LabelFile.config(text=("Current file: " + temp))
        hasfile = True

def updateInterface():
    if (EntryTape.get() != ""):
        hastape = True
    else:
        hastape = False

    if ((hasfile == True) and (hasport == True) and (hastape == True)):
        ButtonExe.config(state="normal")
    else:
        ButtonExe.config(state="disabled")

    variablePort.set(str(port[0]))
    root.after(updateFrequency, updateInterface)

# Declaração de elementos da interface grafica

defaultFont = ("Arial", "13")
defaultBlue = "#275cb0"

LabelTitle = Label(root, text = "TURING MACHINE", font = (defaultFont, 23, "bold"))
LabelFile = Label(root, text = "No file selected.", font = (defaultFont, 13, "italic"))
LabelPort = Label(root, text = "Arduino port:", font = defaultFont, fg = defaultBlue)
LabelTape = Label(root, text = "Input tape:", font = defaultFont, fg = defaultBlue)
LabelComplete = Label(root, text = "", font = (defaultFont, 12, "bold"))

EntryTape = Entry(root, font = defaultFont, width = 18)

ButtonOpen = Button(root, text = "Select File", font = defaultFont, fg = defaultBlue, width = 15, command = getfile)
ButtonExe = Button(root, text = "Execute", font = (defaultFont, 12, "bold"), fg = defaultBlue, width = 15, command = RunTuringMachine)

# Gera a lista com as portas do arduino

try:
    global variablePort
    variablePort = StringVar(root)

    global port
    port = list_ports.comports()

    for i in range(len(port)):
        port[i] = port[i].device

    variablePort.set(str(port[0]))
    ListPort = OptionMenu(root, variablePort, port)
    hasport = True

except:
    variablePort.set("No Ports")

    ListPort = OptionMenu(root, variablePort, variablePort)
    ListPort.config(state="disabled")

    LabelComplete["text"] = "Failed to locate the arduino port,\nplease restart the program."

finally:
    ListPort["width"] = 13
    ListPort["font"] = defaultFont

# Mostra os elementos da interface

LabelTitle.pack(pady=5)
ButtonOpen.pack(padx=100)
LabelFile.pack(pady=10)
LabelPort.pack()
ListPort.pack(pady=5)
LabelTape.pack()
EntryTape.pack(pady=10)
LabelComplete.pack()
ButtonExe.pack(pady=5)

# Atualiza a interface constantemente

root.after(updateFrequency, updateInterface)
root.mainloop()
