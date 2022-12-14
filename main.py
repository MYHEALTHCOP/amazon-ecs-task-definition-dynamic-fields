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
        self.new_revision = self.revision
        self.region = os.environ.get('INPUT_AWS-REGION')
        self.access_key_id = os.environ.get('INPUT_AWS-ACCESS-KEY-ID')
        self.secret_access_key = os.environ.get('INPUT_AWS-SECRET-ACCESS-KEY')
        self.image = os.environ.get('INPUT_IMAGE-URI')
        self.service_name = os.environ.get('INPUT_SERVICE-NAME')
        self.cluster_name = os.environ.get('INPUT_CLUSTER-NAME')
        self.task_definition_name = self.family + ':' + self.revision if self.revision else self.family
        self.config = Config(region_name=self.region, signature_version='v4', retries={'max_attempts': 3, 'mode': 'standard'})
        self.ecs = boto3.client('ecs', aws_access_key_id=self.access_key_id, aws_secret_access_key=self.secret_access_key,config=self.config)
        self.task_definition = dict()
        self.task_role_arn = self.task_definition.get('taskRoleArn')
        self.execution_role_arn = self.task_definition.get('executionRoleArn')
        self.container_definitions = self.task_definition.get('containerDefinitions')
    
    @staticmethod
    def validate_inputs():
        if not self.family:
            raise ValueError('Task family is required!')
        if not self.image:
            raise ValueError('Image URI is required!')
        if not self.service_name:
            raise ValueError('Service name is required!')
        if not self.cluster_name:
            raise ValueError('Cluster name is required!')
        if not self.region:
            raise ValueError('AWS region is required!')
        if not self.access_key_id:
            raise ValueError('AWS access key is required!')
        if not self.secret_access_key:
            raise ValueError('AWS secret access key is required!')
        
        logger.info('Task family: %s', self.family)
        logger.info('Task revision: %s', self.revision if self.revision else 'No revision provided. Using latest!')
        logger.info('Image URI recieved!')
        logger.info('Service was provided!')
        logger.info('Cluster was provided!')
        logger.info('AWS region was provided!')
        logger.info('AWS access key was provided!')
        logger.info('AWS secret access key was provided!')

    @staticmethod
    def download_task_definition():
        try:
            response = self.ecs.describe_task_definition(taskDefinition=self.task_definition_name)
        except Exception as error:
            raise error
        else:
            meta_data = response.pop('ResponseMetadata', None)
            
            if meta_data['HTTPStatusCode'] == 200:
                self.task_definition = self.purge_useless_keys(response['taskDefinition'])
                self.revision = self.task_definition['revision']
                self.task_role_arn = self.task_definition.get('taskRoleArn')
                self.execution_role_arn = self.task_definition.get('executionRoleArn')
                self.container_definitions = self.task_definition.get('containerDefinitions')
                logger.info('Task definition: %s downloaded successfully!', self.task_definition_name)

    def purge_useless_keys(self, taskdef:dict)-> dict: 
        keys = ['registeredAt', 'deregisteredAt', 'ResponseMetadata']
        for key in keys:
            taskdef.pop(key, None)
        return taskdef


    def fill_in_required_info(self):
        self.container_definitions[0]['image'] = self.image
        logger.info('Image URI and other info updated!')
         
       
    @staticmethod
    def save_new_task_definition():
        try:
            response = self.ecs.register_task_definition(containerDefinitions=self.container_definitions, family=self.family, executionRoleArn=self.execution_role_arn, taskRoleArn=self.task_role_arn)
        except Exception as error:
            raise error
        else:
            self.new_revision = response['taskDefinition']['revision']
            logger.info('Sucess: %s:%d --> %s:%d', self.family, self.revision, self.family, self.new_revision)
    
    @staticmethod
    def update_ecs_service():
        try:
            response = self.ecs.update_service(cluster=self.cluster_name, service=self.service_name, taskDefinition=self.task_definition_name, forceNewDeployment=True)
        except Exception as error:
            raise error
        else:
            meta_data = response.pop('ResponseMetadata')
            if meta_data['HTTPStatusCode'] == 200:
                logger.info('Sucess: Service %s updated successfully!', self.service_name)
            else:
                logger.error('Error: Service %s could not be updated!', self.service_name)
                logger.error('Error: %s', response)
    
    @staticmethod
    def wait_for_service_stability():
        waiter = self.ecs.get_waiter('services_stable')
        waiter.wait(cluster=self.cluster_name, services=[self.service_name], WaiterConfig={'Delay': 10, 'MaxAttempts': 20})

if __name__ == "__main__":
    TaskDefinitionConfig.validate_inputs()
    TaskDefinitionConfig.download_task_definition()
    TaskDefinitionConfig.fill_in_required_info()
    TaskDefinitionConfig.save_new_task_definition()
    TaskDefinitionConfig.update_ecs_service()
    TaskDefinitionConfig.wait_for_service_stability()
