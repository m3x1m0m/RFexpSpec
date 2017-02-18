#pylint: disable=trailing-whitespace, line-too-long, bad-whitespace, invalid-name, R0204, C0200
#pylint: disable=superfluous-parens, missing-docstring, broad-except
#pylint: disable=too-many-lines, too-many-instance-attributes, too-many-statements, too-many-nested-blocks
#pylint: disable=too-many-branches, too-many-public-methods, too-many-locals, too-many-arguments

#============================================================================
#This is an example code for RFExplorer python functionality. 
#Display amplitude in dBm and frequency in MHz of the maximum value of frequency range.
#Check more details at https://github.com/RFExplorer/RFExplorer-for-Python/wiki/Python-Example-IoT-2
#============================================================================

import time
import RFExplorer
import sys, getopt

#---------------------------------------------------------
# Helper functions
#---------------------------------------------------------

def PrintPeak(objRFE):
    """This function prints the amplitude and frequency peak of the latest received sweep
    """
    nInd = objRFE.SweepData.Count-1
    objSweepTemp = objRFE.SweepData.GetData(nInd)
    nStep = objSweepTemp.GetPeakStep()      #Get index of the peak
    fAmplitudeDBM = objSweepTemp.GetAmplitude_DBM(nStep)    #Get amplitude of the peak
    fCenterFreq = objSweepTemp.GetFrequencyMHZ(nStep)   #Get frequency of the peak

    print("Peak: " + "{0:.3f}".format(fCenterFreq) + "MHz  " + str(fAmplitudeDBM) + "dBm")

def ControlSettings(objRFE,fstart,fstop):
    """This functions check user settings 
    """
    SpanSize = None
    StartFreq = None
    StopFreq =  None
    
    span = abs(fstart-fstop)

    #print user settings
    print("User settings:" + "Span: " + str(span) +"MHz"+  " - " + "Start freq: " + str(fstart) +"MHz"+" - " + "Stop freq: " + str(fstop) + "MHz")

    #Control maximum Span size
    if(objRFE.MaxSpanMHZ <= span):
        print("Max Span size: " + str(objRFE.MaxSpanMHZ)+"MHz")
    else:
        objRFE.SpanMHZ = span
        SpanSize = objRFE.SpanMHZ
    if(SpanSize):
        #Control minimum start frequency
        if(objRFE.MinFreqMHZ > fstart):
            print("Min Start freq: " + str(objRFE.MinFreqMHZ)+"MHz")
        else:
            objRFE.StartFrequencyMHZ = fstart
            StartFreq = objRFE.StartFrequencyMHZ    
        if(StartFreq):
            #Control maximum stop frequency
            if(objRFE.MaxFreqMHZ < fstop):
                print("Max Start freq: " + str(objRFE.MaxFreqMHZ)+"MHz")
            else:
                if((StartFreq + SpanSize) > fstop):
                    print("Max Stop freq (fstart + span): " + str(fstop) +"MHz")
                else:
                    StopFreq = (StartFreq + SpanSize)
    
    return SpanSize, StartFreq, StopFreq

#---------------------------------------------------------
# global variables and initialization
#---------------------------------------------------------

SERIALPORT = None    #serial port identifier, use None to autodetect
BAUDRATE = 500000

objRFE = RFExplorer.RFECommunicator()     #Initialize object and thread
objRFE.AutoConfigure = False
MIN_SWEEPS_PER_SPAN = 10

OUTPUT_FILE_NAME = '/home/pi/specScanner/temp.csv'

#---------------------------------------------------------
# Main processing loop
#---------------------------------------------------------
def main(argv):

    # Command line arguments to determine different parameters    
    try: 
        opts, args = getopt.getopt(argv,"ha:b:s:")
    except getopt.GetoptError:
        print('blaaa')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('blaaa')
            sys.exit()
        elif opt in ("-a"):
            fstart = int(arg)
        elif opt in ("-b"):
            fstop = int(arg)
        elif opt in ("-s"):
            steps = int(arg)
    
    try:
        #Find and show valid serial ports
        objRFE.GetConnectedPorts()
        
        #Reset IoT board GPIO2 to High Level and GPIO3 to High Level
        objRFE.ResetIOT_HW(True)

        #Connect to available port
        if (objRFE.ConnectPort(SERIALPORT, BAUDRATE)): 
            #Wait for unit to notify reset completed
            while(objRFE.IsResetEvent):
                pass
            #Wait for unit to stabilize
            time.sleep(3)

            #Request RF Explorer configuration
            objRFE.SendCommand_RequestConfigData()
            #Wait to receive configuration and model details
            while(objRFE.ActiveModel == RFExplorer.RFE_Common.eModel.MODEL_NONE):
                objRFE.ProcessReceivedString(True)    #Process the received configuration
            
            #If object is an analyzer, we can scan for received sweeps
            if(objRFE.IsAnalyzer()):
                #Control settings
                SpanSize, StartFreq, StopFreq = ControlSettings(objRFE,fstart,fstop)
                print(SpanSize,StartFreq, StopFreq)
                
                objRFE.UseMaxHold = True
                objRFE.FreqSpectrumSteps = steps
                print(objRFE.FreqSpectrumSteps)
                time.sleep(1)


                if(SpanSize and StartFreq and StopFreq):
                    #set new frequency range
                    objRFE.SendCommand_SweepDataPoints(steps-1)
                    objRFE.UpdateDeviceConfig(StartFreq, StopFreq)
                    print(objRFE.FreqSpectrumSteps)
                    #Wait for new configuration to arrive (as it will clean up old sweep data)
                    objSweep=None
                    while (objSweep==None or objSweep.StartFrequencyMHZ!=StartFreq):
                        objRFE.ProcessReceivedString(True)
                        if (objRFE.SweepData.Count>0):
                            objSweep=objRFE.SweepData.GetData(objRFE.SweepData.Count-1)

                    F_OUT = open(OUTPUT_FILE_NAME, 'w')

                    print(objRFE.FreqSpectrumSteps)
    #                objRFE.FreqSpectrumSteps = 1024
    #                objRFE.FreqSpectrumSteps = 512
                    print(objRFE.FreqSpectrumSteps)
                    LastStartFreq = 0
                    nInd = 0
                    while (StopFreq<=fstop and StartFreq < StopFreq): 
                        #Process all received data from device 
                        while (objRFE.SweepData.Count<MIN_SWEEPS_PER_SPAN):
                            objRFE.ProcessReceivedString(True)

                        #Print data if received new sweep and a different start frequency 
                        if(StartFreq != LastStartFreq):
                            nInd += 1
                            print("Freq range["+ str(nInd) + "]: " + str(StartFreq) +" - "+ str(StopFreq) + "MHz" )
                            #PrintPeak(objRFE)
                            #print(objRFE.SweepData.Dump())
                            amp = objRFE.SweepData.MaxHoldData.m_arrAmplitude
                            freq = range(len(amp))
                            delta = (StopFreq-StartFreq)/objRFE.FreqSpectrumSteps
                            print(len(freq))
                            for i, a in enumerate(amp):
                                F_OUT.write(','.join(map(str, (StartFreq + i*delta, a))))
                                F_OUT.write('\n')
                                print(','.join(map(str,(StartFreq + i*delta, a))))
                            #print(objRFE.FreqSpectrumSteps)
                            LastFreqStart = StartFreq

                        #set new frequency range
                        StartFreq = StopFreq
                        StopFreq = StartFreq + SpanSize

                        #Maximum stop/start frequency control
                        if (StopFreq > fstop):
                            StopFreq = fstop
                        if (StartFreq < StopFreq):
                            objRFE.UpdateDeviceConfig(StartFreq, StopFreq)

                            #Wait for new configuration to arrive (as it will clean up old sweep data)
                            objSweep=None
                            while (objSweep==None or objSweep.StartFrequencyMHZ!=StartFreq):
                                objRFE.ProcessReceivedString(True)
                                if (objRFE.SweepData.Count>0):
                                    objSweep=objRFE.SweepData.GetData(objRFE.SweepData.Count-1)
                    F_OUT.close()
                else:
                    print("Error: settings are wrong.\nPlease, change and try again")
            else:
                print("Error: Device connected is a Signal Generator. \nPlease, connect a Spectrum Analyzer")
        else:
            print("Not Connected")
  
    except Exception as obEx:
        print("Error: " + str(obEx))


if __name__ == "__main__":
   main(sys.argv[1:])

#---------------------------------------------------------
# Close object and release resources
#---------------------------------------------------------

objRFE.Close()    #Finish the thread and close port
objRFE = None 


