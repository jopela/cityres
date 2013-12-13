#!/usr/bin/env python3

import argparse
import sys

def main():


    parser = argparse.ArgumentParser(description='return a dbpedia uri'\
            ' given a search string that contains a cityname and bounding box')

    parser.add_argument(
            'search',
            help='search string of the form <cityname>;<north>,<west>,<south>'\
            ',<east>'
            )

    parser.add_argument(
            '-e',
            '--endpoint',
            help='location of the SPARQL endpoint used for the query.'\
            'Defaults to http://192.168.1.202:3030/dbart/query which is the'\
            'mtrip default rdf store.',
            default='http://192.168.1.202:3030/dbart/query'
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


    uri_res = uri(args.search, args.endpoint)
    print(uri_res)

    return


def uri(search,endpoint):
    """ Run a query to extract a location that lies within the given bounding
    box."""

    print(search, endpoint)
    return

def unpack_search(search):
    """ returns the individual component of a search string in a tuple.

    EXAMPLE
    =======

    >>> unpack_search('Bali;0,1,2,3')
    ('Bali','0','1','2','3')
    """

    return None

if __name__ == '__main__':
    main()
