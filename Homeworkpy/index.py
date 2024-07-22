import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os

# Veri tabanı bağlantısı
def create_connection():
    conn = sqlite3.connect('hrms.db')
    return conn

# Veri tabanı tablolarını oluşturma
def create_tables():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS personnel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                salary REAL NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firm_name TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL)''')
    conn.commit()
    conn.close()

# Yeni kullanıcı oluşturma
def register_user(username, password, role):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

# Kullanıcı girişi
def login_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Personel ekleme
def add_personnel_to_db(name, position, salary):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO personnel (name, position, salary) VALUES (?, ?, ?)", (name, position, salary))
    conn.commit()
    conn.close()

# Tüm personel bilgilerini getirme
def get_all_personnel():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM personnel")
    personnel = c.fetchall()
    conn.close()
    return personnel

# Tüm faturaları getirme
def get_all_invoices():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT firm_name FROM invoices")
    invoices = c.fetchall()
    conn.close()
    return invoices

# Fatura oluşturma ve kaydetme
def create_invoice(firm_name, items):
    conn = create_connection()
    c = conn.cursor()
    total_amount = 0
    for item in items:
        product_name, quantity, price = item
        total_price = quantity * price
        total_amount += total_price
        c.execute("INSERT INTO invoices (firm_name, product_name, quantity, price, total) VALUES (?, ?, ?, ?, ?)",
                  (firm_name, product_name, quantity, price, total_price))
    conn.commit()
    conn.close()
    
    invoice_content = f"""
    <html>
    <head><title>Fatura</title></head>
    <body>
        <h1>Fatura</h1>
        <p>Firma: {firm_name}</p>
        <table border="1">
            <tr>
                <th>Ürün Adı</th>
                <th>Adet</th>
                <th>Birim Fiyatı</th>
                <th>Toplam Fiyat</th>
            </tr>
    """
    for item in items:
        product_name, quantity, price = item
        total_price = quantity * price
        invoice_content += f"""
        <tr>
            <td>{product_name}</td>
            <td>{quantity}</td>
            <td>{price}</td>
            <td>{total_price}</td>
        </tr>
        """
    invoice_content += f"""
        </table>
        <p>Toplam Tutar: {total_amount}</p>
    </body>
    </html>
    """
    invoice_filename = f"{firm_name.replace(' ', '_')}_invoice.html"
    with open(invoice_filename, 'w') as f:
        f.write(invoice_content)

    messagebox.showinfo("Başarılı", f"Fatura oluşturuldu: {invoice_filename}")
    return invoice_filename

# Tkinter ana penceresi
class HRMSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("İnsan Kaynakları Yönetim Sistemi")
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)
        
        self.label = tk.Label(self.frame, text="İnsan Kaynakları Yönetim Sistemine Hoş Geldiniz")
        self.label.pack()
        
        self.login_button = tk.Button(self.frame, text="Giriş Yap", command=self.show_login)
        self.login_button.pack(pady=5)
        
        self.register_button = tk.Button(self.frame, text="Kayıt Ol", command=self.show_register)
        self.register_button.pack(pady=5)
        
        self.current_user = None
    
    def show_login(self):
        self.clear_frame()
        
        tk.Label(self.frame, text="Kullanıcı Adı:").pack()
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.pack()
        
        tk.Label(self.frame, text="Şifre:").pack()
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.pack()
        
        tk.Button(self.frame, text="Giriş Yap", command=self.login).pack(pady=5)
        tk.Button(self.frame, text="Geri", command=self.show_main).pack(pady=5)
    
    def show_register(self):
        self.clear_frame()
        
        tk.Label(self.frame, text="Yeni Kullanıcı Adı:").pack()
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.pack()
        
        tk.Label(self.frame, text="Yeni Şifre:").pack()
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.pack()
        
        tk.Label(self.frame, text="Kullanıcı Türü (admin/user):").pack()
        self.role_entry = tk.Entry(self.frame)
        self.role_entry.pack()
        
        tk.Button(self.frame, text="Kayıt Ol", command=self.register).pack(pady=5)
        tk.Button(self.frame, text="Geri", command=self.show_main).pack(pady=5)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = login_user(username, password)
        
        if user:
            messagebox.showinfo("Başarılı", f"Hoş geldiniz, {user[1]}")
            self.current_user = user
            self.show_menu(user)
        else:
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı veya şifre.")
    
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_entry.get()
        
        if role not in ["admin", "user"]:
            messagebox.showerror("Hata", "Kullanıcı türü 'admin' veya 'user' olmalıdır.")
            return
        
        register_user(username, password, role)
        messagebox.showinfo("Başarılı", "Kullanıcı başarıyla oluşturuldu.")
        self.show_main()
    
    def show_menu(self, user):
        self.clear_frame()
        
        if user[3] == 'admin':
            self.admin_menu(user)
        else:
            self.user_menu(user)
    
    def admin_menu(self, user):
        tk.Label(self.frame, text=f"Hoş geldiniz, {user[1]} (Admin)").pack()
        tk.Button(self.frame, text="Personel Ekle", command=self.add_personnel).pack(pady=5)
        tk.Button(self.frame, text="Bilgileri Görüntüle", command=self.view_info).pack(pady=5)
        tk.Button(self.frame, text="Fatura Kes", command=self.invoice_items_count).pack(pady=5)
        tk.Button(self.frame, text="Faturaları Görüntüle", command=self.view_invoices).pack(pady=5)
        tk.Button(self.frame, text="Çıkış Yap", command=self.show_main).pack(pady=5)
    
    def user_menu(self, user):
        tk.Label(self.frame, text=f"Hoş geldiniz, {user[1]} (User)").pack()
        tk.Button(self.frame, text="Faturaları Görüntüle", command=self.view_invoices).pack(pady=5)
        tk.Button(self.frame, text="Çıkış Yap", command=self.show_main).pack(pady=5)
    
    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
    
    def show_main(self):
        self.clear_frame()
        self.__init__(self.root)
    
    def add_personnel(self):
        self.clear_frame()
        
        tk.Label(self.frame, text="Personel Adı:").pack()
        self.name_entry = tk.Entry(self.frame)
        self.name_entry.pack()
        
        tk.Label(self.frame, text="Pozisyon:").pack()
        self.position_entry = tk.Entry(self.frame)
        self.position_entry.pack()
        
        tk.Label(self.frame, text="Maaş:").pack()
        self.salary_entry = tk.Entry(self.frame)
        self.salary_entry.pack()
        
        tk.Button(self.frame, text="Ekle", command=self.save_personnel).pack(pady=5)
        tk.Button(self.frame, text="Geri", command=lambda: self.show_menu(self.current_user)).pack(pady=5)
    
    def save_personnel(self):
        name = self.name_entry.get()
        position = self.position_entry.get()
        salary = self.salary_entry.get()
        
        if name and position and salary:
            try:
                salary = float(salary)
                add_personnel_to_db(name, position, salary)
                messagebox.showinfo("Başarılı", "Personel başarıyla eklendi.")
                self.show_menu(self.current_user)
            except ValueError:
                messagebox.showerror("Hata", "Geçersiz maaş değeri.")
        else:
            messagebox.showerror("Hata", "Tüm alanlar doldurulmalıdır.")
    
    def view_info(self):
        self.clear_frame()
        personnel = get_all_personnel()
        
        if personnel:
            tree = ttk.Treeview(self.frame, columns=("ID", "Ad", "Pozisyon", "Maaş"), show="headings")
            tree.heading("ID", text="ID")
            tree.heading("Ad", text="Ad")
            tree.heading("Pozisyon", text="Pozisyon")
            tree.heading("Maaş", text="Maaş")
            
            for person in personnel:
                tree.insert("", tk.END, values=person)
            
            tree.pack()
        else:
            tk.Label(self.frame, text="Gösterilecek personel bilgisi yok.").pack()
        
        tk.Button(self.frame, text="Geri", command=lambda: self.show_menu(self.current_user)).pack(pady=5)
    
    def invoice_items_count(self):
        self.clear_frame()
        
        tk.Label(self.frame, text="Faturayı kesmek istediğiniz firmanın adını girin:").pack()
        self.firm_name_entry = tk.Entry(self.frame)
        self.firm_name_entry.pack()
        
        tk.Label(self.frame, text="Kaç kalem ürün kesileceğini girin:").pack()
        self.item_count_entry = tk.Entry(self.frame)
        self.item_count_entry.pack()
        
        tk.Button(self.frame, text="Devam", command=self.create_invoice_form).pack(pady=5)
        tk.Button(self.frame, text="Geri", command=lambda: self.show_menu(self.current_user)).pack(pady=5)
    
    def create_invoice_form(self):
        try:
            self.item_count = int(self.item_count_entry.get())
            self.firm_name = self.firm_name_entry.get()
            self.show_invoice_form()
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz ürün sayısı.")
    
    def show_invoice_form(self):
        self.clear_frame()
        
        self.entries = []
        tk.Label(self.frame, text=f"Firma: {self.firm_name}").pack()
        
        for i in range(self.item_count):
            row_frame = tk.Frame(self.frame)
            row_frame.pack(fill=tk.X)
            
            tk.Label(row_frame, text=f"Ürün Adı {i+1}:").pack(side=tk.LEFT)
            product_name_entry = tk.Entry(row_frame)
            product_name_entry.pack(side=tk.LEFT)
            
            tk.Label(row_frame, text="Adet:").pack(side=tk.LEFT)
            quantity_entry = tk.Entry(row_frame)
            quantity_entry.pack(side=tk.LEFT)
            
            tk.Label(row_frame, text="Birim Fiyatı:").pack(side=tk.LEFT)
            price_entry = tk.Entry(row_frame)
            price_entry.pack(side=tk.LEFT)
            
            self.entries.append((product_name_entry, quantity_entry, price_entry))
        
        tk.Button(self.frame, text="Fatura Oluştur", command=self.generate_invoice).pack(pady=5)
        tk.Button(self.frame, text="Geri", command=lambda: self.show_menu(self.current_user)).pack(pady=5)
    
    def generate_invoice(self):
        items = []
        for entry in self.entries:
            product_name = entry[0].get()
            quantity = entry[1].get()
            price = entry[2].get()
            
            if product_name and quantity and price:
                try:
                    quantity = int(quantity)
                    price = float(price)
                    items.append((product_name, quantity, price))
                except ValueError:
                    messagebox.showerror("Hata", "Geçersiz adet veya fiyat değeri.")
                    return
            else:
                messagebox.showerror("Hata", "Tüm alanlar doldurulmalıdır.")
                return
        
        if items:
            invoice_filename = create_invoice(self.firm_name, items)
            messagebox.showinfo("Başarılı", f"Fatura başarıyla oluşturuldu: {invoice_filename}")
            self.show_menu(self.current_user)

    def view_invoices(self):
        self.clear_frame()
        invoices = get_all_invoices()
        
        if invoices:
            tree = ttk.Treeview(self.frame, columns=("Firma Adı", "Fatura Dosyası"), show="headings")
            tree.heading("Firma Adı", text="Firma Adı")
            tree.heading("Fatura Dosyası", text="Fatura Dosyası")
            
            for invoice in invoices:
                firm_name = invoice[0]
                invoice_filename = f"{firm_name.replace(' ', '_')}_invoice.html"
                tree.insert("", tk.END, values=(firm_name, invoice_filename))
            
            tree.pack()
            
            if self.current_user[3] == "admin":
                tree.bind("<Double-1>", self.download_invoice)
        else:
            tk.Label(self.frame, text="Gösterilecek fatura bilgisi yok.").pack()
        
        tk.Button(self.frame, text="Geri", command=lambda: self.show_menu(self.current_user)).pack(pady=5)

    def download_invoice(self, event):
        selected_item = event.widget.selection()[0]
        invoice_filename = event.widget.item(selected_item, "values")[1]
        if os.path.exists(invoice_filename):
            file_path = os.path.abspath(invoice_filename)
            os.startfile(file_path)
        else:
            messagebox.showerror("Hata", f"{invoice_filename} dosyası bulunamadı.")
    

if __name__ == "__main__":
    create_tables()
    root = tk.Tk()
    app = HRMSApp(root)
    root.mainloop()
