from bottle import request, Bottle, run
from os.path import join, dirname
from action_network_token import api_key
from checkin import get_all_people, person_attend_event, get_event_details

appPath = dirname(__file__)

app = Bottle()

people = get_all_people(api_key)

@app.get('/gmSignIn')
def get_gm_sign_in():
    event_id = request.query.get('event')
    event_details = get_event_details(api_key, event_id)
    print(event_details)

    html_string = \
        "<p>Web Check-in for "+event_details['name']+"</p>" + \
        "Total so far: "+str(event_details['total_accepted']) + "<br><br>"

    html_string += \
        '''
            <form action="/gmSignIn" method="post" enctype="multipart/form-data" id="keyform">
            <label> Enter a BDSA member:<br/>
              <input type="text" name="member" list="members" size="32"/>
              <datalist id="members">
              <select name="members">
        '''

    for person in people:
        html_string += '<option value="' + person['email_addresses'][0]['address'] + '">' + person['given_name'] + ' ' \
        + person['family_name'] + '</option>'

    html_string += \
        '''
              </select>            
              </datalist>
             </label>
             <input name="event" type="hidden" value="''' + event_id + '">' + \
        '''
             <input value="Check 'em in" type="submit"/>
             </form>
        '''
    return html_string


@app.post('/gmSignIn')
def post_gm_sign_in():
    member_email = request.forms.get('member')
    event_id = request.forms.get('event')
    print(event_id, 'from post')


    output = member_email

    for person in people:
        if person['email_addresses'][0]['address'] == member_email:
            person_attend_event(api_key, person, event_id)
            output+= ' added to event'

    if output == member_email:
        output += 'not found in db'


    html_string = '<font size=2 face="Helvetica Neue"><p>'
    html_string += output
    html_string += '</p></font>'
    return html_string




if __name__ == "__main__":
    run(app, host='localhost', port=8988, reloader=True)
