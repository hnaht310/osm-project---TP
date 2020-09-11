import re
import audit
import pprint

richardson_sample = "r_sample.osm"
richardson = "richardson.osm"


mapping = { "Rd" : "Road",
            "St" : "Street",
            "Ct" : "Court",
            "Dr" : "Drive",
            "Hwy": "Highway",
            "Blvd" : "Boulevard",
            "North Garland Avenue (Spring Creek Way)" : "North Garland Avenue",
            "Goldmark" : "Goldmark Drive",
            "Cedar Sage" : "Cedar Sage Drive",
           }


def update_name(name, mapping):
    for x, y in mapping.items():
        if name.endswith(x):
            name = name.replace(x,y)
        else:
            name = name
    return name


def improve_street_name():
    st_types = audit.audit(richardson_sample)[0]
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            print(name, "=>", better_name)
#print(update_name(street_types, mapping ))


if __name__ == "__main__":
    improve_street_name()
