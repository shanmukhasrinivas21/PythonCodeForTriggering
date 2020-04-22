import queu, json, uuid, configparser, requests,logging
from APIBot import APIBot

def trigger():
    # This function will trigger the bot
     #  Get list of queues from get_queues in queue
    logger = logging.getLogger(__name__)
    try:
        logger.info("Triggering the bot execution started")
        queues = queu.get_queues()
        qnames = dict()                        #Empty dict()
        config = configparser.ConfigParser()
        config.read('config.INI')
        tenant_name = (config.get("APIconfiguration", "tenant"))
        user_name = (config.get("APIconfiguration", "username"))
        password = (config.get("APIconfiguration", "password"))
        # To get single queue from a list of queues
        for queue in queues:
            qnames[queue["Id"]] = queue["Name"]
            # pass the Name of the queue to get items
            queueitems = queu.get_queue_items(status='New', qid=queue["Id"])
            if(queueitems['@odata.count'] > 0):
                API_ENDPOINT = "https://rpaorchestrator.vfc.com/api/account/authenticate"
                data = {
                    "tenancyName": tenant_name,
                    "usernameOrEmailAddress": user_name,
                    "password": password
                }
                response = requests.post(url=API_ENDPOINT, data=data)
                auth_res = response.json()
                result = auth_res["result"]
                API_ENDPOINT = "https://rpaorchestrator.vfc.com/odata/Jobs?$filter=ReleaseName%20eq%20'" + \
                    queue["Name"] + \
                    "'%20and%20(State%20eq%20'Running'%20or%20State%20eq%20'Pending')&$orderby=CreationTime%20desc&$top=5"
                Headers = {"Authorization": "Bearer " + result}
                response = requests.get(url=API_ENDPOINT, headers=Headers)
                jobsres = response.json()
                # To get the details of robots and process from the orchestrator
                new_bot = APIBot()
                if(jobsres['@odata.count'] > 0):
                    print("Busy ", queue["Name"])
                else:
                    request_id = uuid.uuid4().hex
                    new_bot.run_job(process_name=queue["Name"], request_id=request_id ,environment="saptest", triggered_by="Email")
                    print("Trigger", queue["Name"])
                    logger.info("Triggering the bot execution Completed")
    except:
        logger.warning("Triggering the bot execution Failed")
