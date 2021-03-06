import binascii
import hashlib
import mimetypes
import ntpath
import os
import sys

from evernote.api.client import EvernoteClient
from evernote.edam.type import ttypes

token = 'S=s1:U=8f638:E=14fa461a474:C=1484cb075d0:P=1cd:A=en-devtoken:V=2:H=bc4556aec20e956f5ca3db29de428784'

directory_path = '/Users/jakemagner/dev/evernote/hack'


class EvernoteUploader(object):
    def __init__(self, token):
        self.client = EvernoteClient(token=token)
        self.note_store = self.client.get_note_store()

    def upload_directory_tree(self, directory_path, parent_name=None):
        notebook = self.create_notebook_from_directory(directory_path, parent_name=parent_name)
        notebook = self.save_notebook(notebook)
        for subfile in os.listdir(directory_path):
            full_subfile_path = os.path.join(directory_path, subfile)
            if os.path.isdir(full_subfile_path):
                self.upload_directory_tree(full_subfile_path)
                continue
            note = self.create_note(full_subfile_path, notebook.guid)
            note = self.save_note(note)

    def create_notebook_from_directory(self, directory_path, parent_name):
        child_name = ntpath.basename(directory_path)
        if parent_name is None:
            name = child_name
        else:
            name = '{parent_name} - {child_name}'.format(
                child_name=child_name,
                parent_name=parent_name,
            )
        notebook = ttypes.Notebook(name=name)
        return notebook

    def save_notebook(self, notebook):
        return self.note_store.createNotebook(notebook)

    def create_note(self, file_path, notebook_guid):
        title = ntpath.basename(file_path)
        resource = self.create_resource_from_file(file_path)
        hash_hex = binascii.hexlify(resource.data.bodyHash)

        # The content of an Evernote note is represented using Evernote Markup Language
        # (ENML). The full ENML specification can be found in the Evernote API Overview
        # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
        content = '<?xml version="1.0" encoding="UTF-8"?>'
        content += '<!DOCTYPE en-note SYSTEM ' \
            '"http://xml.evernote.com/pub/enml2.dtd">'
        content += '<en-note>'
        content += '<en-media type="' + resource.mime + '" hash="' + hash_hex + '"/>'
        content += '</en-note>' 
        note = ttypes.Note(
            title=title,
            content=content,
            notebookGuid=notebook_guid,
            resources=[resource]
        )
        return note

    def save_note(self, note):
        return self.note_store.createNote(note)

    def create_resource_from_file(self, file_path):
        content = open(file_path, 'rb').read()
        md5 = hashlib.md5()
        _hash = md5.digest()
        md5.update(content)
        data = ttypes.Data()
        data.size = len(content)
        data.bodyHash = _hash
        data.body = content
        resource = ttypes.Resource()
        mtype, encoding =  mimetypes.guess_type(file_path)
        if mtype is None:
            mtype = 'text/plain'
        resource.mime = mtype
        resource.data = data
        return resource 

