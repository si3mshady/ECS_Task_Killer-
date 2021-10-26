import boto3,  datetime

ecs = boto3.client('ecs', region_name='us-east-1')
current_time = datetime.datetime.now().astimezone()

def get_chaos_cluster_arn(event,context):
  
    return [cluster for cluster in  ecs.list_clusters().get('clusterArns', None) \
        if event['cluster_name'] in cluster.split('/')[-1]][0]

def get_cluster_tasks(event,context):    
    print(event, context)    
    tasks = ecs.list_tasks(cluster=event['cluster_arn']).get('taskArns', None)
    return tasks

def manage_running_tasks(event,context):

        number_of_tasks = len(event['tasks'])
        print("number of tasks",number_of_tasks)
        max_containers_to_kill = 2
        tasks_killed = 0

        for task in event['tasks']:
            started = ecs.describe_tasks(tasks=[task],cluster=event['cluster_arn'])['tasks'][0].get('startedAt',None)
            try:
                delta_hours  = (current_time - started).seconds / 60 / 60  #hours               
                if delta_hours <= 2:
                    if tasks_killed <= max_containers_to_kill -1:   
                        ecs.stop_task(task=task, cluster=event['cluster_arn'])                    
                        tasks_killed += 1
                      
                
            except Exception as e:
                print(e)

        return f'killed {tasks_killed} tasks'
