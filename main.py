import os
import boto3
from botocore.config import Config



class TaskDefinitionConfig:
    def __init__(self):
        self.family = os.environ.get('INPUT_FAMILY-NAME')
        self.region = os.environ.get('INPUT_REGION')
        self.access_key_id = os.environ.get('INPUT_AWS_ACCESS_KEY_ID')
        self.secret_access_key = os.environ.get('INPUT_AWS_SECRET_ACCESS_KEY')
        self.config = Config(region_name=self.region, signature_version='v4', retries={'max_attempts': 3, 'mode': 'standard'})
        self.ecs = boto3.client('ecs', aws_access_key_id=self.access_key_id, aws_secret_access_key=self.secret_access_key,config=self.config)

    def download_latest_revision(self):
        return self.ecs.describe_task_definition(taskDefinition='{}:latest'.format(self.family))
    
    def fill_in_given_fields(self):
        pass

    def save_new_task_definition(self):
        pass
    
    def credentials():
        return {
            "access_key_id": self.acess_key_id,
            "region": self.region,
            "family": self.family,
            "secret_access_key": self.secret_access_key
        }


    
    

if __name__ == "__main__":
    
    print(self.credentials())