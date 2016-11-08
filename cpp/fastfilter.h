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
#ifndef FASTFILTER_IMPL_H
#define FASTFILTER_IMPL_H

#include "fastfilter_base.h"
#include "firfilter.h"
#include "FirFilterDesigner.h"
#include <boost/thread/mutex.hpp>

class fastfilter_i;

class FilterWrapper
{
	public:
		FilterWrapper() :
			filter(NULL),
			fs_(1.0)
		{
		}
		~FilterWrapper()
		{
			if (filter!=NULL)
				delete filter;
		}
		void setParams(float sampleRate, firfilter* filter)
		{
			this->filter =filter;
			fs_ = sampleRate;
		}
		bool hasSampleRateChanged(float sampleRate)
		{
			bool ret(false);
			if (fs_ != sampleRate)
			{
				ret=true;
				fs_=sampleRate;
			}
			return ret;
		}
		float getSampleRate()
		{
			return fs_;
		}
		firfilter* filter;
	private:
		float fs_;
};

class fastfilter_i : public fastfilter_base
{
    ENABLE_LOGGING
    public:
        fastfilter_i(const char *uuid, const char *label);
        ~fastfilter_i();
        int serviceFunction();

        void configure (const CF::Properties& configProperties)
            throw (CF::PropertySet::PartialConfiguration,
                   CF::PropertySet::InvalidConfiguration, CORBA::SystemException);

    private:

        typedef std::map<std::string, FilterWrapper> map_type;
   		map_type filters_;

        firfilter::realVector realOut;
        firfilter::complexVector complexOut;

        void complexFilterCoefficientsChanged(const std::vector<std::complex<float> > *oldValue, const std::vector<std::complex<float> > *newValue);
        void correlationModeChanged(const bool *oldValue, const bool *newValue);
        void filterPropsChanged(const filterProps_struct *oldValue, const filterProps_struct *newValue);
        void fftSizeChanged(const CORBA::ULong *oldValue, const CORBA::ULong *newValue);
        void realFilterCoefficientsChanged(const std::vector<float> *oldValue, const std::vector<float> *newValue);

        void getManualTaps(bool& doReal, bool& doComplex);
        template<typename T, typename U>
        void getManualTapsTemplate(T& in, U& out);
        template<typename T>
        void designTaps(T& taps, float sampleRate);
        void validateFftSize(size_t numTaps);

        FirFilterDesigner filterdesigner_;
        bool manualTaps_;

        RealFFTWVector realTaps_;
        ComplexFFTWVector complexTaps_;

        boost::mutex filterLock_;
};

#endif
