import sqlite3
import random

get_inventory_declaration = {
    "name": "get_inventory",
    "description": "Retrieves the inventory list"
}

def setup_database():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    sql = '''CREATE TABLE IF NOT EXISTS inventory (
       part_id INTEGER PRIMARY KEY,
       part_name TEXT NOT NULL,
       quantity INTEGER NOT NULL,
       price INTEGER NOT NULL,
       vendor1 TEXT NOT NULL,
       vendor2 TEXT NOT NULL,
       vendor3 TEXT NOT NULL,
       purchaseprice_vendor1 INTEGER NOT NULL,
       purchaseprice_vendor2 INTEGER NOT NULL,
       purchaseprice_vendor3 INTEGER NOT NULL,
       vendorquality1 TEXT NOT NULL,
       vendorquality2 TEXT NOT NULL,
       vendorquality3 TEXT NOT NULL,
       optimalsolution TEXT NOT NULL
    )'''

    cursor.execute(sql)
    print("Table created successfully")
    conn.close()


def insert_sample_data():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Danh sách xe và linh kiện thường gặp:
    cars = [
        "Toyota Vios", "Hyundai Accent", "Honda CR-V", "Mazda CX-5", "Kia Seltos", 
        "Toyota Fortuner", "Ford Ranger", "Honda City", "Mazda3", "Kia Morning",
        "Hyundai Grand i10", "Mitsubishi Xpander", "VinFast Lux A2.0"
    ]

    parts_list = [
        "Đèn pha trái", "Đèn pha phải", "Cản trước", "Cản sau", "Gương chiếu hậu",
        "Đèn hậu trái", "Đèn hậu phải", "Đèn sương mù", "Lưới tản nhiệt", "Bánh xe dự phòng",
        "Lốp xe", "Thanh cản", "Bộ phanh"
    ]

    vendors = ["VendorA", "VendorB", "VendorC"]
    qualities = ["Good", "Medium", "Poor"]

    parts = []
    # Sinh ngẫu nhiên 100 bản ghi
    for part_id in range(1, 101):
        # Chọn ngẫu nhiên một mẫu xe và linh kiện
        car = random.choice(cars)
        p = random.choice(parts_list)
        part_name = f"{car} - {p}"

        # quantity và price giả lập
        quantity = random.randint(1, 30)
        price = random.randint(50, 600) * 10  # Giá bán ra

        # Chọn vendor cố định
        vendor1, vendor2, vendor3 = vendors
        # Giá mua từ vendor
        purchase1 = random.randint(30, 500) * 10
        purchase2 = random.randint(30, 500) * 10
        purchase3 = random.randint(30, 500) * 10

        # Chất lượng vendor
        # Để đơn giản: VendorA luôn Good, VendorB Medium, VendorC Poor
        vendorquality1 = "Good"
        vendorquality2 = "Medium"
        vendorquality3 = "Poor"

        # Xác định optimal solution: chọn vendor có giá mua thấp nhất trong nhóm "Good" trước, nếu không có Good thì Medium, cuối cùng Poor.
        # Ở đây VendorA luôn Good, nên chọn VendorA nếu giá hợp lý.
        # Tuy nhiên, chúng ta luôn có VendorA=Good, nên optimalsolution sẽ chọn VendorA.
        # Để tạo sự đa dạng, giả sử optimal chọn vendor rẻ nhất trong trường hợp đồng nhất chất lượng.
        
        # Nếu giả định VendorA luôn Good, chúng ta mặc định VendorA là optimal solution.
        # Hoặc chọn vendor có giá mua thấp nhất.
        prices = [(purchase1, vendor1, vendorquality1),
                  (purchase2, vendor2, vendorquality2),
                  (purchase3, vendor3, vendorquality3)]
        # Sắp xếp theo giá mua
        prices.sort(key=lambda x: x[0])
        # Chọn vendor có chất lượng tốt nhất trong nhóm giá thấp nhất
        # Ở đây Good > Medium > Poor
        # Chúng ta sẽ chọn vendor có chất lượng cao nhất trong nhóm vendor có giá thấp nhất hoặc bằng nhau
        # Vì chúng ta sort theo giá, vendor đầu tiên là giá thấp nhất
        # Nếu chất lượng vendor đầu tiên không phải Good, có thể xét vendor tiếp theo cùng giá
        # Tuy nhiên, để đơn giản: vendor giá thấp nhất chính là optimal
        optimal_vendor = prices[0][1]

        optimalsolution = f"Chọn {optimal_vendor} do giá và chất lượng phù hợp"

        part_record = (
            part_id,
            part_name,
            quantity,
            price,
            vendor1,
            vendor2,
            vendor3,
            purchase1,
            purchase2,
            purchase3,
            vendorquality1,
            vendorquality2,
            vendorquality3,
            optimalsolution
        )

        parts.append(part_record)

    # cursor.executemany('INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', parts)
    conn.commit()
    conn.close()
    print("100 rows inserted successfully")


def get_inventory():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    query = "SELECT * FROM inventory;"
    cursor.execute(query)

    rows = cursor.fetchall()

    # Cập nhật để lấy toàn bộ cột
    inventory_list = []
    for row in rows:
        inventory_list.append({
            "part_id": row[0],
            "part_name": row[1],
            "quantity": row[2],
            "price": row[3],
            "vendor1": row[4],
            "vendor2": row[5],
            "vendor3": row[6],
            "purchaseprice_vendor1": row[7],
            "purchaseprice_vendor2": row[8],
            "purchaseprice_vendor3": row[9],
            "vendorquality1": row[10],
            "vendorquality2": row[11],
            "vendorquality3": row[12],
            "optimalsolution": row[13]
        })

    conn.close()

    return inventory_list


# setup_database()
# insert_sample_data()
# print(get_inventory())