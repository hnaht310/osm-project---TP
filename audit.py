import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re


# https://wiki.openstreetmap.org/wiki/Key:phone
# phone=+<country code>-<area code>-<local number>, following the RFC 3966/NANP pattern
richardson_sample = "r_sample.osm"
richardson = "richardson.osm"

# Check phone numbers:

phone_re = re.compile(r'^\+1\-\d{3}\-\d{3}\-\d{4}$')


def audit_phone_num(phone_types, num):
    good_format = phone_re.search(num)
    if not good_format:
        phone_types.add(num)
    #else:
        #print("good one: ", num)


def is_phone_num(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "phone")



# Check street types:

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "Expressway", "Freeway", "Highway", "Row"]



def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print("%s: %d" % (k, v))

def is_street_name(elem):
    return ((elem.tag == "tag") and (elem.attrib['k'] == "addr:street"))


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    phone_types = set()
    for event, elem in ET.iterparse(osm_file):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone_num(tag):
                    audit_phone_num(phone_types, tag.attrib['v'])
                if is_street_name(tag):
                    #print(tag.attrib['v'])
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return (street_types, phone_types)

pprint.pprint(audit(richardson_sample))
