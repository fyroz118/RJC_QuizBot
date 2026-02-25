import csv
from database import cursor, conn

with open("questions_usmle.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        cursor.execute("""
        INSERT INTO questions(
            exam, subject, topic,
            question,
            option_a, option_b, option_c, option_d,
            answer, explanation
        )
        VALUES(?,?,?,?,?,?,?,?,?,?)
        """, (
            row["exam"],
            row["subject"],
            row["topic"],
            row["question"],
            row["option_a"],
            row["option_b"],
            row["option_c"],
            row["option_d"],
            row["answer"],
            row["explanation"]
        ))

conn.commit()
print("Questions imported successfully!")
