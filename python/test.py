import sys
from omnikeeper_client.functions import get_access_token, create_graphql_client, execute_graphql

def main(argv):

    config = dict(
        client_id = "omnikeeper",
        omnikeeper_url = "http://localhost:9080/backend",
        username="testuser",
        password="123123"
    )

    access_token = get_access_token(config)

    client = create_graphql_client("%s/graphql" % config['omnikeeper_url'], access_token)

    query = """
        query {
            ciids
        }
    """
    result = execute_graphql(client, query)

    print(result)

    return 0

if __name__ == "__main__":
   main(sys.argv[1:])

