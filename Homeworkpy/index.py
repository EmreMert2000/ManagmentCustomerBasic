import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

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
            self.current_user = user  # current_user'ı set ediyoruz
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
        tk.Button(self.frame, text="Çıkış Yap", command=self.show_main).pack(pady=5)
    
    def user_menu(self, user):
        tk.Label(self.frame, text=f"Hoş geldiniz, {user[1]} (User)").pack()
        tk.Button(self.frame, text="Bilgileri Görüntüle", command=self.view_info).pack(pady=5)
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
            tree = ttk.Treeview(self.frame, columns=("ID", "Adı", "Pozisyon", "Maaş"), show='headings')
            tree.heading("ID", text="ID")
            tree.heading("Adı", text="Adı")
            tree.heading("Pozisyon", text="Pozisyon")
            tree.heading("Maaş", text="Maaş")
            
            for person in personnel:
                tree.insert("", tk.END, values=person)
            
            tree.pack()
        else:
            tk.Label(self.frame, text="Gösterilecek personel bilgisi yok.").pack()
        
        tk.Button(self.frame, text="Geri", command=lambda: self.show_menu(self.current_user)).pack(pady=5)

if __name__ == "__main__":
    create_tables()
    root = tk.Tk()
    app = HRMSApp(root)
    root.mainloop()
