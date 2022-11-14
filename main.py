import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import logging


logging.basicConfig(level = logging.INFO, format='%(levelname)s: %(message)s')

logger = logging.getLogger()



class TaskDefinitionConfig:
    def __init__(self):
        self.family = os.environ.get('INPUT_TASK-FAMILY')
        self.revision = os.environ.get('INPUT_TASK-REVISION')
        self.region = os.environ.get('INPUT_AWS-REGION')
        self.access_key_id = os.environ.get('INPUT_AWS-ACCESS-KEY-ID')
        self.secret_access_key = os.environ.get('INPUT_AWS-SECRET-ACCESS-KEY')
        self.image = os.environ.get('INPUT_IMAGE-URI')
        self.service_name = os.environ.get('INPUT_SERVICE-NAME')
        self.cluster_name = os.environ.get('INPUT_CLUSTER-NAME')
        self.config = Config(region_name=self.region, signature_version='v4', retries={'max_attempts': 3, 'mode': 'standard'})
        self.ecs = boto3.client('ecs', aws_access_key_id=self.access_key_id, aws_secret_access_key=self.secret_access_key,config=self.config)
        self.task_definition = None
        self.updated_task_definition = None

        # log the input parameters
        logger.info('Task family: %s', self.family)
        logger.info('Task revision: %s', self.revision if self.revision else 'No revision provided. Using latest!')

    
    def download_task_definition(self):
        task_definition_identifier = self.family + ':' + self.revision if self.revision else self.family
        try:
            response = self.ecs.describe_task_definition(taskDefinition=task_definition_identifier)
        except Exception as error:
            raise error
        else:
            meta_data = response.pop('ResponseMetadata', None)
            logger.info(response.get('taskDefinition').get('requiredCompatibilities'))
            if meta_data['HTTPStatusCode'] == 200:
                self.task_definition = response['taskDefinition']
                task_definition_name = response['taskDefinition']['family'] + ':' + str(response['taskDefinition']['revision'])
                logger.info('Task definition: %s downloaded successfully!', task_definition_name)
                          

    def replace_image_uri(self):
        self.task_definition['containerDefinitions'][0]['image'] = self.image
        self.task_definition['requiresCompatibilities'] = ['FARGATE']
        logger.info('Image URI updated!')
         
       

    def save_new_task_definition(self):
        self.task_definition.pop("registeredAt", None)
        self.task_definition.pop("deregisteredAt", None)
        try:
            response = self.ecs.register_task_definition(containerDefinitions=self.task_definition['containerDefinitions'], family=self.family, executionRoleArn=self.task_definition['executionRoleArn'], taskRoleArn=self.task_definition['taskRoleArn'])
        except Exception as error:
            raise error
        else:
            self.updated_task_definition = response['taskDefinition']
            old_task_definition_name = self.task_definition['family'] + ':' + str(self.task_definition['revision'])
            new_task_definition_name = self.updated_task_definition['family'] + ':' + str(self.updated_task_definition['revision'])
            logger.info('Sucess: %s --> %s', old_task_definition_name, new_task_definition_name)
    
    def update_ecs_service(self):
        try:
            response = self.ecs.update_service(cluster=self.cluster_name, service=self.service_name, taskDefinition=self.updated_task_definition['family'] + ':' + str(self.updated_task_definition['revision']))
        except Exception as error:
            raise error
        else:
            meta_data = response.pop('ResponseMetadata')
            if meta_data['HTTPStatusCode'] == 200:
                logger.info('Sucess: Service %s updated successfully!', service_name)
            else:
                logger.error('Error: Service %s could not be updated!', service_name)
                logger.error('Error: %s', response)

if __name__ == "__main__":
    task_definition_config = TaskDefinitionConfig()
    task_def = task_definition_config.download_task_definition()
    task_definition_config.replace_image_uri()
    task_definition_config.save_new_task_definition()
    task_definition_config.update_ecs_service()