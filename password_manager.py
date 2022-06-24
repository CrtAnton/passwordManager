import sqlite3, random, os.path, hashlib
from tkinter import *
from configparser import ConfigParser
from tkinter import ttk
from cryptography.fernet import Fernet

#   5.  Connect/create a database
with sqlite3.connect("Passwords_database.db") as db:
    cursor = db.cursor()

#   6.Create a table in the database to store the master password
cursor.execute("""
CREATE TABLE IF NOT EXISTS master_password(
    id integer PRIMARY KEY,
    password text NOT NULL
);
""")

#   10.Create table for passwords
cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords(
    id integer PRIMARY KEY AUTOINCREMENT,
    website text NOT NULL,
    username text NOT NULL,
    password text NOT NULL
);
""")   


#   20. Create a random password generator
def generate_password():
    password = []
    chars_pool = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!$#@%^.?+"
    for i in range(12):
        password += random.choice(chars_pool)
    random.shuffle(password)
    return "".join(password)

# Parser function to check the config file after settings are changed
def theme_parser():
    parser = ConfigParser()
    parser.read("config.ini")
    return parser.get("theme", "status")
#Parse function to check the config file for show data status
def show_parser():
    parser = ConfigParser()
    parser.read("config.ini")
    return parser.get("show", "status")

#   25. Generate encryption key and save it on outside device
new_key = Fernet.generate_key()
def erorr_startup():
    window = Tk()
    window.title("Password Vault")
    window.geometry("500x400")
    window.wm_iconbitmap("lock.ico")
    lbl = Label(window, text = "You don t have the encryption key to access database.").pack(pady = 20)
    window.mainloop()

#################################################
#################################################
#################################################
#################################################
#   Change the key paths below to where you want the encryption the key to be saved
#################################################
#################################################
#################################################
#################################################

#   If a key file exists, don t overwrite key as all data will be lost
if os.path.exists("D://SecretKey.txt") == False:
    try: 
        with open("D://SecretKey.txt", "wb") as file:
            file.write(new_key)
    except FileNotFoundError:
        erorr_startup()
#   Retrive the already existing key
with open("D://SecretKey.txt", "rb") as f:
    key = f.readline()
f = Fernet(key)

#   26. Create a hash for the master password and check if a match when login
def hashing(input):
    hashed_password = hashlib.sha256(input.encode())
    hashed_password = hashed_password.hexdigest()
    return hashed_password

#   Create encrypt/decrypt functions
def enc(input):
    return f.encrypt(input.encode())

def dec(input):
    return f.decrypt(input).decode()

#   1.Main window setup
window = Tk()
window.title("Password Vault")
window.geometry("500x400")
window.wm_iconbitmap("lock.ico")

#   23.Define theme colors

dark_primary, dark_secundary, dark_third = "#292929", "#E1E1E1", "#BB86FC"
light_primary, light_secundary, light_third = "white", "#37474f", "#40E0D0"

#   Check the current theme saved from last session and apply it
show_theme_status = theme_parser()
if show_theme_status == "light":
    selected_primary, selected_secundary, selected_third = light_primary, light_secundary, light_third
else:
    selected_primary, selected_secundary, selected_third = dark_primary, dark_secundary, dark_third
window.configure(bg = selected_primary)

#   21. Create the menu bar and back functionality
def menu_bar_function():
    menubar = Menu(window)
    window.config(menu = menubar)
    def go_back():
        vault()
    menubar.add_command(label = "Back", command=go_back)

#   2.Create the master password setup
def setup():
    lbl = Label(window, text = "Enter your master password", bg = selected_primary, fg = selected_secundary)
    lbl.pack(pady = 10)

    txt = Entry(window)
    txt.pack()
    txt.focus()

    lbl1 = Label(window, text = "Re-enter you master password", bg = selected_primary, fg = selected_secundary)
    lbl1.pack(pady = 10)

    txt1 = Entry(window)
    txt1.pack()

    lbl2 = Label(window, bg = selected_primary, fg = selected_secundary)
    lbl2.pack(pady=10)
    
    def check ():
        if txt.get() == txt1.get():
            pass_to_introduce = hashing(txt.get())
            #   7.Insert password into db table
            cursor.execute("""INSERT INTO master_password(password) VALUES(?)""", [pass_to_introduce])
            db.commit()
            login()
        else:
            lbl2.configure(text = "Paswwords don`t match")

    btn = Button(text = "Save", command = check, background = selected_third, foreground= "black")
    btn.pack()

#   3.Create the login Screen
count, delay_time = 0, 0

def login():

    for widget in window.winfo_children():
        widget.destroy()

    lbl = Label(window, text = "Enter your master password", bg = selected_primary, fg = selected_secundary)
    lbl.pack(pady=10)

    txt = Entry(window)
    txt.pack()

    lbl1 = Label(window, bg = selected_primary, fg = selected_secundary)
    lbl1.pack()
  
    #   9.Retrive master password from database and check for a match
    def check():
        password = hashing(txt.get())
        cursor.execute("SELECT * FROM master_password WHERE id = 1 and password = ? ", [password])
        password = cursor.fetchall()
        if password:
            vault()
        else:
            global count
            count += 1
            if count < 3:
                txt.delete(0, "end")
                lbl1.configure(text = "Wrong password, try again")
            else:
                #   22. Create anti-bruteforce system
                def countdown(count):      
                    lbl1['text'] = f"Too many wrong attempts, you are locked for {count} seconds."
                    if count > 0:
                        window.after(1000, countdown, count-1)
                    else:
                        btn.config(state = "active")
                        lbl1.configure(text = "")
                        txt.delete(0, END)
                global delay_time
                delay_time+=5
                btn.config(state = "disabled")
                countdown(delay_time)
                count = 0

    btn =  Button(window, text = "Submit", command= check, background = selected_third, foreground="black")
    btn.pack(pady = 10)

#   4.Create the vault screen
def vault():
    for widget in window.winfo_children():
        widget.destroy()
        
    btn = Button(window, text = "Add entry", command = new_entry, background = selected_third, foreground= "black")
    btn.grid(row = 0, column = 0, pady = 10, padx = 47)

    btn = Button(window, text = "Delete Credentials", command = delete, background = selected_third, foreground= "black")
    btn.grid(row = 0, column = 1, pady = 10, padx = 47)

    btn = Button(window, text = "Update Info", command = update_info, background = selected_third, foreground= "black")
    btn.grid(row = 0, column = 2, pady = 10, padx = 47)

    btn_show = Button(window, text = "Show All", command = show_all, background = selected_third, foreground= "black")
    btn_show.grid(row = 1, column = 0, pady = 10, padx = 47)

    btn = Button(window, text = "Query Database", command = query_database, background = selected_third, foreground= "black")
    btn.grid(row = 1, column = 1, pady = 10, padx = 47)

    btn = Button(window, text = "Settings", command = settings_screen, background = selected_third, foreground= "black")
    btn.grid(row = 1, column = 2, pady = 10, padx = 47)

    show_hide_status = show_parser()
    if show_hide_status == "show":
        show_treeview()

def show_treeview():
    show_theme_status = theme_parser()
    if show_theme_status == "dark":
        tree_background_color = "D3D3D3"
    else:
        tree_background_color = "white"
    cursor.execute("SELECT * FROM passwords")
    data = cursor.fetchall()
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
        background = tree_background_color,
        foreground = "black",
        rowheight = 25,
        fieldbackground = "D3D3D3")

    if show_theme_status == "light":
        style.map("Treeview", background = [("selected","#5F9EA0")])
    else:
        style.map("Treeview", background = [("selected","#7c1e94")])

    tree_frame = Frame(window)
    tree_frame.grid(column=0, columnspan=3, pady = 25)

    tree_scroll = Scrollbar(tree_frame)
    tree_scroll.pack(side = RIGHT, fill=Y)

    my_tree = ttk.Treeview(tree_frame,yscrollcommand=tree_scroll.set, selectmode = "extended")
    my_tree.pack()

    tree_scroll.config(command=my_tree.yview)

    my_tree["columns"] =  ("Website", "User/email", "Password")
    my_tree.column("#0", width = 0, stretch = NO)
    my_tree.column("Website", anchor = W, width = 140)
    my_tree.column("User/email", anchor = W, width = 140)
    my_tree.column("Password", anchor = W, width = 140)

    my_tree.heading("#0", text = "", anchor = W)
    my_tree.heading("Website", text = "Website", anchor = W)
    my_tree.heading("User/email",text = "User/email", anchor = W)
    my_tree.heading("Password",text = "Password", anchor = W)

    show_theme_status = theme_parser()
    if show_theme_status == "light":
        my_tree.tag_configure("oddrow", background=selected_primary)
        my_tree.tag_configure("evenrow", background=selected_third)
    else:
        my_tree.tag_configure("oddrow", background=selected_secundary)
        my_tree.tag_configure("evenrow", background=selected_third)
    count = 0
    for record in data:
        if count%2 ==0:
            my_tree.insert(parent = "", index = "end", iid=count, text="", values=(record[1], dec(record[2]), dec(record[3])), tags=("evenrow",))
        else:
            my_tree.insert(parent = "", index = "end", iid=count, text="", values=(record[1], dec(record[2]), dec(record[3])), tags=("oddrow",))
        count += 1
    
    

#   11. New entry screen
def new_entry():
    for widget in window.winfo_children():
        widget.destroy()
    
    menu_bar_function()
    lbl = Label(window, text = "Add website", bg = selected_primary, fg = selected_secundary)
    lbl.pack(pady = 10)
    txt = Entry(window)
    txt.pack()
    txt.focus()

    lbl1 = Label(window, text = "Add usename or email", bg = selected_primary, fg = selected_secundary)
    lbl1.pack(pady = 10)
    txt1 = Entry(window)
    txt1.pack()

    lbl2 = Label(window, text = "Add password", bg = selected_primary, fg = selected_secundary)
    lbl2.pack(pady = 10)
    txt2 = Entry(window)
    txt2.pack()

    def generation():
        suggestion = generate_password()
        txt2.delete(0, "end")
        txt2.insert(0, suggestion)

    btn = Button(window, text = "Generate Password", command=generation, background = selected_third, foreground= "black")
    btn.pack(pady = 10)
    
    
    #   12.Save new credentials in database
    def save():
        values = (str(txt.get()), enc(str(txt1.get())), enc(str(txt2.get())))
        cursor.execute("""INSERT INTO passwords(id, website, username, password) VALUES(null, ?,?,?)""", values)
        db.commit()
        vault()

    btn = Button(window, text = "Save", command = save, background = selected_third, foreground= "black")
    btn.pack(pady = 10)

#   14.Delete option

def delete():
    for widget in window.winfo_children():
        widget.destroy()
    
    menu_bar_function()
    lbl = Label(window, text = "Website", bg = selected_primary, fg = selected_secundary)
    lbl.pack(pady = 10)
    txt = Entry(window)
    txt.pack()
    txt.focus()

    lbl1 = Label(window, text = "Username", bg = selected_primary, fg = selected_secundary)
    lbl1.pack(pady = 10)
    txt1 = Entry(window)
    txt1.pack()

    def dele():
        cursor.execute("SELECT * FROM passwords")
        data = cursor.fetchall()
        for row in data:
            new_data = list(row)
            if new_data[1] == str(txt.get()) and dec(new_data[2]) == str(txt1.get()):
                data_id = new_data[0] 
        cursor.execute("DELETE FROM passwords WHERE id=?", (data_id, ))
        db.commit()
        vault()

    btn = Button(window, text = "Delete", command = dele, background = selected_third, foreground= "black")
    btn.pack(pady = 10)

#   15.Update credentials
def update_info():
    
    for widget in window.winfo_children():
        widget.destroy()

    menu_bar_function()
    lbl = Label (window, text = "Enter old credentials", bg = selected_primary, fg = selected_secundary)
    lbl.pack(pady = 10)

    lbl = Label(window, text = "Website", bg = selected_primary, fg = selected_secundary)
    lbl.pack(pady = 10)
    txt = Entry(window)
    txt.pack()
    txt.focus()

    lbl1 = Label(window, text = "Username", bg = selected_primary, fg = selected_secundary)
    lbl1.pack(pady = 10)
    txt1 = Entry(window)
    txt1.pack()

    lbl2 = Label(window, text = "Password", bg = selected_primary, fg = selected_secundary)
    lbl2.pack(pady = 10)
    txt2 = Entry(window)
    txt2.pack()

    lbl3 = Label(window, bg = selected_primary, fg = selected_secundary)
    lbl3.pack(pady = 10)
    
    def search_credentials():
        cursor.execute("SELECT * FROM passwords")
        data = cursor.fetchall()
        for row in data:
            new_data = list(row)
            if new_data[1] == str(txt.get()) and dec(new_data[2]) == str(txt1.get()) and dec(new_data[3]) == str(txt2.get()):
                data_id = new_data[0] 

        if len(str(data_id)) == 0:
            lbl3.configure(text = "No such credentials in the databse")
        else: 
            def update_screen():
                for widget in window.winfo_children():
                    widget.destroy()
                
                menubar = Menu(window)
                window.config(menu = menubar)
                def go_back():
                    update_info()
                menubar.add_command(label = "Back", command=go_back)
            
                lbl = Label (window, text = "Enter new credentials", bg = selected_primary, fg = selected_secundary)
                lbl.pack(pady = 10)

                lbl = Label(window, text = "Website", bg = selected_primary, fg = selected_secundary)
                lbl.pack(pady = 10)
                txt = Entry(window)
                txt.pack()
                txt.focus()

                lbl1 = Label(window, text = "Username", bg = selected_primary, fg = selected_secundary)
                lbl1.pack(pady = 10)
                txt1 = Entry(window)
                txt1.pack()

                lbl2 = Label(window, text = "Password", bg = selected_primary, fg = selected_secundary)
                lbl2.pack(pady = 10)
                txt2 = Entry(window)
                txt2.pack()

                def update_credentials():
                    values = (str(txt.get()), enc(str(txt1.get())), enc(str(txt2.get())), str(data_id))
                    cursor.execute(f"UPDATE passwords SET website = ?, username = ?, password = ? WHERE id = ?", values)
                    db.commit()
                    vault()

                def generation():
                    suggestion = generate_password()
                    txt2.delete(0, "end")
                    txt2.insert(0, suggestion)

                btn = Button(window, text = "Generate Password", command = generation, background = selected_third, foreground= "black")
                btn.pack(pady = 10)

                btn = Button(window, text = "Update", command = update_credentials, background = selected_third, foreground= "black")
                btn.pack(pady = 10)

            update_screen()
        
    btn = Button(window, text = "Search", command = search_credentials, background = selected_third, foreground= "black")
    btn.pack(pady = 10)

#   16. Show all function
def show_all():

    #   19. Creating a config file and save settings

    show_hide_status = show_parser()
    if show_hide_status == "hide":
        show_treeview()
        new_status = "show"
        parser = ConfigParser()
        parser.read("config.ini")
        parser.set("show", "status", new_status)
        with open("config.ini", "w") as configfile:
            parser.write(configfile)

    if show_hide_status == "show":
        new_status = "hide"
        parser = ConfigParser()
        parser.read("config.ini")
        parser.set("show", "status", new_status)
        with open("config.ini", "w") as configfile:
            parser.write(configfile)
        vault()
        
#   17. Query database function
def query_database():
    for widget in window.winfo_children():
        widget.destroy()

    menu_bar_function()    
    lbl = Label(window, text= "Enter website", bg = selected_primary, fg = selected_secundary)
    lbl.grid(row = 0, column = 1, pady = 10)
 
    txt = Entry(window)
    txt.grid(row = 1, column = 1)
    lbl = Label(window, text = "Enter username/email", bg = selected_primary, fg = selected_secundary)
    lbl.grid(row = 2, column = 1, pady = 10)
    txt1 = Entry(window)
    txt1.grid(row = 3, column = 1)
    lbl = Label(window, text = "You can search by website, user or both", bg = selected_primary, fg = selected_secundary)
    lbl.grid(row = 4, column = 1)
    def search_and_display():
        cursor.execute("SELECT * FROM passwords")
        data = cursor.fetchall()
        decrypted_data = []
        for row in data:
            row_id, website, user, password = row 
            decrypted_row = [row_id, website, dec(user), dec(password)]
            decrypted_data.append(decrypted_row)
        i=7
        for element in decrypted_data:
            if element[1]==str(txt.get()) or element[2] == str(txt1.get()):
                lbl = Label(window, text = f"{element[1]}", bg = selected_primary, fg = selected_secundary)
                lbl.grid(row = i, column = 0)
                lbl = Label(window, text = f"{element[2]}", bg = selected_primary, fg = selected_secundary)
                lbl.grid(row = i, column = 1)
                lbl = Label(window, text = f"{element[3]}", bg = selected_primary, fg = selected_secundary)
                lbl.grid(row = i, column = 2)
                i+=1
    btn = Button(window, text = "Search", command = search_and_display, background = selected_third, foreground= "black")
    btn.grid(row = 5, column = 1, pady = 10, padx = 47)
    lbl = Label(window, text = "Website", bg = selected_primary, fg = selected_secundary)
    lbl.grid(row = 6, column = 0, padx = 55, pady = 10)
    lbl = Label(window, text = "Username", bg = selected_primary, fg = selected_secundary)
    lbl.grid(row = 6, column = 1, padx = 55, pady = 10)
    lbl = Label(window, text = "Password", bg = selected_primary, fg = selected_secundary)
    lbl.grid(row = 6, column = 2, padx = 55, pady = 10)
    
#   18. Settings function
def settings_screen():
    for widget in window.winfo_children():
        widget.destroy()
    menu_bar_function()

    light = PhotoImage(file = "Lightmode.png")
    dark = PhotoImage(file = "Darkmode.png")

    show_theme_status = theme_parser()
    if show_theme_status == "light":
        settings_label_text = "Light mode on"
        show_image = dark
    else:
        settings_label_text = "Dark mode on"
        show_image = light

    lbl = Label(window, text = settings_label_text, bg = selected_primary, fg = selected_secundary)
    lbl.pack(pady = 10)
    
    def switch():
        show_theme_status = theme_parser()
        # Determine  light or dark
        if show_theme_status == "light":
            global selected_primary
            global selected_secundary
            global selected_third
            mode_button.config(image = light)
            selected_primary, selected_secundary, selected_third = dark_primary, dark_secundary, dark_third
            window.configure(bg = selected_primary)
            lbl.config(text = "Dark mode on", bg = selected_primary, fg = selected_secundary)
            new_status = "dark"
            parser = ConfigParser()
            parser.read("config.ini")
            parser.set("theme", "status", new_status)
            with open("config.ini", "w") as configfile:
                parser.write(configfile)
        else:
            selected_primary, light_secundary, light_third = light_primary, light_secundary, light_third
            mode_button.config(image = dark)
            window.configure(bg = selected_primary)
            lbl.config(text = "Light mode on", bg = selected_primary, fg = selected_secundary)
            new_status = "light"
            parser = ConfigParser()
            parser.read("config.ini")
            parser.set("theme", "status", new_status)
            with open("config.ini", "w") as configfile:
                parser.write(configfile)
    
    mode_button = Button(window,image = show_image, bd = 0,command = switch)
    mode_button.pack(pady = 50)
#   8.If pass in db, chose a screen
cursor.execute("SELECT * FROM master_password")
if cursor.fetchall():
    login()
else:
    setup()

window.mainloop()