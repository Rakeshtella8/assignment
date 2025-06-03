import pytest
from flask import url_for
from app.models.user import User

def test_register(client):
    """Test user registration."""
    data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'Test123!',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    response = client.post('/api/v1/auth/register', json=data)
    assert response.status_code == 201
    assert 'user' in response.json
    assert 'tokens' in response.json
    assert response.json['user']['email'] == data['email']
    assert response.json['user']['username'] == data['username']

def test_login(client, test_user):
    """Test user login."""
    data = {
        'username': test_user.username,
        'password': 'password123'
    }
    
    response = client.post('/api/v1/auth/login', json=data)
    assert response.status_code == 200
    assert 'user' in response.json
    assert 'tokens' in response.json
    assert response.json['user']['username'] == test_user.username

def test_invalid_login(client):
    """Test login with invalid credentials."""
    data = {
        'username': 'nonexistent',
        'password': 'wrongpass'
    }
    
    response = client.post('/api/v1/auth/login', json=data)
    assert response.status_code == 401
    assert 'message' in response.json

def test_get_me(client, auth_headers, test_user):
    """Test getting current user profile."""
    response = client.get('/api/v1/auth/me', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['username'] == test_user.username

def test_refresh_token(client, refresh_headers):
    """Test refreshing access token."""
    response = client.post('/api/v1/auth/refresh', headers=refresh_headers)
    assert response.status_code == 200
    assert 'access_token' in response.json

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            email='test@example.com',
            username='testuser',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        user.save()
        return user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers."""
    response = client.post('/api/v1/auth/login', json={
        'username': test_user.username,
        'password': 'password123'
    })
    token = response.json['tokens']['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def refresh_headers(client, test_user):
    """Get refresh token headers."""
    response = client.post('/api/v1/auth/login', json={
        'username': test_user.username,
        'password': 'password123'
    })
    token = response.json['tokens']['refresh_token']
    return {'Authorization': f'Bearer {token}'} 