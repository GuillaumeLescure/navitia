# Copyright (c) 2001-2017, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io
from __future__ import absolute_import, print_function, unicode_literals, division
import pytest

from jormungandr.tests.utils_test import MockResponse
from tests.check_utils import get_not_null, s_coord, r_coord
from tests.tests_mechanism import dataset, NewDefaultScenarioAbstractTestFixture

MOCKED_INSTANCE_CONF = {
    'scenario': 'new_default',
    'instance_config': {
        'ridesharing': [
            {
                "args": {
                    "service_url": "http://wtf",
                    "api_key": "key",
                    "network": "Super Covoit",
                    "rating_scale_min": 0,
                    "rating_scale_max": 5
                },
                "modes": [
                    "ridesharing"
                ],
                "class": "jormungandr.scenarios.ridesharing.instant_system.InstantSystem"
            }
        ]
    }
}

INSTANCE_SYSTEM_RESPONSE = {
    "total": 1,
    "journeys": [
        {
            "id": "4bcd0b9d-2c9d-42a2-8ffb-4508c952f4fb",
            "departureDate": "2017-12-25T08:07:59+01:00",
            "arrivalDate": "2017-12-25T08:25:36+01:00",
            "duration": 55,
            "distance": 300,
            "url": "https://jky8k.app.goo.gl/?efr=1&apn=com.is.android.rennes&ibi=&isi=&utm_campaign=KISIO&link=https%3A%2F%2Fwww.star.fr%2Fsearch%2F%3FfeatureName%3DsearchResultDetail%26networkId%3D33%26journeyId%3D4bcd0b9d-2c9d-42a2-8ffb-4508c952f4fb",
            "paths": [
                {
                    "mode": "RIDESHARINGAD",
                    "from": {
                        "name": "",
                        "lat": 52.4999825,
                        "lon": 13.399965
                    },
                    "to": {
                        "name": "",
                        "lat": 52.49879,
                        "lon": 13.45107
                    },
                    "departureDate": "2017-12-25T08:07:59+01:00",
                    "arrivalDate": "2017-12-25T08:25:36+01:00",
                    "shape": "wosdH|ihIRVDTFDzBjPNhADJ\\`C?TJt@Hj@h@tDp@bFR?bAFRBZDR@JCL@~AJl@Df@DfBNv@B~@DjAFh@HXH~@VbEfANDh@PdAl@\\RdAZnBHpADvBDf@@d@Gv@S\\OlAOl@EbAHjAVNDd@Dd@Mt@u@FGrE{EtBaBr@zCp@dDd@~BRtAHj@X`BFXlAjDLd@v@dDXlAh@TVl@hBtIB`ANpAh@nBf@xATf@Xd@JFPD@JHRLBLKDBbCbBbBbBjApA?VHPPBL`@\\^|BrBDHJ`@AP?PDRFL\\TRAJGRD`Al@jBhA~BbBx@VfALl@PHVDHPFNCVNdCnBpHzDdB|AfAjAj@h@^d@jAhBhAvA?^BNFJPHPCFGVNpBhApBt@ZL|B^dCJfDAZFLRHBNEJQZIdUa@b@JJ`@TXTFTAPKNUH]nBGtOb@vDd@`C`ArAp@zAjAnBnBJJh@h@`_@l`@fIvIfMhNl@t@dAzBnAnDx@xDh@jFfBbRdAnMdBnSjB|JbDbIhMj[rN`_@nEfJzCxDrCtDl@pBDtE^Bn@?h@?t@IdAe@XUFIvBaBvBaBf@Wl@OdAEfAJJXJHJBLCbAbAx@j@fBn@p@X`HfDdAd@NB\\CBLJDFCBI?OGILYn@gDb@uAVe@\\_@jEgDlFgARElBa@|G}AxFwA`AWv@YNI~AaArAg@bEw@pA[t@Y`B{@~BmAtAo@fAk@TYBBH?DGBKTEd@U^QlBcA^QvEcCP@Le@Cm@Eo@Ia@AI",
                    "rideSharingAd": {
                        "id": "24bab9de-653c-4cc4-a947-389c59cf0423",
                        "type": "DRIVER",
                        "from": {
                            "name": "9 Allee Rochester, Rennes",
                            "lat": 52.4999525,
                            "lon": 13.399985
                        },
                        "to": {
                            "name": "2 Avenue Alphonse Legault, Bruz",
                            "lat": 52.4988,
                            "lon": 13.4511
                        },
                        "user": {
                            "alias": "Jean P.",
                            "gender": "MALE",
                            "imageUrl": "https://dummyimage.com/128x128/C8E6C9/000.png&text=JP",
                            "rating": {
                                "rate": 0,
                                "count": 0
                            }
                        },
                        "price": {
                            "amount": 170,
                            "currency": "EUR"
                        },
                        "vehicle": {
                            "availableSeats": 4
                        }
                    }
                }
            ]
        }
    ],
    "url": "https://jky8k.app.goo.gl/?efr=1&apn=com.is.android.rennes&ibi=&isi=&utm_campaign=KISIO&link=https%3A%2F%2Fwww.star.fr%2Fsearch%2F%3FfeatureName%3DsearchResults%26networkId%3D33%26from%3D48.109377%252C-1.682103%26to%3D48.020335%252C-1.743929%26multimodal%3Dfalse%26departureDate%3D2017-12-25T08%253A00%253A00%252B01%253A00"
}

QUERY_DATETIME_STR = "20120614T070000"


def mock_instance_system(_, params):
    return MockResponse(INSTANCE_SYSTEM_RESPONSE, 200)


@pytest.fixture(scope="function", autouse=True)
def mock_http_instance_system(monkeypatch):
    monkeypatch.setattr('jormungandr.scenarios.ridesharing.instant_system.InstantSystem._call_service',
                        mock_instance_system)


@dataset({'main_routing_test': MOCKED_INSTANCE_CONF})
class TestInstanceSystem(NewDefaultScenarioAbstractTestFixture):
    """
    Integration test with Instace System
    """

    def test_basic_ride_sharing(self):
        """
        test ridesharing_jouneys details
        """
        q = "journeys?from=0.0000898312;0.0000898312&to=0.00188646;0.00071865&datetime=20120614T075500&"\
            "first_section_mode[]={first}&last_section_mode[]={last}&debug=true"\
            .format(first='ridesharing', last='walking')
        response = self.query_region(q)
        self.is_valid_journey_response(response, q, check_journey_links=False)

        journeys = get_not_null(response, 'journeys')
        assert len(journeys) == 3
        tickets = response.get('tickets')
        assert len(tickets) == 1
        assert tickets[0].get('cost').get('currency') == 'centime'
        assert tickets[0].get('cost').get('value') == '170.0'
        ticket_id = tickets[0].get('id')

        walking_direct = journeys[0]
        assert 'walking' in walking_direct['tags']
        assert walking_direct.get('type') == 'best'

        walking_direct = journeys[1]
        assert 'walking' in walking_direct['tags']
        assert walking_direct.get('type') == 'fastest'

        ridesharing = journeys[2]
        assert 'ridesharing' in ridesharing['tags']
        assert 'ecologic' in ridesharing['tags']
        assert ridesharing.get('type') == 'rapid'

        distances = ridesharing.get('distances')
        assert distances.get('ridesharing') == 211
        assert distances.get('car') == 0
        assert distances.get('walking') == 0

        durations = ridesharing.get('durations')
        assert durations.get('ridesharing') == 926
        assert durations.get('total') == 926

        rs_sections = ridesharing.get('sections')
        assert len(rs_sections) == 1
        assert rs_sections[0].get('mode') == 'ridesharing'
        assert rs_sections[0].get('type') == 'crow_fly'

        rs_journeys = rs_sections[0].get('ridesharing_journeys')
        assert len(rs_journeys) == 1
        assert 'ridesharing' in rs_journeys[0].get('tags')
        rsj_sections = rs_journeys[0].get('sections')
        assert len(rsj_sections) == 3

        assert rsj_sections[0].get('type') == 'crow_fly'
        assert rsj_sections[0].get('mode') == 'walking'

        assert rsj_sections[1].get('type') == 'ridesharing'
        rsj_info = rsj_sections[1].get('ridesharing_informations')
        assert rsj_info.get('driver').get('alias') == 'Jean P.'
        assert rsj_info.get('driver').get('gender') == 'male'
        assert rsj_info.get('driver').get('image') == 'https://dummyimage.com/128x128/C8E6C9/000.png&text=JP'
        assert rsj_info.get('driver').get('rating').get('scale_min') == 0.0
        assert rsj_info.get('driver').get('rating').get('scale_max') == 5.0
        assert rsj_info.get('network') == 'Super Covoit'
        assert rsj_info.get('operator') == 'Instant System'
        assert rsj_info.get('seats').get('available') == 4
        assert rsj_info.get('seats').get('total') == 4

        rsj_links = rsj_sections[1].get('links')
        assert len(rsj_links) == 2
        assert rsj_links[0].get('rel') == 'ridesharing_ad'
        assert rsj_links[0].get('type') == 'ridesharing_ad'

        assert rsj_links[1].get('rel') == 'tickets'
        assert rsj_links[1].get('type') == 'ticket'
        assert rsj_links[1].get('id') == ticket_id

        assert rsj_sections[2].get('type') == 'crow_fly'
        assert rsj_sections[2].get('mode') == 'walking'
