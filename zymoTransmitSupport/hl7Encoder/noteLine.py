from .generics import Hl7Field
from . import generics


lineStart = "NTE"


class SetId(generics.SingleValueField):
    lengthLimit = 4
    default = "1"


class SourceOfNote(generics.SingleValueField):
    lengthLimit = 4
    default = "L"


class NoteText(generics.SingleValueField):
    lengthLimit = 65536
    default = ""


class NoteLine(generics.Hl7Line):

    def __init__(self, noteText:NoteText, sourceOfNote:SourceOfNote=SourceOfNote()):
        self.setID = SetId()
        self.sourceOfNote = sourceOfNote
        self.noteText = noteText
        self.fields = [
            lineStart,
            self.setID,
            self.sourceOfNote,
            self.noteText
        ]