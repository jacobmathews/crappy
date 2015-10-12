from PyDAQmx import *
import numpy
import time

class DaqmxSensor(object):
    """
    Sensor class for Daqmx devices.
    """
    
    def __init__(self,device='Dev1',channels=0,
                 range_num=0, mode= "single"):
        
        self._ranges_tab = [[0.0,0.5],[0.0,1.0],[0.0,2.5],[0.0,5.0],[0.0,7.5],[0.0,10.0],
                     [-0.5,0.5],[-1.0,1.0],[-2.5,2.5],[-5.0,5.5],[-7.5,7.5],[-10.0,10.0]]
        self._channels_tab = ["ai0", "ai1","ai2","ai3","ai4","ai5","ai6","ai7"]
        
        # Declaration of variable passed by reference
        
        self.mode = mode
        self.channels=channels
        self.range_num=range_num
        
        
        #if type(self.channels)==list:
            ## if multiple channels
            #self.nchans=len(self.channels)
            #self.range_num=[self.range_num]*self.nchans
        #if type(self.gain)==int:
            #self.gain=[self.gain]*self.nchans
        #if type(self.offset)==int:
            #self.offset=[self.offset]*self.nchans
            #self.new()
        #else:
            #raise Exception("channels must be int or list")

        self.device = "%s/%s"%(device,self._channels_tab[channels])
        
        
        DAQmxResetDevice('Dev1')
        
        self.taskHandle = TaskHandle()
        self.read = int32()

        
        # DAQmx Configure Code
        DAQmxCreateTask("", byref(self.taskHandle))
        
        print self.device
        print type(self.device)
        DAQmxCreateAIVoltageChan(self.taskHandle,self.device,"",DAQmx_Val_Cfg_Default,
                                 self._ranges_tab[self.range_num][0],self._ranges_tab[self.range_num][1],
                                 DAQmx_Val_Volts,None)
        ## DAQmx Start Code
        DAQmxStartTask(self.taskHandle)


    def getData(self,nbPoints=1):
        """Read the signal"""
        try:
            DAQmxCfgSampClkTiming(self.taskHandle, "", 
                                  10000.0, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 
                                  nbPoints)
            # DAQmx Start Code
            DAQmxStartTask(self.taskHandle)
            data = numpy.zeros((nbPoints,), dtype=numpy.float64)
            DAQmxReadAnalogF64(self.taskHandle, nbPoints, 10.0, 
                               DAQmx_Val_GroupByChannel, data, 
                               nbPoints, byref(self.read), None) # DAQmx Read Code
            t=time.time()
            if(nbPoints==1):
                return (t, data[0])
            else:
                return (t, data)
            
        except DAQError as err:
            raise Exception("DAQmx Error: %s"%err)


    def close(self):
        if self.taskHandle:
            # DAQmx Stop Code
            DAQmxStopTask(self.taskHandle)
            DAQmxClearTask(self.taskHandle)
        else:
            raise Exception('closing failed...')
    
    def __str__(self):
        """
        This method prints out the attributes values
        """
        return " Device: {0} \n Channels({1}): {2} \n Range({3}): min:{4} max: {5} \
               \n Mode: {6}".format(self.device,
                                    self.channels,self._channels_tab[self.channels], 
                                    self.range_num, self._ranges_tab[self.range_num][0],
                                    self._ranges_tab[self.range_num][1], self.mode)