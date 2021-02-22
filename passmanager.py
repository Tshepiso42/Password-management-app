from cryptography.fernet import Fernet
from tkinter import messagebox
import sqlite3
import tkinter as tk

class App:
    def __init__(self, master):
        self.master = master
        self.LARGE_FONT= ("Verdana", 11)

        ################## Retrieve section #############################
        self.retrieve_heading = tk.Label(master, text="Retrieve Credentials", font=self.LARGE_FONT)
        self.retrieve_heading.grid(column=0, row=1, pady=(20,20))

        self.app_name = tk.Label(text="App name")
        self.app_name.grid(column=0, row=2)


        self.nameEntry = tk.Entry(master, width=30)
        self.nameEntry.grid(column=1, row=2, padx=20)
        self.textArea = tk.Text(master, height=4, width=26,font=("Helvetica", 9))
        self.textArea.grid(column=1, row=3)

        #Retrieve button setup
        self.retrieve_button = tk.Button(master, text="Retrieve", command=self.retrieve)
        self.retrieve_button.grid(column=0, row=3)

        ############## Store Credentials section ###########################

        self.pass_heading = tk.Label(text="Store Credentials", font=self.LARGE_FONT)
        self.pass_heading.grid(column=0, row=5)

        self.app_name2 = tk.Label(text="App name")
        self.app_name2.grid(column=0, row=6)
        self.username = tk.Label(text="Username")
        self.username.grid(column=0, row=7)
        self.pass_name = tk.Label(text="Password")
        self.pass_name.grid(column=0, row=8)

        self.AppnameEntry = tk.Entry(master, width=30)
        self.AppnameEntry.grid(column=1, row=6)
        self.usernameEntry = tk.Entry(master, width=30)
        self.usernameEntry.grid(column=1, row=7)
        self.passwordEntry = tk.Entry(master, width=30)
        self.passwordEntry.grid(column=1, row=8)

        self.save_button = tk.Button(master, text="Save Credentials", command=self.store)
        self.save_button.grid(column=1, row=10, pady=(6,0))


        ###############  Remove Credentials Section #############################
        self.pass_heading2 = tk.Label(text="Remove Credentials", font=self.LARGE_FONT)
        self.pass_heading2.grid(column=0, row=11, pady=(20,20))

        self.app_name2 = tk.Label(text="App name")
        self.app_name2.grid(column=0, row=12)

        self.nameEntry2 = tk.Entry(master, width=30)
        self.nameEntry2.grid(column=1, row=12)

        self.my_listbox = tk.Listbox(master, width=30, height=4)
        self.my_listbox.grid(column=1, row=14, pady=(20,20))

        self.search_button = tk.Button(master, text="Search", command=self.search)
        self.search_button.grid(column=1, row=13, pady=(6,0))

        self.delete_button = tk.Button(master, text="Delete item",command=self.delete)
        self.delete_button.grid(column=0, row=14)

    ############# class functions/methods #################################

    #Retrieve credentials function
    def retrieve(self):
        #Create a database or connect to one
        conn = sqlite3.connect('app_password.db')
        #Create cursor
        c = conn.cursor()
        app_name = self.nameEntry.get()
        row = c.execute("SELECT * FROM app_password WHERE application=:appName",
                {
                    'appName': app_name.lower()

                }
            )
        fetched_info = row.fetchone()

        if fetched_info:
            password_decrypted = self.decrypt_message(fetched_info[3])
            answer = """App name: {appn} \nUsername: {usern}\nPassword: {passw}
            """.format(appn=fetched_info[1], usern=fetched_info[2], passw=password_decrypted)
            self.textArea.delete("1.0", tk.END)
            self.textArea.insert(tk.END, answer)
        else:
            answer = "No information found"
            self.textArea.delete("1.0", tk.END)
            self.textArea.insert(tk.END, answer)
        #Commit changes
        conn.commit()
        #Close connection
        conn.close()

    #Store credentials function
    def store(self):

        encrypted_password = self.encrypt_message(self.passwordEntry.get())

        if self.AppnameEntry.get() == "" or self.usernameEntry.get()=="" or self.passwordEntry.get()=="":
            tk.messagebox.showerror("Incomplete data", "Complete all fields and try again!")
        else:
            #Create a database or connect to one
            conn = sqlite3.connect('app_password.db')
            #Create cursor
            c = conn.cursor()

            c.execute("Insert into app_password (application, username, password) VALUES (:appName, :userName, :passWord)",
                    {
                        'appName': self.AppnameEntry.get().lower(),
                        'userName': self.usernameEntry.get(),
                        'passWord': encrypted_password
                    }
                )
            #Commit changes
            conn.commit()
            #Close connection
            conn.close()

            tk.messagebox.showinfo("Saved", "Information has been saved")
            #clear entries
            self.AppnameEntry.delete(0, tk.END)
            self.usernameEntry.delete(0, tk.END)
            self.passwordEntry.delete(0, tk.END)

    #Search function
    def search(self):
        #Create a database or connect to one
        conn = sqlite3.connect('app_password.db')
        #Create cursor
        c = conn.cursor()

        app_name = self.nameEntry2.get().lower()
        if app_name != "" :
            row = c.execute("SELECT * FROM app_password WHERE application=:appName",
                    {
                        'appName': app_name

                    }
                )
            fetched_info = row.fetchall()

            if fetched_info:
                #clear listbox first
                self.my_listbox.delete('0', tk.END)
                for element in fetched_info:
                    self.my_listbox.insert(tk.END, "{pk} {appname} {username}".format(pk=element[0], appname=element[1], username=element[2]))
            else:
                self.my_listbox.delete("0", tk.END)
                self.my_listbox.insert(tk.END, "No information found")
        else:
            tk.messagebox.showerror("Error", "Please enter application name!")
        #Commit changes
        conn.commit()
        #Close connection
        conn.close()

    #Delete function
    def delete(self):
        #Create a database or connect to one
        conn = sqlite3.connect('app_password.db')
        #Create cursor
        c = conn.cursor()
        selected_item = self.my_listbox.get(tk.ANCHOR)

        if selected_item != "" and selected_item != "No information found":
            choice = tk.messagebox.askquestion("Confirmation", "Are you sure you want to delete this item?", icon='warning')
            #Extract primary key from input
            s = selected_item
            primaryKey = [int(n) for n in s.split() if n.isdigit()]

            if choice == "yes":
                row = c.execute("DELETE FROM app_password WHERE id=:id_no",
                        {
                            'id_no': primaryKey[0]

                        }
                    )
                #clear from display
                self.my_listbox.delete(tk.ANCHOR)

        #Commit changes
        conn.commit()
        #Close connection
        conn.close()

    ############## Password encryption functions ###########################

    def generate_key():
        key = Fernet.generate_key()
        with open("secret.txt", "wb") as key_file:
            key_file.write(key)

    def load_key(self):
        return open("secret.txt", "rb").read()

    def encrypt_message(self, message):
        key = self.load_key()
        encoded_message = message.encode()
        f = Fernet(key)
        encrypted_message = f.encrypt(encoded_message)

        return encrypted_message

    def decrypt_message(self, encrypted_message):
        key = self.load_key()
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message)

        return decrypted_message.decode()


    ################ Database creation ###########################
    def databaseTable():
        #Create a database table
        conn = sqlite3.connect('app_password.db')
        #Create cursor
        c = conn.cursor()

        #Create table
        c.execute("""
            CREATE TABLE app_password (
            id integer primary key autoincrement,
            application text,
            username text,
            password text
            )""")

        #Commit changes
        conn.commit()
        #Close connection
        conn.close()

###############  Run the application  ##############################
def startApp():
    #Create window
    window = tk.Tk()
    window.geometry("440x500")
    window.title("Password Management App")
    app_object = App(window)
    window.mainloop()

if __name__ == "__main__":
    # #Step 1: Generate key in textfile
    #     App.generate_key()
    # #Step 2: Create database file
    #     App.databaseTable()
    #Step 3: Run application
        startApp()
