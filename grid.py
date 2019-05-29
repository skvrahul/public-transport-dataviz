import json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import os
import pickle
import requests

#Defines the BASE_POINT as the Mustek Metro station.
BASE_POINT = Point(14.4243832,50.083593)

def get_walking_time(p2, p1=BASE_POINT):
    URL = 'http://dev.virtualearth.net/REST/V1/Routes/Transit?timeType=Departure&dateTime=1:00:00PM&output=json&key=<APIKEYGOESHERE>'
    params = {'wp.0':str(p1.y)+','+str(p1.x), 'wp.1':str(p2.y)+','+str(p2.x)}
    try:
        resp = requests.get(URL, params = params)
        resp = resp.json()
        print(params)
        transits = resp['resourceSets'][0]['resources'][0]['routeLegs'][0]['itineraryItems']
        walkingTime = 0
        walkingDist = 0
        for t in transits:
            if t['iconType'] == 'Walk':
                walkingTime += float(t['travelDuration'])
                walkingDist+= float(t['travelDistance'])
        walkingTime/=60
        return (walkingTime, walkingDist)
    except:
        return None


def create_grid(bbox,polygon ,num_intervals=50):
    #Y, X = Lat, Long
    lowY = float(bbox[0])
    highY = float(bbox[1])
    lowX =float( bbox[2])
    highX =float( bbox[3])
    gridPoints = []
    intervalX = (highX - lowX)/num_intervals
    intervalY = (highY - lowY)/num_intervals
    print('Interval X :', intervalX)
    print('Interval Y :', intervalY)
    for i in range(num_intervals+1):
        for j in range(num_intervals+1):
           point = Point(lowX + (i*intervalX), lowY+ (j*intervalY)) 
           if point.within(polygon):
               gridPoints.append(point)
    print(len(gridPoints), ' points added')
    return gridPoints 

def get_grid(num_intervals=50):
    f = open('prague_bounding_box.json')
    if(os.path.exists('./points.pkl')):
        pklf = open('./points.pkl', 'rb')
        return pickle.load(pklf)
    pragueJson = json.load(f)[0]
    praguePoints = pragueJson['geojson']['coordinates'][0]
    #praguePoly = Polygon(praguePoints, pragueJson['boundingbox'])

    points = [Point((p[0], p[1])) for p in praguePoints]
    points_tuples = [(p[0], p[1]) for p in praguePoints]
    polygon = Polygon(points_tuples)
    grid = create_grid(pragueJson['boundingbox'], polygon, num_intervals = num_intervals)    
    pklf = open('./points.pkl', 'wb')
    print('saving points to points.pkl')
    pickle.dump(grid, pklf)
    return grid
