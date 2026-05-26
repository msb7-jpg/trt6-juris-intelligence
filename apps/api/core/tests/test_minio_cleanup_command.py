from django.core.management import call_command


def test_limpar_minio_pdfs_invalidos_command(monkeypatch):
    from shared import minio_cleanup

    class DummyClient:
        def __init__(self):
            self.deleted = []

        def list_objects(self, bucket):
            from collections import namedtuple

            Obj = namedtuple('Obj', 'object_name')
            return [Obj('1000_1.pdf'), Obj('arquivo.tmp'), Obj('1000_1.pdf')]

        def delete_object(self, bucket, name):
            self.deleted.append(name)

    dummy_client = DummyClient()
    monkeypatch.setattr(minio_cleanup, 'get_s3_client', lambda: dummy_client)

    call_command('limpar_minio_pdfs_invalidos', verbosity=0)

    assert 'arquivo.tmp' in dummy_client.deleted
    assert dummy_client.deleted.count('1000_1.pdf') == 1
