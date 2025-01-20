import h3
from geopandas import GeoDataFrame
from shapely.geometry import Polygon, Point
import shapely.wkt
import geopandas as gpd
import numpy as np
import plotly.express as px
from shapely.geometry import Polygon
import pandas as pd
from geojson import Feature, Point, FeatureCollection, Polygon
import json
import matplotlib.pyplot as plt
# def output_h3_id_attributes(h3_id):
#     return {
#         "co_ordinates" : h3.h3_to_geo(h3_id),
#         "geo_boundary" : Polygon(h3.h3_to_geo_boundary(h3_id, geo_json=True)).wkt,
#         "parent" : h3.h3_to_parent(h3_id),
#         "children" : h3.h3_to_children(h3_id)
#     }
#
#
# def add_geometry(row):
#   points = h3.h3_to_geo_boundary(row['h3_cell'], True)
#   return Polygon(points)
# #Apply function into our dataframe
#
#
# print(output_h3_id_attributes('8843acd819fffff'))

H3_res = 5


def geo_to_h3(row):
    return h3.geo_to_h3(lat=row.lat, lng=row.lng, resolution=H3_res)


def add_geometry(row):
    try:
        points = h3.h3_to_geo_boundary(row['H3_CELL'], True)
        expected_coordinates = [[[coord[0], coord[1]] for coord in points]]
        # print("Printing Points: ")
        # print(points)
        # print(expected_coordinates)
        # print(Polygon(points))
        return {
            "coordinates": expected_coordinates,
            "type": "Polygon"
        }
    except Exception as e:
        print(row['H3_CELL'])
        print("error in add_geometry", e)

    #return Polygon(points)


def hexagons_dataframe_to_geojson(df_hex, hex_id_field, geometry_field, value_field, file_output=None):
    list_features = []

    for i, row in df_hex.iterrows():
        feature = Feature(geometry=row[geometry_field],
                          id=row[hex_id_field],
                          properties={
                              value_field: row[value_field],
                              hex_id_field: row[hex_id_field]
                          })
        list_features.append(feature)

    feat_collection = FeatureCollection(list_features)

    if file_output is not None:
        with open(file_output, "w") as f:
            json.dump(feat_collection, f)

    return feat_collection


fire_ignitions = gpd.read_file('2024-06-10 12_07pm_store.csv')

numeric_columns = (fire_ignitions
                   .select_dtypes(include=np.number)
                   .columns
                   .to_list())
#print(fire_ignitions[numeric_columns].head())
#print(fire_ignitions.head())
#
#fire_ignitions['h3_cell'] = fire_ignitions.apply(geo_to_h3, axis=1)
#
# fire_ignitions_g = (fire_ignitions
#                           .groupby('h3_cell')
#                           .ignition_id
#                           .agg(list)
#                           .to_frame("ids")
#                           .reset_index())
# # Let's count each points inside the hexagon
# fire_ignitions_g['count'] =(fire_ignitions_g['ids']
#                       .apply(lambda ignition_ids:len(ignition_ids)))
print("getting geometry")
fire_ignitions['geometry'] = (fire_ignitions
                              .apply(add_geometry, axis=1))
print("getting geometry done")

#pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)  # show all cols

# print(fire_ignitions[["CONSUMER_COUNT"]].head(1))
# print(fire_ignitions[["H3_CELL"]].head(1))
# print(fire_ignitions[["geometry"]].head(1))
fire_ignitions = fire_ignitions[["CONSUMER_COUNT", "H3_CELL", "geometry", "STORE_ID", "STORE_LATITUDE", "STORE_LONGITUDE"]]
#print(fire_ignitions.head())
#print(fire_ignitions.describe())

fire_ignitions['CONSUMER_COUNT'] = fire_ignitions['CONSUMER_COUNT'].astype(int)


print("getting geojson")

geojson_obj = (hexagons_dataframe_to_geojson
               (fire_ignitions,
                hex_id_field='H3_CELL',
                value_field='STORE_ID',
                geometry_field='geometry',
                file_output='test_file_output_geoson.json'))

print("getting geojson done")

print(geojson_obj)
print("plotting chart")
fig = (px.choropleth_mapbox(
    fire_ignitions,
    geojson=geojson_obj,
    locations=fire_ignitions['H3_CELL'],
    color=fire_ignitions['CONSUMER_COUNT'],
    color_continuous_scale="Viridis",
    range_color=(0, fire_ignitions['CONSUMER_COUNT'].mean()), mapbox_style='carto-positron',
    zoom=4,
    featureidkey="properties.H3_CELL",
    opacity=0.7,
    labels={'count': '# of fire ignitions '}))
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()


geometry = [Point(xy) for xy in zip(fire_ignitions['STORE_LONGITUDE'], fire_ignitions['STORE_LATITUDE'])]

gdf = GeoDataFrame(fire_ignitions, geometry=geometry)


plt.scatter(x=fire_ignitions['STORE_LONGITUDE'], y=fire_ignitions['STORE_LATITUDE'])
plt.show()