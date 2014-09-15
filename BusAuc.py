from evernote.api.client import EvernoteClient
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
from evernote.edam.error.ttypes import EDAMUserException, EDAMSystemException

import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types


authToken = "S=s1:U=8f639:E=14fa45f98ae:C=1484cae6a60:P=1cd:A=en-devtoken:V=2:H=93c15bd8ccbff04139e1567f24ec179e"
EN_URL="https://sandbox.evernote.com"

def getBusinessNoteStoreInstance(bNoteStoreUrl):
    "Create and return an instance of NoteStore.Client to interface with Business"
    bNoteStoreHttpClient = THttpClient.THttpClient(bNoteStoreUrl)
    bNoteStoreProtocol = TBinaryProtocol.TBinaryProtocol(bNoteStoreHttpClient)
    bNoteStore = NoteStore.Client(bNoteStoreProtocol)
    return bNoteStore

def authenticateToBusiness(authToken, userStore):
    "Authenticate with Evernote Business, return AuthenticationResult instance"
    try:
        bAuthResult = userStore.authenticateToBusiness(authToken)
    except EDAMUserException, e:
        print e
        return None
    except EDAMSystemException, e:
        print e
        return None
 
    return bAuthResult

def getToken():
    client = EvernoteClient(token=authToken, sandbox=True)

    userStore = client.get_user_store()
    noteStore = client.get_note_store()

    ourUser = userStore.getUser(authToken)
     
    if ourUser.accounting.businessId:
        # we're part of a business
        print "Business Name: %s" % ourUser.accounting.businessName
    else:
    	print "user not in a business account"


    bAuthResult = authenticateToBusiness(authToken, userStore) #defined in previous gist
    if bAuthResult:
        bNoteStoreUrl = bAuthResult.noteStoreUrl
        bNoteStore = getBusinessNoteStoreInstance(bNoteStoreUrl)
    else:
        print "User not authenticated"

    #print bAuthResult
    return  bAuthResult.authenticationToken
