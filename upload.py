import binascii
import hashlib
import mimetypes
import ntpath
import os

from evernote.api.client import EvernoteClient
from evernote.edam.error.ttypes import EDAMUserException
from evernote.edam import notestore
from evernote.edam.type import ttypes


class EvernoteUploader(object):
    def __init__(self, token):
        self.client = EvernoteClient(token=token)
        self.note_store = self.client.get_note_store()
        notebooks = self.note_store.listNotebooks()
        self.notebook_guid_by_name = {}
        for notebook in notebooks:
            self.notebook_guid_by_name[notebook.name] = notebook.guid


    def upload_directory_tree(self, directory_path, parent_name=None):
        notebook = self.create_notebook_from_directory(directory_path, parent_name=parent_name)
        notebook_guid = self.save_notebook_return_guid(notebook)
        for subfile in os.listdir(directory_path):
            full_subfile_path = os.path.join(directory_path, subfile)
            if os.path.isdir(full_subfile_path):
                self.upload_directory_tree(full_subfile_path)
                continue
            note = self.create_note(full_subfile_path, notebook_guid)
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

    def save_notebook_return_guid(self, notebook):
        if notebook.name not in self.notebook_guid_by_name:
            return self.note_store.createNotebook(notebook).guid
        return self.notebook_guid_by_name[notebook.name]

    def find_note(self, note):
        note_filter = notestore.NoteStore.NoteFilter()
        note_filter.words = 'intitle:"%s"' % note.title
        note_filter.notebookGuid = note.notebookGuid
        # for now assuming no notes with duplicate titles
        notesList = self.note_store.findNotes(note_filter, 0, 1)
        if notesList.totalNotes > 0:
            return notesList.notes[0]
        return None

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
        old_note = self.find_note(note)
        if old_note is not None:
            return old_note
        try:
            return self.note_store.createNote(note)
        except EDAMUserException:
            print "Saving note titled %s failed." % note.title
            return None

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

