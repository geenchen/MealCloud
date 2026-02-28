import sqlite3

conn = sqlite3.connect('Backend/MealCloud_API/mealcloud.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables in database:')
for table in tables:
    print(table[0])
    
# 检查区域表是否存在
cursor.execute('SELECT * FROM areas LIMIT 5')
areas = cursor.fetchall()
print(f'\nAreas in database: {len(areas)}')
for area in areas:
    print(area)
    
conn.close()