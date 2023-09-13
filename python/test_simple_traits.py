from gql import Client, gql
from omnikeeper_client.functions import get_access_token, create_graphql_client, create_logger
from omnikeeper_client import simple_traits
import argparse
import logging
import yaml
import pandas as pd
from gql.transport.requests import RequestsHTTPTransport
import urllib3
urllib3.disable_warnings()

def get_config(config_file_path: str) -> dict:
    """Parses the configuration file and returns the parsed content in a dictionary format."""
    try:
        with open(config_file_path, "r") as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_file_path}")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Unable to parse config file at {config_file_path}: {e}")
        exit(1)

def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(description='omnikeeper-api-tests')
    parser.add_argument('--config_file', type=str, required=False, help=' Configuration file location', default='config/config.yml')
    return parser.parse_args()

def main():
    args = parse_args()
    config = get_config(args.config_file)

    if 'log_level' not in config:
        print('Please provide the logging level in configuration file.')
        exit(1)

    logger = create_logger(logging.getLevelName(config['log_level']))

    access_token = get_access_token(config['oauth'])

    client = create_graphql_client(f"{config['omnikeeper']['url']}/graphql", access_token)

    # test = simple_traits.get_all(client, trait_name="test", layers=["test"])
    # print (test)

    # hosts = simple_traits.get_all(client, trait_name="tsa_cmdb.host", layers=["tsa_cmdb"])
    # print (hosts)
    
    # host_interfaces = simple_traits.get_relation(client, trait_name="tsa_cmdb.host", relation_name="interfaces", layers=["tsa_cmdb"])
    # print (host_interfaces)

    df = pd.DataFrame.from_records([
        {"id": 1, "array": ["a", "b"]},
        {"id": 3, "array": ["c", "d"]}
    ])
    simple_traits.bulk_replace(client, trait_name="test", input=df, id_attributes=["id"], id_relations=[], write_layer="test", filter={"foo": 2})

    df_returned = simple_traits.get_all(client, trait_name="test", layers=["test"])
    print (df_returned)

if __name__ == "__main__":
    main()

