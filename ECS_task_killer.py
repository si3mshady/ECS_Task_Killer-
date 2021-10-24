import boto3,  datetime


class ECS_MGMT:
    def __init__(self):
        self.ecs = boto3.client('ecs', region_name='us-east-1')
        self.current_time = datetime.datetime.now().astimezone()

    def get_chaos_cluster_arn(self):
        return [cluster for cluster in  self.ecs.list_clusters().get('clusterArns', None) \
        if 'chaos' in cluster.split('/')[-1]][0]

    def get_cluster_tasks(self,cluster):
        return self.ecs.list_tasks(cluster=cluster).get('taskArns', None)

    def manage_running_tasks(self,taskList, cluster):

        number_of_tasks = len(taskList)
        print("number of tasks",number_of_tasks)
        max_containers_to_kill = 2
        tasks_killed = 0

        for task in taskList:
            started = self.ecs.describe_tasks(tasks=[task],cluster=cluster)\
            ['tasks'][0].get('startedAt',None)
            try:
                delta_hours  = (self.current_time - started).seconds / 60 / 60  #hours                
                if delta_hours <= 2:
                    if tasks_killed <= max_containers_to_kill -1:   
                        self.ecs.stop_task(task=task, cluster=cluster)                    
                        tasks_killed += 1
                      
                print(f'killed {tasks_killed} tasks')
            except Exception as e:
                print(e)
                

    def init(self):
        cluster_arn = self.get_chaos_cluster_arn()
        task_list = self.get_cluster_tasks(cluster_arn)
        self.manage_running_tasks(task_list,cluster_arn)


def lambda_handler(event,context):
    mgmt = ECS_MGMT()
    mgmt.init()
    
    
#Elliott Arnold - ECS practice - use AWS lambda to stop running ECS tasks after a given time period
#10-24-21
