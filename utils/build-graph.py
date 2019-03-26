from neo4j import GraphDatabase
import csv

dataset_dir = '../dataset'
csv_departments = dataset_dir + '/departments.csv'
csv_aisles = dataset_dir + '/aisles.csv'
csv_products = dataset_dir + '/products.csv'

server = None

with open('../Downloads/ip') as f:
    server = f.readline().rstrip()

driver = GraphDatabase.driver("bolt://" + server + ":7687", auth=("neo4j", "instacart"))

def add_friend(tx, name, friend_name):
    tx.run("MERGE (a:Person {name: $name}) "
           "MERGE (a)-[:KNOWS]->(friend:Person {name: $friend_name})",
           name=name, friend_name=friend_name)

def print_friends(tx, name):
    for record in tx.run("MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
                         "RETURN friend.name ORDER BY friend.name", name=name):
        print(record["friend.name"])


def add_departments(tx):
    with open(csv_departments) as departments_file:
        next(departments_file)
        departments = csv.reader(departments_file, delimiter=',')
        for dept in departments:
            id = int(dept[0])
            name = dept[1]
            tx.run("CREATE (d:Department {id: $id, name: $name})",
                   id=id, name=name)


def add_aisles(tx):
    with open(csv_aisles) as aisles_file:
        next(aisles_file)
        aisles = csv.reader(aisles_file, delimiter=',')
        for aisle in aisles:
            id = int(aisle[0])
            name = aisle[1]
            tx.run("CREATE (a:Aisle {id: $id, name: $name})",
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
            print("%s: %s" % (dept, aisle))
            tx.run("MATCH (d:Department {id: $dept_id}), "
                   "(a:Aisle {id: $aisle_id}) "
                   "CREATE (d)-[r:MANAGES]->(a) RETURN type(r)",
                   dept_id=dept, aisle_id=aisle)


def add_products(tx):
    with open(csv_products) as products_file:
        next(products_file)
        products = csv.reader(products_file, delimiter=',')
        relates = {}
        for product in products:
            id = int(product[0])
            name = product[1]
            aisle = int(product[2])
            print("(%d: %s) --> %d" % (id,name,aisle))
            tx.run("MATCH (a:Aisle {id: $aisle_id}) "
                   "CREATE (p:Product {id: $id, name: $name})"
                   "-[r:LOCATED_IN]->(a) RETURN type(r)",
                   id=id, name=name, aisle_id=aisle)



with driver.session() as session:
    session.write_transaction(add_departments)
    session.write_transaction(add_aisles)
    session.write_transaction(add_products)
