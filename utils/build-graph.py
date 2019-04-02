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


def add_departments():
    with open(csv_departments) as departments_file:
        next(departments_file)
        departments = csv.reader(departments_file, delimiter=',')
        for dept in departments:
            id = int(dept[0])
            name = dept[1]
            with driver.session() as session:
                print("Department %d: %s" % (id, name))
                session.run("CREATE (d:Department {id: $id, name: $name})",
                            id=id, name=name)


def add_aisles():
    with open(csv_aisles) as aisles_file:
        next(aisles_file)
        aisles = csv.reader(aisles_file, delimiter=',')
        for aisle in aisles:
            id = int(aisle[0])
            name = aisle[1]
            with driver.session() as session:
                session.run("CREATE (a:Aisle {id: $id, name: $name})",
                            id=id, name=name)

        # Look into the Product list and extract Aisle-Department relationships
        with open(csv_products) as products_file:
            next(products_file)
            products = csv.reader(products_file, delimiter=',')
            relates = {}
            for product in products:
                dept = int(product[3])
                aisle = int(product[2])
                if not dept in relates.keys():
                    relates[dept] = []
                relates[dept].append(aisle)
                relates[dept] = list(dict.fromkeys(relates[dept]))
                relates[dept].sort()

        for dept in sorted(relates.iterkeys()):
            for aisle in relates[dept]:
                print("Aisle %s in Department %s" % (aisle, dept))
                with driver.session() as session:
                    session.run("MATCH (d:Department {id: $dept_id}), "
                                "(a:Aisle {id: $aisle_id}) "
                                "CREATE (d)-[r:MANAGES]->(a) RETURN type(r)",
                                dept_id=dept, aisle_id=aisle)


def add_products():
    with open(csv_products) as products_file:
        next(products_file)
        products = csv.reader(products_file, delimiter=',')
        relates = {}
        for product in products:
            id = int(product[0])
            name = product[1]
            aisle = int(product[2])
            print("(%d: %s) --> %d" % (id,name,aisle))
            with driver.session() as session:
                session.run("MATCH (a:Aisle {id: $aisle_id}) "
                            "CREATE (p:Product {id: $id, name: $name})"
                            "-[r:LOCATED_IN]->(a) RETURN type(r)",
                            id=id, name=name, aisle_id=aisle)


def add_orders(data_set):
    with open(csv_orders) as orders_file:
        next(orders_file)
        orders = csv.reader(orders_file, delimiter=',')
        users = {}
        for order in orders:
            if order[2] == data_set:
                user_id = int(order[1])
                if not user_id in users.keys():
                    users[user_id] = None
                    print("User %d" % user_id)
                    with driver.session() as session:
                        session.run("CREATE (u:User {id: $id})", id=user_id)

                    order_id = int(order[0])
                    print("User %d placed Order %d" % (user_id,order_id))
                    with driver.session() as session:
                        session.run("MATCH (u:User {id: $user_id}) "
                                    "CREATE (o:Order "
                                    "{id: $order_id, data_set: $data_set})"
                                    "<-[r:PLACED]-(u) RETURN type(r)",
                                    order_id=int(order_id), user_id=int(user_id),
                                    data_set=data_set)


def add_order_details(csv_file):
    csv_order_items = dataset_dir + '/' + csv_file
    with open(csv_order_items) as order_items_file:
        next(order_items_file)
        items = csv.reader(order_items_file, delimiter=',')
        add_to_cart_order = 0
        order_id_prev = None
        for item in items:
            order_id = int(item[0])

            if len(item) < 3 and order_id_prev != order_id:
                order_id_prev = order_id
                add_to_cart_order = 0

            product_id = int(item[1])
            if len(item) > 2:
                add_to_cart_order = int(item[2])
                reordered = (item[3] == 1)
            else:
                add_to_cart_order += 1
                reordered = False

            print("Order %d [%d] --> %d (repeat: %s)" %
                    (order_id, add_to_cart_order, product_id, reordered))
            with driver.session() as session:
                session.run("MATCH (o:Order {id: $order_id}),"
                            "(p:Product {id: $product_id}) "
                            "CREATE (o)-[r:INCLUDES {order: $cart_order}]->(p) "
                            "RETURN type(r)",
                            order_id=order_id, product_id=product_id,
                            cart_order=add_to_cart_order)





def wipe_clean():
    print("Wiping database clean...")
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


#wipe_clean()
#add_departments()
#add_aisles()
#add_products()
#add_orders("test")
#add_order_details("order_products__train_cap.csv")
add_order_details("order_products__test_cap.csv")
