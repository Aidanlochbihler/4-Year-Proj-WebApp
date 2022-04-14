import graphene
# from core.database import client
from core.database import trip_col
from .Queries import *
import json
from datetime import datetime
from statistics import median


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


class AddTripMutation(graphene.ObjectType):
    add_trip = graphene.Field(Success,
                              trip=graphene.String(""),
                              filename=graphene.String(""))

    def resolve_add_trip(self, info, trip,filename):
        print(filename)
        data = trip.replace("'", '"')
        data = json.loads(data)
        # data = [{'date':datetime.fromisoformat(d)}|{n:data[d][n] for n in data[d]}for d in data]
        data_formatted = []
        for d in data:
            if len(d) == 6:
                try:
                    data_formatted += [{'DateTime': datetime.strptime(d['DateTime'], "%Y-%m-%dT%H:%M:%S.00")} | {
                        n: d[n] for n in d if n != 'DateTime'}]
                except:
                    pass
        for i in range(-len(data_formatted), 0, 1):
            if data_formatted[i]['Lat'] == data_formatted[i + 1]['Lat'] and data_formatted[i]['Long'] == data_formatted[i + 1]['Long']:
                data_formatted.pop(i)
                # print(f"poped {i} because of duplicate lat and long")
                continue

            neighbours = data_formatted[max(i - 5, -len(data_formatted)):min(i + 5, -1)]

            median_Lat = median([n["Lat"] for n in neighbours])
            median_Long = median([n["Long"] for n in neighbours])

            Lat = data_formatted[i]['Lat']
            Long = data_formatted[i]['Long']

            if abs(Lat) > abs(median_Lat * 1.1) or abs(Lat) < abs(median_Lat * 0.9) or abs(Long) > abs(median_Long * 1.1) or abs(Long) < abs(median_Long * 0.9):
                data_formatted.pop(i)
                # print(f"poped {i} because of wrong lat or long")

        duration = data_formatted[-1]['DateTime'] - data_formatted[0]['DateTime']
        # print(duration)
        trip_col.insert_one({'user_id': info.context.user.id, 'data': data_formatted,
                             'duration': str(duration),
                             'Filename': filename,
                             'StartTime': data_formatted[0]['DateTime'],
                             'EndTime': data_formatted[-1]['DateTime']})
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


class Mutation(AddTripMutation, graphene.ObjectType):
    pass


# schema = graphene.Schema(query=Query,mutation=Mutation)
schema = graphene.Schema(query=Query, mutation=Mutation)
