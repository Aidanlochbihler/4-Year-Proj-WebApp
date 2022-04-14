import graphene
# from core.database import client
from bson.objectid import ObjectId
from core.database import trip_col
from .Queries import *
import json
from datetime import datetime
from statistics import median
from datetime import datetime

class Hi(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info):
        if info.context.user.has_perm('can_view_all'):
            return 'Hi'
        else:
            return None


class Hi2(graphene.ObjectType):
    hello2 = graphene.String(default_value="Hi2")

# schema = graphene.Schema(query=Query)


# import graphene
# from graphql_auth.schema import UserQuery, MeQuery
# from graphql_auth import mutations
# import graphene
# import graphql_jwt

# class AuthMutation(graphene.ObjectType):
#   token_auth = graphql_jwt.ObtainJSONWebToken.Field()
#   verify_token = graphql_jwt.Verify.Field()
#   refresh_token = graphql_jwt.Refresh.Field()
class Success(graphene.ObjectType):
    success = graphene.Boolean()


class RemoveTripMutation(graphene.ObjectType):
    remove_trip = graphene.Field(Success, trip_id=graphene.String(""))

    def resolve_remove_trip(self, info, trip_id):
        trip_col.delete_one({'_id': ObjectId(trip_id)})

        return {"success": True}


class AddTripMutation(graphene.ObjectType):
    add_trip = graphene.Field(Success,
                              trip=graphene.String(""),
                              filename=graphene.String(""))

    def resolve_add_trip(self, info, trip, filename):
        print(filename)
        data = trip.replace("'", '"')
        data = json.loads(data)
        # data = [{'date':datetime.fromisoformat(d)}|{n:data[d][n] for n in data[d]}for d in data]
        offsets = {'X': 0, 'Y': 0, 'Z': 0}
        count = 0
        for d in data[2:7]:
            if len(d) == 9:
                count += 1
                for n in offsets:
                    offsets[n] += d[f'MIN{n}'] + d[f'MAX{n}']
        for n in offsets:
            offsets[n] = offsets[n]/(count*2)
        data_raw = []
        data_processed = []
        for d in data:
            # print(d)
            if len(d) == 9:
                try:
                    data_raw += [{'DateTime': datetime.strptime(d['DateTime'], "%Y-%m-%dT%H:%M:%S.00")} | {
                        n: d[n] for n in d if n != 'DateTime'}]
                except:
                    pass
        for i in range(-len(data_raw), 0, 1):
            # if data_raw[i]['Lat'] == data_raw[i + 1]['Lat'] and data_raw[i]['Long'] == data_raw[i + 1]['Long']:
            #     data_raw.pop(i)
            #     # print(f"poped {i} because of duplicate lat and long")
            #     continue

            neighbours = data_raw[max(i - 5, -len(data_raw)):min(i + 5, -1)]

            median_Lat = median([n["Lat"] for n in neighbours])
            median_Long = median([n["Long"] for n in neighbours])

            Lat = data_raw[i]['Lat']
            Long = data_raw[i]['Long']

            if abs(Lat) > abs(median_Lat * 1.1) or abs(Lat) < abs(median_Lat * 0.9) or abs(Long) > abs(median_Long * 1.1) or abs(Long) < abs(median_Long * 0.9):
                data_raw.pop(i)
                # print(f"poped {i} because of wrong lat or long")
        
        for d in data_raw:
            data_processed += [{'DateTime': d['DateTime'], 'Lat': d['Lat'], 'Long': d['Long']}]
            for n in offsets:
                data_processed[-1][n] = max(abs(d[f'MAX{n}']-offsets[n]), abs(d[f'MIN{n}']-offsets[n]))

        # print(data_raw)
        duration = data_raw[-1]['DateTime'] - data_raw[0]['DateTime']
        # print(duration)
        trip_col.insert_one({'user_id': info.context.user.id, 'data': data_processed,
                             'data_raw': data_raw,
                             'duration': str(duration),
                             'Filename': filename,
                             'UploadTime': datetime.utcnow(),
                             'StartTime': data_raw[0]['DateTime'],
                             'EndTime': data_raw[-1]['DateTime']})
        return {"success": True}


class Trips(graphene.ObjectType):
    trips = graphene.String()


class GetAllTripsQuery(graphene.ObjectType):
    get_all_trips = graphene.Field(Trips)

    def resolve_get_all_trips(self, info):
        trips = trip_col.find({"user_id": info.context.user.id}, {"_id": 0, "user_id": 0})

        return {"success": True, "trips": list(trips).__str__()}


class Query(Hi, Hi2, GetAllTripsQuery, graphene.ObjectType):
    pass


class Mutation(AddTripMutation,RemoveTripMutation, graphene.ObjectType):
    pass


# schema = graphene.Schema(query=Query,mutation=Mutation)
schema = graphene.Schema(query=Query, mutation=Mutation)
