#ifndef FASTFILTER_IMPL_H
#define FASTFILTER_IMPL_H

#include "fastfilter_base.h"
#include "firfilter.h"

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
        void filterChanged(const std::string& id);

};

#endif
