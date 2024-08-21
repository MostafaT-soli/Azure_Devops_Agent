import requests
from requests.auth import HTTPBasicAuth
import sys

def check_assigned_request(auth_token,azdp,org,pool_id,max_node):
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
    if int(data['count']) <=  int(max_node):
        for agent in data['value']:
            if agent.get('status') == 'online' and agent.get('enabled') == True and 'assignedRequest' not in agent:
                return True
    else:
        return False
    return False

# #  uncomment for Testing only 
# azdp='172.16.40.21'
# org='DefaultCollection'
# pool_id=3
# auth_token='ayfanaksdxrrpjhfxe4nys4my6cnsvemk7pba2xtsk4hyu2jnnia'
# max_node=4

# result = check_assigned_request(auth_token,azdp,org,pool_id)
# print(result)
# #  uncomment for Testing only 

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python script.py <azdp> <org> <pool_id> <auth_token> <max_node> ")
        sys.exit(1)

    azdp = sys.argv[1]
    org = sys.argv[2]
    pool_id = int(sys.argv[3])
    auth_token = sys.argv[4]
    max_node = sys.argv[5]

    
    result = check_assigned_request(auth_token, azdp, org, pool_id, max_node)
    print(result)

