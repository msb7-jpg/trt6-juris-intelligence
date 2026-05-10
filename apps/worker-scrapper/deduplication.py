from shared.celery_client import app


@app.task(name="pje_scraper.deduplication.run")
def deduplicate_processos():
    """Simple placeholder deduplication:
    - list objects in MinIO bucket `pje-documents`
    - delete any duplicate filenames (keep first)
    """
    from shared.s3_client import get_s3_client
    client = get_s3_client()
    bucket = "pje-documents"
    objs = client.list_objects(bucket)
    seen = set()
    for obj in objs:
        name = obj.object_name
        if name in seen:
            client.delete_object(bucket, name)
        else:
            seen.add(name)
