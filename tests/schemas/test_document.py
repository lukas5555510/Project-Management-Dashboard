from app.schemas.document import DocumentResponse


class FakeDocument:
    def __init__(self, id, s3_path, project_id):
        self.id = id
        self.s3_path = s3_path
        self.project_id = project_id


def test_document_response_from_attributes():
    obj = FakeDocument(
        id=1,
        s3_path="s3://bucket/file.pdf",
        project_id=10
    )

    schema = DocumentResponse.model_validate(obj)

    assert schema.id == 1
    assert schema.s3_path == "s3://bucket/file.pdf"
    assert schema.project_id == 10