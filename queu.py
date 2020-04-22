import requests
import json
import configparser,logging


def add_queue_item(qname, values=dict(), priority="Normal"):
    # This function add the items into the queue
    # priority cane be Low, Normal and High
    logger = logging.getLogger(__name__)
    try:
        logger.info("Adding items to the Queue Started")
        config = configparser.ConfigParser()
        config.read('config.INI')
        tenant_name = (config.get("APIconfiguration", "tenant"))
        user_name = (config.get("APIconfiguration", "username"))
        password = (config.get("APIconfiguration", "password"))
        # Authenticating and getting bearear token
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/api/account/authenticate"
        data = {
            "tenancyName": tenant_name,
            "usernameOrEmailAddress": user_name,
            "password": password
        }
        response = requests.post(url=API_ENDPOINT, data=data)
        auth_res = response.json()
        # print(auth_res)
        result = auth_res["result"]
        # Add to Queue
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/odata/Queues/UiPathODataSvc.AddQueueItem"
        Body = {

            "itemData": {
                "Name": qname,
                "Priority": priority,
                "SpecificContent": values
            }
        }
        Headers = {"Authorization": "Bearer " + result}
        response = requests.post(url=API_ENDPOINT, json=Body, headers=Headers)
        qstatus = response.json()
        #print(qstatus)
        logger.info("Adding items to the Queue Completed")
    except:
        logger.warning("Adding items to Queue Failed")
def get_queues():
    # This function will get the list of Queues
    logger = logging.getLogger(__name__)
    try:
        logger.info("Getting List of Queues Started")
        config = configparser.ConfigParser()
        config.read('config.INI')
        tenant_name = (config.get("APIconfiguration", "tenant"))
        user_name = (config.get("APIconfiguration", "username"))
        password = (config.get("APIconfiguration", "password"))
        # Authenticating and getting bearear token
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/api/account/authenticate"
        data = {
            "tenancyName": tenant_name,
            "usernameOrEmailAddress": user_name,
            "password": password
        }
        response = requests.post(url=API_ENDPOINT, data=data)
        auth_res = response.json()
        #print(auth_res)
        result = auth_res["result"]
        #get list of Queues
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/odata/QueueDefinitions"
        Headers = {"Authorization": "Bearer " + result}
        response = requests.get(url=API_ENDPOINT, headers=Headers)
        qres = response.json()
        return(qres['value'])
        logger.info("Getting List of Queues Completed")
    except:
        logger.warning("Getting List of Queues failed")    

def get_queue_items(status="",qid=0):
    # This function will return the Queue items
    logger = logging.getLogger(__name__)
    try:
        logger.info("Getting List of Queue items Started")
        config = configparser.ConfigParser()
        config.read('config.INI')
        tenant_name = (config.get("APIconfiguration", "tenant"))
        user_name = (config.get("APIconfiguration", "username"))
        password = (config.get("APIconfiguration", "password"))
        # Authenticating and getting bearear token
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/api/account/authenticate"
        data = {
            "tenancyName": tenant_name,
            "usernameOrEmailAddress": user_name,
            "password": password
        }
        response = requests.post(url=API_ENDPOINT, data=data)
        auth_res = response.json()
        #print(auth_res)
        result = auth_res["result"]
        #get list of QueuesId
        API_ENDPOINT = "https://rpaorchestrator.vfc.com/odata/QueueItems?$filter=Status%20eq%20'"+status+"'%20and%20%20QueueDefinitionId%20eq%20"+str(qid)+"&$count=true"
        Headers = {"Authorization": "Bearer " + result}
        response = requests.get(url=API_ENDPOINT, headers=Headers)
        qres = response.json()
        #print(qres)
        return(qres)
        logger.info("Getting List of Queue items Completed")
    except:
        logger.warning("Getting List of Queue items Failed")
