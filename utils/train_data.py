
from neo4j import GraphDatabase
import pandas as pd
import numpy as np
import json
import os

json_x_file = 'train_x.json'
json_y_file = 'train_y.json'
fx = open(json_x_file, 'w')
fx.write('{"data": [\n')
fx.close()
fy = open(json_y_file, 'w')
fy.write('{"data": [\n')
fy.close()

server = None

with open('../Downloads/ip') as f:
    server = f.readline().rstrip()

driver = GraphDatabase.driver("bolt://" + server + ":7687", auth=("neo4j", "instacart"))

#import numpy as np
#cart = np.zeros((101,2))
#dt_id = np.dtype([("user", np.int32),("order", np.int32),("dow",np.int8),("hour",np.int8)])
#dt_cart = np.dtype([("dept",np.int16),("aisle",np.int16),("prod",np.int32)])
#dt_step = np.dtype([("step",dt_id,dt_id),("cart",dt_cart,(50,))])
#x = np.empty((0,3), dtype=dt_step)
#x = np.append(x, [((1,36,0,13),[(1,1,1),(1,2,5),(1,6,19),(2,1,56),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0)])]

# Initialize data frames
frame_x = []
frame_y = []
cols_x = ["dow", "hour"]
cols_y = ["dept", "aisle", "prod"]
max_item_count = 0


def get_order(id):
    global cols_x
    global cols_y
    global max_item_count

    with driver.session() as s:
        order = s.run(
                "MATCH (o:Order{id: $order_id}) "
                "RETURN o.dow AS dow, o.hour AS hour",
                order_id = id
                ).data()

    # Get the data that is the same for all returned paths
    dow = order[0].get("dow")
    hour = order[0].get("hour")

    with driver.session() as s:
        items = s.run(
                "MATCH (:Order{id: $order_id})"
                "-[i:INCLUDES]->(p:Product) "
                "RETURN i.order AS item, p.id AS prod "
                "ORDER BY item",
                order_id = id
                ).data()

    # The first X row is an empty cart
    x = {"dow": dow, "hour": hour}
    y = {}

    print ("Day of the week %d, Hour %d, %d items" % (dow, hour, len(items)))
    i = 0
    while i < len(items):
        item = items[i]

        if item["item"] > max_item_count:
            cols_x.append("dept" + str(item["item"]))
            cols_x.append("aisle" + str(item["item"]))
            cols_x.append("prod" + str(item["item"]))
            max_item_count = item["item"]

        prod = None
        with driver.session() as s:
            prod = s.run(
                "MATCH (:Product {id: $prod_id})"
                "-[:LOCATED_IN]->(a:Aisle)<-[:MANAGES]-(d:Department) "
                "RETURN a.id AS aisle, d.id AS dept",
                prod_id = item["prod"]
                ).data()
            prod = prod[0]

        #print (prod)
        y = {
            "dept": prod["dept"],
            "aisle": prod["aisle"],
            "prod": item["prod"]
            }

        fx = open(json_x_file, 'a')
        fx.write(json.dumps(x) + ',\n')
        fx.close()
        fy = open(json_y_file, 'a')
        fy.write(json.dumps(y) + ',\n')
        fy.close()

        # Next X row
        x["dept" + str(item["item"])] = prod["dept"]
        x["aisle" + str(item["item"])] = prod["aisle"]
        x["prod" + str(item["item"])] = item["prod"]

        # Next item
        i += 1
    # end of while




orders = None
with driver.session() as s:
    orders = s.run(
            "MATCH (u:User)-[:PLACED]->(o:Order)-[:INCLUDES]->(p:Product)"
            "-[:LOCATED_IN]->(a:Aisle)<-[:MANAGES]-(d:Department) "
            "RETURN o.id AS id LIMIT 10000"
            ).data()

c = 1
total = len(orders)
for order in orders:
    print ("Order %d of %d (%d%%): %d"
            % (c, total, int(100 * c/total + .5), order["id"]))
    get_order(order["id"])
    c += 1

fx = open(json_x_file, 'r+')
fx.seek(-2, os.SEEK_END)
fx.write('\n],\n')
fx.write('"columns": ' + json.dumps(cols_x) + '\n}\n')
fx.close()
fy = open(json_y_file, 'r+')
fy.seek(-2, os.SEEK_END)
fy.write('\n],\n')
fy.write('"columns": ' + json.dumps(cols_y) + '\n}\n')
fy.close()

quit()

# Load X,Y pickles into dataframes
df_x = pd.DataFrame(columns=cols_x)
with open(json_x_file, 'rb') as fx:
    while True:
        try:
            x = pickle.load(fx)
            print x
            df = pd.DataFrame([x], columns=cols_x)
            df_x = df_x.append(df, ignore_index=True)
        except EOFError:
            break

df_y = pd.DataFrame(columns=cols_y)
with open(json_y_file, 'rb') as fy:
    while True:
        try:
            y = pickle.load(fy)
            print y
            df = pd.DataFrame([y], columns=cols_y)
            df_y = df_y.append(df, ignore_index=True)
        except EOFError:
            break

df_x.to_csv('train_x.csv')
df_y.to_csv('train_y.csv')
