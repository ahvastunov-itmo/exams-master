def test_home_page(test_client, init_database):
    """
    GIVEN Flask app
    WHEN (GET) to '/'
    THEN check if redirected to login page
    """
    response = test_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'login' in response.data
    assert b'form' in response.data
    assert b'submit' in response.data


def test_valid_login_logout(test_client, init_database):
    """
    GIVEN Flask app
    WHEN (POST) to '/login'
    THEN check if response is valid
    """
    response = test_client.post(
        '/login',
        data=dict(
            username='Username69',
            role='student'
        ),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Logged in as: Username69' in response.data
    assert b'Random' in response.data
    assert b'Grade' not in response.data
    assert b'Results' not in response.data
    assert b'Load' not in response.data
    assert b'Status' not in response.data
    """
    GIVEN Flask app
    WHEN (GET) to '/logout'
    THEN check if response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'login' in response.data
    assert b'form' in response.data
    assert b'submit' in response.data
    assert b'Logged in' not in response.data
