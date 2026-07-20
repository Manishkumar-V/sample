from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import sqlite3
import random
import os

try:
    from PIL import ImageTk, Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import calendar as cal_module
from datetime import date

# ###################DATABASE Functions

DB_NAME = "ATMdatabase.db"

# ###################ADMIN Credentials
# Simple hardcoded admin login (separate from customer records in the DB).
ADMIN_USERNAME = "admin"
ADMIN_PIN = "1234"

def migrate_database():
    """Migrate existing database to include balance column if it doesn't exist."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        # Check if balance column exists
        cur.execute("PRAGMA table_info(Registration_data)")
        columns = [column[1] for column in cur.fetchall()]
        
        if "balance" not in columns:
            # Add balance column to existing table
            cur.execute("ALTER TABLE Registration_data ADD COLUMN balance real DEFAULT 0.0")
            con.commit()
            print("Migration: Added 'balance' column to Registration_data table")
    except sqlite3.OperationalError as e:
        print(f"Migration error: {e}")
    finally:
        con.close()

def create_registration_table():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Registration_data(
        Name text,
        gender text,
        dob text,
        Mobile_No text,
        Aadhar_No integer,
        username text,
        Account_number integer,
        PIN integer,
        balance real DEFAULT 0.0
    )""")
    con.commit()
    con.close()
    migrate_database()  # Run migration after creating/checking table

# ####GUI
root = Tk()
root.geometry('600x500')
root.resizable(0, 0)
root.title("ATM - Login")

global account_userName
account_userName = StringVar()

# ####Helper to load a background image safely (falls back to plain color if missing)
def load_bg(frame, filename, fallback_bg="#317099"):
    path = os.path.join("./Additional_files", filename)
    if PIL_AVAILABLE and os.path.exists(path):
        img = ImageTk.PhotoImage(Image.open(path))
        lbl = Label(frame, bg=fallback_bg, width=600, height=500, image=img)
        lbl.image = img  # keep reference so it isn't garbage collected
        lbl.place(x=0, y=0)
    else:
        frame.configure(bg=fallback_bg)

# #Functions############

def check_user_exist(un):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("SELECT username from Registration_data")
        li = cur.fetchall()
        li = [i for i in li if i[0] == un]
        return len(li)
    except sqlite3.OperationalError:
        return 0
    finally:
        con.close()

def check_acNo_exist(un):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("SELECT Account_number from Registration_data")
        li = cur.fetchall()
        un = int(un)
        li = [i for i in li if i[0] == un]
        return len(li)
    except (sqlite3.OperationalError, ValueError):
        return 0
    finally:
        con.close()

def get_PIN(username):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("SELECT PIN FROM Registration_data WHERE username=?", (username,))
        row = cur.fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        return None
    finally:
        con.close()

def get_all_customers():
    """Returns a list of tuples: (Name, gender, dob, Mobile_No, Aadhar_No, username, Account_number, balance)
    -- PIN is intentionally left out of what the admin panel displays."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("""SELECT Name, gender, dob, Mobile_No, Aadhar_No, username, Account_number, COALESCE(balance, 0.0)
                        FROM Registration_data""")
        return cur.fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()

def create_transactions_table():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Transactions(
        username text,
        ttype text,
        amount real,
        reason text,
        note text,
        txn_date text
    )""")
    con.commit()
    con.close()

def search_customers(term):
    """Matches on username, account number, or a partial (case-insensitive) name."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        like_term = f"%{term}%"
        cur.execute("""SELECT Name, gender, dob, Mobile_No, Aadhar_No, username, Account_number, COALESCE(balance, 0.0)
                        FROM Registration_data
                        WHERE username = ? OR Account_number = ? OR Name LIKE ?""",
                    (term, term if term.isdigit() else -1, like_term))
        return cur.fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()

def get_customer_by_username(username):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("""SELECT Name, gender, dob, Mobile_No, Aadhar_No, username, Account_number, COALESCE(balance, 0.0)
                        FROM Registration_data WHERE username=?""", (username,))
        return cur.fetchone()
    except sqlite3.OperationalError:
        return None
    finally:
        con.close()

def update_customer_record(original_username, name, gender, dob, mobile, aadhar, new_username):
    """Updates every editable field for a customer, keyed on their original username.
    PIN and Account_number are left untouched here (handled elsewhere)."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("""UPDATE Registration_data
                        SET Name=?, gender=?, dob=?, Mobile_No=?, Aadhar_No=?, username=?
                        WHERE username=?""",
                    (name, gender, dob, mobile, aadhar, new_username, original_username))
        con.commit()
        return cur.rowcount > 0
    except sqlite3.OperationalError:
        return False
    finally:
        con.close()

def delete_customer_record(username):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM Registration_data WHERE username=?", (username,))
        con.commit()
        return cur.rowcount > 0
    except sqlite3.OperationalError:
        return False
    finally:
        con.close()

def get_customer_balance(username):
    """Get the current balance for a customer."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("SELECT COALESCE(balance, 0.0) FROM Registration_data WHERE username=?", (username,))
        row = cur.fetchone()
        return row[0] if row else 0.0
    except sqlite3.OperationalError:
        return 0.0
    finally:
        con.close()

def update_customer_balance(username, new_balance):
    """Update the balance for a customer."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("UPDATE Registration_data SET balance=? WHERE username=?", (new_balance, username))
        con.commit()
        return True
    except sqlite3.OperationalError:
        return False
    finally:
        con.close()

def get_transactions(username=None):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        if username:
            cur.execute("SELECT txn_date, username, ttype, amount, reason, note FROM Transactions WHERE username=? ORDER BY txn_date DESC", (username,))
        else:
            cur.execute("SELECT txn_date, username, ttype, amount, reason, note FROM Transactions ORDER BY txn_date DESC")
        return cur.fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()

def add_transaction(username, ttype, amount, reason="", note=""):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO Transactions VALUES (?,?,?,?,?,?)",
                     (username, ttype, amount, reason, note, date.today().strftime("%d/%m/%Y")))
        con.commit()
    except sqlite3.OperationalError:
        create_transactions_table()
        cur.execute("INSERT INTO Transactions VALUES (?,?,?,?,?,?)",
                     (username, ttype, amount, reason, note, date.today().strftime("%d/%m/%Y")))
        con.commit()
    finally:
        con.close()

def get_report_stats():
    """Aggregate stats pulled from whatever customer/transaction data currently exists."""
    customers = get_all_customers()
    total_customers = len(customers)
    gender_counts = {"Male": 0, "Female": 0, "Others": 0}
    ages = []
    total_balance = 0.0
    
    for row in customers:
        gender = row[1]
        if gender in gender_counts:
            gender_counts[gender] += 1
        age = calculate_age(row[2])
        if age is not None:
            ages.append(age)
        total_balance += row[7]  # balance is at index 7
    
    avg_age = round(sum(ages) / len(ages), 1) if ages else 0

    txns = get_transactions()
    total_txns = len(txns)
    total_deposits = round(sum(t[3] for t in txns if t[2] == "Deposit"), 2) if txns else 0
    total_withdrawals = round(sum(t[3] for t in txns if t[2] == "Withdrawal"), 2) if txns else 0

    return {
        "total_customers": total_customers,
        "gender_counts": gender_counts,
        "avg_age": avg_age,
        "total_txns": total_txns,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_balance": round(total_balance, 2),
    }

def calculate_age(dob_str):
    """dob_str is expected as dd/mm/yyyy. Returns age in years, or None if unparsable."""
    try:
        day, month, year = (int(part) for part in dob_str.split("/"))
        born = date(year, month, day)
    except (ValueError, AttributeError):
        return None
    today = date.today()
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    return age

def generateAcNo(e):
    acNo = random.randint(11111111, 99999999)
    e.delete(0, END)
    e.insert(0, acNo)

def login(e1, e2):
    global account_userName
    username = e1.get()
    password = e2.get()

    if "" in (username, password):
        tkinter.messagebox.showerror('Error Message', 'Missing fields')
        return

    # ___Admin login check (fixed credentials, not part of the customer table)___
    if username == ADMIN_USERNAME and password == ADMIN_PIN:
        tkinter.messagebox.showinfo('Successful', 'Admin Login Successful')
        AdminWindow()
        return

    # ___Customer login check___
    dbPass = get_PIN(username)
    if dbPass is not None and password == str(dbPass):
        tkinter.messagebox.showinfo('Successful', 'Login Successfully')
        account_userName.set(username)
        WelcomeWindow()
    else:
        tkinter.messagebox.showerror('Error Message', 'Invalid Username/PIN')

def registration_data(en1, en2, en4, en5, en6, en7, en8):
    pin = random.randint(1111, 9999)
    name = en1.get()

    gender = en2.get()
    if gender == 1:
        gender = "Male"
    elif gender == 2:
        gender = "Female"
    else:
        gender = "Others"

    dob = en4.get()
    cNo = en5.get()
    AdharNo = en6.get()
    Username = en7.get()
    acNo = en8.get()

    if "" in (name, gender, dob, cNo, AdharNo, Username, acNo):
        tkinter.messagebox.showerror(title="Error", message="Missing Fields")
        return

    age = calculate_age(dob)
    if age is None:
        tkinter.messagebox.showerror(title="Error", message="Date of Birth is invalid")
        return
    if age < 18:
        tkinter.messagebox.showerror(title="Error", message="You must be at least 18 years old to register.")
        return

    if len(cNo) != 10:
        tkinter.messagebox.showerror(title="Error", message="Mobile Number is invalid")
        return
    try:
        int(cNo)
    except ValueError:
        tkinter.messagebox.showerror(title="Error", message="Mobile Number is invalid")
        return

    if len(AdharNo) != 12:
        tkinter.messagebox.showerror(title="Error", message="Aadhar Number is invalid")
        return
    try:
        int(AdharNo)
    except ValueError:
        tkinter.messagebox.showerror(title="Error", message="Aadhar Number is invalid")
        return

    if check_user_exist(Username) == 1:
        tkinter.messagebox.showerror(title="Error", message="Username already Exists. Try New!")
        return

    if check_acNo_exist(acNo) == 1:
        tkinter.messagebox.showerror(title="Error", message="Account Number already Exists. Try New!")
        return

    account_userName.set(Username)
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO Registration_data VALUES (?,?,?,?,?,?,?,?,?)",
                     (name, gender, dob, cNo, AdharNo, Username, acNo, pin, 0.0))
    except sqlite3.OperationalError:
        create_registration_table()
        cur.execute("INSERT INTO Registration_data VALUES (?,?,?,?,?,?,?,?,?)",
                     (name, gender, dob, cNo, AdharNo, Username, acNo, pin, 0.0))
    con.commit()
    con.close()
    tkinter.messagebox.showinfo(title="Successful", message=f"Account has been created. Your PIN is {pin}")
    Home()

def clear_root():
    for widget in root.winfo_children():
        widget.destroy()

# #Calendar Date-Picker (no external library needed)############

class DatePicker(Toplevel):
    """A small popup calendar. Clicking a day fills the given entry
    with a dd/mm/yyyy string and closes the popup."""

    def __init__(self, parent, entry_widget):
        super().__init__(parent)
        self.title("Select Date of Birth")
        self.resizable(0, 0)
        self.transient(parent)
        self.grab_set()

        self.entry_widget = entry_widget
        today = date.today()
        # Start on a plausible birth year (25 years back) rather than the
        # current year, so users don't have to click back through decades.
        self.year = today.year - 25
        self.month = today.month

        self.month_var = StringVar(value=cal_module.month_name[self.month])
        self.year_var = StringVar(value=str(self.year))

        self._build_widgets()

    def _build_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        header = Frame(self)
        header.pack(pady=5, padx=5)

        prevBtn = Button(header, text="<", width=2, command=self._prev_month)
        prevBtn.grid(row=0, column=0)

        month_names = list(cal_module.month_name)[1:]  # skip empty index 0
        self.month_var.set(cal_module.month_name[self.month])
        monthMenu = OptionMenu(header, self.month_var, *month_names, command=self._on_month_change)
        monthMenu.config(width=9, font='Helvetica 9')
        monthMenu.grid(row=0, column=1, padx=2)

        # Years from 100 years ago to the current year, most recent last
        # so opening the menu near "today" is quick, but any year is one click away.
        current_year = date.today().year
        year_options = [str(y) for y in range(current_year - 100, current_year + 1)]
        self.year_var.set(str(self.year))
        yearMenu = OptionMenu(header, self.year_var, *year_options, command=self._on_year_change)
        yearMenu.config(width=6, font='Helvetica 9')
        yearMenu.grid(row=0, column=2, padx=2)

        nextBtn = Button(header, text=">", width=2, command=self._next_month)
        nextBtn.grid(row=0, column=3)

        daysFrame = Frame(self)
        daysFrame.pack(padx=5, pady=(0, 5))

        for i, d in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
            Label(daysFrame, text=d, width=4, font='Helvetica 9 bold').grid(row=0, column=i)

        calendar_obj = cal_module.Calendar(firstweekday=0)
        month_days = calendar_obj.monthdayscalendar(self.year, self.month)

        for r, week in enumerate(month_days, start=1):
            for c, day in enumerate(week):
                if day == 0:
                    Label(daysFrame, text="", width=4).grid(row=r, column=c, pady=1)
                else:
                    Button(daysFrame, text=str(day), width=4,
                           command=lambda d=day: self._select_date(d)).grid(row=r, column=c, pady=1)

    def _prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self._build_widgets()

    def _next_month(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self._build_widgets()

    def _on_month_change(self, selected_name):
        self.month = list(cal_module.month_name).index(selected_name)
        self._build_widgets()

    def _on_year_change(self, selected_year):
        self.year = int(selected_year)
        self._build_widgets()

    def _select_date(self, day):
        selected = f"{day:02d}/{self.month:02d}/{self.year}"
        self.entry_widget.config(state='normal')
        self.entry_widget.delete(0, END)
        self.entry_widget.insert(0, selected)
        self.entry_widget.config(state='readonly')
        self.destroy()

# ####################### SCREENS #######################

def RegistrationWindow():
    clear_root()
    varGen = IntVar()  # Gender Variable

    signUpFrame = Frame(root, width=600, height=500)
    signUpFrame.place(x=0, y=0)
    root.title("Registration")

    load_bg(signUpFrame, "s.jpg", fallback_bg="#a9a9a9")

    lbIntr = Label(signUpFrame, width=20, text='Registration Form', fg="white", font='Helvetica 18 bold', bg="#317099")
    lbIntr.place(x=20, y=20)

    enAcNo = Entry(signUpFrame, width=14, font='Helvetica 12', bd=3)
    enAcNo.place(x=150, y=330)

    getNewAcNo = Button(signUpFrame, text="Get New", width=6, font="arial 8 bold", command=lambda: generateAcNo(enAcNo))
    getNewAcNo.place(x=295, y=330)

    lbName = Label(signUpFrame, width=11, text='Name', fg="white", font='Helvetica 12 bold', bg="#317099")
    lbName.place(x=20, y=90)

    lbGen = Label(signUpFrame, width=11, text='Gender', fg="white", font='Helvetica 12 bold', bg="#317099")
    lbGen.place(x=20, y=130)

    lbDob = Label(signUpFrame, width=11, text='Date of Birth', fg="white", font='Helvetica 12 bold', bg="#317099")
    lbDob.place(x=20, y=170)

    lbCont = Label(signUpFrame, width=11, text="Mobile No", fg="white", font='Helvetica 12 bold', bg="#317099")
    lbCont.place(x=20, y=210)

    lbAdhar = Label(signUpFrame, width=11, text="Aadhar No", fg="white", font='Helvetica 12 bold', bg="#317099")
    lbAdhar.place(x=20, y=250)

    lblUsername = Label(signUpFrame, width=11, text="User Name", fg="white", font='Helvetica 12 bold', bg="#317099")
    lblUsername.place(x=20, y=290)

    lblAcNumber = Label(signUpFrame, width=11, text="Account No", fg="white", font='Helvetica 12 bold', bg="#317099")
    lblAcNumber.place(x=20, y=330)

    enName = Entry(signUpFrame, width=21, font='Helvetica 12', bd=3)
    enName.place(x=150, y=90)

    genRadioMale = Radiobutton(signUpFrame, text="Male", font='Helvetica 8', variable=varGen, value=1)
    genRadioMale.place(x=150, y=130)

    genRadioFemale = Radiobutton(signUpFrame, text="Female", font='Helvetica 8', variable=varGen, value=2)
    genRadioFemale.place(x=210, y=130)

    genRadioOther = Radiobutton(signUpFrame, text="Others", font='Helvetica 8', variable=varGen, value=3)
    genRadioOther.place(x=280, y=130)

    # ____Date of Birth - calendar picker instead of free text_____
    enDob = Entry(signUpFrame, width=15, font='Helvetica 12', bd=3, state='readonly')
    enDob.place(x=150, y=170)

    dobCalBtn = Button(signUpFrame, text="📅", width=3, font="arial 8 bold",
                        command=lambda: DatePicker(root, enDob))
    dobCalBtn.place(x=280, y=170)

    enCno = Entry(signUpFrame, width=21, font='Helvetica 12', bd=3)
    enCno.place(x=150, y=210)

    enAdhar = Entry(signUpFrame, width=21, font='Helvetica 12', bd=3)
    enAdhar.place(x=150, y=250)

    enUsername = Entry(signUpFrame, width=21, font='Helvetica 12', bd=3)
    enUsername.place(x=150, y=290)

    submitButton = Button(signUpFrame, text="Submit", width=10, font="arial 10 bold",
                            command=lambda: registration_data(enName, varGen, enDob, enCno, enAdhar, enUsername, enAcNo))
    submitButton.place(x=50, y=420)

    resetButton = Button(signUpFrame, text="Reset", width=10, font="arial 10 bold", command=RegistrationWindow)
    resetButton.place(x=150, y=420)

    BackButton = Button(signUpFrame, text="Back", width=10, font="arial 10 bold", command=Home)
    BackButton.place(x=250, y=420)

def WelcomeWindow():
    """Simple placeholder shown after a successful login (auth-only project)."""
    clear_root()
    f1 = Frame(root, width=600, height=500, bg="#b32b59")
    f1.place(x=0, y=0)
    root.title("Welcome")

    lblWel = Label(f1, text=f'Welcome, {account_userName.get()}!', bg="#b32b59", fg="white", font='Helvetica 18 bold')
    lblWel.place(x=150, y=200)

    LogoutBTN = Button(f1, width=10, text='Logout', fg="white", font='arial 10 bold', bg="#95013d", borderwidth=5, command=Home)
    LogoutBTN.place(x=250, y=280)

# _ Admin window (shown after admin login) ____________________________________________________
# The dashboard is a persistent sidebar (8 menu options) + a content area on the
# right that gets cleared and rebuilt whenever a menu option is chosen.

ADMIN_WIN_W, ADMIN_WIN_H = 1000, 560
SIDEBAR_W = 200

def AdminWindow():
    """Admin dashboard entry point. Builds the sidebar once, then defaults to
    the 'View All Customers' panel."""
    clear_root()
    root.geometry(f'{ADMIN_WIN_W}x{ADMIN_WIN_H}')
    root.resizable(0, 0)
    root.title("Admin Dashboard")

    create_transactions_table()

    outer = Frame(root, width=ADMIN_WIN_W, height=ADMIN_WIN_H, bg="#1c2b39")
    outer.place(x=0, y=0)

    sidebar = Frame(outer, width=SIDEBAR_W, height=ADMIN_WIN_H, bg="#12202c")
    sidebar.place(x=0, y=0)

    content = Frame(outer, width=ADMIN_WIN_W - SIDEBAR_W, height=ADMIN_WIN_H, bg="#f2f2f2")
    content.place(x=SIDEBAR_W, y=0)

    lblTitle = Label(sidebar, text='Admin Menu', bg="#12202c", fg="white", font='Helvetica 14 bold')
    lblTitle.place(x=20, y=15)

    menu_items = [
        ("1. Add Customer", lambda: _admin_add_customer(content)),
        ("2. View All Customers", lambda: _admin_view_all(content)),
        ("3. Search Customer", lambda: _admin_search(content)),
        ("4. Update Customer", lambda: _admin_update(content)),
        ("5. Delete Customer", lambda: _admin_delete(content)),
        ("6. Deposit Amount", lambda: _admin_deposit(content)),
        ("7. Withdrawal Amount", lambda: _admin_withdrawal(content)),
        ("8. View Transactions", lambda: _admin_transactions(content)),
        ("9. Generate Reports", lambda: _admin_reports(content)),
        ("10. Logout", Home),
    ]

    for i, (label, cmd) in enumerate(menu_items):
        btn = Button(sidebar, text=label, width=22, anchor="w", font='arial 8 bold',
                     fg="white", bg="#317099", activebackground="#3d8bbd",
                     borderwidth=0, command=cmd)
        btn.place(x=15, y=60 + i * 38)

    _admin_view_all(content)  # default landing panel


def _clear_content(content):
    for widget in content.winfo_children():
        widget.destroy()


def _content_heading(content, text):
    Label(content, text=text, bg="#f2f2f2", fg="#1c2b39", font='Helvetica 15 bold').place(x=20, y=15)


def _make_customer_table(parent, x, y, width, height):
    tableFrame = Frame(parent)
    tableFrame.place(x=x, y=y, width=width, height=height)
    columns = ("Name", "Gender", "DOB", "Mobile No", "Aadhar No", "Username", "Account No", "Balance")
    tree = ttk.Treeview(tableFrame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=95, anchor="center")
    scrollbar = ttk.Scrollbar(tableFrame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)
    return tree


# ___ 1. Add Customer ___________________________________________________________
def _admin_add_customer(content):
    _clear_content(content)
    _content_heading(content, "Add Customer")

    varGen = IntVar()
    fields = [
        ("Name", 60), ("Gender", 100), ("Date of Birth", 140), ("Mobile No", 180),
        ("Aadhar No", 220), ("User Name", 260), ("Account No", 300),
    ]
    for label, y in fields:
        Label(content, text=label, bg="#f2f2f2", font='Helvetica 11 bold', width=11, anchor="w").place(x=20, y=y)

    enName = Entry(content, width=25, font='Helvetica 11', bd=2); enName.place(x=170, y=60)
    Radiobutton(content, text="Male", variable=varGen, value=1, bg="#f2f2f2").place(x=170, y=100)
    Radiobutton(content, text="Female", variable=varGen, value=2, bg="#f2f2f2").place(x=230, y=100)
    Radiobutton(content, text="Others", variable=varGen, value=3, bg="#f2f2f2").place(x=300, y=100)

    enDob = Entry(content, width=15, font='Helvetica 11', bd=2, state='readonly'); enDob.place(x=170, y=140)
    Button(content, text="📅", width=3, command=lambda: DatePicker(root, enDob)).place(x=300, y=140)

    enCno = Entry(content, width=25, font='Helvetica 11', bd=2); enCno.place(x=170, y=180)
    enAdhar = Entry(content, width=25, font='Helvetica 11', bd=2); enAdhar.place(x=170, y=220)
    enUsername = Entry(content, width=25, font='Helvetica 11', bd=2); enUsername.place(x=170, y=260)
    enAcNo = Entry(content, width=15, font='Helvetica 11', bd=2); enAcNo.place(x=170, y=300)
    Button(content, text="Get New", width=6, font="arial 8 bold",
           command=lambda: generateAcNo(enAcNo)).place(x=300, y=300)

    def submit():
        registration_data(enName, varGen, enDob, enCno, enAdhar, enUsername, enAcNo)
        _admin_view_all(content)  # jump to the updated list once added

    Button(content, text="Add Customer", width=14, font="arial 10 bold", bg="#317099", fg="white",
           command=submit).place(x=170, y=350)


# ___ 2. View All Customers _____________________________________________________
def _admin_view_all(content):
    _clear_content(content)
    _content_heading(content, "All Registered Customers")
    tree = _make_customer_table(content, 20, 55, 760, 380)
    for row in get_all_customers():
        tree.insert("", END, values=row)
    Button(content, text="Refresh", width=10, font='arial 9 bold', bg="#317099", fg="white",
           command=lambda: _admin_view_all(content)).place(x=20, y=445)


# ___ 3. Search Customer _________________________________________________________
def _admin_search(content):
    _clear_content(content)
    _content_heading(content, "Search Customer")

    Label(content, text="Username / Account No / Name:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=55)
    enSearch = Entry(content, width=30, font='Helvetica 11', bd=2)
    enSearch.place(x=280, y=55)

    tree = _make_customer_table(content, 20, 95, 760, 340)

    def do_search():
        for i in tree.get_children():
            tree.delete(i)
        term = enSearch.get().strip()
        if not term:
            return
        for row in search_customers(term):
            tree.insert("", END, values=row)

    Button(content, text="Search", width=10, font='arial 9 bold', bg="#317099", fg="white",
           command=do_search).place(x=600, y=52)


# ___ 4. Update Customer _________________________________________________________
def _admin_update(content):
    _clear_content(content)
    _content_heading(content, "Update Customer")

    Label(content, text="Enter existing Username:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=55)
    enLookup = Entry(content, width=22, font='Helvetica 11', bd=2)
    enLookup.place(x=220, y=55)

    formFrame = Frame(content, bg="#f2f2f2")
    formFrame.place(x=20, y=100, width=760, height=320)

    def load_customer():
        for w in formFrame.winfo_children():
            w.destroy()
        row = get_customer_by_username(enLookup.get().strip())
        if not row:
            Label(formFrame, text="No customer found with that username.", bg="#f2f2f2", fg="red",
                  font='Helvetica 10 bold').place(x=0, y=0)
            return

        name, gender, dob, mobile, aadhar, username, acno, balance = row
        varGen = IntVar(value={"Male": 1, "Female": 2}.get(gender, 3))

        Label(formFrame, text="Name", bg="#f2f2f2", font='Helvetica 10 bold', width=11, anchor="w").place(x=0, y=0)
        enName = Entry(formFrame, width=25, font='Helvetica 11', bd=2); enName.place(x=150, y=0)
        enName.insert(0, name)

        Label(formFrame, text="Gender", bg="#f2f2f2", font='Helvetica 10 bold', width=11, anchor="w").place(x=0, y=40)
        Radiobutton(formFrame, text="Male", variable=varGen, value=1, bg="#f2f2f2").place(x=150, y=40)
        Radiobutton(formFrame, text="Female", variable=varGen, value=2, bg="#f2f2f2").place(x=210, y=40)
        Radiobutton(formFrame, text="Others", variable=varGen, value=3, bg="#f2f2f2").place(x=280, y=40)

        Label(formFrame, text="Date of Birth", bg="#f2f2f2", font='Helvetica 10 bold', width=11, anchor="w").place(x=0, y=80)
        enDob = Entry(formFrame, width=15, font='Helvetica 11', bd=2, state='normal')
        enDob.insert(0, dob); enDob.config(state='readonly')
        enDob.place(x=150, y=80)
        Button(formFrame, text="📅", width=3, command=lambda: DatePicker(root, enDob)).place(x=280, y=80)

        Label(formFrame, text="Mobile No", bg="#f2f2f2", font='Helvetica 10 bold', width=11, anchor="w").place(x=0, y=120)
        enCno = Entry(formFrame, width=25, font='Helvetica 11', bd=2); enCno.place(x=150, y=120)
        enCno.insert(0, mobile)

        Label(formFrame, text="Aadhar No", bg="#f2f2f2", font='Helvetica 10 bold', width=11, anchor="w").place(x=0, y=160)
        enAdhar = Entry(formFrame, width=25, font='Helvetica 11', bd=2); enAdhar.place(x=150, y=160)
        enAdhar.insert(0, aadhar)

        Label(formFrame, text="User Name", bg="#f2f2f2", font='Helvetica 10 bold', width=11, anchor="w").place(x=0, y=200)
        enNewUser = Entry(formFrame, width=25, font='Helvetica 11', bd=2); enNewUser.place(x=150, y=200)
        enNewUser.insert(0, username)

        def save():
            gender_map = {1: "Male", 2: "Female", 3: "Others"}
            ok = update_customer_record(
                username, enName.get(), gender_map.get(varGen.get(), "Others"),
                enDob.get(), enCno.get(), enAdhar.get(), enNewUser.get()
            )
            if ok:
                tkinter.messagebox.showinfo("Success", "Customer updated.")
                _admin_view_all(content)
            else:
                tkinter.messagebox.showerror("Error", "Update failed.")

        Button(formFrame, text="Save Changes", width=14, font="arial 10 bold", bg="#317099", fg="white",
               command=save).place(x=150, y=250)

    Button(content, text="Load", width=8, font='arial 9 bold', bg="#317099", fg="white",
           command=load_customer).place(x=450, y=52)


# ___ 5. Delete Customer _________________________________________________________
def _admin_delete(content):
    _clear_content(content)
    _content_heading(content, "Delete Customer")

    Label(content, text="Enter Username to delete:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=55)
    enLookup = Entry(content, width=22, font='Helvetica 11', bd=2)
    enLookup.place(x=230, y=55)

    resultLbl = Label(content, text="", bg="#f2f2f2", font='Helvetica 10')
    resultLbl.place(x=20, y=100)

    def do_delete():
        username = enLookup.get().strip()
        if not username:
            return
        if not get_customer_by_username(username):
            resultLbl.config(text="No customer found with that username.", fg="red")
            return
        confirmed = tkinter.messagebox.askyesno("Confirm Delete",
                                                  f"Are you sure you want to delete '{username}'?")
        if not confirmed:
            return
        if delete_customer_record(username):
            resultLbl.config(text=f"Deleted '{username}'.", fg="green")
        else:
            resultLbl.config(text="Delete failed.", fg="red")

    Button(content, text="Delete", width=10, font='arial 9 bold', bg="#95013d", fg="white",
           command=do_delete).place(x=430, y=52)


# ___ 6. Deposit Amount __________________________________________________________
def _admin_deposit(content):
    _clear_content(content)
    _content_heading(content, "Deposit Amount")

    Label(content, text="Username:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=55)
    enUsername = Entry(content, width=22, font='Helvetica 11', bd=2)
    enUsername.place(x=220, y=55)

    Label(content, text="Amount:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=95)
    enAmount = Entry(content, width=22, font='Helvetica 11', bd=2)
    enAmount.place(x=220, y=95)

    Label(content, text="Reason:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=135)
    reasonVar = StringVar()
    reasons = ["ATM Deposit", "Transfer In", "Salary Credit", "Refund", "Other"]
    reasonMenu = OptionMenu(content, reasonVar, *reasons)
    reasonMenu.config(width=20, font='Helvetica 10')
    reasonMenu.place(x=220, y=135)
    reasonVar.set(reasons[0])

    Label(content, text="Notes:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=175)
    enNote = Entry(content, width=22, font='Helvetica 11', bd=2)
    enNote.place(x=220, y=175)

    resultLbl = Label(content, text="", bg="#f2f2f2", font='Helvetica 10')
    resultLbl.place(x=20, y=250)

    def do_deposit():
        username = enUsername.get().strip()
        try:
            amount = float(enAmount.get().strip())
            if amount <= 0:
                resultLbl.config(text="Amount must be greater than 0.", fg="red")
                return
        except ValueError:
            resultLbl.config(text="Invalid amount. Please enter a number.", fg="red")
            return

        customer = get_customer_by_username(username)
        if not customer:
            resultLbl.config(text="No customer found with that username.", fg="red")
            return

        current_balance = get_customer_balance(username)
        new_balance = current_balance + amount
        reason = reasonVar.get()
        note = enNote.get().strip()

        if update_customer_balance(username, new_balance):
            add_transaction(username, "Deposit", amount, reason, note)
            resultLbl.config(
                text=f"Deposit successful! Previous Balance: ₹{current_balance:.2f} → New Balance: ₹{new_balance:.2f}",
                fg="green"
            )
            enUsername.delete(0, END)
            enAmount.delete(0, END)
            enNote.delete(0, END)
        else:
            resultLbl.config(text="Deposit failed. Please try again.", fg="red")

    Button(content, text="Deposit", width=10, font='arial 9 bold', bg="#317099", fg="white",
           command=do_deposit).place(x=220, y=215)


# ___ 7. Withdrawal Amount _______________________________________________________
def _admin_withdrawal(content):
    _clear_content(content)
    _content_heading(content, "Withdrawal Amount")

    Label(content, text="Username:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=55)
    enUsername = Entry(content, width=22, font='Helvetica 11', bd=2)
    enUsername.place(x=220, y=55)

    Label(content, text="Amount:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=95)
    enAmount = Entry(content, width=22, font='Helvetica 11', bd=2)
    enAmount.place(x=220, y=95)

    Label(content, text="Reason:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=135)
    reasonVar = StringVar()
    reasons = ["ATM Withdrawal", "SMS Charge", "Annual ATM Maintenance", "Minimum Balance Fee", "Account Maintenance"]
    reasonMenu = OptionMenu(content, reasonVar, *reasons)
    reasonMenu.config(width=20, font='Helvetica 10')
    reasonMenu.place(x=220, y=135)
    reasonVar.set(reasons[0])

    Label(content, text="Notes:", bg="#f2f2f2", font='Helvetica 10 bold').place(x=20, y=175)
    enNote = Entry(content, width=22, font='Helvetica 11', bd=2)
    enNote.place(x=220, y=175)

    resultLbl = Label(content, text="", bg="#f2f2f2", font='Helvetica 10')
    resultLbl.place(x=20, y=250)

    def do_withdrawal():
        username = enUsername.get().strip()
        try:
            amount = float(enAmount.get().strip())
            if amount <= 0:
                resultLbl.config(text="Amount must be greater than 0.", fg="red")
                return
        except ValueError:
            resultLbl.config(text="Invalid amount. Please enter a number.", fg="red")
            return

        customer = get_customer_by_username(username)
        if not customer:
            resultLbl.config(text="No customer found with that username.", fg="red")
            return

        current_balance = get_customer_balance(username)
        if current_balance < amount:
            resultLbl.config(
                text=f"Insufficient balance. Current Balance: ₹{current_balance:.2f}",
                fg="red"
            )
            return

        new_balance = current_balance - amount
        reason = reasonVar.get()
        note = enNote.get().strip()

        if update_customer_balance(username, new_balance):
            add_transaction(username, "Withdrawal", amount, reason, note)
            resultLbl.config(
                text=f"Withdrawal successful! Previous Balance: ₹{current_balance:.2f} → New Balance: ₹{new_balance:.2f}",
                fg="green"
            )
            enUsername.delete(0, END)
            enAmount.delete(0, END)
            enNote.delete(0, END)
        else:
            resultLbl.config(text="Withdrawal failed. Please try again.", fg="red")

    Button(content, text="Withdraw", width=10, font='arial 9 bold', bg="#95013d", fg="white",
           command=do_withdrawal).place(x=220, y=215)


# ___ 8. View Transactions _______________________________________________________
def _admin_transactions(content):
    _clear_content(content)
    _content_heading(content, "Transactions")

    tableFrame = Frame(content)
    tableFrame.place(x=20, y=55, width=760, height=380)
    columns = ("Date", "Username", "Type", "Amount", "Reason", "Note")
    tree = ttk.Treeview(tableFrame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=125, anchor="center")
    scrollbar = ttk.Scrollbar(tableFrame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    rows = get_transactions()
    for row in rows:
        tree.insert("", END, values=row)

    if not rows:
        Label(content, text="No transactions recorded yet.",
              bg="#f2f2f2", fg="#555", font='Helvetica 9', justify="left").place(x=20, y=445)

    Button(content, text="Refresh", width=10, font='arial 9 bold', bg="#317099", fg="white",
           command=lambda: _admin_transactions(content)).place(x=20, y=445)


# ___ 9. Generate Reports ________________________________________________________
def _admin_reports(content):
    _clear_content(content)
    _content_heading(content, "Reports")

    stats = get_report_stats()

    lines = [
        f"Total Customers: {stats['total_customers']}",
        f"  Male: {stats['gender_counts']['Male']}   "
        f"Female: {stats['gender_counts']['Female']}   "
        f"Others: {stats['gender_counts']['Others']}",
        f"Average Customer Age: {stats['avg_age']} years",
        "",
        f"Total Transactions: {stats['total_txns']}",
        f"Total Deposits: ₹{stats['total_deposits']:.2f}",
        f"Total Withdrawals: ₹{stats['total_withdrawals']:.2f}",
        f"Total Customer Balance: ₹{stats['total_balance']:.2f}",
    ]

    y = 60
    for line in lines:
        Label(content, text=line, bg="#f2f2f2", fg="#1c2b39", font='Helvetica 11', justify="left", anchor="w") \
            .place(x=20, y=y, width=740)
        y += 30

    Button(content, text="Refresh", width=10, font='arial 9 bold', bg="#317099", fg="white",
           command=lambda: _admin_reports(content)).place(x=20, y=y + 20)


def Home():
    clear_root()
    root.geometry('600x500')
    mainFrame = Frame(root, height=500, width=600)
    mainFrame.place(x=0, y=0)
    root.title("ATM - Login")

    load_bg(mainFrame, "home.jpg", fallback_bg="#317099")

    lblIntro = Label(mainFrame, text='INTELLIGENT ATM PROJECT', width=23, height=2, bg="#ffd60c", font='arial 18 bold')
    lblIntro.place(x=240, y=40)

    lblAcNo = Label(mainFrame, text='User Name', width=15, font='Times 12')
    lblAcNo.place(x=250, y=150)

    lblPIN = Label(mainFrame, text='PIN', width=15, font='times 12')
    lblPIN.place(x=250, y=200)

    enUser = Entry(mainFrame, width=20, font='times 12', bd=3)
    enUser.place(x=400, y=150)

    enPass = Entry(mainFrame, width=20, font='times 12', bd=3, show="*")
    enPass.place(x=400, y=200)

    loginButton = Button(mainFrame, text="Login", width=10, font="arial 10 bold", command=lambda: login(enUser, enPass))
    loginButton.place(x=360, y=250)

    signupButton = Button(mainFrame, text="New User? Create an Account", width=30, font="arial 10 bold", command=RegistrationWindow)
    signupButton.place(x=280, y=300)

create_registration_table()
create_transactions_table()
Home()
root.mainloop()
