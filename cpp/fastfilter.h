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

        void fftSizeChanged(const std::string& id);
        void realFilterCoefficientsChanged(const std::string& id);
        void complexFilterCoefficientsChanged(const std::string& id);
        void filterPropsChanged(const std::string& id);
        void correlationModeChanged(const std::string& id);

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
