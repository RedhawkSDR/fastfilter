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
from ossie.utils import sb
import time
import math

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
        self.comp.filterCoeficients = filter
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
        self.comp.filterCoeficients = cxFilter
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
        self.comp.filterCoeficients = filter
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
        self.comp.filterCoeficients = cxFilter
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        #inData = [data[500*i:500*(i+1)] for i in xrange((len(data)+499)/500)]
        inData=[[x+y for x,y in zip(dataA,dataB)]]
        self.main(inData)
        
        re,im = demux(self.output)
        reSS = self.output = re[(len(filter)-1)/2:]
        self.assertTrue(all([abs(x)<.01 for x in im]))
        self.assertTrue(all([abs(x-y)<.1 for x,y in zip(reSS,inData[0])]))

    
    def main(self, inData, dataCx=False):    
        count=0
        for data in inData:
            #just to mix things up I'm going to push threw in two stages 
            #to ensure the filter is working properly with its state
            
            self.src.push(data,complexData=dataCx)
        while True:
            newData = self.sink.getData()
            if newData:
                count = 0
                self.output.extend(newData)
            elif count==50:
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
