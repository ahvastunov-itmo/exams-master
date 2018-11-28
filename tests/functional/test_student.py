from io import BytesIO


def test_student_gets_tickets(test_client, init_database):
    """
    GIVEN Flask app
    WHEN (GET) to '/random' by student
    THEN check if everything works
    """
    test_client.post(
        '/login',
        data=dict(
            username='Florinsky',
            role='professor'
        ),
        follow_redirects=True
    )
    json = """
    {
        "number_of_lists": "2",
        "problems_from_each_list": "2",
        "lists": [
            {
                "name": "theory questions",
                "tickets": [
                    {"url": "/list1/ticket1.pdf"},
                    {"url": "/list1/ticket2.pdf"},
                    {"url": "/list1/ticket3.pdf"}
                ]
            },
            {
                "name": "practice problems",
                "tickets": [
                    {"url": "/list2/ticket1.pdf"},
                    {"url": "/list2/ticket2.pdf"},
                    {"url": "/list2/ticket3.pdf"}
                ]
            }
        ]
    }
    """

    upload_response = test_client.post(
        '/load',
        content_type='multipart/form-data',
        data=dict(
            file=(
                BytesIO(json.encode('utf-8')),
                'file.json'
            )
        ),
        follow_redirects=True
    )
    assert upload_response.status_code == 200

    test_client.get('/logout')

    test_client.post(
        '/login',
        data=dict(
            username='Username69',
            role='student'
        ),
        follow_redirects=True
    )

    ticket_response = test_client.get('/random')
    assert ticket_response.status_code == 200
    assert b'Your ticket url' in ticket_response.data

    test_client.get('/logout')

    test_client.post(
        '/login',
        data=dict(
            username='Florinsky',
            role='professor'
        ),
        follow_redirects=True
    )

    status_response = test_client.get(
        '/status'
    )

    assert status_response.status_code == 200
    assert b'Username69' in status_response.data
