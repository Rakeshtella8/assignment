import io
import pytest
from flask import url_for
from app.models.document import Document
from app.models.recent_view import RecentView

def test_create_document(client, auth_headers):
    """Test document creation."""
    data = {
        'title': 'Test Document',
        'description': 'Test description',
        'document_type': 'bank_statement'
    }
    
    # Create a test file
    file = (io.BytesIO(b"test file content"), 'test.pdf')
    
    response = client.post(
        '/api/v1/documents',
        data={**data, 'file': file},
        headers=auth_headers,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    assert 'document' in response.json
    assert response.json['document']['title'] == data['title']
    assert response.json['document']['document_type'] == data['document_type']

def test_list_documents(client, auth_headers, test_document):
    """Test document listing."""
    response = client.get('/api/v1/documents', headers=auth_headers)
    
    assert response.status_code == 200
    assert 'documents' in response.json
    assert 'pagination' in response.json
    assert len(response.json['documents']) > 0

def test_get_document(client, auth_headers, test_document):
    """Test getting a specific document."""
    response = client.get(
        f'/api/v1/documents/{test_document.id}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['id'] == test_document.id
    assert response.json['title'] == test_document.title

def test_update_document(client, auth_headers, test_document):
    """Test document update."""
    data = {
        'title': 'Updated Title',
        'description': 'Updated description'
    }
    
    response = client.put(
        f'/api/v1/documents/{test_document.id}',
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['document']['title'] == data['title']
    assert response.json['document']['description'] == data['description']

def test_delete_document(client, auth_headers, test_document):
    """Test document deletion."""
    response = client.delete(
        f'/api/v1/documents/{test_document.id}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'message' in response.json

def test_recent_documents(client, auth_headers, test_document, test_user, db):
    """Test recently viewed documents."""
    # View the document
    client.get(
        f'/api/v1/documents/{test_document.id}',
        headers=auth_headers
    )
    
    # Get recent documents
    response = client.get('/api/v1/documents/recent', headers=auth_headers)
    
    assert response.status_code == 200
    assert 'documents' in response.json
    assert len(response.json['documents']) > 0
    assert response.json['documents'][0]['id'] == test_document.id

@pytest.fixture
def test_document(app, test_user):
    """Create a test document."""
    with app.app_context():
        document = Document(
            title='Test Document',
            description='Test description',
            document_type='bank_statement',
            file_path='test.pdf',
            file_type='pdf',
            file_size=1024,
            mime_type='application/pdf',
            owner_id=test_user.id
        )
        document.save()
        return document 