from tkinter import * 
from tkinter import messagebox 
from tkinter import ttk
import datetime

import sqlite3 as mysql
connection = mysql.connect('ATM_Users1.db')
mycursor = connection.cursor() 
mycursor.execute('''CREATE TABLE IF NOT EXISTS users
        (user_name TEXT PRIMARY KEY,
        password TEXT,
        balance TEXT,
        dob TEXT,
        phoneno TEXT,
        gender TEXT,
        address TEXT,
        trans TEXT)''')


#For creating welcome window:  
welcome_screen = Tk()
welcome_screen.geometry("1100x700+220+80") 
welcome_screen.resizable(0,0)
welcome_screen.title("ATM Service")
welcome_screen.iconbitmap(default="1.ico") 


#Image setting:

bank_icon = PhotoImage(file="bank.png") 
dollar_icon = PhotoImage(file="dollar.png") 
withdraw_icon = PhotoImage(file="withdraw.png") 
deposit_icon = PhotoImage(file="deposit.png") 
check_your_balance_icon = PhotoImage(file="check_your_balance.png") 
change_your_pin_icon = PhotoImage(file="change_your_pin.png")
account_info_icon = PhotoImage(file="account_info.png") 
username_icon = PhotoImage(file="account_info.png")
password_icon = PhotoImage(file="password.png") 
new_icon = PhotoImage(file="new.png")
confirm_icon = PhotoImage(file="confirm.png")
trans_icon = PhotoImage(file="tran.png")
phoneno_icon = PhotoImage(file="mobli.png")
window_bg = PhotoImage(file="window_bg.png") 

global_username = [" "]
menu_im = [" "," "," "," "," "," "]
menu_btn = [" "," "," "," "," "," "]

def fetch_usernames():
    mycursor.execute("SELECT user_name FROM users")
    usernames = [row[0] for row in mycursor.fetchall()]
    return usernames

def fetch_password():
        query = "select password from users where user_name = '{}';".format(global_username[0])
        mycursor.execute(query)
        password = mycursor.fetchone()
        password = password[0]
        return password

def fetch_balance():
        query = "select balance from users where user_name = '{}';".format(global_username[0])
        mycursor.execute(query)
        balance = mycursor.fetchone()
        balance = balance[0]
        return balance

def fetch_dob():
        query = "select dob from users where user_name = '{}';".format(global_username[0])
        mycursor.execute(query)
        dob = mycursor.fetchone()
        dob = dob[0]
        return dob

def fetch_phoneno():
        query = "select phoneno from users where user_name = '{}';".format(global_username[0])  
        mycursor.execute(query)
        phoneno = mycursor.fetchone()
        phoneno = phoneno[0]
        return phoneno

    
def fetch_gender():
        query = "select gender from users where user_name = '{}';".format(global_username[0])
        mycursor.execute(query)
        gender = mycursor.fetchone()
        gender = gender[0]
        return gender

def fetch_address():
        query = "select address from users where user_name = '{}';".format(global_username[0])
        mycursor.execute(query)
        address = mycursor.fetchone()
        address = address[0]
        return address

def fetch_trans():
        query = "select trans from users where user_name = '{}';".format(global_username[0])
        mycursor.execute(query)
        transation = mycursor.fetchone()
        trans = transation[0]
        return trans

def update_trans(log):
        query = "UPDATE users SET trans = ? WHERE user_name = ?"
        values = (log, global_username[0])
        mycursor.execute(query, values)
        mycursor.connection.commit()
     
def save_un_ps_ba_dob_phoneno_gen_address(username,password,dob,phoneno,gen,address):
        if (gen==1):
                gender = "MALE"
        else:
                gender = "FEMALE"
        query = "insert into users (user_name, password, balance, dob, phoneno, gender, address) values('{}','{}',{},'{}','{}','{}','{}');".format(global_username[0],password,500,dob,phoneno,gender,address)
        mycursor.execute(query)
        mycursor.execute("commit;")

def update_ps(new_ps):
        un = global_username[0]
        query = "update users set password = '{}' where user_name = '{}';".format(new_ps,un)
        mycursor.execute(query)
        mycursor.execute("commit;")

def update_ba(new_ba):
        un = global_username[0]
        query = "update users set balance = {} where user_name = '{}';".format(new_ba,un)
        mycursor.execute(query)
        mycursor.execute("commit;")

def delete_user():
        query = "delete from users where user_name = '{}';".format(global_username[0])
        mycursor.execute(query)
        mycursor.execute("commit;")


def account_info_window():
        def destroy_all():
        
                window.place_forget()
                confirm_btn.destroy()
                delete_btn.destroy()
                menu_im[0].destroy()
                menu_im[1].destroy()
                menu_im[2].destroy()
                menu_im[3].destroy()
                menu_im[4].destroy()
                menu_btn[0].destroy()
                menu_btn[1].destroy()
                menu_btn[2].destroy()
                menu_btn[3].destroy()
                menu_btn[4].destroy()
                menu_btn[5].destroy()
                creating_verifying_form()
                
        def back(event=""):

                window.place_forget()
                confirm_btn.destroy()
                delete_btn.destroy()
                back_btn.destroy()
                
        def delete_my_acc(event=""):
                c_v = confirm_value.get()
                if (c_v==1):
                        delete_user()
                        messagebox.showinfo("SUCCESSFUL","YOUR ACCOUNT IS DELETED")
                        destroy_all()
                else :
                        messagebox.showinfo("WARNING","PLEASE CHECK CONFIRM BUTTON")
        window = Frame(width=700,height=500,bg="yellow")
        window.place(x=35,y=130)
        icon = Label(window,bg="white",width=50,height=50,image=account_info_icon)
        icon.place(x=15,y=10)
        title = Label(window,text=" ACCOUNT INFO ",bg="red",fg="#000066",font="calibri 20")
        title.place(x=270,y=20)
        acc_name = Label(window,text=" ACCOUNT NAME :  "+global_username[0].upper(),bg="pink",fg="#000066",font="calibri 20")
        acc_name.place(x=100,y=60)
        dob_name = Label(window,text=" DATE OF BIRTH :  "+fetch_dob(),bg="pink",fg="#000066",font="calibri 20")
        dob_name.place(x=100,y=120)
        phoneno_name = Label(window,text=" PHONENUMBER :  "+fetch_phoneno(),bg="pink",fg="#000066",font="calibri 20")
        phoneno_name.place(x=100,y=180)
        gen_name = Label(window,text=" GENDER :  "+fetch_gender(),bg="pink",fg="#000066",font="calibri 20")
        gen_name.place(x=100,y=240)
        address_name = Label(window,text=" ADDRESS :  "+fetch_address(),bg="pink",fg="#000066",font="calibri 20")
        address_name.place(x=100,y=300)
        confirm_value = IntVar()
        confirm_btn = Checkbutton(text=" CONFIRM ",font="calibri",variable=confirm_value,fg="white",bg="#000066")
        confirm_btn.place(x=300,y=480)
        delete_btn = Button(command=delete_my_acc,text=" DELETE MY ACCOUNT ",font="calibri",fg="white",bg="#000066",border=0,padx=10,pady=5)
        delete_btn.place(x=300,y=540)
        back_btn = Button(command=back,text=" BACK ",font="calibri",fg="white",bg="#000066",border=0,padx=10,pady=5)
        back_btn.place(x=280,y=580)

        welcome_screen.bind("<Return>",delete_my_acc) 
        welcome_screen.bind("<BackSpace>",back)

def report_transaction_window():
        def back(event=""):
                window.place_forget()
                back_btn.destroy()

        window = Frame(width=700,height=500,bg="yellow")
        window.place(x=35,y=130)
        title = Label(window,text="TRANSACTION INFO",bg="red",fg="#000066",font="calibri 20")
        title.place(x=270,y=20)
        trans_string = fetch_trans()
        transactions = trans_string.split("|")

        trans_str = "Deposited Rs500 Initial Amount\n"
        for transaction in transactions:
                if transaction.strip() == "":
                        continue
                trans_info = transaction.strip().split(" ")
                trans_type = trans_info[1]
                trans_amount = int(trans_info[0])
                trans_date = trans_info[2]
                trans_time = trans_info[3]

                if trans_type == "W":
                        trans_str += f"Witdraw Rs{trans_amount} {trans_date} {trans_time}\n"
                elif trans_type == "D":
                        trans_str += f"Deposit Rs{trans_amount} {trans_date} {trans_time}\n"
                else:
                        pass

        log = Label(window,text=trans_str,bg="pink",fg="#000066",font="calibri 20")
        log.place(relx=0.5,rely=0.5,anchor=CENTER)
        back_btn = Button(command=back,text=" BACK ",font="calibri",fg="white",bg="#000066",border=0,padx=10,pady=5)
        back_btn.place(x=280,y=580)  

        #welcome_screen.bind("<BackSpace>",back)
 

def create_new_account_screen():
        def back():
        
                window.place_forget() 
                un_icon.destroy()
                un_text.destroy()
                un_entry.destroy()
                ps_icon.destroy()
                ps_text.destroy()
                ps_entry.destroy()
                cps_icon.destroy()
                cps_text.destroy()
                cps_entry.destroy()
                dob_label.destroy()
                year_box.destroy()
                month_box.destroy()
                date_box.destroy()
                phoneno_text.destroy()
                gender_label.destroy()
                male.destroy()
                female.destroy()
                address_text.destroy()
                phoneno_entry.destroy()
                address_entry.destroy()
                phoneno_icon.destroy()
                address_icon.destroy()
                submit_btn.destroy()

                creating_verifying_form()
        def proceed_to_menu_screen():
                 
                window.place_forget() 
                un_icon.destroy()
                un_text.destroy()
                un_entry.destroy()
                ps_icon.destroy()
                ps_text.destroy()
                ps_entry.destroy()
                cps_icon.destroy()
                cps_text.destroy()
                cps_entry.destroy()
                dob_label.destroy()
                year_box.destroy()
                month_box.destroy()
                date_box.destroy()
                phoneno_text.destroy()
                phoneno_icon.destroy()
                phoneno_entry.destroy()
                gender_label.destroy()
                male.destroy()
                female.destroy()
                address_text.destroy()
                address_icon.destroy()
                address_entry.destroy() 
                submit_btn.destroy()
                
                #menu_screen()
        def create_account(event=""):
                un = un_value.get()
                ps = ps_value.get()
                cps = cps_value.get()
                year = year_box.get()
                month = month_box.get()
                date = date_box.get()
                dob = date + " " + month + " " + "," + " " + year
                phoneno = phoneno_value.get()
                gen = gender.get()
                address = address_value.get()
                usernames = fetch_usernames()

                if (un=="") :
                        messagebox.showinfo("WARNING","PLEASE TYPE YOUR USERNAME")
                elif (len(un) <= 2) or (len(un) >= 25):
                        un_entry.delete(0,END)
                        messagebox.showinfo("WARNING","PLEASE TYPE GENUINE USERNAME")
                elif (ps=="") :
                        messagebox.showinfo("WARNING","PLEASE TYPE YOUR PASSWORD")
                elif (cps=="") :
                        messagebox.showinfo("WARNING","PLEASE TYPE YOUR CONFIRM PASSWORD")
                elif (un in usernames) :
                        un_entry.delete(0,END)
                        messagebox.showinfo("WARNING","THIS USERNAME ALREADY EXISTS")
                elif (ps != cps) :
                        ps_entry.delete(0,END)
                        cps_entry.delete(0,END)
                        messagebox.showinfo("WARNING","YOUR PASSWORD AND CONFIRM PASSWORD DOES NOT MATCH")
                elif (len(ps) <= 4):
                        ps_entry.delete(0,END)
                        cps_entry.delete(0,END)
                        messagebox.showinfo("WARNING","YOUR PASSWORD IS TO SHORT")
                elif (dob == "1 JANUARY , 2019"):
                        messagebox.showinfo("WARNING","PLEASE MENTION YOUR DATE OF BIRTH")
                elif (phoneno <= 10):
                        messagebox.showinfo("WARNING","PLEASE PUT YOUR CORRECT PHONENUMBER")
                elif (gen!=1) and (gen!=0):
                        messagebox.showinfo("WARNING","PLEASE DETERMINE YOUR GENDER")
                elif (address ==""):
                        messagebox.showinfo("WARNING","PLEASE PUT YOUR ADDRESS") 
                else :
                        global_username[0] = un
                        save_un_ps_ba_dob_phoneno_gen_address(un,ps,dob,phoneno,gen,address)
                        messagebox.showinfo("SUCCESSFUL","YOU HAVE SUCCESSFULY CREATED A NEW ACCOUNT : YOUR USERNAME IS-> "+un)
                        proceed_to_menu_screen()
        window = Frame(width=700,height=500,bg="cyan")
        window.place(x=210,y=130)
        icon = Label(window,bg="white",width=50,height=50,image=account_info_icon)
        icon.place(x=15,y=10)
        title = Label(window,text=" CREATING NEW ACCOUNT ",bg="orange",fg="#000066",font="calibri 20")
        title.place(x=200,y=20)
        un_icon = Label(bg="white",width=50,height=50,image=username_icon)
        un_icon.place(x=430,y=204)
        un_text = Label(bg="pink",text=" USERNAME : ",font="calibri 14",fg="#000066")
        un_text.place(x=490,y=200)
        un_value = StringVar()
        un_entry = Entry(bg="white",fg="#000066",font="calibri",textvariable=un_value)
        un_entry.place(x=499,y=230)
        ps_icon = Label(bg="white",width=50,height=50,image=password_icon)
        ps_icon.place(x=430,y=274)
        ps_text = Label(bg="pink",text=" PASSWORD : ",font="calibri 14",fg="#000066")
        ps_text.place(x=490,y=270)
        ps_value = StringVar()
        ps_entry = Entry(bg="white",fg="#000066",font="calibri",textvariable=ps_value,show="X")
        ps_entry.place(x=499,y=300)
        cps_icon = Label(bg="white",width=50,height=50,image=confirm_icon)
        cps_icon.place(x=430,y=344)
        cps_text = Label(bg="pink",text="CONFIRM PASSWORD :",font="calibri 14",fg="#000066")
        cps_text.place(x=490,y=340)
        cps_value = StringVar()
        cps_entry = Entry(bg="white",fg="#000066",font="calibri",textvariable=cps_value,show="X")
        cps_entry.place(x=499,y=370)

        dob_label = Label(window,text="D.O.B :",bg="pink",fg="#000066")
        dob_label.place(x=80,y=400)
        year_box = ttk.Combobox(window,width=5)
        year_box["values"] = (2008,2007,2006,2005,2004,2003,2002,2001,2000,1999,1998,1997,1996,1995,1994,1993,1992,1991,1990,1989,1988,1987,1986,1985,1984,1983,1982,1981,1980)
        year_box.current(0)
        year_box.place(x=140,y=400)
        month_box = ttk.Combobox(window,width=10)
        month_box["values"] = ("JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE","JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER")
        month_box.current(0)
        month_box.place(x=200,y=400)
        date_box = ttk.Combobox(window,width=10)
        date_box["values"] = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31)
        date_box.current(0)
        date_box.place(x=300,y=400)

        phoneno_icon = Label(bg="white",width=50,height=50,image=confirm_icon)
        phoneno_icon.place(x=430,y=414)
        phoneno_text = Label(bg="pink",text="PHONENUMBER :",font="calibri 14",fg="#000066")
        phoneno_text.place(x=490,y=410)
        phoneno_value = IntVar()
        phoneno_entry = Entry(bg="white",fg="#000066",font="calibri",textvariable=phoneno_value)
        phoneno_entry.place(x=499,y=440)
        
        gender_label = Label(window,text="GENDER :",bg="pink",fg="#000066")
        gender_label.place(x=400,y=400)
        gender = IntVar()
        gender.set(2)
        male = Radiobutton(window,text="MALE",value=1,variable=gender,bg="white")
        female = Radiobutton(window,text="FEMALE",value=0,variable=gender,bg="white")
        male.place(x=480,y=400)
        female.place(x=560,y=400)

        address_icon = Label(bg="white",width=50,height=50,image=confirm_icon)
        address_icon.place(x=430,y=474)
        address_text = Label(bg="pink",text="ADDRESS :",font="calibri 14",fg="#000066")
        address_text.place(x=490,y=470)
        address_value = StringVar()
        address_entry = Entry(bg="white",fg="#000066",font="calibri",textvariable=address_value)
        address_entry.place(x=499,y=500)
        
        submit_btn = Button(command=create_account,text=" PROCEED ",font="calibri",fg="white",bg="#000066",border=0,padx=10,pady=5)
        submit_btn.place(x=530,y=580)

        back_btn = Button(command=back,text=" BACK ",font="calibri",fg="white",bg="#000066",border=0,padx=10,pady=5)
        back_btn.place(x=430,y=580)

        welcome_screen.bind("<Return>",create_account) 

def creating_verifying_form():
        def proceed_to_menu_screen():

                window.place_forget()
                un_icon.destroy()
                un_text.destroy()
                un_entry.destroy()
                ps_icon.destroy()
                ps_text.destroy()
                ps_entry.destroy()
                submit_btn1.destroy()
                submit_btn2.destroy()
                
               # menu_screen()
        def proceed_to_create_new_account_screen():
                 
                window.place_forget()
                un_icon.destroy()
                un_text.destroy()
                un_entry.destroy()
                ps_icon.destroy()
                ps_text.destroy()
                ps_entry.destroy()
                submit_btn1.destroy()
                submit_btn2.destroy()
                
                create_new_account_screen()
        def verify_un_and_ps(event=""):
                username = un_value.get()
                password = ps_value.get()
                #print(f"Password : {password} | Username : {username}")
                registered_usernames = fetch_usernames()
                if (username in registered_usernames):
                        global_username[0] = username 
                        registered_password = fetch_password()
                        if (registered_password==password):
                                #proceed_to_menu_screen()
                                messagebox.showinfo(" WARNING "," Login Succesfully ")
                        
                        elif (password==""):
                                messagebox.showinfo(" WARNING "," PLEASE ENTER YOUR PASSWORD ")
                        else:
                                ps_entry.delete(0,END)
                                messagebox.showinfo(" WARNING "," YOUR PASSWORD IS WRONG ")
                else :
                        un_entry.delete(0,END)
                        ps_entry.delete(0,END)
                        messagebox.showinfo(" WARNING ", " PLEASE ENTER YOUR USERNAME AND PASSWORD CORRECTLY ")
        
        window = Frame(width=700,height=500,bg="orange")
        window.place(x=210,y=130)
        icon1 = Label(window,bg="white",width=50,height=50,image=account_info_icon)
        icon1.place(x=15,y=10)
        icon2 = Label(window,bg="white",width=50,height=50,image=account_info_icon)
        icon2.place(x=630,y=10)
        title = Label(window,text=" VERIFY YOUR ACCOUNT ",bg="yellow",fg="#000066",font="calibri 20")
        title.place(x=215,y=20)
        
        un_icon = Label(bg="white",width=50,height=50,image=username_icon)
        un_icon.place(x=430,y=274)
        un_text = Label(bg="cyan",text=" USERNAME : ",font="calibri 14",fg="#000066")
        un_text.place(x=490,y=270)
        un_value = StringVar()
        un_entry = Entry(bg="white",fg="#000066",font="calibri",textvariable=un_value)
        un_entry.place(x=499,y=300)
        ps_icon = Label(bg="white",width=50,height=50,image=password_icon)
        ps_icon.place(x=430,y=374)
        ps_text = Label(bg="cyan",text=" PASSWORD : ",font="calibri 14",fg="#000066")
        ps_text.place(x=490,y=370)
        ps_value = StringVar()
        ps_entry = Entry(bg="white",fg="#000066",font="calibri",textvariable=ps_value,show="X")
        ps_entry.place(x=499,y=400)
        submit_btn1 = Button(command=verify_un_and_ps,text=" PROCEED ",font="calibri",fg="white",bg="#000066",border=0,padx=10,pady=5)
        submit_btn1.place(x=520,y=470)
        submit_btn2 = Button(command=proceed_to_create_new_account_screen,text=" CREATE A NEW ACCOUNT ",font="calibri",fg="white",bg="#000066",border=0,padx=10,pady=5)
        submit_btn2.place(x=465,y=530)

        welcome_screen.bind("<Return>",verify_un_and_ps) 




bg_image = Label(image = window_bg).pack()


header = Label(text = "WELCOME TO ATM",font = "calibri 20",bg="#fff",fg="#000066",width=80,pady=15)  
header.place(x=0,y=0) 

icon1 = Label(image = bank_icon,bg="#fff",height=50,width=50) 
icon1.place(x=350,y=6)                                          
icon2 = Label(image = bank_icon,bg="#fff",height=50,width=50) 
icon2.place(x=720,y=6)


 
creating_verifying_form()


welcome_screen.mainloop()
