#ifndef STRUCTPROPS_H
#define STRUCTPROPS_H

/*******************************************************************************************

    AUTO-GENERATED CODE. DO NOT MODIFY

*******************************************************************************************/

#include <ossie/CorbaUtils.h>
#include <ossie/PropertyInterface.h>

struct filterProps_struct {
    filterProps_struct ()
    {
        TransitionWidth = 800;
        Ripple = 0.01;
        freq1 = 1000;
        freq2 = 2000;
    };

    static std::string getId() {
        return std::string("filterProps");
    };

    double TransitionWidth;
    std::string Type;
    double Ripple;
    double freq1;
    double freq2;
};

inline bool operator>>= (const CORBA::Any& a, filterProps_struct& s) {
    CF::Properties* temp;
    if (!(a >>= temp)) return false;
    CF::Properties& props = *temp;
    for (unsigned int idx = 0; idx < props.length(); idx++) {
        if (!strcmp("TransitionWidth", props[idx].id)) {
            if (!(props[idx].value >>= s.TransitionWidth)) return false;
        }
        if (!strcmp("Type", props[idx].id)) {
            if (!(props[idx].value >>= s.Type)) return false;
        }
        if (!strcmp("Ripple", props[idx].id)) {
            if (!(props[idx].value >>= s.Ripple)) return false;
        }
        if (!strcmp("freq1", props[idx].id)) {
            if (!(props[idx].value >>= s.freq1)) return false;
        }
        if (!strcmp("freq2", props[idx].id)) {
            if (!(props[idx].value >>= s.freq2)) return false;
        }
    }
    return true;
};

inline void operator<<= (CORBA::Any& a, const filterProps_struct& s) {
    CF::Properties props;
    props.length(5);
    props[0].id = CORBA::string_dup("TransitionWidth");
    props[0].value <<= s.TransitionWidth;
    props[1].id = CORBA::string_dup("Type");
    props[1].value <<= s.Type;
    props[2].id = CORBA::string_dup("Ripple");
    props[2].value <<= s.Ripple;
    props[3].id = CORBA::string_dup("freq1");
    props[3].value <<= s.freq1;
    props[4].id = CORBA::string_dup("freq2");
    props[4].value <<= s.freq2;
    a <<= props;
};

inline bool operator== (const filterProps_struct& s1, const filterProps_struct& s2) {
    if (s1.TransitionWidth!=s2.TransitionWidth)
        return false;
    if (s1.Type!=s2.Type)
        return false;
    if (s1.Ripple!=s2.Ripple)
        return false;
    if (s1.freq1!=s2.freq1)
        return false;
    if (s1.freq2!=s2.freq2)
        return false;
    return true;
};

inline bool operator!= (const filterProps_struct& s1, const filterProps_struct& s2) {
    return !(s1==s2);
};

template<> inline short StructProperty<filterProps_struct>::compare (const CORBA::Any& a) {
    if (super::isNil_) {
        if (a.type()->kind() == (CORBA::tk_null)) {
            return 0;
        }
        return 1;
    }

    filterProps_struct tmp;
    if (fromAny(a, tmp)) {
        if (tmp != this->value_) {
            return 1;
        }

        return 0;
    } else {
        return 1;
    }
}


#endif
