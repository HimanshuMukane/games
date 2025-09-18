import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

def export_users_to_pdf(output_file="users.pdf"):
    # 1. Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",        # change to your host
        user="root",             # change to your username
        password="", # change to your password
        database="office_games"  # change to your DB name
    )
    cursor = conn.cursor()

    # 2. Run query
    query = "SELECT username, real_name FROM Users WHERE is_deleted = 0"
    cursor.execute(query)
    rows = cursor.fetchall()

    # 3. Prepare data for PDF
    data = [["Username", "Real Name"]]  # table header
    data.extend(rows)

    # 4. Create PDF
    pdf = SimpleDocTemplate(output_file, pagesize=letter)
    table = Table(data)

    # Style table
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)

    elements = [table]
    pdf.build(elements)

    # 5. Cleanup
    cursor.close()
    conn.close()
    print(f"✅ PDF exported: {output_file}")


if __name__ == "__main__":
    export_users_to_pdf("users.pdf")
