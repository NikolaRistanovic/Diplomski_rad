"""
23.7.2024
Luka Simić
Nikola Ristanović

Code is made to work and has been tested on 
- OWON XDS2102A / Required drivers - to be determined, possibly only the OEM driver is enough

The idea behind the code is data aquisition from the Deep Memory Channel from the Oscilloscope
The code interprets both 8-bit and 12-bit data resolution
Tested on 10M samples - working
Tested on 20M/40M samples - working (Not stable - sudden change in packet size while transfering data)

400/Div - adjust for voltage/DIV

TESTED ONLY WHEN ONE CHANELL IS SHOWN - improved
TESTED WITH BOTH CHANELLS

TESTED ON : 
- WINDOWS 10        OPERATIONAL
- Kali Linux        OPERATIONAL(udev privilege issues) 
SUBSYSTEMS=="usb", ATTR{idVendor}=="5345", ATTR{idProduct}=="1234" , MODE="0666"          

"""



import usb.core
import json
import numpy as np

class CH:
    active = False
    scaleInt = 0.0
    position = 0.0
    textUnit = ""
    exp = 1e0
    scale = 0

    def __init__(self, jsonName, ch):

        if(jsonName["CHANNEL"][ch]["DISPLAY"] ==  "ON"):
            self.active = True
        
        if(jsonName["CHANNEL"][ch]["SCALE"][-2].isalpha()):
            self.scaleInt = float(jsonName["CHANNEL"][ch]["SCALE"][0:-2])
            self.textUnit = jsonName["CHANNEL"][ch]["SCALE"][-2:]
        else:
            self.scaleInt = float(jsonName["CHANNEL"][ch]["SCALE"][0:-1])
            self.textUnit = jsonName["CHANNEL"][ch]["SCALE"][-1:]

        self.position = jsonName["CHANNEL"][CH]["OFFSET"] / 50

        match self.textUnit:
            case "V":
                self.exp = 1e0
            case "KV":
                self.exp = 1e3
            case "mV":
                self.exp = 1e-3
            case _:
                print(self.textUnit)
                raise "Unexpected Scale units : "
        self.scale = self.scaleInt * self.exp

class osciloscope:

    def __init__(self,verbose=0):
        self.__verbose = verbose
        self.__dev = usb.core.find(idVendor=0x5345, idProduct=0x1234,product="Oscilloscope") 
        if not isinstance(self.__dev, usb.core.Device):
            raise ValueError('Device is not found')

        # device is found :-)
        if self.__verbose >= 3:
            print(self.__dev) ###Print device cofiguration FOR DEBUGGING

        try:
            self.__dev.set_configuration() #Device configuration *mandatory
        except:
            print("Configuration Failed")
            pass
        #Device finding - "idVendor" and "idProduct" are found in device manager

    def checkChannelValid(self,chNo):
        if chNo not in (1,2):
            raise ValueError("invalid channel number")
        
    def reset(self):
        self.__dev.reset()

    def read(self):
            out = self.__dev.read(0x81,1000,5000).tobytes().decode("utf-8")
            if self.__verbose >= 2:
                print(out)
            return out
    
    def write(self,param):
        if self.__verbose >= 2:
            print(param)
        self.__dev.write(0x3,param)
        return

    def getMax(self,chNo):
        self.checkChannelValid(chNo)
        self.write(f":MEASUrement:CH{chNo}:MAX?")
        max = self.read()[:-3].split(":")[1].replace(' ','')
        return max

    def getMin(self,chNo):
        self.checkChannelValid(chNo)
        self.write(f":MEASUrement:CH{chNo}:MIN?")
        min = self.read()[:-3].split(':')[1].replace(' ','')
        return min

    def getFreq(self,chNo):
            self.checkChannelValid(chNo)
            self.write(f":MEASUrement:CH{chNo}:FREQ?")
            freq = self.read()[:-3].split(':')[1].replace(' ','')
            return freq

    __validTimebases = np.empty((2),dtype=object)
    __validTimebases[0] = np.array([2.e-09, 5.e-09, 1.e-08, 2.e-08, 5.e-08, 1.e-07, 2.e-07, 5.e-07, 1.e-06, 2.e-06, 5.e-06, 1.e-05, 2.e-05, 5.e-05, 1.e-04, 2.e-04, 5.e-04, 1.e-03, 2.e-03, 5.e-03, 1.e-02, 2.e-02, 5.e-02, 1.e-01, 2.e-01, 5.e-01, 1.e+00, 2.e+00, 5.e+00, 1.e+01, 2.e+01, 5.e+01, 1.e+02, 2.e+02, 5.e+02, 1.e+03],dtype=float)
    __validTimebases[1] = np.array(['2.0ns', '5.0ns', '10.0ns', '20.0ns', '50.0ns', '100ns', '200ns', '500ns', '1.0us', '2.0us', '5.0us', '10us', '20us', '50us', '100us', '200us', '500us', '1.0ms', '2.0ms', '5.0ms', '10ms', '20ms', '50ms', '100ms', '200s', '500s', '1.0s', '2.0s', '5.0s', '10s', '20s', '50s', '100s', '200s', '500s', '1000s'],dtype="U10")

    def setTimebase(self,time):
        if type(time) not in (float,int):
            raise ValueError("time should be real number")
        indexTime = np.argmin(np.abs(self.__validTimebases[0]-time))
        self.write(f":HORIzontal:SCALe {self.__validTimebases[1][indexTime]}")
        return

    def getTimebase(self):
        self.write(":HORIzontal:SCALe?")
        return self.read()



    def __printProgressBar (self,iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\033[92m \r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        # Print New Line on Complete
        if iteration == total: 
            print('\033[0m')

    

    def __getDataFromMemory(self):
        self.__dev.write(0x3, ':DATA:WAVE:DEPMem:All?') #Input address for the osciloscope - Sending the inqury


        #Reading the Data header, size of the buffer must be big enoug to collect all of the samples
        #max 2*10e6*2 bytes - 2 channels * 10Milion samples each, each sample is 2 bytes
        header = self.__dev.read(0x81, 10000000, 10000).tobytes() 
        # assert(len(header) == 4)


        #Calculating the total deep memory channel size - First 4 bytes encoded as 2 Byte little endian
        buffer_size = int.from_bytes(header[:4], 'little')

        all_data = header[4:]

        #Reading the deep channel data

        while len(all_data) < buffer_size:
            all_data += self.__dev.read(0x81, 10000000, 5000).tobytes()
            if self.__verbose >= 0:
                self.__printProgressBar(len(all_data),buffer_size,prefix='Data Download',suffix='Complete',length=50)

        if self.__verbose >= 1:
            print('Received data : ', round(len(all_data)/1024,2),"kB",sep='')
        
        jsonSize = int.from_bytes(all_data[:4], 'little')
        self.__jsonData = all_data[4:4 + jsonSize]
        self.__samplesRaw = all_data[4 + jsonSize:]

        if self.__verbose >= 1:
            print("Data lenght/buffer size",len(all_data),buffer_size)

        return

    def __parseJson(self):

        #JSON stuff                 #Parsing the JSON header size - little endian encoded
        self.__json_header = json.loads(self.__jsonData.decode('utf-8'))  #Parsing JSON data
                                #Printing JSON header data
        return

    def __parseScreenInfo(self):
        self.sampleLen = self.__json_header["SAMPLE"]["DATALEN"]
        sampleRateTxt = self.__json_header["SAMPLE"]["SAMPLERATE"][1:-3]   #Truncating JSON Samplerate string

        if sampleRateTxt[-2].isalpha():
            sampleRateValue, sampleRateUnit = (float(sampleRateTxt[:-2]),sampleRateTxt[-2:])      #Separating value from units
        else:
            sampleRateValue, sampleRateUnit = (float(sampleRateTxt[:-1]),sampleRateTxt[-1:])      #Separating value from units
        exponent = 1


        match sampleRateUnit:
            case 'S':
                exponent = float(1)
            case 'KS':
                exponent = float(1e3)
            case 'MS':
                exponent = float(1e6)
            case 'GS':
                exponent = float(1e9)
            case _ :
                print(f"Faulty : {sampleRateUnit}")
                raise("Unexpected value Error!")
        
        self.sampleRate = sampleRateValue * exponent

        return

    def printJsonHeader(self):
        print(self.__json_header)

    def getJsonHeader(self):
        return self.__json_header

    def getSampleRate(self):
        return self.sampleRate

    def getSampleLen(self):
        return self.sampleLen

    def getChannelData(self,chNo):
        if chNo == 1:
            return self.__ch1
        elif chNo == 2:
            return self.__ch2
        else:
            raise ValueError("Invalid channel number")

    def saveData(self,saveName = None):
        #Save data as np Array and JSON metadata

        if saveName == None:
            saveName = input("Filename to save data to (N to skip) : ")

        if(saveName == "N" or saveName == "n"):
            pass
        else:
            with open(saveName + '.npy', 'wb') as dataArray:
                np.save(dataArray, self.samples)
            print("Saved successfully as " + saveName + ".npy")

            with open(saveName + '.json', 'w') as config_file:
                json.dump(self.json_header, config_file, indent=4)
            print("Saved successfully as " + saveName + ".json")

    def getSamples(self):
            self.__getDataFromMemory()
            self.__parseJson()
            self.__parseScreenInfo()

            self.__ch1 = CH(self.__json_header,0)
            self.__ch2 = CH(self.__json_header,1)

            if self.__verbose >= 2:
                print(str(self.__ch1.scaleInt) + self.__ch1.textUnit,str(self.__ch2.scaleInt) + self.__ch2.textUnit)


            #first 4 bytes present the number of bytes for a given channel - little endian
            # print(int.from_bytes(samples[:4], 'little'))
            #Converting datapoints to signed integer samples
            samplesInt = np.ndarray(shape=(len(self.__samplesRaw)//2,),dtype='<i2', buffer=self.__samplesRaw)



            #Reshaping data if 2 channels are present
            if(self.__ch1.active and self.__ch2.active):
                samples = np.reshape(samplesInt,(2,-1))[::,2:]
            else:
                samples = np.zeros((2,self.sampleLen))
                if self.__ch1.active:
                    samples[0] = samplesInt[2:]
                else:
                    samples[1] = samplesInt[2:]

            return np.array(samples)

                