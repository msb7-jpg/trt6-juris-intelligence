def test_deduplicate_processos(monkeypatch):
    import importlib.util
    import pathlib
    # Load the deduplication module directly from file path
    dedup_path = pathlib.Path(__file__).resolve().parents[2] / 'deduplication.py'
    spec = importlib.util.spec_from_file_location('deduplication', dedup_path)
    dedup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dedup)
    deduplicate_processos = dedup.deduplicate_processos

    class DummyClient:
        def __init__(self):
            self.deleted = []
        def list_objects(self, bucket):
            from collections import namedtuple
            Obj = namedtuple('Obj', 'object_name')
            return [Obj('a.pdf'), Obj('b.pdf'), Obj('a.pdf')]
        def delete_object(self, bucket, name):
            self.deleted.append(name)
    # Patch the get_s3_client to return our dummy client
    monkeypatch.setattr('shared.s3_client.get_s3_client', lambda: type('X', (), {'client': DummyClient()}))
    deduplicate_processos()
    # Verify that duplicate was deleted
    assert 'a.pdf' in deduplicate_processos.__globals__['get_s3_client']().client.deleted
