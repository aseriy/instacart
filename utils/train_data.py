
from neo4j import GraphDatabase
import pandas as pd
import numpy as np

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
    global frame_x
    global frame_y
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
        print (item)

        if item["item"] > max_item_count:
            cols_x.append("dept" + str(item["item"]))
            cols_x.append("aisle" + str(item["item"]))
            cols_x.append("prod" + str(item["item"]))
            max_item_count = item["item"]
            print max_item_count

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

        frame_x.append(x.copy())
        frame_y.append(y)

        # Next X row
        x["dept" + str(item["item"])] = prod["dept"]
        x["aisle" + str(item["item"])] = prod["aisle"]
        x["prod" + str(item["item"])] = item["prod"]

        # Next item
        i += 1
    # end of while

    frame_x.append(x.copy())
    frame_y.append({})





orders = None
with driver.session() as s:
    orders = s.run(
            "MATCH (u:User)-[:PLACED]->(o:Order)-[:INCLUDES]->(p:Product)"
            "-[:LOCATED_IN]->(a:Aisle)<-[:MANAGES]-(d:Department) "
            "RETURN o.id AS id"
            ).data()

c = 1
total = len(orders)
for order in orders:
    print ("Order %d of %d: %d" % (c, total, order["id"]))
    get_order(order["id"])
    c += 1

df_x = pd.DataFrame(frame_x, columns=cols_x)
df_y = pd.DataFrame(frame_y, columns=cols_y)
df_x.to_csv('train_x.csv')
df_y.to_csv('train_y.csv')
