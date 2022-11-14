import os
import boto3
from botocore.config import Config

# import ClientError from botocore.exceptions
from botocore.exceptions import ClientError



class TaskDefinitionConfig:
    def __init__(self):
        self.family = os.environ.get('INPUT_TASK-FAMILY')
        self.revision = os.environ.get('INPUT_TASK-REVISION')
        self.region = os.environ.get('INPUT_AWS-REGION')
        self.access_key_id = os.environ.get('INPUT_AWS-ACCESS-KEY-ID')
        self.secret_access_key = os.environ.get('INPUT_AWS-SECRET-ACCESS-KEY')
        self.image = os.environ.get('INPUT_IMAGE-URL')
        self.config = Config(region_name=self.region, signature_version='v4', retries={'max_attempts': 3, 'mode': 'standard'})
        self.ecs = boto3.client('ecs', aws_access_key_id=self.access_key_id, aws_secret_access_key=self.secret_access_key,config=self.config)
        self.task_definition = None
        self.updated_task_definition = None
    
    def download_task_definition(self):
        task_definition_identifier = self.family + ':' + self.revision if self.revision else self.family
        try:
            response = self.ecs.describe_task_definition(taskDefinition=task_definition_identifier)
        except Exception as error:
            raise error
        else:
            meta_data = response.pop('ResponseMetadata')
            if meta_data['HTTPStatusCode'] == 200:
                self.task_definition = response['taskDefinition']
                          

    def replace_image_uri(self):
        self.task_definition['containerDefinitions'][0]['image'] = self.image
         
       

    def save_new_task_definition(self):
        del self.task_definition["registeredAt"]
        del self.task_definition["deregisteredAt"]
        try:
            response = self.ecs.register_task_definition(**self.task_definition)
        except Exception as error:
            raise error
        else:
            self.updated_task_definition = response['taskDefinition']
            print("old: {}, new: {}".format(self.task_definition['containerDefinitions'][0]["image"], self.updated_task_definition['containerDefinitions'][0]["image"]))   

if __name__ == "__main__":
    task_definition_config = TaskDefinitionConfig()
    task_def = task_definition_config.download_task_definition()
    task_definition_config.replace_image_uri()
    task_definition_config.save_new_task_definition()