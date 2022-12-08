import boptest_submit
import sys
import os
import requests
from requests_toolbelt import MultipartEncoder
from collections import OrderedDict

host = os.environ.get('BOPTEST_SERVER', 'http://web')

def upload_testcase(post_form_response, testcase_path):
    json = post_form_response.json()
    postURL = json['url']
    formData = OrderedDict(json['fields'])
    formData['file'] = ('filename', open(testcase_path, 'rb'))
    
    encoder = MultipartEncoder(fields=formData)
    return requests.post(postURL, data=encoder, headers={'Content-Type': encoder.content_type})

def test_ibpsa_boptest_testcase():
    auth_token = os.environ.get('BOPTEST_DASHBOARD_API_KEY')
    testcase_id = 'testcase1'
    testcase_path = f'/testcases/{testcase_id}/models/wrapped.fmu'

    # Delete for an invalid test case should return 404
    response = requests.delete(f'{host}/testcases/{testcase_id + "xyz"}', headers={'Authorization': auth_token})
    assert response.status_code == 404

    # Invalid auth_token to get post-form should return 401
    response = requests.get(f'{host}/testcases/{testcase_id}/post-form', headers={'Authorization': auth_token + 'xyz'})
    assert response.status_code == 401

    # Get post-form should return 200
    # This authorizes a new test case upload
    response = requests.get(f'{host}/testcases/{testcase_id}/post-form', headers={'Authorization': auth_token})
    assert response.status_code == 200

    # New test cases are uploaded directly to storage (e.g. minio/s3)
    # 204 indicates a successful upload
    response = upload_testcase(response, testcase_path)
    assert response.status_code == 204

    # Confirm that the test case has been received
    response = requests.get(f'{host}/testcases')
    assert response.status_code == 200
    assert(testcase_id in map(lambda item: item['testcaseid'], response.json()))

    # Select the test case
    response = requests.post(f'{host}/testcases/{testcase_id}/select')
    assert response.status_code == 200
    testid = response.json()['testid']

    # Get the test's name (testcaseID) to demonstrate that it is running
    # Other test APIs are exercised by the core BOPTEST test suite
    response = requests.get(f'{host}/name/{testid}')
    assert response.status_code == 200

    # Stop the test
    response = requests.put(f'{host}/stop/{testid}')
    assert response.status_code == 200

    # Invalid auth_token to delete test case should return 401
    response = requests.delete(f'{host}/testcases/{testcase_id}', headers={'Authorization': auth_token + 'xyz'})
    assert response.status_code == 401

    # Successful delete should return 200
    response = requests.delete(f'{host}/testcases/{testcase_id}', headers={'Authorization': auth_token})
    assert response.status_code == 200


def test_shared_namespace_testcase():
    auth_token = os.environ.get('BOPTEST_DASHBOARD_API_KEY')
    testcase_namespace = 'resstock'
    testcase_id = 'testcase1'
    testcase_path = f'/testcases/{testcase_id}/models/wrapped.fmu'

    # Delete for an invalid test case should return 404
    response = requests.delete(f'{host}/testcases/{testcase_namespace}/{testcase_id + "xyz"}', headers={'Authorization': auth_token})
    assert response.status_code == 404

    # Invalid auth_token to get post-form should return 401
    response = requests.get(f'{host}/testcases/{testcase_namespace}/{testcase_id}/post-form', headers={'Authorization': auth_token + 'xyz'})
    assert response.status_code == 401

    # Get post-form should return 200
    # This authorizes a new test case upload
    response = requests.get(f'{host}/testcases/{testcase_namespace}/{testcase_id}/post-form', headers={'Authorization': auth_token})
    assert response.status_code == 200

    # New test cases are uploaded directly to storage (e.g. minio/s3)
    # 204 indicates a successful upload
    response = upload_testcase(response, testcase_path)
    assert response.status_code == 204

    # Confirm that the test case has been received
    response = requests.get(f'{host}/testcases/{testcase_namespace}')
    assert response.status_code == 200
    assert(testcase_id in map(lambda item: item['testcaseid'], response.json()))

    # Select the test case
    response = requests.post(f'{host}/testcases/{testcase_namespace}/{testcase_id}/select')
    assert response.status_code == 200
    testid = response.json()['testid']

    # Get the test's name (testcaseID) to demonstrate that it is running
    # Other test APIs are exercised by the core BOPTEST test suite
    response = requests.get(f'{host}/name/{testid}')
    assert response.status_code == 200

    # Stop the test
    response = requests.put(f'{host}/stop/{testid}')
    assert response.status_code == 200

    # Invalid auth_token to delete test case should return 401
    response = requests.delete(f'{host}/testcases/{testcase_namespace}/{testcase_id}', headers={'Authorization': auth_token + 'xyz'})
    assert response.status_code == 401

    # Successful delete should return 200
    response = requests.delete(f'{host}/testcases/{testcase_namespace}/{testcase_id}', headers={'Authorization': auth_token})
    assert response.status_code == 200

def test_private_user_testcase():
    auth_token = os.environ.get('BOPTEST_DASHBOARD_API_KEY')
    username = os.environ.get('BOPTEST_DASHBOARD_USERNAME')
    testcase_id = 'testcase1'
    testcase_path = f'/testcases/{testcase_id}/models/wrapped.fmu'

    # Delete for an invalid test case should return 404
    response = requests.delete(f'{host}/users/{username}/testcases/{testcase_id + "xyz"}', headers={'Authorization': auth_token})
    assert response.status_code == 404

    # Invalid auth_token to get post-form should return 401
    response = requests.get(f'{host}/users/{username}/testcases/{testcase_id}/post-form', headers={'Authorization': auth_token + 'xyz'})
    assert response.status_code == 401

    # Get post-form should return 200
    # This authorizes a new test case upload
    response = requests.get(f'{host}/users/{username}/testcases/{testcase_id}/post-form', headers={'Authorization': auth_token})
    assert response.status_code == 200

    # New test cases are uploaded directly to storage (e.g. minio/s3)
    # 204 indicates a successful upload
    response = upload_testcase(response, testcase_path)
    assert response.status_code == 204

    # Confirm that the test case has been received
    response = requests.get(f'{host}/users/{username}/testcases', headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert(testcase_id in map(lambda item: item['testcaseid'], response.json()))

    # Select the test case
    response = requests.post(f'{host}/users/{username}/testcases/{testcase_id}/select', headers={'Authorization': auth_token})
    assert response.status_code == 200
    testid = response.json()['testid']

    # Get the test's name (testcaseID) to demonstrate that it is running
    # Other test APIs are exercised by the core BOPTEST test suite
    response = requests.get(f'{host}/name/{testid}')
    assert response.status_code == 200

    # Stop the test
    response = requests.put(f'{host}/stop/{testid}')
    assert response.status_code == 200

    # Invalid auth_token to delete test case should return 401
    response = requests.delete(f'{host}/users/{username}/testcases/{testcase_id}', headers={'Authorization': auth_token + 'xyz'})
    assert response.status_code == 401

    # Successful delete should return 200
    response = requests.delete(f'{host}/users/{username}/testcases/{testcase_id}', headers={'Authorization': auth_token})
    assert response.status_code == 200
