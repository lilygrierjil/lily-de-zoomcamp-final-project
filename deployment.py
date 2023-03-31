from flows.full_etl import main_flow
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import IntervalSchedule


deployment = Deployment.build_from_flow(
    flow=main_flow,
    name="one-time-deployment", 
    version=1, 
    work_queue_name="default",
)

daily_deployment = Deployment.build_from_flow(
    flow=main_flow,
    name="daily-deployment", 
    version=1, 
    work_queue_name="default",
    schedule=(IntervalSchedule(interval=86400))
)
if __name__=='__main__':
    deployment.apply()
    daily_deployment.apply()