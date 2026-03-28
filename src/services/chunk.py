from models.document import Document


class ChunkingService:

    def chunk(self, doc: Document, payload):
        if doc.file_type == FileType.PDF:


