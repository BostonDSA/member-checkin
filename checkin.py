import requests
import pickle
import os
from action_network_token import api_key

def find_person(api_token, email=None, last_name=None, first_name=None):
    headers = {'Content-Type': 'application/json',
               'OSDI-API-Token': api_token}
    person_url = 'https://actionnetwork.org/api/v2/people'
    if email:
        response = requests.request(
            method='GET',
            url=person_url+"?filter=email_address eq '" + email + "'",
            headers=headers)
        # print(response.json())
        # print(len(response.json()['_embedded']['osdi:people']))
        people = response.json()['_embedded']['osdi:people']
        if people:
            return people

    # no match on email, search on last and first
    if last_name and first_name:
        filter = "?filter=family_name eq '"+last_name+"' and given_name eq '"+first_name+"'"
        response = requests.request(
            method='GET',
            url=person_url + filter,
            headers=headers)

        people = response.json()['_embedded']['osdi:people']
        if people:
            return people

    # no match for last + first, try just last
    if last_name:
        filter = "?filter=family_name eq '"+last_name+"'"
        response = requests.request(
            method='GET',
            url=person_url + filter,
            headers=headers)

        people = response.json()['_embedded']['osdi:people']
        if people:
            return people

    # lastly, search by first name
    if first_name:
        filter = "?filter=given_name eq '"+first_name+"'"
        response = requests.request(
            method='GET',
            url=person_url + filter,
            headers=headers)

        people = response.json()['_embedded']['osdi:people']
        if people:
            return people

    return []


def select_person(people):
    for person in people:
        print(person['given_name'], person['family_name'], person['email_addresses'][0]['address'])
        if input():
            return person


def person_attend_event(api_token, person, event):
    headers = {'Content-Type': 'application/json',
               'OSDI-API-Token': api_token}
    events_url = 'https://actionnetwork.org/api/v2/events'
    # response = requests.request(
    #     method='GET',
    #     url=events_url + "/" + event,
    #     headers=headers)
    # print(response.json()['name'])

    response = requests.request(
        method='POST',
        url=events_url + "/" + event + '/attendances/',
        headers=headers,
        json={"_links": {"osdi:person": person['_links']['self']}}
    )
    print(response.json())


def get_event_details(api_token, event_id):
    headers = {'Content-Type': 'application/json',
               'OSDI-API-Token': api_token}
    events_url = 'https://actionnetwork.org/api/v2/events'
    response = requests.request(
        method='GET',
        url=events_url + "/" + event_id,
        headers=headers)
    event_json = response.json()
    return event_json


def get_all_people(api_token, refresh=False):
    if not refresh:
        if os.path.exists('people.pickle'):
            with open('people.pickle', 'rb') as pf:
                peeps = pickle.load(pf)
                return peeps

    headers = {'Content-Type': 'application/json',
               'OSDI-API-Token': api_token}
    person_url = 'https://actionnetwork.org/api/v2/people'

    response = requests.request(
        method='GET',
        url=person_url,
        headers=headers)
    peeps = list()

    while response.json()['_links'].get('next'):
        print('page')
        for person in response.json()['_embedded']['osdi:people']:
            peeps.append(person)
            print('<option value="'+person['email_addresses'][0]['address']+'">'+person['given_name'], person['family_name']+'</option>')

        response = requests.request(
            method='GET',
            url=response.json()['_links']['next']['href'],
            headers=headers)

    print(len(peeps))

    with open('people.pickle', 'wb+') as pf:
        pickle.dump(peeps, pf)
    return peeps


if __name__ == "__main__":

    peeps = get_all_people(api_key)
    print(peeps)

    # print('Person?', find_person(api_key, 'jess.smith.dsa2@gmail.com', 'smith', 'jessica'))
    # webber = select_person(find_person(api_key, 'aliasofmike@gmail.com', 'webber', 'michael'))
    # if webber:
    #     person_attend_event(api_key, webber, '17404b83-f6fc-4ff2-92b3-f75aa575894c')
    #
    # a_jess = select_person(find_person(api_key, first_name='Jessica'))