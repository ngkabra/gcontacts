#!/usr/bin/python
from gdata.contacts.service import ContactsService, ContactsQuery, GDATA_VER_HEADER
from gdata.service import RequestError
from getpass import getpass
from gdata.contacts import ContactEntry, Birthday, Event

from mobileno import mobile_no
import os
import tempfile
import shutil
import csv

CSV_FILE = os.path.expanduser('~/.mobiles.csv')

def login(email='navin.kabra@gmail.com', password=None):
    if not password:
        password = getpass('Password for %s: ' % email)
    client = ContactsService(email=email,
                             password=password,
                             source='Smriti-Google-Contacts-0.3',
                             additional_headers=dict(GDATA_VER_HEADER=3))
    client.ProgrammaticLogin()
    return client

def phone_numbers(contacts):
    return [(c.title.text, 
             [mobile_no(p.text) for p in c.phone_number if mobile_no(p.text)]) 
            for c in contacts.entry if len(c.phone_number) > 0]

def get_phone_list(client, max=2000):
    q = ContactsQuery(params={'max-results': str(max)})
    cx = client.GetContactsFeed(q.ToUri())
    phone_list = phone_numbers(cx)
    print 'Fetched', len(phone_list), '...'
    while cx.GetNextLink():
        cx = client.GetContactsFeed(cx.GetNextLink().href)
        phone_list.extend(phone_numbers(cx))
        print 'Fetched', len(phone_list), '...'

    return phone_list

def update_csv():
    client = login()
    px = get_phone_list(client)
    px.sort()
    tmpf = tempfile.NamedTemporaryFile(delete=False)
    cfile = csv.writer(tmpf)
    for p in px:
        if len(p[1]) > 0:
            cfile.writerow([p[0], ":".join(p[1])])
    shutil.move(tmpf.name, CSV_FILE)

def read_csv():
    cfile = csv.reader(open(CSV_FILE))
    return [(p[0], p[1].split(':')) for p in cfile]

if __name__ == '__main__':
    update_csv()
