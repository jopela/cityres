#!/usr/bin/env python3

import argparse
import subprocess
import sys
import strdist
import pylev

def main():


    parser = argparse.ArgumentParser(description='return a dbpedia uri'\
            ' given a search string that contains a cityname and bounding box')

    parser.add_argument(
            'search',
            help='search string of the form <cityname>;<north>,<west>,<south>'\
            ',<east>'
            )

    sparql_endpoint_default = 'http://datastore:8890/sparql'
    parser.add_argument(
            '-e',
            '--endpoint',
            help='location of the SPARQL endpoint used for the query.'\
            'Defaults to {0} which is the'\
            'mtrip default rdf store.'.format(sparql_endpoint_default),
            )

    parser.add_argument(
            '-d',
            '--dump',
            help='dump the SPARQL query generated for the given search param'\
                    ' and exit',
            action='store_true'
            )

    parser.add_argument(
            '-t',
            '--test',
            help='run the doctest test suite and quit',
            action='store_true'
            )

    args = parser.parse_args()

    if args.test:
        import doctest
        doctest.testmod()
        exit(0)

    if args.dump:
        query = query_string(args.search)
        print(query)
        exit(0)


    resource = cityres(args.search, args.endpoint)
    print(resource)

    return

def cityres(search, endpoint):
    """ return the single best city resource match found in the
    http://dbpedia.org/ graph based on geolocation and city name. If no
    uri resource is found, will return none."""

    possible_uris = uri(search, endpoint)
    if len(possible_uris) == 0:
        return None

    (city,_,_,_,_) = unpack_search(search)
    choosen = choose_best(city, possible_uris)

    return choosen

def choose_best(city, uris):
    """
    Chooses the string that most closely resemble to the city name.

    EXAMPLE
    =======
    >>> choose_best('Montreal',['http://dbpedia.org/resource/Montreal','http://dbpedia.org/resource/Westmount_(Montreal)'])
    'http://dbpedia.org/resource/Montreal'

    >>> choose_best('Montreal',['http://dbpedia.org/resource/Mountreal','http://dbpedia.org/resource/Moscow','http://dbpedia.org/resource/Montreal'])
    'http://dbpedia.org/resource/Montreal'

    >>> choose_best('New York',['http://dbpedia.org/resource/New_York_City','http://dbpedia.org/Harlem'])
    'http://dbpedia.org/resource/New_York_City'

    """

    # strategy is to use the longest common subsequence first and
    # take the the string that has the uri that has the longest one.
    # If there are ties, break the tie by computing the levenshtein and
    # taking the uri that has the smallest.

    # this creates a kind of band-pass filter, so to speak.

    distances = [(strdist.longest_sub_len(city, uri), uri) for uri in uris]

    # sort them by sub sequence length
    distances.sort()

    result_subseq_length = distances[-1][0]

    #print("distances",distances)

    ties = [e for e in distances if e[0] == result_subseq_length]

    #print("ties")

    # break the tie with the levenshtein distance.
    if len(ties) > 1:
        tie_distances = [(pylev.levenshtein(city, t[1]),t[1]) for t in ties]
        tie_distances.sort()
        result = tie_distances[0][1]
    else:
        result = distances[-1][1]

    return result

def uri(search,endpoint):
    """
    Run a query to extract a location that lies within the given bounding
    box.
    """

    query_instance = query_string(search)

    shell_template = 's-query --service {0} --output=csv "{1}"'
    shell_instance = shell_template.format(endpoint,query_instance)

    shell_result_raw = subprocess.check_output(shell_instance, shell=True,
            universal_newlines=True)

    shell_lines = shell_result_raw.split("\n")[1:]
    lines = [l for l in shell_lines if l != '']

    return lines


def query_string(search):
    """
    return the sparql query string to get the city that lies in the coord.
    """

    query_template = """
    PREFIX dbowl: <http://dbpedia.org/ontology/>
    PREFIX dbgeo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

    select distinct ?uri where {{
    {{
        ?uri a dbowl:City .
        ?uri dbgeo:lat ?lat .
        ?uri dbgeo:long ?long .
    }}
    UNION
    {{
        ?uri a dbowl:Town .
        ?uri dbgeo:lat ?lat .
        ?uri dbgeo:long ?long .

    }}
        FILTER (?lat < {0} && ?long > {1} && ?lat > {2} && ?long < {3})
    }}
    """

    (city,north,west,south,east) = unpack_search(search)

    query_instance = query_template.format(north,west,south,east)

    return query_instance

def unpack_search(search):
    """
    returns the individual component of a search string in a tuple.

    EXAMPLE
    =======

    >>> unpack_search('Bali;0,1,2,3')
    ('Bali', '0', '1', '2', '3')
    """

    tmp = search.split(';')
    city = tmp[0]

    coords = tmp[1].split(',')

    north = coords[0]
    west = coords[1]
    south = coords[2]
    east = coords[3]

    return (city,north,west,south,east)

if __name__ == '__main__':
    main()
