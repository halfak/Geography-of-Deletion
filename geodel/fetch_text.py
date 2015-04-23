"""
Fetches text for revisions

Usage:
    fetch_text -h | --help
    fetch_text --api=<url> [--check-deleted-first]

Options:
    --api=<url>  URL of a MediaWiki API to query
    --check-deleted-first  Assume that rev_ids will be for deleted pages
"""
import getpass
import sys

import docopt
from mw import api


def main():
    args = docopt.docopt(__doc__)


    headers, rows = read_input(sys.stdin)

    session = api.Session(args['--api'])
    session.login(input("Username: "), getpass.getpass("Password: "))

    check_deleted_first = args['--check-deleted-first']

    new_headers = header + ['last_text']
    run(rows, session, new_headers, check_deleted_first)

def read_input(f):
    headers = f.readline().strip().split("\t")
    return headers, read_rows(f)

def read_rows(headers, f):
    for line in f:
        yield dict(zip(headers, line.strip().split("\t")))

def run(new_headers, rows, session, check_deleted_first):

    print("\t".join(new_headers))
    for row in rows:
        rev_id = row['last_rev_id']
        row['last_text'] = fetch_text(session, rev_id, check_deleted_first)
        sys.stderr.write(".");sys.stderr.flush()
        print("\t".join(encode(row[h]) for h in headers))


def encode(val):
    if val is None:
        return "NULL"
    else:
        val = str(val)
        return val.replace("\t", "\\t").replace("\n", "\\n")


def fetch_text(session, rev_id, check_deleted_first=False):

    if check_deleted_first:
        collections = [session.deleted_revisions, session.revisions]
    else:
        collections = [session.revisions, session.deleted_revisions]

    for collection in collections:
        try:
            rev_doc = collection.get(rev_id, properties={'content'})
            return rev_doc.get("*")
        except KeyError:
            continue

    # If we get here, that means we never found the text
    return None
