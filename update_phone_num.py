import re
import audit
import pprint

#phone_num = '+1-972 761 0550'
richardson_sample = "r_sample.osm"
richardson = "richardson.osm"


def update_num(num):
    pattern = re.compile(r'\D+') # matches one or more characters that are not digits
    n = re.sub(pattern, "", num) # replace all non-digit characters with an empty string.
    good_num = '+{}-{}-{}-{}'.format(n[0], n[1:4], n[4:7], n[7:])
    return good_num

#print(update_num(phone_num))


def improve_phone():
    p_types = audit.audit(richardson_sample)[1]
    #print(p_types)
    for p in p_types:
        better_p = update_num(p)
        print(p, "=>", better_p)



if __name__ == "__main__":
  improve_phone()
