#ifndef FASTFILTER_IMPL_H
#define FASTFILTER_IMPL_H

#include "fastfilter_base.h"
#include "firfilter.h"
#include "FirFilterDesigner.h"
#include <boost/thread/mutex.hpp>

class fastfilter_i;

class fastfilter_i : public fastfilter_base
{
    ENABLE_LOGGING
    public:
        fastfilter_i(const char *uuid, const char *label);
        ~fastfilter_i();
        int serviceFunction();

    private:

        firfilter::realVector realIn;
        firfilter::complexVector complexIn;
        firfilter::realVector realOut;
        firfilter::complexVector complexOut;

        firfilter::realVector complexOutAsReal;
        firfilter filter_;

        //internal helper function
        void cxOutputToReal();
        void fftSizeChanged(const std::string& id);
        void filterCoefficientsChanged(const std::string& id);
        void filterComplexChanged(const std::string& id);
        void filterPropsChanged(const std::string& id);
        FirFilterDesigner filterdesigner_;
        float fs_;
        bool manualTaps_;
        std::string streamID_;
        bool updateFFT_;
        bool updateFilter_;
        boost::mutex filterDesignLock_;
};

#endif
