# amazon-ecs-task-definition-dynamic-fields
When you want to update your  amazon ecs task definition, the official action only allows updating the image URI. Additionally, you have to check a copy of your task definition to version control. This requirement, create a pain-point for people managing their infrastructure with tools like terraform. You can easily update any parameter in your terraform config and deploy instantly. But this will create drift between your live version and the copy in version control. This action is designed to overcome this pain. It first downloads the latest active revision of your task definition, fills in the specified fields and uploads it back to you ECS as new revision. 

# Why you need it


# Hello world docker action

This action prints "Hello World" or "Hello" + the name of a person to greet to the log.

## Inputs

## `who-to-greet`

**Required** The name of the person to greet. Default `"World"`.

## Outputs

## `time`

The time we greeted you.

## Example usage

uses: actions/hello-world-docker-action@v2
with:
  who-to-greet: 'Mona the Octocat'