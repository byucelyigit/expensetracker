from azure.cosmos import CosmosClient, exceptions, PartitionKey
from config import COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COSMOS_DB_DATABASE, COSMOS_DB_EXPENSES_CONTAINER, COSMOS_DB_BUDGET_CONTAINER

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)

database = client.create_database_if_not_exists(id=COSMOS_DB_DATABASE)

expenses_container = database.create_container_if_not_exists(
    id=COSMOS_DB_EXPENSES_CONTAINER,
    partition_key=PartitionKey(path="/id"),
    offer_throughput=400
)

budget_container = database.create_container_if_not_exists(
    id=COSMOS_DB_BUDGET_CONTAINER,
    partition_key=PartitionKey(path="/budgetCode"),
    offer_throughput=400
)
