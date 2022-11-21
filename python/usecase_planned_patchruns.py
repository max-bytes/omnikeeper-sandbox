import sys
from gql import gql, Client
from omnikeeper_client.functions import get_access_token, create_graphql_client, create_layer, upsert_layerdata, hexString2RGBColor, execute_graphql, truncate_layer, create_ci
import time
import pprint
from typing import (
    Any,
    Dict
)

def bulk_replace_planned_patchruns(client: Client, target_layer: str, target_schedule_group: str, runs: list[Dict[str, Any]]):
  response = execute_graphql(client, gql("""
mutation($layers: [String]!, $writeLayer: String!, $targetScheduleGroup: String!, $input: [TE_Upsert_Input_patchmgnt__planned_patchrun]!) {
  bulkReplaceByFilter_patchmgnt__planned_patchrun(
    layers: $layers
    writeLayer: $writeLayer
    filter: {scheduleGroup: {exact: $targetScheduleGroup}}
    input: $input
    idAttributes: ["scheduleGroup", "targetDate"]
    idRelations: ["patchwindowID"]
  ) {
    success
    isNoOp
    changeset {
      ciAttributes {
        ciid
        attributes {
          name
        }
      }
      removedCIAttributes {
        ciid
        attributes {
          name
        }
      }
    }
  }
}
    """), dict(
        layers = [target_layer],
        writeLayer = target_layer,
        targetScheduleGroup = target_schedule_group,
        input = runs
    ))
  return response['bulkReplaceByFilter_patchmgnt__planned_patchrun']

def get_planned_patchruns(client: Client, target_layer: str):
    query = gql("""
query($layers: [String]!) {
  traitEntities(layers: $layers) {
    patchmgnt__planned_patchrun {
      all {
        entity {
          scheduleGroup
          startTime
          endTime
          targetDate
          patchwindowID {
            relatedCIID
          }
        }
      }
    }
  }
}
    """)
    response = execute_graphql(client, query, dict(layers = [target_layer]))

    return list(map(lambda e: e['entity'], response['traitEntities']['patchmgnt__planned_patchrun']['all']))

def main(argv):

    pp = pprint.PrettyPrinter(indent=4)

    # connect to omnikeeper and get graphql client
    config = dict(
        client_id = "omnikeeper",
        omnikeeper_url = "http://localhost:9080/backend",
        username="testuser",
        password="123123"
    )
    access_token = get_access_token(config)
    client = create_graphql_client("%s/graphql" % config['omnikeeper_url'], access_token)

    target_layer = "testlayer"

    # create layer, if it does not exist and set layer data
    create_layer(client, target_layer)
    upsert_layerdata(client, target_layer, "test-layer", hexString2RGBColor("#FF00FF"))

    # empty layer, if anything is inside
    truncate_layer(client, target_layer)

    # create trait
    execute_graphql(client, gql("""
mutation {
  manage_upsertRecursiveTrait(
    trait: {
      id: "patchmgnt.planned_patchrun"
      requiredAttributes: [
        {
          identifier:"scheduleGroup",
          template: {
            name:"patchmgnt.planned_patchrun.schedule_group",
            type:TEXT,
            isArray:false,
            isID:false,
            valueConstraints:[]
          }
        },
        {
          identifier:"startTime",
          template: {
            name:"patchmgnt.planned_patchrun.start_time",
            type:DATE_TIME_WITH_OFFSET,
            isArray:false,
            isID:false,
            valueConstraints:[]
          }
        },
        {
          identifier:"endTime",
          template: {
            name:"patchmgnt.planned_patchrun.end_time",
            type:DATE_TIME_WITH_OFFSET,
            isArray:false,
            isID:false,
            valueConstraints:[]
          }
        },
        {
          identifier:"targetDate",
          template: {
            name:"patchmgnt.planned_patchrun.target_date",
            type:TEXT,
            isArray:false,
            isID:false,
            valueConstraints:[]
          }
        }
      ]
      optionalAttributes: []
      optionalRelations: [
        {
          identifier: "patchwindowID",
          template: {
            predicateID: "belongs_to_patchwindow",
            directionForward: true,
            traitHints: ["patchmgnt.patchwindow"]
          }
        }
      ]
      requiredTraits: []
    }
  ) {
    id
  }
}
    """))

    # wait until graphql model is updated
    time.sleep(5)

    # create an empty CI just for testing purposes to have a CI to relate planned_patchruns to
    test_patchwindow_ciid = create_ci(client, "test-patchwindow", target_layer)

    # insert initial set of planned patchruns
    bulk_replace_planned_patchruns(client, target_layer, "schedule_group_1", [
            {"scheduleGroup": "schedule_group_1", "startTime": "2022-11-17T00:00:00Z", "endTime": "2022-11-17T12:00:00Z", "targetDate": "2022-11-17", "patchwindowID": [str(test_patchwindow_ciid)]},
            {"scheduleGroup": "schedule_group_1", "startTime": "2022-11-24T00:00:00Z", "endTime": "2022-11-25T09:30:00Z", "targetDate": "2022-11-24", "patchwindowID": [str(test_patchwindow_ciid)]},
            {"scheduleGroup": "schedule_group_1", "startTime": "2022-11-25T00:00:00Z", "endTime": "2022-11-26T09:30:00Z", "targetDate": "2022-11-25", "patchwindowID": [str(test_patchwindow_ciid)]}
    ])

    # check what's in omnikeeper
    query_results1 = get_planned_patchruns(client, target_layer)
    print("State after initial set:")
    pp.pprint(query_results1)

    # insert another set of planned patchruns
    bulk_replace_planned_patchruns(client, target_layer, "schedule_group_2", [
            {"scheduleGroup": "schedule_group_2", "startTime": "2022-12-17T00:00:00Z", "endTime": "2022-12-17T12:00:00Z", "targetDate": "2022-12-17", "patchwindowID": [str(test_patchwindow_ciid)]}
    ])

    query_results2 = get_planned_patchruns(client, target_layer)
    print("State after additional set:")
    pp.pprint(query_results2)

    # update first set of planned patchruns
    response = bulk_replace_planned_patchruns(client, target_layer, "schedule_group_1", [
            # {"scheduleGroup": "schedule_group_1", "startTime": "2022-11-17T00:00:00Z", "endTime": "2022-11-17T12:00:00Z", "targetDate": "2022-11-17", "patchwindowID": [str(test_patchwindow_ciid)]}, <- removed
            {"scheduleGroup": "schedule_group_1", "startTime": "2022-11-24T00:00:00Z", "endTime": "2022-11-25T09:30:00Z", "targetDate": "2022-11-24", "patchwindowID": [str(test_patchwindow_ciid)]}, # <- unchanged
            {"scheduleGroup": "schedule_group_1", "startTime": "2022-11-25T00:00:00Z", "endTime": "2022-11-26T10:30:00Z", "targetDate": "2022-11-25", "patchwindowID": [str(test_patchwindow_ciid)]}, # <- changed
            {"scheduleGroup": "schedule_group_1", "startTime": "2022-11-30T00:00:00Z", "endTime": "2022-11-30T09:30:00Z", "targetDate": "2022-11-30", "patchwindowID": [str(test_patchwindow_ciid)]}, # <- new
    ])

    print("Response of update of first set:")
    pp.pprint(response)

    query_results3 = get_planned_patchruns(client, target_layer)
    print("State after update of first set:")
    pp.pprint(query_results3)

    return 0

if __name__ == "__main__":
   main(sys.argv[1:])
