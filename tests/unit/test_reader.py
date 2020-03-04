from unittest.mock import patch, MagicMock

import pytest
from imapclient import IMAPClient

from medium_collector.reader import read_from_mail


@pytest.fixture
def patched_imap():
    imap_client = MagicMock(spec=IMAPClient)
    with patch("medium_collector.reader.IMAPClient", autospec=True) as client:
        client.return_value.__enter__.return_value = imap_client

        yield imap_client


def test_read_from_mail(patched_imap):
    server = "server"
    account = "account"
    password = "pa$$word"
    folder = "Daily Digests"

    patched_imap.search.return_value = [str(i) for i in range(10)]

    def return_message_dict(message_id, attribute):
        return {message_id: {b"RFC822": "Hola Mundo"}}

    patched_imap.fetch = MagicMock(side_effect=return_message_dict)
    with patch(
        "medium_collector.reader.email.message_from_bytes"
    ) as patched_from_bytes:
        patched_from_bytes.return_value = MagicMock()
        results = list(read_from_mail(server, account, password, folder))

        patched_from_bytes.assert_called()
    patched_imap.login.assert_called_once_with(account, password)
    patched_imap.select_folder.assert_called_once_with(folder, readonly=True)
    patched_imap.search.assert_called_once_with(["NOT", "DELETED"])
