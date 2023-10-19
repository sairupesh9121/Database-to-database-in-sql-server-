import pyodbc
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import datetime
import os

log_text = ""
source_server_entry = None
source_database_entry = None
source_uid_entry = None
source_pwd_entry = None
source_port_entry = None
target_server_entry = None
target_database_entry = None
target_uid_entry = None
target_pwd_entry = None
target_port_entry = None
progress = None
progress_var = None

def log(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text_widget.config(state=tk.NORMAL)
    log_text_widget.insert(tk.END, f"{current_time} - {message}\n")
    log_text_widget.config(state=tk.DISABLED)
    log_text_widget.see("end")

def log_error(error_message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text_widget.config(state=tk.NORMAL)
    log_text_widget.insert(tk.END, f"{current_time} - ERROR: {error_message}\n", "error")
    log_text_widget.config(state=tk.DISABLED)
    log_text_widget.see("end")

def test_connection(server, database, uid, pwd, port):
    try:
        conn = pyodbc.connect(
            f'Driver={{SQL Server}};'
            f'Server={server},{port};'
            f'Database={database};'
            f'UID={uid};'
            f'PWD={pwd};'
        )
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def get_db_connections(source=True):
    if source:
        server = source_server_entry.get()
        database = source_database_entry.get()
        uid = source_uid_entry.get()
        pwd = source_pwd_entry.get()
        port = source_port_entry.get()
    else:
        server = target_server_entry.get()
        database = target_database_entry.get()
        uid = target_uid_entry.get()
        pwd = target_pwd_entry.get()
        port = target_port_entry.get()
    return server, database, uid, pwd, port

def show_status_message(message, is_error=False):
    msg_title = "Error" if is_error else "Success"
    messagebox.showinfo(msg_title, message)

def validate_inputs():
    source_server = source_server_entry.get()
    source_database = source_database_entry.get()
    source_uid = source_uid_entry.get()
    source_pwd = source_pwd_entry.get()
    source_port = source_port_entry.get()

    if not source_server or not source_database or not source_uid or not source_pwd or not source_port:
        show_status_message("Please fill in all fields before proceeding.", is_error=True)
        return False

    valid, error = test_connection(source_server, source_database, source_uid, source_pwd, source_port)
    if not valid:
        show_status_message(f"Source DB Connection Error: {error}", is_error=True)
        return False

    return True

def save_connections():
    source_server, source_database, source_uid, source_pwd, source_port = get_db_connections(source=True)
    target_server, target_database, target_uid, target_pwd, target_port = get_db_connections(source=False)

    source_conn_test, source_conn_error = test_connection(source_server, source_database, source_uid, source_pwd, source_port)
    target_conn_test, target_conn_error = test_connection(target_server, target_database, target_uid, target_pwd, target_port)

    if source_conn_test and target_conn_test:
        config = []
        config.append(f"Source_Server={source_server}")
        config.append(f"Source_Database={source_database}")
        config.append(f"Source_UID={source_uid}")
        config.append(f"Source_PWD={source_pwd}")
        config.append(f"Source_Port={source_port}")
        config.append(f"Target_Server={target_server}")
        config.append(f"Target_Database={target_database}")
        config.append(f"Target_UID={target_uid}")
        config.append(f"Target_PWD={target_pwd}")
        config.append(f"Target_Port={target_port}")

        with open("db_config.txt", "w") as config_file:
            config_file.write("\n".join(config))

        show_status_message("Database configuration saved successfully.")
    else:
        show_status_message(f"Source DB Connection Error: {source_conn_error}\nTarget DB Connection Error: {target_conn_error}", is_error=True)

def load_connections():
    if os.path.exists("db_config.txt"):
        with open("db_config.txt", "r") as config_file:
            lines = config_file.read().splitlines()

        config_dict = {}
        for line in lines:
            key, value = line.strip().split("=")
            config_dict[key] = value

        source_server_entry.delete(0, tk.END)
        source_server_entry.insert(0, config_dict.get("Source_Server", ""))
        source_database_entry.delete(0, tk.END)
        source_database_entry.insert(0, config_dict.get("Source_Database", ""))
        source_uid_entry.delete(0, tk.END)
        source_uid_entry.insert(0, config_dict.get("Source_UID", ""))
        source_pwd_entry.delete(0, tk.END)
        source_pwd_entry.insert(0, config_dict.get("Source_PWD", ""))
        source_port_entry.delete(0, tk.END)
        source_port_entry.insert(0, config_dict.get("Source_Port", ""))
        target_server_entry.delete(0, tk.END)
        target_server_entry.insert(0, config_dict.get("Target_Server", ""))
        target_database_entry.delete(0, tk.END)
        target_database_entry.insert(0, config_dict.get("Target_Database", ""))
        target_uid_entry.delete(0, tk.END)
        target_uid_entry.insert(0, config_dict.get("Target_UID", ""))
        target_pwd_entry.delete(0, tk.END)
        target_pwd_entry.insert(0, config_dict.get("Target_PWD", ""))
        target_port_entry.delete(0, tk.END)
        target_port_entry.insert(0, config_dict.get("Target_Port", ""))
    else:
        show_status_message("No configuration found. Please enter the connection details manually.")

root = tk.Tk()
root.title("Database Configuration")

# Set the application icon (replace 'sync.ico' with your icon file path)
root.iconbitmap("sync.ico")

# Create a frame for the source connection settings
source_frame = ttk.LabelFrame(root, text="Source Connection")
source_frame.grid(row=0, column=0, padx=10, pady=10)

source_server_label = ttk.Label(source_frame, text="Server:")
source_server_label.grid(row=0, column=0)
source_server_entry = ttk.Entry(source_frame)
source_server_entry.grid(row=0, column=1)

source_database_label = ttk.Label(source_frame, text="Database:")
source_database_label.grid(row=1, column=0)
source_database_entry = ttk.Entry(source_frame)
source_database_entry.grid(row=1, column=1)

source_uid_label = ttk.Label(source_frame, text="Username:")
source_uid_label.grid(row=2, column=0)
source_uid_entry = ttk.Entry(source_frame)
source_uid_entry.grid(row=2, column=1)

source_pwd_label = ttk.Label(source_frame, text="Password:")
source_pwd_label.grid(row=3, column=0)
source_pwd_entry = ttk.Entry(source_frame, show="*")
source_pwd_entry.grid(row=3, column=1)

source_port_label = ttk.Label(source_frame, text="Port:")
source_port_label.grid(row=4, column=0)
source_port_entry = ttk.Entry(source_frame)
source_port_entry.grid(row=4, column=1)

# Create a frame for the target connection settings
target_frame = ttk.LabelFrame(root, text="Target Connection")
target_frame.grid(row=0, column=1, padx=10, pady=10)

target_server_label = ttk.Label(target_frame, text="Server:")
target_server_label.grid(row=0, column=0)
target_server_entry = ttk.Entry(target_frame)
target_server_entry.grid(row=0, column=1)

target_database_label = ttk.Label(target_frame, text="Database:")
target_database_label.grid(row=1, column=0)
target_database_entry = ttk.Entry(target_frame)
target_database_entry.grid(row=1, column=1)

target_uid_label = ttk.Label(target_frame, text="Username:")
target_uid_label.grid(row=2, column=0)
target_uid_entry = ttk.Entry(target_frame)
target_uid_entry.grid(row=2, column=1)

target_pwd_label = ttk.Label(target_frame, text="Password:")
target_pwd_label.grid(row=3, column=0)
target_pwd_entry = ttk.Entry(target_frame, show="*")
target_pwd_entry.grid(row=3, column=1)

target_port_label = ttk.Label(target_frame, text="Port:")
target_port_label.grid(row=4, column=0)
target_port_entry = ttk.Entry(target_frame)
target_port_entry.grid(row=4, column=1)

# Create buttons
save_button = ttk.Button(root, text="Save Configuration", command=save_connections)
save_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

load_button = ttk.Button(root, text="Load Configuration", command=load_connections)
load_button.grid(row=1, column=1, padx=10, pady=5, sticky="e")

# Create a text widget to display logs
log_frame = ttk.LabelFrame(root, text="Logs")
log_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

log_text_widget = tk.Text(log_frame, wrap=tk.WORD, height=10, width=50)
log_text_widget.grid(row=0, column=0, padx=5, pady=5)

scrollbar = ttk.Scrollbar(log_frame, command=log_text_widget.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
log_text_widget.config(yscrollcommand=scrollbar.set)
log_text_widget.tag_configure("error", foreground="red")

def start_processing():
    source_server = source_server_entry.get()
    source_database = source_database_entry.get()
    source_uid = source_uid_entry.get()
    source_pwd = source_pwd_entry.get()
    source_port = source_port_entry.get()
    target_server = target_server_entry.get()
    target_database = target_database_entry.get()
    target_uid = target_uid_entry.get()
    target_pwd = target_pwd_entry.get()
    target_port = target_port_entry.get()

    # Validation: Check if any of the required fields are empty
    if not source_server or not source_database or not source_uid or not source_pwd or not source_port \
            or not target_server or not target_database or not target_uid or not target_pwd or not target_port:
        show_status_message("Please fill in all fields before starting data synchronization.", is_error=True)
        return

    global progress, progress_var
    # Disable the Start Processing button while synchronization is in progress
    start_button.config(state=tk.DISABLED)

    source_conn_test, source_conn_error = test_connection(source_server, source_database, source_uid, source_pwd, source_port)
    target_conn_test, target_conn_error = test_connection(target_server, target_database, target_uid, target_pwd, target_port)

    if source_conn_test and target_conn_test:
        log("Source and target connections are successful. Starting data synchronization...")

        def synchronization_task():
            conn_a = pyodbc.connect(
                f'Driver={{SQL Server}};'
                f'Server={source_server},{source_port};'
                f'Database={source_database};'
                f'UID={source_uid};'
                f'PWD={source_pwd};'
            )
            conn_b = pyodbc.connect(
                f'Driver={{SQL Server}};'
                f'Server={target_server},{target_port};'
                f'Database={target_database};'
                f'UID={target_uid};'
                f'PWD={target_pwd};'
            )

            while True:
                cursor_a = conn_a.cursor()
                cursor_b = conn_b.cursor()

                try:
                    cursor_a.execute("SELECT emp_code, punch_time FROM iclock_transaction WHERE sync_status = 0")
                    data_from_a = cursor_a.fetchall()

                    rows_inserted_into_b = 0

                    for row in data_from_a:
                        emp_code, punch_time = row
                        sql_insert_b = "INSERT INTO employ_logs (emp_code, punch_time) VALUES (?, ?)"
                        cursor_b.execute(sql_insert_b, (emp_code, punch_time))
                        rows_inserted_into_b += 1

                    conn_b.commit()

                    if rows_inserted_into_b > 0:
                        sql_update_a = "UPDATE iclock_transaction SET sync_status = 1 WHERE emp_code = ? AND punch_time = ?"
                        for row in data_from_a:
                            emp_code, punch_time = row
                            cursor_a.execute(sql_update_a, (emp_code, punch_time))
                        conn_a.commit()

                    log(f"Rows inserted into Database: {rows_inserted_into_b}")

                except Exception as e:
                    log_error(f"Error during synchronization: {str(e)}")

                time.sleep(120)

            conn_a.close()
            conn_b.close()

        # Show an animation while data is syncing (you can use a label or an image)
        sync_animation_label = ttk.Label(root, text="Synchronizing...", font=("Helvetica", 8))
        sync_animation_label.grid(row=9, column=0, columnspan=2, pady=10)

        def update_sync_animation():
            while True:
                sync_animation_label.config(text="Synchronizing.")
                time.sleep(1)
                sync_animation_label.config(text="Synchronizing..")
                time.sleep(1)
                sync_animation_label.config(text="Synchronizing...")
                time.sleep(1)

        sync_thread = threading.Thread(target=update_sync_animation)
        sync_thread.daemon = True
        sync_thread.start()

        sync_thread = threading.Thread(target=synchronization_task)
        sync_thread.daemon = True
        sync_thread.start()

        show_status_message("Data synchronization started successfully.")
    else:
        show_status_message(f"Source DB Connection Error: {source_conn_error}\nTarget DB Connection Error: {target_conn_error}", is_error=True)

    start_button.config(state=tk.NORMAL)

start_button = ttk.Button(root, text="Start Processing", command=start_processing)
start_button.grid(row=8, column=0, columnspan=2)

root.mainloop()
