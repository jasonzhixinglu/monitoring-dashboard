CHINA = {
    "activity": [
        {"code": "h924d@emergepr",    "label": "Industrial Output (IP)",         "transform": "yoy"},
        {"code": "n924trs@emergepr",  "label": "Retail Sales",                   "transform": "yoy"},
        {"code": "n924vr@emergepr",   "label": "Fixed Asset Investment",          "transform": "yoy"},
        {"code": "n924vrrd@emergepr", "label": "Real Estate Investment",          "transform": "yoy", "in_pca": False},
        {"code": "h924ixd@emergepr",  "label": "Exports (USD, SA)",               "transform": "yoy"},
        {"code": "n924euru@emergepr", "label": "Urban Unemployment Rate",         "transform": "level"},
    ],
    "inflation": [
        {"code": "n924pcy@emergepr",  "label": "CPI Headline (YoY)",              "transform": "level"},
        {"code": "n924pcxg@emergepr", "label": "Core CPI ex-Food & Energy (YoY)", "transform": "level"},
        {"code": "n924pcyf@emergepr", "label": "CPI Food (YoY)",                  "transform": "level"},
        {"code": "n924pcs@emergepr",  "label": "CPI Services (YoY)",              "transform": "level"},
    ],
    "pmis": [
        {"code": "s924vm@emergepr",   "label": "NBS Manufacturing PMI",           "transform": "level"},
        {"code": "s924vng@emergepr",  "label": "NBS Non-manufacturing PMI",       "transform": "level"},
        {"code": "s924m@mktpmi",      "label": "Caixin Manufacturing PMI",        "transform": "level"},
        {"code": "s924s@mktpmi",      "label": "Caixin Services PMI",             "transform": "level"},
    ],
}

JAPAN = {
    "activity": [
        {"code": "jpsiip@japan",      "label": "Industrial Production (IP)",      "transform": "yoy"},
        {"code": "jpscaic@japan",     "label": "Real Consumption Activity",       "transform": "yoy"},
        {"code": "h158trs@g10",       "label": "Retail Sales",                    "transform": "yoy"},
        {"code": "jpsivx@japan",      "label": "Real Exports",                    "transform": "yoy"},
        {"code": "fluedr2@japan",     "label": "Unemployment Rate",               "transform": "level"},
        {"code": "jpewfra2@japan",    "label": "Real Wages",                      "transform": "yoy"},
    ],
    "inflation": [
        {"code": "jpcij@japan",       "label": "CPI Headline (YoY)",              "transform": "yoy"},
        {"code": "jpcije@japan",      "label": "CPI ex Fresh Food (YoY)",         "transform": "yoy"},
        {"code": "jpcijef@japan",     "label": "CPI ex Food & Energy (YoY)",      "transform": "yoy"},
        {"code": "jpnce@japan",       "label": "CPI Energy (YoY)",                "transform": "yoy"},
    ],
    "pmis": [
        {"code": "m158m@mktpmi",      "label": "Manufacturing PMI",               "transform": "level"},
        {"code": "m158s@mktpmi",      "label": "Services PMI",                    "transform": "level"},
        {"code": "m158mo@mktpmi",     "label": "Mfg New Orders PMI",              "transform": "level"},
        {"code": "m158mpi@mktpmi",    "label": "Mfg Input Prices PMI",            "transform": "level"},
    ],
}

COUNTRIES = {"China": CHINA, "Japan": JAPAN}
