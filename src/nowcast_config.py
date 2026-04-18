"""Nowcasting panel configuration for US and Japan."""

DEFAULT_ESTIMATION_START = "2006-01-01"

NOWCAST_US = {
    "target": {
        "code": "s111ngpc@g10",
        "label": "GDP Growth",
        "transform": "qoqar",
        "frequency": "Q",
    },
    "indicators": [
        {"code": "s111d@g10",    "label": "Industrial Production",     "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "s111trs@g10",  "label": "Retail Sales",              "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "s111ts@g10",   "label": "Manufacturing Shipments",   "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "cbm@usecon",   "label": "Personal Consumption",      "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "s111cvrt@g10", "label": "Light Vehicle Sales",       "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "s111elrc@g10", "label": "Insured Unemployment Rate", "transform": "level",  "release_day": 10, "in_model": True},
        {"code": "s111vm@g10",   "label": "ISM Manufacturing PMI",     "transform": "level",  "release_day": 1,  "in_model": True},
        {"code": "s111vcc@g10",  "label": "Consumer Confidence",       "transform": "level",  "release_day": 25, "in_model": True},
    ],
}

NOWCAST_JAPAN = {
    "target": {
        "code": "jsngpcp@japan",
        "label": "GDP Growth",
        "transform": "qoqar",
        "frequency": "Q",
        "pre_transformed": True,
    },
    "indicators": [
        {"code": "jpsiip@japan",  "label": "Industrial Production",    "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "h158trs@g10",   "label": "Retail Sales",             "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "omnn2@japan",   "label": "Machinery Orders",         "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "jpsivx@japan",  "label": "Real Exports",             "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "s158ele@g10",   "label": "Total Employment",         "transform": "3m3mar", "release_day": 15, "in_model": True},
        {"code": "h158vcc@g10",   "label": "Consumer Confidence",      "transform": "level",  "release_day": 25, "in_model": True},
        {"code": "m158m@mktpmi",  "label": "Markit Manufacturing PMI", "transform": "level",  "release_day": 1,  "in_model": True},
        {"code": "m158s@mktpmi",  "label": "Markit Services PMI",      "transform": "level",  "release_day": 1,  "in_model": True},
    ],
}

NOWCAST_COUNTRIES = {
    "US": NOWCAST_US,
    "Japan": NOWCAST_JAPAN,
}
