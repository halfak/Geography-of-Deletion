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
import io
import sys
import traceback

import docopt
from mw import api


def main():
    args = docopt.docopt(__doc__)

    input_data = io.TextIOWrapper(sys.stdin.buffer, encoding='utf8', errors='replace')

    headers, rows = read_input(input_data)

    session = api.Session(args['--api'])

    sys.stderr.write("Log into " + args['--api'] + "\n")
    sys.stderr.write("Username: ");sys.stderr.flush()
    username = open('/dev/tty').readline().strip()
    password = getpass.getpass("Password: ")
    session.login(username, password)

    check_deleted_first = args['--check-deleted-first']

    new_headers = headers + ['last_text']
    run(rows, session, new_headers, check_deleted_first)

def read_input(f):
    headers = f.readline().strip().split("\t")
    return headers, read_rows(headers, f)

def read_rows(headers, f):
    try:
        i = 0
        for i, line in enumerate(f):
            yield dict(zip(headers, line.strip().split("\t")))
    except Exception as e:
        sys.stderr.write("An error occurred while processing line {0}.\n".format(i+2))
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)

def run(rows, session, new_headers, check_deleted_first):

    print("\t".join(new_headers))
    for row in rows:
        rev_id = row['last_rev_id']
        try:
            row['last_text'] = fetch_text(session, rev_id, check_deleted_first)
            sys.stderr.write(".");sys.stderr.flush()
        except Exception as e:
            row['last_text'] = None
            sys.stderr.write("An error occurred while processing revision {0}.\n".format(rev_id))
            sys.stderr.write(traceback.format_exc())
        print("\t".join(encode(row[h]) for h in new_headers))


def encode(val):
    if val is None:
        return "NULL"
    else:
        val = str(val)
        return val.replace("\t", "\\t").replace("\n", "\\n")


def fetch_text(session, rev_id, check_deleted_first=False):
    try:
        rev_id = int(rev_id)
    except ValueError:
        return ""

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
