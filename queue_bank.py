import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='quequ')

mycur = conn.cursor()

try:
    mycur.execute("CREATE TABLE customer (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(30))")
    mycur.execute("CREATE TABLE queue (id INT, state ENUM('waiting', 'served'), serves ENUM('A','B','C'), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(id) REFERENCES customer(id))")
except mysql.connector.Error as r:
    print(r, '\n\n')

try:
    customer_count = 0  # Counter for the number of customers added
    while True:
        print('\n\n')
        choice = input("Enter:\n1 - Add a customer\n2 - Complete the current customer\n3 - Show all customers and their serves\n4 - Show customers in serves A, B, or C\n5 - Exit\n")
        choice = int(choice)

        if choice == 1:
            if customer_count > 5:
                print("You have reached the maximum number of customers (5).")
            else:
                name = input("Enter the name: ")
                serves = input("Enter the serve (A, B, or C): ")

                query = "INSERT INTO customer (name) VALUES (%s)"
                values = (name,)
                mycur.execute(query, values)

                last_inserted_id = mycur.lastrowid
                query2 = "INSERT INTO queue (state, serves, id) VALUES ('waiting', %s, %s)"
                values2 = (serves, last_inserted_id)
                mycur.execute(query2, values2)

                conn.commit()
                print("Customer added to the queue.")
                customer_count += 1  # Increment the customer count

        elif choice == 2:
            serves = input("Enter the serve to complete (A, B, or C): ")
            query = "SELECT c.id, c.name FROM customer c JOIN queue q ON c.id = q.id WHERE q.state = 'waiting' AND q.serves = %s"
            values = (serves,)
            mycur.execute(query, values)
            result = mycur.fetchone()

            if result is not None:
                customer_id = result[0]
                customer_name = result[1]
                
                # Consume the result before executing the UPDATE statement
                mycur.fetchall()
                
                query2 = "UPDATE queue SET state = 'served' WHERE id = %s"
                values2 = (customer_id,)
                mycur.execute(query2, values2)

                conn.commit()
                print("Customer served.")
                customer_count -= 1
                print("Completed Customer - ID:", customer_id, "Name:", customer_name)

            else:
                print("No customers in the queue for serve", serves + ".")

        elif choice == 3:
            query = "SELECT c.id, c.name, q.serves FROM customer c JOIN queue q ON c.id = q.id"
            mycur.execute(query)
            result = mycur.fetchall()

            if len(result) > 0:
                print("All Customers and Their Serves:")
                for row in result:
                    print("ID:", row[0], "Name:", row[1], "Serve:", row[2])
            else:
                print("No customers found.")

        elif choice == 4:
            serves = input("Enter the serve (A, B, or C): ")
            query = "SELECT c.id, c.name FROM customer c JOIN queue q ON c.id = q.id WHERE q.serves = %s AND q.state = 'waiting'"
            values = (serves,)
            mycur.execute(query, values)
            result = mycur.fetchall()
            if len(result) > 0:
                print("Customers in Serve", serves + ":")
                for row in result:
                    print("ID:", row[0], "Name:", row[1])
            else:
                print("No customers found in Serve", serves + ".")

        elif choice == 5:
            break

        else:
            print("Invalid choice. Please try again.")

except mysql.connector.Error as r:
    print("Error:", r)

conn.close()
