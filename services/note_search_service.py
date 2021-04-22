from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.filedb.filestore import FileStorage
from whoosh.writing import BufferedWriter, AsyncWriter
from whoosh import query
from jieba.analyse import ChineseAnalyzer
from config_manager import config
import threading


class NoteSearchService:
    _instance_lock = threading.Lock()

    def __init__(self):
        self.schema = Schema(note_id=NUMERIC(stored=True, unique=True), notebook_id=NUMERIC(stored=True), title=TEXT(stored=True, analyzer=ChineseAnalyzer()), snippet=TEXT(analyzer=ChineseAnalyzer()))
        try:
            self.index = FileStorage(config.get("PATH", "notes_index_dir")).open_index()
        except:
            self.index = FileStorage(config.get("PATH", "notes_index_dir")).create_index(self.schema)

    def __new__(cls, *args, **kwargs):
        if not hasattr(NoteSearchService, "_instance"):
            with NoteSearchService._instance_lock:
                if not hasattr(NoteSearchService, "_instance"):
                    NoteSearchService._instance = super(NoteSearchService, cls).__new__(cls, *args, **kwargs)
        return NoteSearchService._instance

    def bulk_update(self, notes):
        writer = self.index.writer(procs=4,multisegment=True)
        for note in notes:
            writer.update_document(note_id=note.id, notebook_id=note.notebook_id, title=note.title, snippet=note.snippet)
        writer.commit()

    def add(self, note):
        writer = AsyncWriter(self.index)
        writer.add_document(note_id=note.id, notebook_id=note.notebook_id, title=note.title, snippet=note.snippet)
        writer.commit()

    def update(self, note):
        writer = BufferedWriter(self.index, period=10, limit=10)
        writer.update_document(note_id=note.id, notebook_id=note.notebook_id, title=note.title, snippet=note.snippet)
        writer.close()

    def delete(self, note_id):
        writer = BufferedWriter(self.index)
        writer.delete_by_term('note_id', note_id)
        writer.close()

    def search(self, query_string, notebook_id=None):
        with AsyncWriter(self.index).searcher() as searcher:
            query_parser = MultifieldParser(["title", "snippet"], schema=self.index.schema).parse(query_string)
            notebook_filter = query.Term("notebook_id", notebook_id) if notebook_id else None
            results = searcher.search(query_parser, filter=notebook_filter, limit=None)
            return [res['note_id'] for res in results]
