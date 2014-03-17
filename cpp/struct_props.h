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
#ifndef STRUCTPROPS_H
#define STRUCTPROPS_H

/*******************************************************************************************

    AUTO-GENERATED CODE. DO NOT MODIFY

*******************************************************************************************/
#include <ossie/CorbaUtils.h>

struct filterProps_struct {
    filterProps_struct ()
    {
        TransitionWidth = 800;
        Ripple = 0.01;
        freq1 = 1000;
        freq2 = 2000;
        filterComplex = false;
    };

    static std::string getId() {
        return std::string("filterProps");
    };

    double TransitionWidth;
    std::string Type;
    double Ripple;
    double freq1;
    double freq2;
    bool filterComplex;
};

inline bool operator>>= (const CORBA::Any& a, filterProps_struct& s) {
    CF::Properties* temp;
    if (!(a >>= temp)) return false;
    CF::Properties& props = *temp;
    for (unsigned int idx = 0; idx < props.length(); idx++) {
        if (!strcmp("TransitionWidth", props[idx].id)) {
            if (!(props[idx].value >>= s.TransitionWidth)) return false;
        }
        else if (!strcmp("Type", props[idx].id)) {
            if (!(props[idx].value >>= s.Type)) return false;
        }
        else if (!strcmp("Ripple", props[idx].id)) {
            if (!(props[idx].value >>= s.Ripple)) return false;
        }
        else if (!strcmp("freq1", props[idx].id)) {
            if (!(props[idx].value >>= s.freq1)) return false;
        }
        else if (!strcmp("freq2", props[idx].id)) {
            if (!(props[idx].value >>= s.freq2)) return false;
        }
        if (!strcmp("filterComplex", props[idx].id)) {
            if (!(props[idx].value >>= s.filterComplex)) return false;
        }
    }
    return true;
};

inline void operator<<= (CORBA::Any& a, const filterProps_struct& s) {
    CF::Properties props;
    props.length(6);
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
    props[5].id = CORBA::string_dup("filterComplex");
    props[5].value <<= s.filterComplex;
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
    if (s1.filterComplex!=s2.filterComplex)
        return false;
    return true;
};

inline bool operator!= (const filterProps_struct& s1, const filterProps_struct& s2) {
    return !(s1==s2);
};


#endif
