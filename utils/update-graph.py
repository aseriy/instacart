from neo4j import GraphDatabase
import csv

dataset_dir = '../dataset'
csv_departments = dataset_dir + '/departments.csv'
csv_aisles = dataset_dir + '/aisles.csv'
csv_products = dataset_dir + '/products.csv'
csv_orders = dataset_dir + '/orders.csv'

server = None

with open('../Downloads/ip') as f:
    server = f.readline().rstrip()

driver = GraphDatabase.driver("bolt://" + server + ":7687", auth=("neo4j", "instacart"))


def update_orders(eval_set):
    with open(csv_orders) as orders_file:
        next(orders_file)
        orders = csv.reader(orders_file, delimiter=',')
        for order in orders:
            if order[2] == eval_set:
                user_id = int(order[1])
                order_id = int(order[0])
                order_number = int(order[3])
                order_dow = int(order[4])
                order_hour_of_day = int(order[5])
                # days_since_prior_order = int(order[6])
                print("Order %d" % order_id)
                with driver.session() as session:
                    session.run("MATCH (o:Order {id: $order_id}) "
                                "SET o += {dow: $dow, hour: $hour} "
                                "RETURN o",
                                order_id=order_id,
                                dow=order_dow, hour=order_hour_of_day)


update_orders("train")
