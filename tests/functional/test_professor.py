def test_professor_login_logout(test_client, init_database):
    """
    GIVEN Flask app
    WHEN (POST) to '/login' by professor
    THEN check if response is valid
    """
    response = test_client.post(
        '/login',
        data=dict(
            username='Florinsky',
            role='professor'
        ),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Logged in as: Florinsky' in response.data
    assert b'Random' not in response.data
    assert b'Grade' in response.data
    assert b'Results' in response.data
    assert b'Load' in response.data
    assert b'Status' in response.data
    """
    GIVEN Flask app
    WHEN (GET) to '/logout' by professor
    THEN check if response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'login' in response.data
    assert b'form' in response.data
    assert b'submit' in response.data
    assert b'Logged in' not in response.data


def test_professor_saving_grades(test_client, init_database):
    """
    GIVEN Flask app
    WHEN (POST) to '/finished'
    THEN check if exam results are saved
    """
    login_response = test_client.post(
        '/login',
        data=dict(
            username='Florinsky',
            role='professor'
        ),
        follow_redirects=True
    )
    assert login_response.status_code == 200
    assert b'Grade' in login_response.data

    grade_response = test_client.get('/finished')
    assert grade_response.status_code == 200
    assert b'form' in grade_response.data
    assert b'submit' in grade_response.data

    post_grade_response = test_client.post(
        '/finished',
        data=dict(
            username='Petya',
            listnumber='1',
            number='30',
            grade='2',
            time='23:59'
        ),
        follow_redirects=True
    )
    assert post_grade_response.status_code == 200
    assert b'Logged in' in post_grade_response.data

    test_client.post(
        '/finished',
        data=dict(
            username='Vasya',
            listnumber='2',
            number='4',
            grade='3',
            time='0:00'
        )
    )

    response = test_client.post(
        '/history',
        data=dict(
            html='Get HTML'
        ),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Petya' in response.data
    assert b'Vasya' in response.data
