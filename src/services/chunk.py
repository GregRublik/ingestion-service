from models.document import Document


class ChunkingService:

    def chunk(self, doc: Document, payload):

        if doc.file_extension == '.docx':
            pass
        elif doc.file_extension == '.doc':
            pass
        elif doc.file_extension == '.pdf':
            pass
        elif doc.file_extension == '.json':
            pass
        elif doc.file_extension == '.md':
            pass
        elif doc.file_extension == '.txt':
            pass
        elif doc.file_extension in ['.jpg', '.png']:
            pass





