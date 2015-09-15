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

from ossie.cf import CF
from omniORB import CORBA
from ossie.properties import props_to_dict

import math
import scipy.signal
import scipy.fftpack
import numpy

#Scipy changed the api for correlate in version 0.8
from distutils.version import LooseVersion
SCIPY_GREATER_18 = LooseVersion(scipy.__version__) >= LooseVersion('0.8')
_orig_correlate = scipy.signal.correlate
def correlatewrap(data,filter,command, *kwargs):
    return _orig_correlate(data,numpy.conj(filter),command, *kwargs)
if SCIPY_GREATER_18:
    scipy.signal.correlate = correlatewrap

DISPLAY = False
if DISPLAY:
    import matplotlib.pyplot
 
class ImpulseResponseMixIn(object):
    RIPPLE_MULT=1.0
    def makeFilterProps(self, tw=400, filterType='lowpass', ripple=0.01, freq1=1000.0, freq2=2000.0,cx=False):
        """set the filter properties on the component
        """
        return CF.DataType(id='filterProps', value=CORBA.Any(CORBA.TypeCode("IDL:CF/Properties:1.0"),
                                                             [CF.DataType(id='TransitionWidth', value=CORBA.Any(CORBA.TC_double, tw)),
                                                              CF.DataType(id='Type', value=CORBA.Any(CORBA.TC_string, filterType)), 
                                                              CF.DataType(id='Ripple', value=CORBA.Any(CORBA.TC_double, ripple)), 
                                                              CF.DataType(id='freq1', value=CORBA.Any(CORBA.TC_double, freq1)), 
                                                              CF.DataType(id='freq2', value=CORBA.Any(CORBA.TC_double, freq2)),
                                                              CF.DataType(id='filterComplex', value=CORBA.Any(CORBA.TC_boolean, cx))
                                                              ]))
    def setFilterProps(self, *args, **keys):
        filtProp = self.makeFilterProps(*args, **keys)
        self.comp.configure([filtProp])

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
            self.plotFft(self.output, 1024, fs)

    def testLowpass2(self):
        """transition width is too small - we will maximize our taps and not pass validation
        """
        filterType = 'lowpass'
        self.setFilterProps(filterType=filterType, tw=10)
        fs = 10000
        #note - set validate to false because our filter props are impossible to meet and we cannot pass validation
        self.doImpulseResponse(fs, False)
        if DISPLAY:
            self.plotFft(self.output, 1024, fs)

    def testLowpass3(self):
        """do a lowpass with different specifications
        """
        filterType = 'lowpass'
        self.setFilterProps(filterType=filterType, tw=500, ripple=.001, freq1=3000)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 1024, fs)

    def testHighpass(self):
        filterType = 'highpass'
        self.setFilterProps(filterType=filterType)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 1024, fs)

    def testBandpass(self):
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 1024, fs)

    def testBandstop(self):
        filterType = 'bandstop'
        self.setFilterProps(filterType=filterType)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 1024, fs)


    def testLowpassCx(self):
        filterType = 'lowpass'
        self.setFilterProps(filterType=filterType, cx=True)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 16*1024, fs)

    def testHighpassCx(self):
        filterType = 'highpass'
        self.setFilterProps(filterType=filterType,cx=True)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 1024, fs)

    def testBandpassCx(self):
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType,cx=True)
        self.comp.filterComplex=True
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 16*1024, fs)
            
    def testBandpassCx2(self):
        """use negative frequencies only for complex filtering
        """
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType, freq1=-1000.0, freq2=-2000.0,cx=True)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 16*1024, fs)

    def testBandpassCx3(self):
        """Use negative frequencies only but "reverse" f1 and f2
        """
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType, freq1=-2000.0, freq2=-1000.0,cx=True)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 16*1024, fs)
    
    def testBandpassCx4(self):
        """use a complex fitler which spans d.c - its lower frequency is negative but its upper is postiive
        """
        filterType = 'bandpass'
        self.setFilterProps(filterType=filterType, freq1=-1000.0, freq2=2000.0,cx=True)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 16*1024, fs)

    def testBandstopCx(self):
        filterType = 'bandstop'
        self.setFilterProps(filterType=filterType,cx=True)
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 1024, fs)

    def testeos(self):
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
        self.validateSRIPushing()
        self.output = []
        
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 1024, fs)

    def testSRChange(self):
        filterType = 'lowpass'
        self.setFilterProps(filterType=filterType)
        fs = 10000
        self.doImpulseResponse(fs)
        self.output=[]
        fs = 2500
        self.doImpulseResponse(fs)

    def testMultistream(self):
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
        self.main(inData, streamID ='streamA')
        self.validateSRIPushing(streamID='streamA')
        self.output = []
        
        fs = 10000
        self.doImpulseResponse(fs)
        if DISPLAY:
            self.plotFft(self.output, 1024, fs)

    def doImpulseResponse(self, sampleRate, validate=True):
        #create an input with all zeros except an initial value of 1 to get the filter impulse response
        try:
            impulseLen = int(self.comp.fftSize*1.5)
        except AttributeError:
            impulseLen = 2048
        data = [0]*impulseLen
        data[0]=1
        
        #send data into fhe filter
        self.main(inData=[data],dataCx=False,sampleRate =sampleRate)
        self.validateSRIPushing(sampleRate=sampleRate)

        if DISPLAY:
            self.plotFft(self.output, 16*1024, sampleRate)

        #validate the response
        if validate==True:
            self.validateImpulseResponse()
        elif isinstance(validate,list):
            self.cmpList(validate,self.output[:len(validate)])

    def cmpList(self,a,b):
        if isinstance(b, list):
            self.assertTrue(len(a)==len(b))
            self.assertTrue(all([abs(x-y)<.01 for x, y in zip(a,b)]))
        else:
            self.assertTrue(all([abs(x-b)<.01 for x in a]))

    def validateImpulseResponse(self):        
        
        #take the fft of the fitler taps and validate the passband/stopband 
        #regions are correct for the given filter specifications
        filtLen = getFiltLen(self.output)
        fftSize = int(2**(math.ceil(math.log(filtLen,2))+1))
        fs = 1.0/self.sink.sri().xdelta
        fIn =scipy.fftpack.fft(self.output,fftSize)
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
                if self.outputCmplx:
                   passband = [(fl+delta, fh-delta)]
                   stopband = [(-fs/2.0,fl-delta), (fh+delta, fs/2.0)]
                else:
                   passband = [(-fh+delta, -fl-delta), (fl+delta, fh-delta)]
                   stopband = [(-fs/2.0,-fh-delta), (-fl+delta,fl-delta), (fh+delta, fs/2.0)]
            else:
                if self.outputCmplx:
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
                    self.assertTrue(1.0-abs(val)<ripple*self.RIPPLE_MULT)
                    inPassband = True
                    break
            if not inPassband:
                for fmin, fmax in stopband:
                    if fmin<=freq<=fmax:
                        #print "sb, freq = ", freq, "val = ", val, "abs(val) = ", abs(val), "ripple = ", ripple
                        self.assertTrue(abs(val)<ripple*self.RIPPLE_MULT)
                        break

    def plotFft(self, sig, fftSize=None, sampleRate=1.0):
        if fftSize==None:
            fftSize = len(sig)
        fIn = scipy.fftpack.fftshift(scipy.fftpack.fft(sig[:fftSize],fftSize))
        freqsIn = scipy.fftpack.fftshift(scipy.fftpack.fftfreq(fftSize,1.0/sampleRate))
        matplotlib.pyplot.plot(freqsIn, [abs(x) for x in fIn])
        #matplotlib.pyplot.plot(freqs, testOut)
        matplotlib.pyplot.show()

def scipyCorl(filter,data):
    if len(data)<=len(filter):
        #make sure that the data is bigger then the filter by padding zeros to the end
        numPad =  len(filter) - len(data) +1
        dataPad = data[:]
        dataPad.extend([0]*numPad)
        #now take only the non-zero ouputs that we need
        return scipy.signal.correlate(dataPad,filter,'full')[:len(filter) + len(data)-1]
    else:
        return scipy.signal.correlate(data,filter,'full')

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

def getFiltLen(impulseResponse):
    last=None
    for i in xrange(len(impulseResponse)):
        if abs(impulseResponse[i])>.01:
            out=last
        else:
            last=i
    return last+1
