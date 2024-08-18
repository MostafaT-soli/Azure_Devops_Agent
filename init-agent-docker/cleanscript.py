import requests
from datetime import datetime, timezone
from requests.auth import HTTPBasicAuth
import sys

# Replace this URL with the actual API endpoint

azdp='172.16.40.21'
org='DefaultCollection'
pool_id=3


def get_idle_time_in_minutes(finish_time_str):
    finish_time = datetime.fromisoformat(finish_time_str.replace('Z', '+00:00'))
    current_time = datetime.now(timezone.utc)
    idle_time = current_time - finish_time
    return idle_time.total_seconds() / 60

def check_assigned_request(auth_token,azdp,org,pool_id):
    url = f"http://{azdp}/{org}/_apis/distributedtask/pools/{pool_id}/agents?includeLastCompletedRequest=true&includeAssignedRequest=true"
    content_type = "application/json"
    headers = {
        "Content-Type": content_type,
    }
    auth = HTTPBasicAuth('', auth_token)
    response = requests.get(url, headers=headers, auth=auth)
    return response

def main(response):
    
    if response.status_code != 200:
        print(f"Failed to fetch data from API. Status code: {response.status_code}")
        return
    
    data = response.json()
    
    for agent in data.get('value', []):
        if agent.get('status') == 'online' and agent.get('enabled') == True and 'assignedRequest' not in agent:
            last_completed_request = agent.get('lastCompletedRequest')
            #print(agent)
            if last_completed_request:
                finish_time = last_completed_request.get('finishTime')
                if finish_time:
                    idle_minutes = get_idle_time_in_minutes(finish_time)
                    print(f"Agent {agent['name']} has been idle for {idle_minutes:.2f} minutes.")
                else:
                    print(f"Agent {agent['name']} does not have a finish time for the last completed request.")
            else:
                print(f"Agent {agent['name']} does not have a last completed request.")
        else:
            print(f"Agent {agent['name']} is either not online, not enabled, or has an assigned request.")

if __name__ == "__main__":
    response = check_assigned_request(auth_token, azdp, org, pool_id)
    main(response)