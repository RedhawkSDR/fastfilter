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
import time
import random

from filter_test_helpers import *

class ComponentTests(ossie.utils.testing.ScaComponentTestCase, ImpulseResponseMixIn):
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
        execparams['DEBUG_LEVEL']=4
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
  
    def testBadCfg1(self):
        """Set with multiple filterProp settings simultaniously and verify we get an error
        """
        prop1 =  self.makeFilterProps()
        prop2 = self.makeCxCoefProps()
        try:
            self.comp.configure([prop1,prop2])
        except CF.PropertySet.InvalidConfiguration:
            return
        raise RunTimeError("No error raised in testBadCfg1")

    def testBadCfg2(self):
        """Set with multiple filterProp settings simultaniously and verify we get an error
        """
        prop1 =  self.makeFilterProps()
        prop2 = self.makeRealCoefProps()
        try:
            self.comp.configure([prop1,prop2])
        except CF.PropertySet.InvalidConfiguration:
            return
        raise RunTimeError("No error raised in testBadCfg1") 

    def testBadCfg3(self):
        """Set with multiple filterProp settings simultaniously and verify we get an error
        """
        prop1 =  self.makeCxCoefProps()
        prop2 = self.makeRealCoefProps()
        try:
            self.comp.configure([prop1,prop2])
        except CF.PropertySet.InvalidConfiguration:
            return
        raise RunTimeError("No error raised in testBadCfg1")

    def testDefaultConfiguration(self):
        """ Test that default configuration is a working allpass filter
        """
        dataPoints = 1024
        data = range(dataPoints)
        
        self.src.push(data,complexData=False, sampleRate=1.0, EOS=False,streamID="someSRI")
        count = 0
        while True:
            newData = self.sink.getData()
            if newData:
                count = 0
                self.output.extend(newData)
            elif count==200:
                break
            time.sleep(.01)
            count+=1
     
        # Very vague but there's padding in the beginning
        # Just want to verify it doesn't fail miserably
        self.assertTrue(len(self.output) > dataPoints/2)
 
    def testEOS(self):
        """ Test EOS
        """
        dataPoints = 1024
        data = range(dataPoints)
        
        self.src.push(data,complexData=False, sampleRate=1.0, EOS=False,streamID="someSRI")
        count = 0
        while True:
            newData = self.sink.getData()
            if newData:
                count = 0
                self.output.extend(newData)
            elif count==200:
                break
            time.sleep(.01)
            count+=1

        self.assertFalse(self.sink.eos())
        self.src.push([],complexData=False, sampleRate=1.0, EOS=True,streamID="someSRI")
        time.sleep(.1)
        self.assertTrue(self.sink.eos())
  
    def testReal(self):
        """ Real Filter real data
        """
        filter = getSink(.2, 513)
        self.comp.fftSize = 1024
        self.comp.realFilterCoefficients = filter
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        #inData = [data[500*i:500*(i+1)] for i in xrange((len(data)+499)/500)]
        inData=[[x+y for x,y in zip(dataA,dataB)]]
        self.main(inData)
        self.validateSRIPushing()
        
        outDataSS = self.output[(len(filter)-1)/2:]
        
        self.assertTrue(all([abs(x-y)<.1 for x,y in zip(outDataSS,inData[0])]))

    def testCxFilt(self):
        """ complex Filter complex data
        """
        filter = getSink(.2, 513)
        self.comp.fftSize = 1024
        self.comp.filterComplex = True
        self.comp.complexFilterCoefficients = filter
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        #inData = [data[500*i:500*(i+1)] for i in xrange((len(data)+499)/500)]
        inData=[x+y for x,y in zip(dataA,dataB)]
        cxInData = [muxZeros(inData)]
        self.main(cxInData,dataCx=True)
        self.validateSRIPushing()
        
        re,im = demux(self.output)
        reSS = self.output = re[(len(filter)-1)/2:]
        self.assertTrue(all([abs(x)<.01 for x in im]))
        self.assertTrue(all([abs(x-y)<.1 for x,y in zip(reSS,inData)]))

    def testCxRealFilt(self):
        """real filter complex data
        """
        filter = getSink(.2, 513)
        self.comp.fftSize = 1024
        self.comp.realFilterCoefficients = filter
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        inData=[x+y for x,y in zip(dataA,dataB)]
        cxInData = [muxZeros(inData)]
        self.main(cxInData,dataCx=True)
        self.validateSRIPushing()
        
        re,im = demux(self.output)
        reSS = self.output = re[(len(filter)-1)/2:]
        self.assertTrue(all([abs(x)<.01 for x in im]))
        self.assertTrue(all([abs(x-y)<.1 for x,y in zip(reSS,inData)]))


    def testRealCxFilt(self):
        """complex filter real data
        """
        filter = getSink(.2, 513)
        self.comp.fftSize = 1024
        self.comp.complexFilterCoefficients = filter
        dataA = getSin(.05, 4*513)
        dataB = getSin(.0123, 4*513,phase0=.054)
        #inData = [data[500*i:500*(i+1)] for i in xrange((len(data)+499)/500)]
        inData=[[x+y for x,y in zip(dataA,dataB)]]
        self.main(inData)
        self.validateSRIPushing()
        
        re,im = demux(self.output)
        reSS = self.output = re[(len(filter)-1)/2:]
        self.assertTrue(all([abs(x)<.01 for x in im]))
        self.assertTrue(all([abs(x-y)<.1 for x,y in zip(reSS,inData[0])]))

    def testRealManualImpulse(self):
        """use manual configuration (real taps) and ensure that the impulse response matches the response
        """
        filter = [random.random() for _ in xrange(513)]
        self.comp.fftSize = 1024
        self.comp.realFilterCoefficients = filter
        self.doImpulseResponse(1e6,filter)    

    def testCxManualImpulse(self):
        """use manual configuration (complex taps) and ensure that the impulse response matches the response
        """
        filter = [complex(random.random(), random.random()) for _ in xrange(513)]
        self.comp.fftSize = 1024
        self.comp.complexFilterCoefficients = filter
        self.doImpulseResponse(1e6,filter) 

    def testRealCorrelation(self):
        """Put the filter into correlation mode and ensure that it correlates
        """
        filter = [random.random() for _ in xrange(513)]
        self.comp.correlationMode=True
        self.comp.fftSize = 1024
        self.comp.realFilterCoefficients = filter
        data = [random.random() for _ in range(int(self.comp.fftSize)/2)]
        outExpected = scipyCorl(filter,data)
        data.extend([0]*(self.comp.fftSize))

        sampleRate = 1e6
        self.main([data],False,sampleRate)
        self.validateSRIPushing(sampleRate=sampleRate)
        self.cmpList(outExpected,self.output[:len(outExpected)])


    def testCxCorrelation(self):
        """Put the filter into correlation mode and ensure that it correlates with cx data and coeficients
        """
        filter = [complex(random.random(),random.random()) for _ in xrange(513)]
        self.comp.correlationMode=True
        self.comp.fftSize = 1024
        self.comp.complexFilterCoefficients = filter
        data = [random.random() for _ in range(int(self.comp.fftSize))]
        dataCx = toCx(data)
        outExpected =  scipyCorl(filter,dataCx)
        data.extend([0]*(int(2*self.comp.fftSize)))
        self.main([data],True,1e6)
        self.validateSRIPushing(sampleRate=1e6)
        self.cmpList(outExpected,self.output[:len(outExpected)])         

    def testCxRealCorrelation(self):
        """real filter complex data for correlation
        """
        filter = [random.random() for _ in xrange(513)]
        self.comp.correlationMode=True
        self.comp.fftSize = 1024
        self.comp.realFilterCoefficients = filter
        data = [random.random() for _ in range(int(self.comp.fftSize))]
        dataCx = toCx(data)
        outExpected =  scipyCorl(filter,dataCx)
        data.extend([0]*(self.comp.fftSize))
        self.main([data],True,1e6)
        self.validateSRIPushing(sampleRate=1e6)
        self.cmpList(outExpected,self.output[:len(outExpected)])

    def testRealCxCorrelationWithReconnecting(self):
        """complex filter real data
        """
        filter = [complex(random.random(),random.random()) for _ in xrange(513)]
        self.comp.correlationMode=True
        self.comp.fftSize = 1024
        self.comp.complexFilterCoefficients = filter
        
        data = [random.random() for _ in range(int(self.comp.fftSize)/2)]
        outExpected = scipyCorl(filter,data)
        data.extend([0]*(self.comp.fftSize))
        self.comp.disconnect(self.sink)
        self.comp.connect(self.sink)
        self.main([data],False,1e6)
        self.validateSRIPushing(sampleRate=1e6)
        self.cmpList(outExpected,self.output[:len(outExpected)])
    
    def makeCxCoefProps(self):
        return ossie.cf.CF.DataType(id='complexFilterCoefficients', value=CORBA.Any(CORBA.TypeCode("IDL:CF/complexFloatSeq:1.0"), []))

    def makeRealCoefProps(self):
        return ossie.cf.CF.DataType(id='realFilterCoefficients', value=CORBA.Any(CORBA.TypeCode("IDL:omg.org/CORBA/FloatSeq:1.0"), []))
   
    def validateSRIPushing(self, sampleRate=1.0, streamID='test_stream'):
        self.assertEqual(self.sink.sri().streamID, streamID, "Component not pushing streamID properly")
        # Account for rounding error
        calcSR = 1/self.sink.sri().xdelta
        diffSR = abs(calcSR-sampleRate)
        tolerance = 1
        self.assertTrue(diffSR < tolerance, "Component not pushing samplerate properly")

    def main(self, inData, dataCx=False, sampleRate=1.0, eos=False,streamID='test_stream'):    
        count=0
        lastPktIndex = len(inData)-1
        for i, data in enumerate(inData):
            #just to mix things up I'm going to push through in two stages
            #to ensure the filter is working properly with its state
            EOS = eos and i == lastPktIndex
            self.src.push(data,complexData=dataCx, sampleRate=sampleRate, EOS=EOS,streamID=streamID)
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
