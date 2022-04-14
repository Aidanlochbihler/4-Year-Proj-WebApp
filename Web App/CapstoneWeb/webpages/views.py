from django.shortcuts import render, redirect
from CapstoneWeb import settings
from core.database import trip_col
import plotly
import plotly.express as px
from bson.objectid import ObjectId
from colorsys import hsv_to_rgb
from collections import defaultdict


def home(request):
    context = {'data': [1, 2, 3, 4, 'hi']}
    return render(request, 'webpages/home.html', context)


def welcome(request, sort_by='UploadTime', is_ascending=0):
    is_ascending = bool(is_ascending)

    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    t = trip_col.find({"user_id": request.user.id}, {"data": 0, "data_raw": 0})
    t = list(t)
    icons = {i: ' ' for i in ['TripDuration', 'Filename', 'StartTime', 'EndTime', 'UploadTime']}

    if sort_by == 'TripDuration':
        t = sorted(t, key=lambda i: i['EndTime'] - i['StartTime'], reverse=is_ascending)

    elif sort_by in icons.keys():
        t = sorted(t, key=lambda i: i[sort_by], reverse=is_ascending)

    # elif sort_by == 'EndTime':
    #     t = sorted(t, key=lambda i: i['EndTime'], reverse=is_ascending)

    # elif sort_by == 'DateUploaded':
    #     t = sorted(t, key=lambda i: i['StartTime'], reverse=is_ascending)

    if is_ascending:
        icons[sort_by + "Icon"] = '▲'
    else:
        icons[sort_by + "Icon"] = '▼'

    for trip in t:
        trip['_id'] = str(trip['_id'])
        trip['StartTime'] = str(trip['StartTime'])
        trip['EndTime'] = str(trip['EndTime'])
        trip['UploadTime'] = str(trip['UploadTime'])
        # trip['_id'] = str(trip['_id'])

    if is_ascending:
        sort_direction = 0
    if not is_ascending:
        sort_direction = 1
    t = str(t).replace("'", '"')

    context = {"trips": t, "sort_direction": sort_direction} | icons
    return render(request, 'webpages/welcome.html', context)


def grid(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    trips = trip_col.find({"user_id": request.user.id})
    trips = list(trips)

    grid = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    # print(trips[0]['data'][0])
    # print(trips[0]['data'][0]['Lat'])
    # print(round(trips[0]['data'][0]['Lat'] / 0.00005) * 0.00005)
    # print(round(trips[0]['data'][0]['Long'] / 0.00007) * 0.00007)
    grid_height = 0.00005  # height
    grid_width = 0.00007  # width
    for trip in trips:
        for data_point in trip['data']:
            avg_acc = (data_point["X"]**2 + data_point["Y"]**2 + data_point["Z"]**2)**(0.5)
            rounded_lat = round(data_point['Lat'] / grid_height) * grid_height - grid_height / 2
            rounded_lat = str(round(rounded_lat, 10))
            rounded_long = round(data_point['Long'] / grid_width) * grid_width - grid_width / 2
            rounded_long = str(round(rounded_long, 10))
            grid[rounded_lat][rounded_long]['accsum'] += avg_acc
            grid[rounded_lat][rounded_long]['count'] += 1

    grid = dict(grid)
    for rounded_lat in grid:
        grid[rounded_lat] = dict(grid[rounded_lat])
        for rounded_long in grid[rounded_lat]:
            avg_acc = grid[rounded_lat][rounded_long]['accsum'] / \
                grid[rounded_lat][rounded_long]['count']
            red, green, blue = hsv_to_rgb(min(max(-0.075 * avg_acc + 0.3, 0), 0.3), 0.9, 1)
            grid[rounded_lat][rounded_long]['color'] = f'#{"{0:0{1}x}".format(int(red*254),2)}{"{0:0{1}x}".format(int(green*254),2)}{"{0:0{1}x}".format(int(blue*254),2)}'
            grid[rounded_lat][rounded_long] = dict(grid[rounded_lat][rounded_long])
    print(grid[rounded_lat][rounded_long])

    context = {'grid': grid, 'grid_height': grid_height, 'grid_width': grid_width}

    return render(request, 'webpages/grid.html', context)


def inspect_trip(request, trip_id):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    trip = trip_col.find_one({"_id": ObjectId(trip_id), "user_id": request.user.id}, {
                             "_id": 0, "user_id": 0})

    DateTimes = []
    acc = []
    axis = []
    points = []
    colors = []
    x_vals = []
    y_vals = []
    count = 0
    for data_point in trip["data"]:
        count += 1
        points += [{"lat": data_point["Lat"], "lng":data_point["Long"]}]

        avg_acc = (data_point["X"]**2 + data_point["Y"]**2 + data_point["Z"]**2)**(0.5)
        red, green, blue = hsv_to_rgb(min(max(-0.075 * avg_acc + 0.3, 0), 0.3), 0.9, 1)
        colors += [f'#{"{0:0{1}x}".format(int(red*254),2)}{"{0:0{1}x}".format(int(green*254),2)}{"{0:0{1}x}".format(int(blue*254),2)}']

        acc += [data_point[n] for n in data_point if n == "X"]
        acc += [data_point[n] for n in data_point if n == "Y"]
        acc += [data_point[n] for n in data_point if n == "Z"]
        axis += ["X", "Y", "Z"]
        DateTimes += [data_point[n] for n in data_point if n == "DateTime"]
        DateTimes += [data_point[n] for n in data_point if n == "DateTime"]
        DateTimes += [data_point[n] for n in data_point if n == "DateTime"]

        x_vals += [str(data_point[n]) for n in data_point if n == "DateTime"]
        y_vals += [avg_acc]

    fig = px.scatter({"DateTime": DateTimes, "Accleration": acc, "Axis": axis},
                     x="DateTime", y="Accleration", color="Axis")
    graph_div = plotly.offline.plot(fig, auto_open=False, output_type="div")
    points = str(points).replace("'", '"')
    colors = str(colors).replace("'", '"')
    x_vals = str(x_vals).replace("'", '"')
    context = {'graph_div': graph_div, "cords": points, "colors": colors, 'x_vals': x_vals,
               'y_vals': y_vals, 'trip_id': str(trip_id), 'Filename': trip['Filename']}
    return render(request, 'webpages/trip.html', context)
