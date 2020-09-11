import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema
import update_phone_num
import update_street_type

OSM_PATH = "richardson.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def update_tag(tag):
    if tag['key'] == "street":
        tag['value'] = update_street_type.update_name(tag['value'], update_street_type.mapping)
    elif tag['key'] == "phone":
        tag['value'] = update_phone_num.update_num(tag['value'])


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        for node_field in NODE_FIELDS:
            node_attribs[node_field] = element.attrib[node_field]
        node_attribs['id'] = int(node_attribs['id'])
        node_attribs['lat'] = float(node_attribs['lat'])
        node_attribs['lon'] = float(node_attribs['lon'])
        node_attribs['uid'] = int(node_attribs['uid'])
        node_attribs['changeset'] = int(node_attribs['changeset'])

        for node_tag in element.iter("tag"):
            node_tag_dict = {}
            # print(node_tag.attrib['k'])
            # print(node_tag.attrib['v'])
            # print(node_tag.attrib)
            problem = re.match(PROBLEMCHARS, node_tag.attrib['k'])
            colon = re.match(LOWER_COLON, node_tag.attrib['k'])
            if problem:
                continue  # ignore
            elif colon:
                node_tag_dict['id'] = int(element.attrib['id'])
                node_tag_dict['key'] = node_tag.attrib['k'].split(":", 1)[1]  # using max split to get key after colon
                node_tag_dict['value'] = node_tag.attrib['v']
                node_tag_dict['type'] = node_tag.attrib['k'].split(":", 1)[
                    0]  # using max split to get type before colon
                # print(node_tag_dict['value'])
                update_tag(node_tag_dict)
                tags.append(node_tag_dict)

            else:
                node_tag_dict['id'] = int(element.attrib['id'])
                node_tag_dict['key'] = node_tag.attrib['k']
                node_tag_dict['value'] = node_tag.attrib['v']
                node_tag_dict['type'] = 'regular'
                update_tag(node_tag_dict)
                tags.append(node_tag_dict)

        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for way_field in WAY_FIELDS:
            way_attribs[way_field] = element.attrib[way_field]
        way_attribs['id'] = int(way_attribs['id'])
        way_attribs['uid'] = int(way_attribs['uid'])
        way_attribs['changeset'] = int(way_attribs['changeset'])

        count = 0
        for way_node in element.iter('nd'):
            way_node_dict = {}
            way_node_dict['id'] = int(element.attrib['id'])
            way_node_dict['node_id'] = int(way_node.attrib['ref'])
            way_node_dict['position'] = count
            count += 1
            way_nodes.append(way_node_dict)

        for way_tag in element.iter("tag"):
            way_tag_dict = {}
            #print(way_tag.attrib['k'])
            # print(way_tag.attrib['v'])
            # print(element.attrib['id'])
            problem = re.match(PROBLEMCHARS, way_tag.attrib['k'])
            colon = re.match(LOWER_COLON, way_tag.attrib['k'])
            if problem:
                continue
            elif colon:
                way_tag_dict['id'] = int(element.attrib['id'])
                way_tag_dict['key'] = way_tag.attrib['k'].split(":", 1)[1]
                way_tag_dict['type'] = way_tag.attrib['k'].split(":", 1)[0]
                way_tag_dict['value'] = way_tag.attrib['v']
                update_tag(way_tag_dict)
                tags.append(way_tag_dict)

            else:
                way_tag_dict['id'] = int(element.attrib['id'])
                way_tag_dict['key'] = way_tag.attrib['k']
                way_tag_dict['type'] = "regular"
                way_tag_dict['value'] = way_tag.attrib['v']
                update_tag(way_tag_dict)
                tags.append(way_tag_dict)

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

    # ================================================== #


#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(iter(validator.errors.items()))
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))

'''
class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, str) else v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
'''
class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, bytes) else v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)

