/* Copyright © 2001-2014, Canal TP and/or its affiliates. All rights reserved.
  
This file is part of Navitia,
    the software to build cool stuff with public transport.
 
Hope you'll enjoy and contribute to this project,
    powered by Canal TP (www.canaltp.fr).
Help us simplify mobility and open public transport:
    a non ending quest to the responsive locomotion way of traveling!
  
LICENCE: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
   
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.
   
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
  
Stay tuned using
twitter @navitia 
IRC #navitia on freenode
https://groups.google.com/d/forum/navitia
www.navitia.io
*/

#pragma once
#include "type/pt_data.h"
#include "type/datetime.h"
#include "routing/raptor_utils.h"
#include "routing/idx_map.h"

#include <boost/foreach.hpp>
#include <boost/dynamic_bitset.hpp>
namespace navitia { namespace routing {

/** Données statiques qui ne sont pas modifiées pendant le calcul */
struct dataRAPTOR {

    // cache friendly access to the connections
    struct Connections {
        struct Connection {
            DateTime duration;
            SpIdx sp_idx;
        };
        inline const std::vector<Connection>& get_forward(const SpIdx& sp) const {
            return forward_connections[sp];
        }
        inline const std::vector<Connection>& get_backward(const SpIdx& sp) const {
            return backward_connections[sp];
        }
        void load(const navitia::type::PT_Data &data);

    private:
        // for a stop point, get the corresponding forward connections
        IdxMap<type::StopPoint, std::vector<Connection>> forward_connections;
        // for a stop point, get the corresponding backward connections
        IdxMap<type::StopPoint, std::vector<Connection>> backward_connections;
    };
    Connections connections;

    // cache friendly access to JourneyPatternPoints from a StopPoint
    struct JppsFromSp {
        // compressed JourneyPatternPoint
        struct Jpp {
            JppIdx idx; // index
            JpIdx jp_idx; // corresponding JourneyPattern index
            int order; // order of the jpp in its jp
        };
        inline const std::vector<Jpp>& operator[](const SpIdx& sp) const {
            return jpps_from_sp[sp];
        }
        void load(const navitia::type::PT_Data &data);
        void filter_jpps(const boost::dynamic_bitset<>& valid_jpps);

    private:
        IdxMap<type::StopPoint, std::vector<Jpp>> jpps_from_sp;
    };
    JppsFromSp jpps_from_sp;

    // cache friendly access to in order JourneyPatternPoints from a JourneyPattern
    struct JppsFromJp {
        // compressed JourneyPatternPoint
        struct Jpp {
            JppIdx idx;
            SpIdx sp_idx;
            uint16_t order;
            bool has_freq;
        };
        inline const std::vector<Jpp>& operator[](const JpIdx& jp) const {
            return jpps_from_jp[jp];
        }
        void load(const navitia::type::PT_Data &data);
    private:
        IdxMap<type::JourneyPattern, std::vector<Jpp>> jpps_from_jp;
    };
    JppsFromJp jpps_from_jp;

    struct BestStopTimeData {
        void load(const navitia::type::PT_Data &data);
        bool empty() const { return departure_times.empty(); }
        size_t nb_stop_times() const { return departure_times.size(); }

        // Returns the range of the stop times in increasing departure
        // time order
        boost::iterator_range<std::vector<const type::StopTime*>::const_iterator>
        stop_time_range_forward(const JpIdx jp_idx, const uint16_t jpp_order) const {
            const auto r = stop_time_idx_range(jp_idx, jpp_order);
            return boost::make_iterator_range(st_forward.begin() + r.first,
                                              st_forward.begin() + r.second);
        }
        // Returns the range of the stop times in decreasing arrival
        // time order
        boost::iterator_range<std::vector<const type::StopTime*>::const_iterator>
        stop_time_range_backward(const JpIdx jp_idx, const uint16_t jpp_order) const {
            const auto r = stop_time_idx_range(jp_idx, jpp_order);
            return boost::make_iterator_range(st_backward.begin() + r.first,
                                              st_backward.begin() + r.second);
        }
        // Returns the range of the stop times in increasing departure
        // time order begining after hour(dt)
        boost::iterator_range<std::vector<const type::StopTime*>::const_iterator>
        stop_time_range_after(const JpIdx jp_idx, const uint16_t jpp_order, const DateTime dt) const {
            const auto idx_range = stop_time_idx_range(jp_idx, jpp_order);
            const auto begin = departure_times.begin();
            const auto it = std::lower_bound(begin + idx_range.first, begin + idx_range.second,
                                             DateTimeUtils::hour(dt), std::less<DateTime>());

            const type::idx_t idx = it - begin;
            const type::idx_t end = idx_range.second;
            return boost::make_iterator_range(st_forward.begin() + idx, st_forward.begin() + end);
        }
        // Returns the range of the stop times in decreasing arrival
        // time order ending before hour(dt)
        boost::iterator_range<std::vector<const type::StopTime*>::const_iterator>
        stop_time_range_before(const JpIdx jp_idx, const uint16_t jpp_order, const DateTime dt) const {
            const auto idx_range = stop_time_idx_range(jp_idx, jpp_order);
            const auto begin = arrival_times.begin();
            const auto it = std::lower_bound(begin + idx_range.first, begin + idx_range.second,
                                             DateTimeUtils::hour(dt), std::greater<DateTime>());

            const type::idx_t idx = it - begin;
            const type::idx_t end = idx_range.second;
            return boost::make_iterator_range(st_backward.begin() + idx, st_backward.begin() + end);
        }
    private:
        std::pair<type::idx_t, type::idx_t>
        stop_time_idx_range(const JpIdx jp_idx, const uint16_t jpp_order) const {
            const type::idx_t begin = first_stop_time[jp_idx] + jpp_order * nb_trips[jp_idx];
            const type::idx_t end = begin + nb_trips[jp_idx];
            return std::make_pair(begin, end);
        }

        // arrival_times (resp. departure_times) are the different arrival
        // (resp. departure) times of each stop time sorted by
        //     lex(jp, jpp, arrival_time (resp. departure_time)).
        //
        // Then, you have:
        //     for all i, st_forward[i]->departure_time == departure_times[i]
        //     for all i, st_backward[i]->arrival_time == arrival_times[i]
        //
        // st_forward and st_backward contains StopTime* from
        // std::vector<StopTime> (in VehicleJourney).  This is safe as
        // pt_data MUST be const for a given dataRAPTOR (else, you'll have
        // much troubles, and not only from here).
        std::vector<DateTime> arrival_times;
        std::vector<DateTime> departure_times;
        std::vector<const type::StopTime*> st_forward;
        std::vector<const type::StopTime*> st_backward;

        // index of the first st of a jp in the previous vectors
        IdxMap<type::JourneyPattern, size_t> first_stop_time;

        // number of vj in an jp
        IdxMap<type::JourneyPattern, size_t> nb_trips;
    };
    BestStopTimeData best_stop_time_data;

    // blank labels, to fast init labels with a memcpy
    Labels labels_const;
    Labels labels_const_reverse;

    // jp_validity_patterns[date][jp_idx] == any(vj.validity_pattern->check2(date) for vj in jp)
    std::vector<boost::dynamic_bitset<> > jp_validity_patterns;

    // as jp_validity_patterns for the adapted ones
    std::vector<boost::dynamic_bitset<> > jp_adapted_validity_pattern;


    dataRAPTOR() {}
    void load(const navitia::type::PT_Data &data);
};

}}

