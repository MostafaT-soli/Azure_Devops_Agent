import subprocess
import requests
from datetime import datetime, timezone
from requests.auth import HTTPBasicAuth
import sys

def run_kubectl_delete(agent):
    #Define the base command
    command = f"kubectl delete pod {agent}"
    # # # test command
    # command = f"echo {agent}"
    try:
        # Run the command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Get the output and errors (if any)
        stdout, stderr = process.communicate()

        # Decode the output and errors
        output = stdout.decode()
        errors = stderr.decode()

        return output, errors
    except Exception as e:
        return "", str(e)


def get_idle_time_in_minutes(finish_time_str):
    finish_time = datetime.fromisoformat(finish_time_str.replace('Z', '+00:00'))
    current_time = datetime.now(timezone.utc)
    idle_time = current_time - finish_time
    return idle_time.total_seconds() / 60

def check_assigned_request(auth_token,azdp,org,pool_id):
    url = f"https://{azdp}/{org}/_apis/distributedtask/pools/{pool_id}/agents?includeLastCompletedRequest=true&includeAssignedRequest=true"
    content_type = "application/json"
    headers = {
        "Content-Type": content_type,
    }
    auth = HTTPBasicAuth('', auth_token)
    response = requests.get(url, headers=headers, auth=auth, verify=False)
    return response

def delete_agent_api(auth_token,azdp,org,pool_id,agent_id):
    url = f"https://{azdp}/{org}/_apis/distributedtask/pools/{pool_id}/agents/{agent_id}?api-version=7.0"
    content_type = "application/json"
    headers = {
        "Content-Type": content_type,
    }
    auth = HTTPBasicAuth('', auth_token)
    response = requests.delete(url, headers=headers, auth=auth, verify=False)
    return response

def get_idle_agents(response,idle_threshold_minutes):
    
    if response.status_code != 200:
        print(f"Failed to fetch data from API. Status code: {response.status_code}")
        return
    
    data = response.json()
    delete_agent= []
    for agent in data.get('value', []):
        if 'assignedRequest' not in agent:
            if agent.get('status') == 'online' and agent.get('enabled') == True : 
                last_completed_request = agent.get('lastCompletedRequest')
                if last_completed_request:
                    finish_time = last_completed_request.get('finishTime')
                    if finish_time:
                        idle_minutes = get_idle_time_in_minutes(finish_time)
                        if idle_minutes > idle_threshold_minutes:
                            print(f"Agent {agent['name']} has been idle for {idle_minutes:.2f} minutes.")
                            delete_agent.append({'name': agent['name'] , 'id' : agent['id'] })
                    else:
                        print(f"Agent {agent['name']} does not have a finish time for the last completed request.")
                else:
                    print(f"Agent {agent['name']} does not have a last completed request.")
            else:
                print(f"Agent {agent['name']}  This Agent is not enabled or offline.")
                delete_agent.append({'name': agent['name'] , 'id' : agent['id'] })
        else:
            print(f"Agent {agent['name']}  has an assigned request.")
    return(delete_agent)
    
def delet_idle_agents(idle_agents):
    for agent in idle_agents:
        output, errors = run_kubectl_delete(agent['name'])
        print(f"agents to be deleted:{output}")
        if errors:
            print(f"There was an error in deleting agent {agent} from kube8  errors:\n", errors)
            print("trying api")
            delete_agent_api(auth_token, azdp, org, pool_id,agent['id'])

# #Testing only 
# #Testing Values

# azdp='172.16.40.21'
# org='DefaultCollection'
# pool_id=3
# auth_token='ayfanaksdxrrpjhfxe4nys4my6cnsvemk7pba2xtsk4hyu2jnnia'
# idle_threshold_minutes=10

# response = check_assigned_request(auth_token, azdp, org, pool_id)
# idle_agents = get_idle_agents(response,idle_threshold_minutes)
# delet_idle_agents(idle_agents)
# ##################################

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python script.py <azdp> <org> <pool_id> <auth_token> <idle_threshold_minutes>")
        sys.exit(1)

    azdp = sys.argv[1]
    org = sys.argv[2]
    pool_id = int(sys.argv[3])
    auth_token = sys.argv[4]
    idle_threshold_minutes=  int(sys.argv[5])
    
    response = check_assigned_request(auth_token, azdp, org, pool_id)
    idle_agents = get_idle_agents(response,idle_threshold_minutes)
    delet_idle_agents(idle_agents)
