# Real HSL stops and routes used for local development when Digitransit is
# unreachable (USE_MOCK_SEED=true).  Coordinates are accurate.

MOCK_STOPS: list[dict] = [
    # --- Helsinki ---
    {"id": "HSL:1020453", "name": "Rautatientori", "code": "0017", "vehicle_type": 3, "platform_code": None, "zone_id": "A", "lat": 60.17064, "lon": 24.94146},
    {"id": "HSL:1173432", "name": "Kamppi", "code": "1278", "vehicle_type": 3, "platform_code": None, "zone_id": "A", "lat": 60.16866, "lon": 24.93219},
    {"id": "HSL:1285110", "name": "Pasila", "code": "1291", "vehicle_type": 2, "platform_code": None, "zone_id": "A", "lat": 60.19840, "lon": 24.93318},
    {"id": "HSL:1174101", "name": "Hakaniemi", "code": "1291", "vehicle_type": 3, "platform_code": None, "zone_id": "A", "lat": 60.17961, "lon": 24.95059},
    {"id": "HSL:1304130", "name": "Kallio", "code": "1234", "vehicle_type": 3, "platform_code": None, "zone_id": "A", "lat": 60.18308, "lon": 24.95024},
    {"id": "HSL:1150108", "name": "Töölö", "code": "1101", "vehicle_type": 0, "platform_code": None, "zone_id": "A", "lat": 60.17487, "lon": 24.92195},
    {"id": "HSL:1300116", "name": "Sörnäinen", "code": "1156", "vehicle_type": 1, "platform_code": None, "zone_id": "A", "lat": 60.18530, "lon": 24.96521},
    {"id": "HSL:1220410", "name": "Itäkeskus", "code": "2234", "vehicle_type": 1, "platform_code": None, "zone_id": "B", "lat": 60.21030, "lon": 25.07993},
    {"id": "HSL:1121482", "name": "Ruoholahti", "code": "1056", "vehicle_type": 1, "platform_code": None, "zone_id": "A", "lat": 60.16373, "lon": 24.91220},
    {"id": "HSL:1020452", "name": "Kaisaniemi", "code": "0018", "vehicle_type": 0, "platform_code": None, "zone_id": "A", "lat": 60.17165, "lon": 24.94530},
    # --- Espoo ---
    {"id": "HSL:2131252", "name": "Tapiola", "code": "2121", "vehicle_type": 1, "platform_code": None, "zone_id": "B", "lat": 60.17558, "lon": 24.80533},
    {"id": "HSL:2173261", "name": "Matinkylä", "code": "2173", "vehicle_type": 1, "platform_code": None, "zone_id": "B", "lat": 60.15889, "lon": 24.73935},
    {"id": "HSL:2115201", "name": "Leppävaara", "code": "2115", "vehicle_type": 2, "platform_code": None, "zone_id": "B", "lat": 60.21900, "lon": 24.81234},
    {"id": "HSL:2231611", "name": "Kivenlahti", "code": "2231", "vehicle_type": 1, "platform_code": None, "zone_id": "C", "lat": 60.14285, "lon": 24.69528},
    # --- Vantaa ---
    {"id": "HSL:4610212", "name": "Myyrmäki", "code": "4610", "vehicle_type": 2, "platform_code": None, "zone_id": "C", "lat": 60.26066, "lon": 24.85555},
    {"id": "HSL:4620201", "name": "Tikkurila", "code": "4620", "vehicle_type": 2, "platform_code": None, "zone_id": "C", "lat": 60.29278, "lon": 25.04417},
    {"id": "HSL:4750201", "name": "Aviapolis", "code": "4750", "vehicle_type": 2, "platform_code": None, "zone_id": "C", "lat": 60.31697, "lon": 24.96690},
]

MOCK_ROUTES: list[dict] = [
    # Trams
    {"id": "HSL:1001", "short_name": "1", "long_name": "Eira – Käpylä", "mode": "TRAM", "color": "00985f", "agency_name": "Helsingin kaupunkiliikenne"},
    {"id": "HSL:1007", "short_name": "7", "long_name": "Töölö – Pasila", "mode": "TRAM", "color": "00985f", "agency_name": "Helsingin kaupunkiliikenne"},
    {"id": "HSL:1009", "short_name": "9", "long_name": "Eira – Pasila", "mode": "TRAM", "color": "00985f", "agency_name": "Helsingin kaupunkiliikenne"},
    {"id": "HSL:1010", "short_name": "10", "long_name": "Pikku Huopalahti – Itäkeskus", "mode": "TRAM", "color": "00985f", "agency_name": "Helsingin kaupunkiliikenne"},
    # Metro
    {"id": "HSL:31M1", "short_name": "M1", "long_name": "Matinkylä – Vuosaari", "mode": "METRO", "color": "ff6319", "agency_name": "Helsingin kaupunkiliikenne"},
    {"id": "HSL:31M2", "short_name": "M2", "long_name": "Kivenlahti – Mellunmäki", "mode": "METRO", "color": "ff6319", "agency_name": "Helsingin kaupunkiliikenne"},
    # Rail (commuter)
    {"id": "HSL:3001H", "short_name": "H", "long_name": "Helsinki – Riihimäki", "mode": "RAIL", "color": "8c4799", "agency_name": "VR"},
    {"id": "HSL:3001I", "short_name": "I", "long_name": "Helsinki – Kerava", "mode": "RAIL", "color": "8c4799", "agency_name": "VR"},
    {"id": "HSL:3001P", "short_name": "P", "long_name": "Helsinki – Kerava – Lentoasema", "mode": "RAIL", "color": "8c4799", "agency_name": "VR"},
    # Buses
    {"id": "HSL:1016", "short_name": "16", "long_name": "Rautatientori – Kumpula", "mode": "BUS", "color": "0066cc", "agency_name": "Helsingin kaupunkiliikenne"},
    {"id": "HSL:1023N", "short_name": "23N", "long_name": "Rautatientori – Töölö (night)", "mode": "BUS", "color": "0066cc", "agency_name": "Helsingin kaupunkiliikenne"},
    {"id": "HSL:4560", "short_name": "560", "long_name": "Kamppi – Kivistö", "mode": "BUS", "color": "0066cc", "agency_name": "Nobina"},
    {"id": "HSL:4300", "short_name": "300", "long_name": "Kamppi – Leppävaara", "mode": "BUS", "color": "0066cc", "agency_name": "Nobina"},
]
