#!/usr/bin/env python
#
# This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
# source distribution.
# 
# This file is part of REDHAWK Basic Components fastfilter.
# 
# REDHAWK Basic Components fastfilter is free software: you can redistribute it and/or modify it under the terms of 
# the GNU General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# 
# REDHAWK Basic Components fastfilter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with this 
# program.  If not, see http://www.gnu.org/licenses/.
#

import unittest
import ossie.utils.testing
import os
from omniORB import any
from ossie.cf import CF
from omniORB import CORBA
from ossie.utils import sb
from ossie.properties import props_to_dict
import time
import math
import matplotlib.pyplot
import scipy.fftpack


DISPLAY = False

def plotFft(sig, fftSize=None, sampleRate=1.0):
    if fftSize==None:
        fftSize = len(sig)
    fIn = scipy.fftpack.fftshift(scipy.fftpack.fft(sig[:fftSize],fftSize))
    freqsIn = scipy.fftpack.fftshift(scipy.fftpack.fftfreq(fftSize,1.0/sampleRate))
    matplotlib.pyplot.plot(freqsIn, [abs(x) for x in fIn])
    #matplotlib.pyplot.plot(freqs, testOut)
    matplotlib.pyplot.show()

def toClipboard(data):
    import pygtk
    pygtk.require('2.0')
    import gtk

    # get the clipboard
    clipboard = gtk.clipboard_get()
    txt = str(data)
    clipboard.set_text(txt)

    # make our data available to other applications
    clipboard.store()

def toCx(input):
    cx=[]
    for i in xrange(len(input)/2):
        cx.append(complex(input[2*i],input[2*i+1]))
    return cx

def realToCx(input):
    cx=[]
    for x in input:
        cx.append(complex(x,0))
    return cx

def muxZeros(input):
    cx=[]
    for x in input:
        cx.append(x)
        cx.append(0)
    return cx

def demux(input):
    re =[]
    im =[]
    if isinstance(input[0],complex):
        for x in input:
            re.append(x.real)
            im.append(x.imag)
    else:
        for i in xrange(len(input)/2):
            re.append(input[2*i])
            im.append(input[2*i+1])
    return re, im 

def getSink(bw, numPts):
    out = []
    fc = math.pi*2*bw
    for n in xrange(numPts):
        if 2*n==numPts-1:
            out.append(2*bw)
        else:
            t= n-(numPts-1)/2.0
            num = math.sin(fc*t)
            den = math.pi*t
            out.append(num/den)
    return out

def getSin(fc,numPts, cx=False, phase0=0):
    fcRad = fc*math.pi*2
    if cx:
        out = []
        for n in xrange(numPts):
            rad = fcRad*n+phase0
            out.append(math.cos(rad))
            out.append(math.sin(rad))
    else:
        out = [math.sin(fcRad*n) for n in xrange(numPts)]
    return out


class ComponentTests(ossie.utils.testing.ScaComponentTestCase):
    """Test for all component implementations in fastfilter"""


    def setUp(self):
        """Set up the unit test - this is run before every method that starts with test
        """
        ossie.utils.testing.ScaComponentTestCase.setUp(self)
        self.src = sb.DataSource()
        self.sink = sb.DataSink()
        
        #setup my components
        self.setupComponent()
        
        self.comp.start()
        self.src.start()
        self.sink.start()
        
        #do the connections
        self.src.connect(self.comp)        
        self.comp.connect(self.sink)
        self.output=[]
 
    def tearDown(self):
        """Finish the unit test - this is run after every method that starts with test
        """
        self.comp.stop()
        #######################################################################
        # Simulate regular component shutdown
        self.comp.releaseObject()
        self.sink.stop()
        self.src.stop()
        self.src.releaseObject()
        self.sink.releaseObject()  
        ossie.utils.testing.ScaComponentTestCase.tearDown(self)
        

    def setupComponent(self):
        #######################################################################
        # Launch the component with the default execparams
        execparams = self.getPropertySet(kinds=("execparam",), modes=("readwrite", "writeonly"), includeNil=False)
        execparams = dict([(x.id, any.from_any(x.value)) for x in execparams])
        self.launch(execparams, initialize=True)
        
        #######################################################################
        # Verify the basic state of the component
        self.assertNotEqual(self.comp, None)
        self.assertEqual(self.comp.ref._non_existent(), False)
        self.assertEqual(self.comp.ref._is_a("IDL:CF/Resource:1.0"), True)
        
        #######################################################################
        # Validate that query returns all expected parameters
        # Query of '[]' should return the following set of properties
        expectedProps = []
        expectedProps.extend(self.getPropertySet(kinds=("configure", "execparam"), modes=("readwrite", "readonly"), includeNil=True))
        expectedProps.extend(self.getPropertySet(kinds=("allocate",), action="external", includeNil=True))
        props = self.comp.query([])
        props = dict((x.id, any.from_any(x.value)) for x in props)
        # Query may return more than expected, but not less
        for expectedProp in expectedProps:
            self.assertEquals(props.has_key(expectedProp.id), True)
        
        #######################################################################
        # Verify that all expected ports are available
        for port in self.scd.get_componentfeatures().get_ports().get_uses():
            port_obj = self.comp.getPort(str(port.get_usesname()))
            self.assertNotEqual(port_obj, None)
            self.assertEqual(port_obj._non_existent(), False)
            self.assertEqual(port_obj._is_a("IDL:CF/Port:1.0"),  True)
            
        for port in self.scd.get_componentfeatures().get_ports().get_provides():
            port_obj = self.comp.getPort(str(port.get_providesname()))
            self.assertNotEqual(port_obj, None)
            self.assertEqual(port_obj._non_existent(), False)
            self.assertEqual(port_obj._is_a(port.get_repid()),  True)
  
    def testReal(self):
        filter = getSink(.2, 513)
        self.comp.fftSize = 1024
        self.comp.filterCoefficients = filter
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        #inData = [data[500*i:500*(i+1)] for i in xrange((len(data)+499)/500)]
        inData=[[x+y for x,y in zip(dataA,dataB)]]
        self.main(inData)
        
        outDataSS = self.output[(len(filter)-1)/2:]
        
        self.assertTrue(all([abs(x-y)<.1 for x,y in zip(outDataSS,inData[0])]))

    def testCxFilt(self):
        filter = getSink(.2, 513)
        cxFilter = muxZeros(filter)
        self.comp.fftSize = 1024
        self.comp.filterComplex = True
        self.comp.filterCoefficients = cxFilter
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        #inData = [data[500*i:500*(i+1)] for i in xrange((len(data)+499)/500)]
        inData=[x+y for x,y in zip(dataA,dataB)]
        cxInData = [muxZeros(inData)]
        self.main(cxInData,dataCx=True)
        
        re,im = demux(self.output)
        reSS = self.output = re[(len(filter)-1)/2:]
        self.assertTrue(all([abs(x)<.01 for x in im]))
        self.assertTrue(all([abs(x-y)<.1 for x,y in zip(reSS,inData)]))

    def testCxRealFilt(self):
        filter = getSink(.2, 513)
        self.comp.fftSize = 1024
        self.comp.filterCoefficients = filter
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        inData=[x+y for x,y in zip(dataA,dataB)]
        cxInData = [muxZeros(inData)]
        self.main(cxInData,dataCx=True)
        
        re,im = demux(self.output)
        reSS = self.output = re[(len(filter)-1)/2:]
        self.assertTrue(all([abs(x)<.01 for x in im]))
        self.assertTrue(all([abs(x-y)<.1 for x,y in zip(reSS,inData)]))


    def testRealCxFilt(self):
        filter = getSink(.2, 513)
        cxFilter = muxZeros(filter)
        self.comp.fftSize = 1024
        self.comp.filterComplex = True
        self.comp.filterCoefficients = cxFilter
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        #inData = [data[500*i:500*(i+1)] for i in xrange((len(data)+499)/500)]
        inData=[[x+y for x,y in zip(dataA,dataB)]]
        self.main(inData)
        
        re,im = demux(self.output)
        reSS = self.output = re[(len(filter)-1)/2:]
        self.assertTrue(all([abs(x)<.01 for x in im]))
        self.assertTrue(all([abs(x-y)<.1 for x,y in zip(reSS,inData[0])]))

    def doImpulseResponse(self, sampleRate, validateFft=True):
        #create an input with all zeros except an initial value of 1 to get the filter impulse response
        data = [0]*int(self.comp.fftSize*1.5)
        data[0]=1
        
        #send data into fhe filter
        self.main([data],False,sampleRate)

        #validate the response
        self.validateImpulseResponse(validateFft)

    def cmpList(self,a,b):
        if isinstance(b, list):
            self.assertTrue(len(a)==len(b))
            self.assertTrue(all([abs(x-y)<.01 for x, y in zip(a,b)]))
        else:
            self.assertTrue(all([abs(x-b)<.01 for x in a]))
    
    def setFilterProps(self, tw=400, filterType='lowpass', ripple=0.01, freq1=1000.0, freq2=2000.0):
        """set the filter properties on the component
        """
        prop = ossie.cf.CF.DataType(id='filterProps', value=CORBA.Any(CORBA.TypeCode("IDL:CF/Properties:1.0"), [ossie.cf.CF.DataType(id='TransitionWidth', value=CORBA.Any(CORBA.TC_double, tw)), 
                                                                                                                ossie.cf.CF.DataType(id='Type', value=CORBA.Any(CORBA.TC_string, filterType)), 
                                                                                                                ossie.cf.CF.DataType(id='Ripple', value=CORBA.Any(CORBA.TC_double, ripple)), 
                                                                                                                ossie.cf.CF.DataType(id='freq1', value=CORBA.Any(CORBA.TC_double, freq1)), 
                                                                                                                ossie.cf.CF.DataType(id='freq2', value=CORBA.Any(CORBA.TC_double, freq2))]))
        self.comp.configure([prop])

    def getFilterProps(self):
        """ get the filter properties from the component
        """
        props = self.comp.query([])
        d = props_to_dict(props)
        return d['filterProps']
        
    def testLowpass(self):
        filterType = 'lowpass'
        self.setFilterProps(filterType=filterType)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 1024, fs)

    def testLowpass2(self):
        """transition width is too small - we will maximize our taps and not pass validation
        """
        filterType = 'lowpass'
        self.setFilterProps(filterType=filterType, tw=10)
        fs = 10000
        self.doImpulseResponse(fs, False)
        if DISPLAY:
            plotFft(self.output, 1024, fs)

    def testLowpass3(self):
        """do a lowpass with different specifications
        """
        filterType = 'lowpass'
        self.setFilterProps(filterType=filterType, tw=500, ripple=.001, freq1=3000)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 1024, fs)

    def testHighPass(self):
        filterType = 'highpass'
        self.setFilterProps(filterType=filterType)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 1024, fs)

    def testBandPass(self):
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.comp.filterCoefficients, 1024, fs)

    def testBandStop(self):
        filterType = 'bandstop'
        self.setFilterProps(filterType=filterType)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.comp.filterCoefficients, 1024, fs)


    def testLowpassCx(self):
        filterType = 'lowpass'
        self.setFilterProps(filterType=filterType)
        self.comp.filterComplex=True
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 16*1024, fs)

    def testHighPassCx(self):
        filterType = 'highpass'
        self.setFilterProps(filterType=filterType)
        self.comp.filterComplex=True
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 1024, fs)

    def testBandPassCx(self):
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType)
        self.comp.filterComplex=True
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 16*1024, fs)

    def testBandPassCx2(self):
        """use negative frequencies only for complex filtering
        """
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType, freq1=-1000.0, freq2=-2000.0)
        self.comp.filterComplex=True
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 16*1024, fs)

    def testBandPassCx3(self):
        """Use negative frequencies only but "reverse" f1 and f2
        """
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType, freq1=-2000.0, freq2=-1000.0)
        self.comp.filterComplex=True
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 16*1024, fs)
    
    def testBandPassCx4(self):
        """use a complex fitler which spans d.c - its lower frequency is negative but its upper is postiive
        """
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType, freq1=-1000.0, freq2=2000.0)
        self.comp.filterComplex=True
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 16*1024, fs)

    def testBandStopCx(self):
        filterType = 'bandstop'
        self.setFilterProps(filterType=filterType)
        self.comp.filterComplex=True
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 1024, fs)

    def eos(self):
        """ensure sending eos clears out the data appropriately
        """
        self.comp.fftSize = 1024
        filterType = 'lowpass'
        self.setFilterProps(filterType=filterType)
                         
        #run data through the filter to get state in there  
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        #inData = [data[500*i:500*(i+1)] for i in xrange((len(data)+499)/500)]
        inData=[[x+y for x,y in zip(dataA,dataB)]]
        self.main(inData, eos=True)
        self.output = []
        
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            plotFft(self.output, 1024, fs)

    def validateImpulseResponse(self, validateFft):        
        filtLen = len(self.comp.filterCoefficients)
        cxTaps = self.comp.filterComplex
        if cxTaps:
            filtLen/=2
            coeffs = toCx(self.comp.filterCoefficients)
        else:
            coeffs = list(self.comp.filterCoefficients)

        #verify we have enough data
        self.assertTrue(len(self.output)>= len(coeffs))
        #verify the impulse response out of the filter is equal to the filter taps
        self.assertTrue(all([abs(x-y) < .01 for x, y in zip(self.output, coeffs)]))
        self.assertTrue(all([abs(x)<.01 for x in self.output[filtLen:]]))
        
        if validateFft:
            #take the fft of the fitler taps and validate the passband/stopband 
            #regions are correct for the given filter specifications
            fftSize = int(2**(math.ceil(math.log(filtLen,2))+1))
            fs = 1.0/self.sink.sri().xdelta
            fIn =scipy.fftpack.fft(coeffs,fftSize)
            freqsIn = scipy.fftpack.fftfreq(fftSize,1.0/fs)
    
            #get the filter properties
            filterProps = self.getFilterProps()
            filterType = filterProps['Type']
            tol = filterProps['TransitionWidth']
            ripple=filterProps['Ripple']
            f1 = filterProps['freq1']
            f2 = filterProps['freq2']
            delta = tol #technically this should be tol*.5 but we have a little grace in our calculations
            
            #build up the passband/stopband regions per the filter specs
            if filterType == 'lowpass':
                passband = [(-f1+delta, f1-delta)]
                stopband = [(-fs/2.0,-f1-delta), (f1+delta, fs/2.0)]
            elif filterType == 'highpass':
                stopband = [(-f1+delta, f1-delta)]
                passband = [(-fs/2.0,-f1-delta), (f1+delta, fs/2.0)]
            else: #bandpass or stopband
                l = [f1, f2]
                l.sort()
                fl, fh = l 
                if filterType == 'bandpass':
                    if cxTaps:
                       passband = [(fl+delta, fh-delta)]
                       stopband = [(-fs/2.0,fl-delta), (fh+delta, fs/2.0)]
                    else:
                       passband = [(-fh+delta, -fl-delta), (fl+delta, fh-delta)]
                       stopband = [(-fs/2.0,-fh-delta), (-fl+delta,fl-delta), (fh+delta, fs/2.0)]
                else:
                    if cxTaps:
                       stopband = [(fl+delta, fh-delta)]
                       passband = [(-fs/2.0,fl-delta), (fh+delta, fs/2.0)]
                    else:
                       stopband = [(-fh+delta, -fl-delta), (fl+delta, fh-delta)]
                       passband = [(-fs/2.0,-fh-delta), (-fl+delta,fl-delta), (fh+delta, fs/2.0)]
    
            for freq, val in zip(freqsIn, fIn):
                #for each fft value/frequency - if in passband or stopband ensure the value is correct
                inPassband = False
                for fmin, fmax in passband:
                    if fmin<=freq<=fmax:
                        #print "pb, freq = ", freq, "val = ", val, "1.- abs(val) = ", 1.0-abs(val), "ripple = ", ripple
                        self.assertTrue(1.0-abs(val)<ripple)
                        inPassband = True
                        break
                if not inPassband:
                    for fmin, fmax in stopband:
                        if fmin<=freq<=fmax:
                            #print "sb, freq = ", freq, "val = ", val, "abs(val) = ", abs(val), "ripple = ", ripple
                            self.assertTrue(abs(val)<ripple)
                            break
    
        
    def main(self, inData, dataCx=False, sampleRate=1.0, eos=False):    
        count=0
        lastPktIndex = len(inData)-1
        for i, data in enumerate(inData):
            #just to mix things up I'm going to push through in two stages
            #to ensure the filter is working properly with its state
            EOS = eos and i == lastPktIndex
            self.src.push(data,complexData=dataCx, sampleRate=sampleRate, EOS=EOS)
        while True:
            newData = self.sink.getData()
            if newData:
                count = 0
                self.output.extend(newData)
            elif count==200:
                break
            time.sleep(.01)
            count+=1
        #convert the output to complex if necessary    
        self.outputCmplx = self.sink.sri().mode==1
        if self.outputCmplx:
            self.output = toCx(self.output)
    # TODO Add additional tests here
    #
    # See:
    #   ossie.utils.bulkio.bulkio_helpers,
    #   ossie.utils.bluefile.bluefile_helpers
    # for modules that will assist with testing components with BULKIO ports
    
if __name__ == "__main__":
    ossie.utils.testing.main("../fastfilter.spd.xml") # By default tests all implementations
