from gql import gql, Client
from omnikeeper_client.functions import get_access_token, create_graphql_client, create_logger, execute_graphql
from omnikeeper_client import simple_traits
import argparse
import logging
import yaml
import pandas as pd
import urllib3
urllib3.disable_warnings()
import uuid

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

def upsert_test_trait(client: Client):
    # create trait
    execute_graphql(client, gql("""
mutation {
  manage_upsertRecursiveTrait(
    trait: {
      id: "test"
      requiredAttributes: [
        {
          identifier:"id",
          template: {
            name:"test.id",
            type:INTEGER,
            isArray:false,
            isID:false,
            valueConstraints:[]
          }
        },
        {
          identifier:"array",
          template: {
            name:"test.array",
            type:TEXT,
            isArray:true,
            isID:false,
            valueConstraints:[]
          }
        }
      ]
      optionalAttributes: []
      optionalRelations: []
      requiredTraits: []
    }
  ) {
    id
  }
}
    """))

def main():
    args = parse_args()
    config = get_config(args.config_file)

    if 'log_level' not in config:
        print('Please provide the logging level in configuration file.')
        exit(1)

    logger = create_logger(logging.getLevelName(config['log_level']))

    access_token = get_access_token(config['oauth'])

    client = create_graphql_client(f"{config['omnikeeper']['url']}/graphql", access_token)

    # ensure our test trait exists
    upsert_test_trait(client)

    # test = simple_traits.get_all(client, trait_name="test", layers=["test"])
    # print (test)

    # hosts = simple_traits.get_all(client, trait_name="tsa_cmdb.host", layers=["tsa_cmdb"])
    # print (hosts)
    
    # host_interfaces = simple_traits.get_relation(client, trait_name="tsa_cmdb.host", relation_name="interfaces", layers=["tsa_cmdb"])
    # print (host_interfaces)

    # create a completely new data set (trait "test")
    df_init = pd.DataFrame.from_records([
        {"id": 1, "array": ["a", "b"]},
        {"id": 3, "array": ["c", "d"]}
    ])
    print("Initial dataframe:")
    print(df_init)
    print("")
    # insert that new data, this will also delete all old trait entities
    simple_traits.bulk_replace(client, trait_name="test", input=df_init, id_attributes=["id"], id_relations=[], write_layer="test", filter={})

    # get that data back out from omnikeeper, use it
    df_work = simple_traits.get_all(client, trait_name="test", layers=["test"])

    # change things in the returned data
    # change single value of existing data
    df_work.iat[0, df_work.columns.get_loc("array")] = ["a", "b", "z"]
    # add a new row, using our own created CIID
    df_work = pd.concat([df_work, pd.DataFrame([{"id": 4, "array": ["x"]}], index=[str(uuid.uuid4())])])
    # drop a row
    df_work.drop([df_work.index[1]], inplace = True)
    print("Work dataframe:")
    print (df_work)
    print("")

    # send our changes to omnikeeper
    simple_traits.set_all(client, trait_name="test", input=df_work, write_layer="test")
    
    # get that data back out from omnikeeper again
    df_final = simple_traits.get_all(client, trait_name="test", layers=["test"])
    print("Final dataframe:")
    print (df_final)
    print("")

if __name__ == "__main__":
    main()

