from cryptography.fernet import Fernet
from tkinter import messagebox
import sqlite3
import tkinter as tk

#Create window
window = tk.Tk()
window.geometry("440x500")
window.title("Password Management App")

LARGE_FONT= ("Verdana", 11)

# #Create a database or connect to one
# conn = sqlite3.connect('app_password.db')
# #Create cursor
# c = conn.cursor()
#
# #Create table
# c.execute("""
#     CREATE TABLE app_password (
#     id integer primary key autoincrement,
#     application text,
#     username text,
#     password text
#     )""")
#
# #Commit changes
# conn.commit()
# #Close connection
# conn.close()

#Password encryption functions
def generate_key():
    key = Fernet.generate_key()
    with open("secret.txt", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.txt", "rb").read()

def encrypt_message(message):
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message

def decrypt_message(encrypted_message):
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    return decrypted_message.decode()

#Credentials storage function
def store():

    encrypted_password = encrypt_message(passwordEntry.get())

    if AppnameEntry.get() == "" or usernameEntry.get()=="" or passwordEntry.get()=="":
        tk.messagebox.showerror("Incomplete data", "Complete all fields and try again!")
    else:
        #Create a database or connect to one
        conn = sqlite3.connect('app_password.db')
        #Create cursor
        c = conn.cursor()

        c.execute("Insert into app_password (application, username, password) VALUES (:appName, :userName, :passWord)",
                {
                    'appName': AppnameEntry.get(),
                    'userName': usernameEntry.get(),
                    'passWord': encrypted_password
                }
            )
        #Commit changes
        conn.commit()
        #Close connection
        conn.close()

        tk.messagebox.showinfo("Saved", "Information has been saved")
        #Because these are global
        AppnameEntry.delete(0, tk.END)
        usernameEntry.delete(0, tk.END)
        passwordEntry.delete(0, tk.END)




#Retrieve section
retrieve_heading = tk.Label(text="Retrieve Credentials", font=LARGE_FONT)
retrieve_heading.grid(column=0, row=1, pady=(20,20))

app_name = tk.Label(text="App name")
app_name.grid(column=0, row=2)


nameEntry = tk.Entry(window, width=30)
nameEntry.grid(column=1, row=2, padx=20)
textArea = tk.Text(master=window, height=4, width=26,font=("Helvetica", 9))
textArea.grid(column=1, row=3)

def retrieve():
    #Create a database or connect to one
    conn = sqlite3.connect('app_password.db')
    #Create cursor
    c = conn.cursor()

    row = c.execute("SELECT * FROM app_password WHERE application=:appName",
            {
                'appName': nameEntry.get(),

            }
        )
    fetched_info = row.fetchone()

    if fetched_info:
        password_decrypted = decrypt_message(fetched_info[2])
        answer = """App name: {appn} \nUsername: {usern}\nPassword: {passw}
        """.format(appn=fetched_info[0], usern=fetched_info[1], passw=password_decrypted)
        textArea.delete("1.0", tk.END)
        textArea.insert(tk.END, answer)
    else:
        answer = "No information found"
        textArea.delete("1.0", tk.END)
        textArea.insert(tk.END, answer)
    #Commit changes
    conn.commit()
    #Close connection
    conn.close()

    return None

#Retrieve button setup
retrieve_button = tk.Button(window, text="Retrieve", command=retrieve)
retrieve_button.grid(column=0, row=3)

#Password section
pass_heading = tk.Label(text="Store Credentials", font=LARGE_FONT)
pass_heading.grid(column=0, row=5)

app_name2 = tk.Label(text="App name")
app_name2.grid(column=0, row=6)
username = tk.Label(text="Username")
username.grid(column=0, row=7)
pass_name = tk.Label(text="Password")
pass_name.grid(column=0, row=8)

AppnameEntry = tk.Entry(window, width=30)
AppnameEntry.grid(column=1, row=6)
usernameEntry = tk.Entry(window, width=30)
usernameEntry.grid(column=1, row=7)
passwordEntry = tk.Entry(window, width=30)
passwordEntry.grid(column=1, row=8)

save_button = tk.Button(window, text="Save Credentials", command=store)
save_button.grid(column=1, row=10, pady=(6,0))

#Remove password
pass_heading = tk.Label(text="Remove Credentials", font=LARGE_FONT)
pass_heading.grid(column=0, row=11, pady=(20,20))

app_name2 = tk.Label(text="App name")
app_name2.grid(column=0, row=12)

nameEntry2 = tk.Entry(window, width=30)
nameEntry2.grid(column=1, row=12)

my_listbox = tk.Listbox(window, width=30, height=4)
my_listbox.grid(column=1, row=14, pady=(20,20))
#Add item to listbox


def search():
    #Create a database or connect to one
    conn = sqlite3.connect('app_password.db')
    #Create cursor
    c = conn.cursor()

    row = c.execute("SELECT * FROM app_password WHERE application=:appName",
            {
                'appName': nameEntry2.get(),

            }
        )
    fetched_info = row.fetchall()

    if fetched_info:
        my_listbox.delete('0', tk.END)
        for element in fetched_info:
            my_listbox.insert(tk.END, "{pk} {appname} {username}".format(pk=element[0], appname=element[1], username=element[2]))
    else:
        my_listbox.delete("0", tk.END)
        my_listbox.insert(tk.END, "No information found")

    #Commit changes
    conn.commit()
    #Close connection
    conn.close()

    return None

search_button = tk.Button(window, text="Search", command=search)
search_button.grid(column=1, row=13, pady=(6,0))

def delete():
    #Create a database or connect to one
    conn = sqlite3.connect('app_password.db')
    #Create cursor
    c = conn.cursor()

    selected_item = my_listbox.get(tk.ANCHOR)

    row = c.execute("DELETE FROM app_password WHERE id=:id_no",
            {
                'id_no': int(selected_item[0]),

            }
        )

    my_listbox.delete(tk.ANCHOR)
    #Commit changes
    conn.commit()
    #Close connection
    conn.close()

    return None

delete_button = tk.Button(window, text="Delete item",
                command=delete)
delete_button.grid(column=0, row=14)

window.mainloop()



# if __name__ == "__main__":
#     encrypt_message("encrypt this message1")
#     encrypt_message("hidden information here number2")
#     encrypt_message("last secret communication for testing3")
    # decrypt_message()
