# OpenStreetMap Data Case Study

## Map Area

The area selected for this project is Richardson, TX. Below is the link to download the data:
- https://overpass-api.de/api/map?bbox=-96.7708,32.9218,-96.6112,33.0064

I’m interested in this area because this is where I would like to move to within two years. I would like to see what the database would reveal about the city.

## Problems Encountered in the Map

After downloading the data from Openstreetmap (OSM) website, the <code>audit.py</code> file was run to see if there’s problems in the dataset. The following issues were found:
- Over-abbreviated street names such as "St", "Dr", "Blvd", "Rd", "Ct", and "Hwy". There are a few street names without street types such as "Goldmark" and "Cedar Sage". Google Maps shows the full street names with their street types as "Drive". 
- There is also a case where the street name include two streets: 'North Garland Avenue (Spring Creek Way)'. According to Google Maps, the house is located on North Garland Avenue near the intersection of North Garland Avenue and Spring Creek Way.
- There are phone numbers not in international format. According to <a href="https://wiki.openstreetmap.org/wiki/Key:phone" target="_blank">OpenStreetMap Wiki</a>, the correct pattern is 
+country code-area code-local number. Since the area chosen for this project is in the U.S, the country code would be +1. An example of a phone number with correct pattern is +1-201-555-0123. The output shows some phone numbers do not include hyphens, and some having area code in parentheses. A few examples of phone numbers that do not follow the correct format are: '+1 (972) 761-0550', +1 469 8996600', and +1972-238-3546.

## Data Cleaning 

In order to clean the street names, update_name function will be used. First, a dictionary called "mapping" was created with over-abbreviated street types and incorrect street names being keys, and corrected types being values.

```python
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
```

After <code>update_name()</code> function was written, <code>improve_name()</code> function was used to see whether <code>update_name()</code> worked on <code>r_sample</code>, a small sample of the dataset.
```python
def improve_street_name():
    st_types = audit.audit(richardson_sample)[0]
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            print(name, "=>", better_name)```
```{'Circle': {'Hillfawn Circle'},
 'Dr': {'Lakespur Dr', 'East CityLine Dr'},
 'Rd': {'Abrams Rd', '3301 N Shiloh Rd'},
 'Way': {'Lake Park Way'},
 'West': {'Executive Drive West'}}
Executive Drive West => Executive Drive West
Abrams Rd => Abrams Road
3301 N Shiloh Rd => 3301 N Shiloh Road
Lakespur Dr => Lakespur Drive
East CityLine Dr => East CityLine Drive
Lake Park Way => Lake Park Way
Hillfawn Circle => Hillfawn Circle```

Next step is to fix the problems with phone numbers. First, regular expressions were used to find any non-digit characters. All such characters, subsequently, were replaced with an empty string. Finally, <code>format()</code>function was used to standardize the phone numbers. 
```python
def update_num(num):
    pattern = re.compile(r'\D+') # matches one or more characters that are not digits
    n = re.sub(pattern, "", num) # replace all non-digit characters with an empty string.
    good_num = '+{}-{}-{}-{}'.format(n[0], n[1:4], n[4:7], n[7:])
    return good_num```

Likewise, <code>improve_phone()</code>was executed to confirm<code>update_num()</code>worked as expected.
```python
def improve_phone():
    p_types = audit.audit(richardson_sample)[1]
    for p in p_types:
        better_p = update_num(p)
        print(p, "=>", better_p)```
```
+1 469-204-1000 => +1-469-204-1000
+1 972-474-3221 => +1-972-474-3221
+1 972-234-3447 => +1-972-234-3447
+1 972-675-8600 => +1-972-675-8600
+1 972-907-9999 => +1-972-907-9999
+1 972-235-3338 => +1-972-235-3338
+1 972-495-1243 => +1-972-495-1243
+1 972 613 3589 => +1-972-613-3589```

After all the issues encountered during the auditing process, final_data.py was run to parse the data, call the <code>update_name()</code> and <code>the update_num() function</code>, and export the cleaned data into CSV files, namely 'nodes.csv', 'nodes_tags'.csv, 'ways.csv', 'ways_tags.csv' and 'ways_nodes.csv'. Finally, the CSV files were imported into a SQL database using the schema provided by Udacity.

# Data Overview

This section includes summary statistics about the cleaned dataset, SQL queries used to retrieve such information.

### File sizes

`richardson.osm .............. 129.5 MB
r_sample.db .................. 26.2 MB
openstreetmap.db ............. 69.1 MB`

### Number of nodes

```SQL
sqlite> SELECT COUNT(*) FROM nodes;```
566122

### Number of ways

```sql
sqlite> SELECT COUNT(*) FROM ways;
```
77566

### Number of unique users

```sql
sqlite> SELECT COUNT(*) 
FROM (SELECT uid FROM nodes UNION SELECT uid FROM ways);```
654

### Top 10 contributing users

```sql
sqlite> SELECT u.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) u
GROUP BY u.user
ORDER BY num DESC
LIMIT 10;```
```
Andrew Matheny_import|434731
woodpeck_fixbot|18490
NoneOfYourBusiness|18398
Andrew Matheny|17158
houston_mapper1|11046
GarrettPennell_import|10950
fmmute|10567
Garrett Pennell|10248
THoffman|9350
SeanTaplinGarlandTx|5187```

### Total number of cuisines

```sql
sqlite> SELECT SUM(count) FROM
(SELECT COUNT(DISTINCT id)as count FROM ways_tags WHERE key = 'cuisine'
UNION 
SELECT COUNT(DISTINCT id) as count FROM nodes_tags WHERE key = 'cuisine');
```
244

### Top 10 cuisines

```sql
sqlite> SELECT value, COUNT(*) as num FROM
(SELECT value FROM nodes_tags WHERE key = 'cuisine'
UNION ALL 
SELECT value FROM ways_tags WHERE key = 'cuisine')
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```
```
burger|39
mexican|22
sandwich|21
pizza|18
coffee_shop|13
tex-mex|11
chicken|11
american|11
chinese|8
seafood|6

```

### Top 10 amenities

```sql
sqlite> SELECT value, COUNT(DISTINCT id) as num
FROM nodes_tags 
WHERE key = 'amenity' 
GROUP BY value
ORDER BY num DESC 
LIMIT 10;
```
```
restaurant|117
fast_food|59
parking_entrance|37
waste_basket|27
cafe|20
bench|12
post_box|11
school|10
drinking_water|9
bicycle_repair_station|9
```

## Additional Ideas and Conclusion

During data audit process, field street and field phone were inspected. A few issues were identified, and cleaned programmatically. In particular, there was inconsistent names for street type, and incorrect format for phone numbers. One way to address the problems is to block incorrectly formatted data from being entered. OSM could provide an automated check to ensure the entered data is complete, and in a correct format or pattern. OSM could also notify users when invalid input is submitted, displaying a message that describes the error. By doing this, users can see what’s wrong and correctly re-enter new data. Another possible solution is to provide automatic corrections for any data entry errors. This will significantly reduce the time spent on data cleaning. However, it is possible that the validation does not catch all the errors. Therefore, it is still important to have validation check in place after user input is inserted into the database.

## References

https://www.tutorialspoint.com/python_data_access/python_sqlite_create_table.htm

http://wiki.openstreetmap.org/wiki/Map_Features

https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md
