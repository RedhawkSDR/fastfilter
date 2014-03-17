/*
 * This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this
 * source distribution.
 *
 * This file is part of REDHAWK Basic Components fastfilter.
 *
 * REDHAWK Basic Components fastfilter is free software: you can redistribute it and/or modify it under the terms of
 * the GNU General Public License as published by the Free Software Foundation, either
 * version 3 of the License, or (at your option) any later version.
 *
 * REDHAWK Basic Components fastfilter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with this
 * program.  If not, see http://www.gnu.org/licenses/.
 */

/**************************************************************************

    This is the component code. This file contains the child class where
    custom functionality can be added to the component. Custom
    functionality to the base class can be extended here. Access to
    the ports can also be done from this class

**************************************************************************/

#include "fastfilter.h"

PREPARE_LOGGING(fastfilter_i)

fastfilter_i::fastfilter_i(const char *uuid, const char *label) :
    fastfilter_base(uuid, label),
    manualTaps_(false)
{
	setPropertyChangeListener("fftSize", this, &fastfilter_i::fftSizeChanged);
	setPropertyChangeListener("realFilterCoefficients", this, &fastfilter_i::realFilterCoefficientsChanged);
	setPropertyChangeListener("complexFilterCoefficients", this, &fastfilter_i::complexFilterCoefficientsChanged);
	setPropertyChangeListener("filterProps", this, &fastfilter_i::filterPropsChanged);
	setPropertyChangeListener("correlationMode", this, &fastfilter_i::correlationModeChanged);
}

fastfilter_i::~fastfilter_i()
{
}

/***********************************************************************************************

    Basic functionality:

        The service function is called by the serviceThread object (of type ProcessThread).
        This call happens immediately after the previous call if the return value for
        the previous call was NORMAL.
        If the return value for the previous call was NOOP, then the serviceThread waits
        an amount of time defined in the serviceThread's constructor.
        
    SRI:
        To create a StreamSRI object, use the following code:
                std::string stream_id = "testStream";
                BULKIO::StreamSRI sri = bulkio::sri::create(stream_id);

	Time:
	    To create a PrecisionUTCTime object, use the following code:
                BULKIO::PrecisionUTCTime tstamp = bulkio::time::utils::now();

        
    Ports:

        Data is passed to the serviceFunction through the getPacket call (BULKIO only).
        The dataTransfer class is a port-specific class, so each port implementing the
        BULKIO interface will have its own type-specific dataTransfer.

        The argument to the getPacket function is a floating point number that specifies
        the time to wait in seconds. A zero value is non-blocking. A negative value
        is blocking.  Constants have been defined for these values, bulkio::Const::BLOCKING and
        bulkio::Const::NON_BLOCKING.

        Each received dataTransfer is owned by serviceFunction and *MUST* be
        explicitly deallocated.

        To send data using a BULKIO interface, a convenience interface has been added 
        that takes a std::vector as the data input

        NOTE: If you have a BULKIO dataSDDS port, you must manually call 
              "port->updateStats()" to update the port statistics when appropriate.

        Example:
            // this example assumes that the component has two ports:
            //  A provides (input) port of type bulkio::InShortPort called short_in
            //  A uses (output) port of type bulkio::OutFloatPort called float_out
            // The mapping between the port and the class is found
            // in the component base class header file

            bulkio::InShortPort::dataTransfer *tmp = short_in->getPacket(bulkio::Const::BLOCKING);
            if (not tmp) { // No data is available
                return NOOP;
            }

            std::vector<float> outputData;
            outputData.resize(tmp->dataBuffer.size());
            for (unsigned int i=0; i<tmp->dataBuffer.size(); i++) {
                outputData[i] = (float)tmp->dataBuffer[i];
            }

            // NOTE: You must make at least one valid pushSRI call
            if (tmp->sriChanged) {
                float_out->pushSRI(tmp->SRI);
            }
            float_out->pushPacket(outputData, tmp->T, tmp->EOS, tmp->streamID);

            delete tmp; // IMPORTANT: MUST RELEASE THE RECEIVED DATA BLOCK
            return NORMAL;

        If working with complex data (i.e., the "mode" on the SRI is set to
        true), the std::vector passed from/to BulkIO can be typecast to/from
        std::vector< std::complex<dataType> >.  For example, for short data:

            bulkio::InShortPort::dataTransfer *tmp = myInput->getPacket(bulkio::Const::BLOCKING);
            std::vector<std::complex<short> >* intermediate = (std::vector<std::complex<short> >*) &(tmp->dataBuffer);
            // do work here
            std::vector<short>* output = (std::vector<short>*) intermediate;
            myOutput->pushPacket(*output, tmp->T, tmp->EOS, tmp->streamID);

        Interactions with non-BULKIO ports are left up to the component developer's discretion

    Properties:
        
        Properties are accessed directly as member variables. For example, if the
        property name is "baudRate", it may be accessed within member functions as
        "baudRate". Unnamed properties are given a generated name of the form
        "prop_n", where "n" is the ordinal number of the property in the PRF file.
        Property types are mapped to the nearest C++ type, (e.g. "string" becomes
        "std::string"). All generated properties are declared in the base class
        (fastfilter_base).
    
        Simple sequence properties are mapped to "std::vector" of the simple type.
        Struct properties, if used, are mapped to C++ structs defined in the
        generated file "struct_props.h". Field names are taken from the name in
        the properties file; if no name is given, a generated name of the form
        "field_n" is used, where "n" is the ordinal number of the field.
        
        Example:
            // This example makes use of the following Properties:
            //  - A float value called scaleValue
            //  - A boolean called scaleInput
              
            if (scaleInput) {
                dataOut[i] = dataIn[i] * scaleValue;
            } else {
                dataOut[i] = dataIn[i];
            }
            
        A callback method can be associated with a property so that the method is
        called each time the property value changes.  This is done by calling 
        setPropertyChangeListener(<property name>, this, &fastfilter_i::<callback method>)
        in the constructor.
            
        Example:
            // This example makes use of the following Properties:
            //  - A float value called scaleValue
            
        //Add to fastfilter.cpp
        fastfilter_i::fastfilter_i(const char *uuid, const char *label) :
            fastfilter_base(uuid, label)
        {
            setPropertyChangeListener("scaleValue", this, &fastfilter_i::scaleChanged);
        }

        void fastfilter_i::scaleChanged(const std::string& id){
            std::cout << "scaleChanged scaleValue " << scaleValue << std::endl;
        }
            
        //Add to fastfilter.h
        void scaleChanged(const std::string&);
        
        
************************************************************************************************/
int fastfilter_i::serviceFunction()
{
    bulkio::InFloatPort::dataTransfer *tmp = dataFloat_in->getPacket(bulkio::Const::BLOCKING);
	if (not tmp) { // No data is available
		return NOOP;
	}

	if (tmp->inputQueueFlushed)
	{
		LOG_WARN(fastfilter_i, "input queue flushed - data has been thrown on the floor.  flushing internal buffers");
		//flush all our processor states if the queue flushed
		boost::mutex::scoped_lock lock(filterLock_);
		for (map_type::iterator i = filters_.begin(); i!=filters_.end(); i++)
			i->second.filter->flush();
	}
	bool updateSRI = tmp->sriChanged;
    float fs = 1.0/tmp->SRI.xdelta;
	{
		boost::mutex::scoped_lock lock(filterLock_);
		map_type::iterator i = filters_.find(tmp->streamID);
		firfilter* filter;
		if (i==filters_.end())
		{
			//this is a new stream - need to create a new filter & wrapper
			LOG_DEBUG(fastfilter_i, "creating new filter for streamID "<<tmp->streamID);
			if (manualTaps_)
			{
				LOG_DEBUG(fastfilter_i, "using manual taps ");
				bool real, complex;
				getManualTaps(real,complex);
				if (real)
					filter = new firfilter(fftSize, realOut, complexOut, realTaps_);
				else if(complex)
					filter = new firfilter(fftSize, realOut, complexOut, complexTaps_);
				else
				{
					LOG_WARN(fastfilter_i, "state error - using manual taps with no filter provided.  This shouldn't really happen");
					if (updateSRI)
						dataFloat_out->pushSRI(tmp->SRI);
					dataFloat_out->pushPacket(tmp->dataBuffer, tmp->T, tmp->EOS, tmp->streamID);
					delete tmp;
					return NORMAL;
				}
				updateSRI = true;
			}
			else
			{
				LOG_DEBUG(fastfilter_i, "using filter designer");
				correlationMode=false;
				if (filterProps.filterComplex)
				{
					designTaps(complexTaps_, fs);
					filter = new firfilter(fftSize, realOut, complexOut, complexTaps_);
				}
				else
				{
					designTaps(realTaps_, fs);
					filter = new firfilter(fftSize, realOut, complexOut, realTaps_);
				}
			}
			map_type::value_type filterWrapperMap(tmp->streamID, FilterWrapper());
			i = filters_.insert(filters_.end(),filterWrapperMap);
			i->second.setParams(fs,filter);
		}
		else
			//get the filter we have used before
			filter = i->second.filter;

		//if we are in design mode and the sample rate has changed - redesign and apply our filter
		if (!manualTaps_ && i->second.hasSampleRateChanged(fs))
		{
			if (filterProps.filterComplex)
			{
				designTaps(complexTaps_, fs);
				filter->setTaps(complexTaps_);
			}
			else
			{
				designTaps(realTaps_, fs);
				filter->setTaps(realTaps_);
			}
		}

		//now process the data
		if (tmp->SRI.mode==1)
		{
			//data is complex
			//run the filter
			std::vector<std::complex<float> >* cxData = (std::vector<std::complex<float> >*) &(tmp->dataBuffer);
			filter->newComplexData(*cxData);
		}
		else
		{
			//data is real
			//run the filter
			filter->newRealData(tmp->dataBuffer);
			//we might have a single complex frame if the previous data was complex and there were
			//complex data still in the filter taps
			if (!complexOut.empty())
			{
				//update the mode to true for the complex fame and force an sri push
				tmp->SRI.mode=1;
				updateSRI = true;
			}
		}
	    if (tmp->EOS)
	    {
	    	//if we have an eos - remove the wrapper from the container
	    	filters_.erase(i);
	    }
	}

	//to do -- adjust time stamps appropriately on all these output pushes
    // NOTE: You must make at least one valid pushSRI call
    if (updateSRI) {
    	dataFloat_out->pushSRI(tmp->SRI);
    }
    if (!complexOut.empty())
    {
    	std::vector<float>* tmpRealOut = (std::vector<float>*) &(complexOut);
    	dataFloat_out->pushPacket(*tmpRealOut, tmp->T, tmp->EOS, tmp->streamID);
    }
    if (!realOut.empty())
    {
    	//case we we forced a push on real data from previous complex data
    	//need to force our sri back to real and push another sri
    	if (updateSRI && tmp->SRI.mode==1)
    	{
    		//change mode back to 0 and send another sri with our real output
    		tmp->SRI.mode=0;
    		dataFloat_out->pushSRI(tmp->SRI);
    	}
    	dataFloat_out->pushPacket(realOut, tmp->T, tmp->EOS, tmp->streamID);
    }
    delete tmp; // IMPORTANT: MUST RELEASE THE RECEIVED DATA BLOCK
    return NORMAL;
}

void fastfilter_i::configure (const CF::Properties& configProperties)
	throw (CF::PropertySet::PartialConfiguration,
           CF::PropertySet::InvalidConfiguration, CORBA::SystemException)
{
	if (started())
	{
		size_t filtProps=0;
		for (unsigned int index = 0; index < configProperties.length(); ++index)
		{
			if (strcmp(configProperties[index].id,"realFilterCoefficients")==0)
				filtProps++;
			else if (strcmp(configProperties[index].id,"complexFilterCoefficients")==0)
				filtProps++;
			else if (strcmp(configProperties[index].id,"filterProps")==0)
				filtProps++;
		}
		if (filtProps > 1)
		{
			LOG_ERROR(fastfilter_i,"cannot configure multiple combinations of real coeficients cx coeficients and filterProps simultaniously");
			throw CF::PropertySet::InvalidConfiguration("cannot configure multiple combinations of real coeficients cx coeficients and filterProps simultaniously", configProperties);
		}
	}
	fastfilter_base::configure(configProperties);
}

//HERE ARE all the filter callbacks

void fastfilter_i::fftSizeChanged(const std::string& id)
{
	boost::mutex::scoped_lock lock(filterLock_);
	if (!filters_.empty())
	{
		size_t maxNumTaps=0;
		for (map_type::iterator i = filters_.begin(); i!=filters_.end(); i++)
		{
			if (i->second.filter->getNumTaps()> maxNumTaps)
				maxNumTaps=i->second.filter->getNumTaps();
		}
		validateFftSize(maxNumTaps);
		for (map_type::iterator i = filters_.begin(); i!=filters_.end(); i++)
			i->second.filter->setFftSize(fftSize);
	}
}

void fastfilter_i::realFilterCoefficientsChanged(const std::string& id)
{
	//user manually configured the taps with an externally designed filter - set the boolean and update the filter flags
	boost::mutex::scoped_lock lock(filterLock_);
	if (!realFilterCoefficients.empty())
	{
		manualTaps_=true;
		complexFilterCoefficients.clear();
		if (!filters_.empty())
		{
			getManualTapsTemplate(realFilterCoefficients, realTaps_);
			for (map_type::iterator i = filters_.begin(); i!=filters_.end(); i++)
			{
				i->second.filter->setTaps(realTaps_);
			}
		}
	}
	else
	{
		LOG_WARN(fastfilter_i, "Ignoring empty configure for realFilterCoefficients -- to clear this setting configure complexFilterCoefficients or filterProps")
	}
}
void fastfilter_i::complexFilterCoefficientsChanged(const std::string& id)
{
	//user manually configured the taps with an externally designed filter - set the boolean and update the filter flags
	boost::mutex::scoped_lock lock(filterLock_);
	if (!complexFilterCoefficients.empty())
	{
		manualTaps_=true;
		realFilterCoefficients.clear();
		if ( !filters_.empty())
		{
			getManualTapsTemplate(complexFilterCoefficients, complexTaps_);
			for (map_type::iterator i = filters_.begin(); i!=filters_.end(); i++)
				i->second.filter->setTaps(complexTaps_);
		}
	}
}

void fastfilter_i::filterPropsChanged(const std::string& id)
{
	boost::mutex::scoped_lock lock(filterLock_);
	realFilterCoefficients.clear();
	complexFilterCoefficients.clear();
	correlationMode=false;
	manualTaps_=false;
	if (!filters_.empty())
	{
		if (filterProps.filterComplex)
		{
			for (map_type::iterator i = filters_.begin(); i!=filters_.end(); i++)
			{
				designTaps(complexTaps_, i->second.getSampleRate());
				i->second.filter->setTaps(complexTaps_);
			}
		}
		else
		{
			for (map_type::iterator i = filters_.begin(); i!=filters_.end(); i++)
			{
				designTaps(realTaps_, i->second.getSampleRate());
				i->second.filter->setTaps(realTaps_);
			}
		}
	}
}

void fastfilter_i::correlationModeChanged(const std::string& id)
{
	//user manually configured the taps with an externally designed filter - set the boolean and update the filter flags
	boost::mutex::scoped_lock lock(filterLock_);
	if (correlationMode)
		manualTaps_=true;
	bool real, complex;
	if (! filters_.empty())
	{
		getManualTaps(real,complex);
		if (real)
		{
			for (map_type::iterator i = filters_.begin(); i!=filters_.end(); i++)
				i->second.filter->setTaps(realTaps_);
		} else if (complex)
		{
			for (map_type::iterator i = filters_.begin(); i!=filters_.end(); i++)
				i->second.filter->setTaps(complexTaps_);
		}
	}
}

void fastfilter_i::getManualTaps(bool& doReal, bool& doComplex)
{
	if (!realFilterCoefficients.empty())
	{
		getManualTapsTemplate(realFilterCoefficients, realTaps_);
		doReal=true;
		doComplex=false;
	}
	else if(!complexFilterCoefficients.empty())
	{
		getManualTapsTemplate(complexFilterCoefficients, complexTaps_);
		doReal=false;
		doComplex=true;
	}
	else
	{
		doReal=false;
		doComplex=false;
		LOG_ERROR(fastfilter_i, "manual mode but no real or complex coeficients - no impulse response so we are done here");
	}
}

template<typename T, typename U>
void fastfilter_i::getManualTapsTemplate(T& in, U& out)
{
	validateFftSize(in.size());
	if (correlationMode)
	{
		//reverse the taps here
		LOG_DEBUG(fastfilter_i, "doing correlationMode - swapping taps!");
		out.assign(in.rbegin(), in.rend());
	}
	else
		out.assign(in.begin(), in.end());
}

void fastfilter_i::validateFftSize(size_t numTaps)
{
	if (2*(numTaps-1)>fftSize)
	{
		LOG_WARN(fastfilter_i, "Increasing fftSize because you configured with manual taps > fftSize!");
		while (2*(numTaps-1)>fftSize)
			fftSize*=2;
	}
}

template<typename T>
void fastfilter_i::designTaps(T& taps, float sampleRate)
{

	//design the filter according to the filterProps specifications and set the output in the filterCoefficients property
	FIRFilter::filter_type type;
	if (filterProps.Type=="lowpass")
		type = FIRFilter::lowpass;
	else if (filterProps.Type=="highpass")
		type = FIRFilter::highpass;
	else if (filterProps.Type=="bandpass")
		type = FIRFilter::bandpass;
	else if (filterProps.Type=="bandstop")
		type = FIRFilter::bandstop;
	else
	{
		LOG_ERROR(fastfilter_i, "filter type "<<filterProps.Type<<" not suported");
		return;
	}
	//we can only design the filter if we have a valid sampling rate
	//use the interal filter designer to calculate the taps
	size_t fftSizeInt(static_cast<size_t>(fftSize));
	size_t minTaps = std::max(fftSizeInt/16,size_t(10));
	size_t maxTaps = getMaxTapsSize(fftSizeInt);

	std::vector<typename T::value_type> tmp;
	filterdesigner_.wdfirHz(tmp,type,filterProps.Ripple, filterProps.TransitionWidth, filterProps.freq1, filterProps.freq2, sampleRate,minTaps,maxTaps);
	taps.assign(tmp.begin(), tmp.end());
}

