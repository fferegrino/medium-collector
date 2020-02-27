from imapclient import IMAPClient
import quopri
import email
import csv
import os
from medium_collector.parser import parse


def read_from_mail(imap_server, account, password, folder, frm=1):
    with IMAPClient(host=imap_server, use_uid=True)  as client:
        client.login(account, password)
        client.select_folder(folder, readonly=True)
        messages = client.search(['NOT', 'DELETED'])
        for message_id in messages[frm-1:]:
            fetched = client.fetch(message_id, "RFC822")
            data = fetched[message_id]
            email_message = email.message_from_bytes(data[b'RFC822'])
            yield message_id, email_message
