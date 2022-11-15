import sys
from omnikeeper_client.functions import get_access_token, create_graphql_client, create_layer, upsert_layerdata, hexString2RGBColor, mutate_cis, get_ci_attributes, build_graphQL_InsertCIAttributeInputType, create_ci, truncate_layer

def main(argv):

    # connect to omnikeeper and get graphql client
    config = dict(
        client_id = "omnikeeper",
        omnikeeper_url = "http://localhost:9080/backend",
        username="testuser",
        password="123123"
    )
    access_token = get_access_token(config)
    client = create_graphql_client("%s/graphql" % config['omnikeeper_url'], access_token)

    # create layer, if it does not exist and set layer data
    create_layer(client, "testlayer")
    upsert_layerdata(client, "testlayer", "description", hexString2RGBColor("#FF00FF"))

    # empty layer, if anything is inside
    truncate_layer(client, "testlayer")

    # create a single CI with a name attribute
    ciid1 = create_ci(client, "test-ci01", "testlayer")

    # insert an attribute
    mutate_cis(client, "testlayer", ["testlayer"], [build_graphQL_InsertCIAttributeInputType(ciid1, "test_attribute_1", "test_value_1")])

    # read CI
    ci_attributes = get_ci_attributes(client, ["testlayer"], [ciid1])

    print(ci_attributes)

    return 0

if __name__ == "__main__":
   main(sys.argv[1:])

