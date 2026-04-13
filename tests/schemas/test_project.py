from app.schemas.project import ProjectResponse


class FakeDocument:
    def __init__(self, id, s3_path, project_id):
        self.id = id
        self.s3_path = s3_path
        self.project_id = project_id


class FakeProject:
    def __init__(self, id, name, description, documents):
        self.id = id
        self.name = name
        self.description = description
        self.documents = documents


def test_project_response_from_attributes_with_documents():
    documents = [
        FakeDocument(id=1, s3_path="s3://file1.pdf", project_id=10),
        FakeDocument(id=2, s3_path="s3://file2.pdf", project_id=10),
    ]

    project = FakeProject(
        id=10,
        name="Test Project",
        description="Some description",
        documents=documents
    )

    result = ProjectResponse.model_validate(project)

    assert result.id == 10
    assert result.name == "Test Project"
    assert result.description == "Some description"

    # nested mapping check
    assert len(result.documents) == 2
    assert result.documents[0].id == 1
    assert result.documents[0].s3_path == "s3://file1.pdf"
    assert result.documents[1].id == 2

def test_project_response_defaults():
    project = FakeProject(
        id=1,
        name="Project",
        description=None,
        documents=[]
    )

    result = ProjectResponse.model_validate(project)

    assert result.description is None
    assert result.documents == []