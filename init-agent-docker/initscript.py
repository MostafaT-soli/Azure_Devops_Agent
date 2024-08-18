import requests
from requests.auth import HTTPBasicAuth
import sys
# Variabls

azdp='172.16.40.21'
org='DefaultCollection'
pool_id=3


def check_assigned_request(auth_token,azdp,org,pool_id):
    url = f"http://{azdp}/{org}/_apis/distributedtask/pools/{pool_id}/agents?includeAssignedRequest=true"
    content_type = "application/json"
    headers = {
        "Content-Type": content_type,
    }
    auth = HTTPBasicAuth('', auth_token)
    response = requests.get(url, headers=headers, auth=auth)
    data = response.json()
    # Check if the response is empty
    if not data.get('value'):
        return False
    
    # Check if every element has 'assignedRequest'
    for agent in data['value']:
        if agent.get('status') == 'online' and agent.get('enabled') == True and 'assignedRequest' not in agent:
            return True
    
    return False

#  Testing only 
result = check_assigned_request(auth_token,azdp,org,pool_id)
print(result)
# ssd Testing only 

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <azdp> <org> <pool_id> <auth_token>")
        sys.exit(1)

    azdp = sys.argv[1]
    org = sys.argv[2]
    pool_id = int(sys.argv[3])
    auth_token = sys.argv[4]

    
    result = check_assigned_request(auth_token, azdp, org, pool_id)
    print(result)