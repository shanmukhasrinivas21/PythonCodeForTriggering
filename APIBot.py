import requests
import json
import configparser
#from DBcon import MyDB

class APIBot:
    ''' This class is used to create objects to run the robot using API calls. 
    To get the details of robots and process from the orchestrator in a json file'''
    def __init__(self):
        ''' This constructor is used to get a connection from orchestrator and getting bearer token '''
        # initialiasing parameters passed while creating object
        self.environment = ""
        #db = MyDB()
        config = configparser.ConfigParser()
        config.read('config.INI')
        tenant_name = (config.get("APIconfiguration", "tenant"))
        user_name = (config.get("APIconfiguration", "username"))
        password = (config.get("APIconfiguration", "password"))
        #print(tenant_name, user_name, password, sep=',')
        self.environment = (config.get("APIconfiguration", "environment"))
        # Authenticating and getting bearear token
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/api/account/authenticate"

        data = {
            "tenancyName": tenant_name,
            "usernameOrEmailAddress": user_name,
            "password": password
        }

        response = requests.post(url=API_ENDPOINT, data=data)
        self.auth_res = response.json()
        if("result" in self.auth_res):
            self.result = self.auth_res["result"]
            print("Sucessfully Authorized")

        else:
            #db.write("""insert into error_logs(err_src, err_type, err_desc, err_timestamp) 
            #values('API Script', 'Authorization fail',?,CURRENT_TIMESTAMP)""",
            #(self.result + 'Username , password or tenant name is wrong. The orchestrator may be unresponsive'))
            print("Authorization fail")

        # Getting the list of robots connected to orchestrator and know their status
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/odata/Robots"

        Headers = {"Authorization": "Bearer " + self.result}
        response = requests.get(
            url=API_ENDPOINT, headers=Headers)
        self.robot_res = response.json()

        if("@odata.count" in self.robot_res):
            self.robot_count = self.robot_res["@odata.count"]
            print("Robots Data Collected")
        else:
            #db.write("""insert into error_logs(err_src, err_type, err_desc, err_timestamp) 
            #values('API Script', 'Failed getting Robots',?,CURRENT_TIMESTAMP)""",
            #         (self.robot_res + 'Unable to get the information of robots'))
            print("Failed getting Robots")
        # Getting the list of process and their details
       
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/odata/Releases"

        response = requests.get(
            url=API_ENDPOINT, headers=Headers)
        self.process_res = response.json()

        if("@odata.count" in self.process_res):
            self.process_count = self.process_res["@odata.count"]
            print("Process Data Collected")
        else:
            #db.write("""insert into error_logs(err_src, err_type, err_desc, err_timestamp) 
            #        values('API Script', 'Failed getting processes',?,CURRENT_TIMESTAMP)""",
            #(self.process_res+' Info- Unable to get the information of processesfrom orchestrator'))
            print("Failed collecting process")
    
    
    def get_asset(self):
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/odata/Assets"
        Headers = {"Authorization": "Bearer " + self.result}
        response = requests.get(
            url=API_ENDPOINT, headers=Headers)
        
        self.assests = response.json()
        print(self.assests)
        return self.assests
               
    def job_status(self, job_id):
        print(job_id)
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/odata/Jobs?$filter=Key eq "+job_id
        Headers = {"Authorization": "Bearer " + self.result}
        response = requests.get(
            url=API_ENDPOINT, headers=Headers)
        
        self.job_status1 = response.json()
        #print(self.job_status1)
        return self.job_status1['value'][0]['State']

    # Running the job using process name and environment name
    def run_job(self, process_name, request_id, triggered_by, environment, inp_str=""):
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"
        self.robot_id = ""
        self.release_key = ""
        source = "Manual"
        success = False
        error_msg = ""
       # db = MyDB()

        for val in range(self.process_count):
            if(self.process_res["value"][val]["ProcessKey"] == 
               process_name and self.process_res["value"][val]["EnvironmentName"] == 
               environment):
               self.release_key = self.process_res["value"][val]["Key"]
               break

        if(self.release_key):
            Body = {
                "startInfo": {
                    "ReleaseKey": ""+self.release_key,
                    "Strategy": "RobotCount",
                    "RobotIds": [],
                    "NoOfRobots": 1,
                    "Source": source,
                    "InputArguments": inp_str,
                }
            }
            # input string must be in this format '{"var1":"inp1","var2":"inp2"}'
            Headers = {"Authorization": "Bearer " + self.result}
            response = requests.post(
                url=API_ENDPOINT, json=Body, headers=Headers)
            self.run_status = response.json()
            #print(self.run_status)
            if("@odata.context" in self.run_status):
                print(process_name, " started Sucessfully")
                success = True
                job_id = self.run_status['value'][0]['Key']
            else:
                print(self.run_status)
                job_id = "Not Assigned " + error_msg
            # Inserting logs into api_logs table
            #try:
            #    db.write("""insert into api_logs(req_id, process_name, trigg_src,trigg_timestamp,api_status,job_id) 
            #       values(?,?,?,CURRENT_TIMESTAMP,?,?)""",
            #             (request_id, process_name, triggered_by, json.dumps(self.run_status), job_id))
            #except Exception as e:
            #    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            #    message = template.format(type(e).__name__, e.args)
            #    print("Exception Occured - "+message)
        else:
            #db.write("""insert into error_logs(err_src, err_type, err_desc, err_timestamp) 
            #    values('API Script', 'Failed running process',?,CURRENT_TIMESTAMP)""", (str(
            #    self.process_res)+' Info- The specified robot or process not found'))
            print("The specified environment or process not found")
        return {"success":success,"job_id":job_id}
