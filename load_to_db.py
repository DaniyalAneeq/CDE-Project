import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

# 1️⃣ Load CSV
df = pd.read_csv("cleaned_data.csv")

df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace(r'[^\w]', '', regex=True)

# 2️⃣ Fill NaNs (important for SQL Server)
df = df.fillna(0)  # or choose appropriate default values

# 3️⃣ SQL Server connection
server = os.getenv('SERVER_NAME')
database = 'CarDB'
conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;')
cursor = conn.cursor()

# 4️⃣ Create table manually
cursor.execute("""
IF OBJECT_ID('dbo.Cars', 'U') IS NOT NULL
    DROP TABLE dbo.Cars;

CREATE TABLE dbo.Cars (
    title NVARCHAR(255),
    price FLOAT,
    year INT,
    mileage FLOAT,
    fuel NVARCHAR(50),
    engine_capacity FLOAT,
    transmission NVARCHAR(50),
    "Registered_In" NVARCHAR(50),
    "Color" NVARCHAR(50),
    "Body_Type" NVARCHAR(50),
    "Assembly" NVARCHAR(50),
    "Last_Updated" NVARCHAR(50)   
)
""")
conn.commit()

# 5️⃣ Insert rows safely
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO dbo.Cars (title, price, year, mileage, fuel, engine_capacity, transmission, Registered_In, Color, Body_Type, Assembly, Last_Updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    str(row['title']),
    float(row['price']),
    int(row['year']),
    float(row['mileage']),
    str(row['fuel']),
    float(row['engine_capacity']),
    str(row['transmission']),
    str(row['Registered_In']),
    str(row['Color']),
    str(row['Body_Type']),
    str(row['Assembly']),
    str(row['Last_Updated'])
    )

conn.commit()
cursor.close()
conn.close()

print("✅ Data inserted successfully!")
