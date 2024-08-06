# Set up file for sqlite3 database that API retrieves information from 
# script is bugged and adds newlines into DB entries, please advise
import sqlite3
import os 
import uuid

def add_list(connection, list):
    sql = """INSERT INTO lists(list_id, name, maintainer, maintainer_url, category, last_modified)
            VALUES(?,?,?,?,?,?)"""
    cursor = connection.cursor()
    cursor.execute(sql, list)
    connection.commit()
    return cursor.lastrowid

def ip_in_database(connection, ip):
    sql = """SELECT COUNT(1)
            FROM ips
            WHERE ip_address = ?"""
    cursor = connection.cursor()
    cursor.execute(sql, (ip,))
    return cursor.fetchone()[0]

def ip_in_list(connection, ip, list_id):
    sql = """SELECT COUNT(1)
            FROM ips 
            WHERE ip_address = ?
            and list_id = ?"""
    cursor = connection.cursor()
    cursor.execute(sql, (ip, list_id))
    return cursor.fetchone()[0]

def insert_ip(connection, ip):
    sql = """INSERT INTO ips(ip_id, ip_address, ip_or_subnet, list_id)
            VALUES(?, ?, ?, ?)"""
    cursor = connection.cursor()
    cursor.execute(sql, ip)
    connection.commit()
    return cursor.lastrowid

# I'm not super experienced in databases, I originally had it so it would create a temporary table to process 
# appropriate updates in deletions and insertions, but this was wildly inefficent so it was changed to use a list in memory

# def insert_ip_temp(connection, ip):
#     sql = """INSERT INTO temp_ips(ip_address)
#             VALUES(?)"""
#     cursor = connection.cursor()
#     cursor.execute(sql, (ip,))
#     connection.commit()
#     return cursor.lastrowid

# def ip_in_temp_database(connection, ip):
#     sql = """SELECT COUNT(1)
#             FROM temp_ips
#             WHERE ip_address = ?"""
#     cursor = connection.cursor()
#     cursor.execute(sql, (ip,))
#     return cursor.fetchone()[0]

# only set up for initial set up 
def update_ips_table(connection, directory):
    cursor = connection.cursor()
    
    for file in os.scandir(directory):
        if file.is_file():
            if file.name.endswith(('.netset', '.ipset')):
                if os.access(file.path, os.R_OK):
                    f = open(file.path, 'r')
                    list_name = file.name.split('.')[0]
                    # add the IPs and netsets
                    get_provider_id = """SELECT list_id 
                                FROM lists
                                WHERE name = ?"""
                    cursor.execute(get_provider_id, (list_name,))
                    provider_id = cursor.fetchone()[0]
                    for line in f:
                        # IP or subnet 
                        if not line.startswith('#'):
                            # check if it's already in the database
                            exists = ip_in_database(connection, line.strip())
                            ip_id = str(uuid.uuid4())
                            if exists == 0: 
                                ip_or_subnet = 0
                                if '/' in line:
                                    ip_or_subnet = 1
                                else: 
                                    ip_or_subnet = 0
                                ip_info = (ip_id, line.strip(), ip_or_subnet, provider_id)
                                insert_id = insert_ip(connection, ip_info)
                                print(f'added ip {insert_id}')
                    f.close()

# should pass database and id of list needed to be updated
def update_database(connection, list_id, file):
    cursor = connection.cursor()
    # if it's in old_db and not in new, should be removed 
    # if in new and not in old, should be added
    
    sql = """SELECT * FROM ips 
            WHERE list_id = ?"""
    cursor.execute(sql, (list_id,))
    
    # instead of creating a temporary table, make a list in memory 
    new_db_list = []
    
    for line in file:
        if not line.startswith('#'):
            new_db_list.append(line.strip())
    
    # delete old records that aren't in the new list 
    placeholders = ','.join('?' for _ in new_db_list)
    
    # should be delete but will select to test working as of now
    delete_old_records = f"""SELECT * FROM ips WHERE
                    ip_address NOT IN ({placeholders})
                    AND list_id = ?"""
    parameters = new_db_list + [list_id]
    
    cursor.execute(delete_old_records, parameters)
    rows = cursor.fetchall()
    
    # print("Deleted Records: ")
    # for row in rows: 
    #     print(row)
    
    # add in new records
    for entry in new_db_list:
        # check if entry exists in the ips DB
        exists = ip_in_database(connection, entry)
        if exists == 0:
            ip_id = str(uuid.uuid4())
            ip_or_subnet = 0
            if '/' in line:
                ip_or_subnet = 1
            else: 
                ip_or_subnet = 0
            ip_info = (ip_id, line.strip(), ip_or_subnet, list_id)
            insert_id = insert_ip(connection, ip_info)
            print(f'added ip {insert_id}')
    
# check for last updated timestamp 
# update if different and compare old table 
def update_providers_table(connection, directory):
    cursor = connection.cursor()
    
    for file in os.scandir(directory):
        if file.is_file():
            # only open if it's ascii text, should only read from ipset and netset files 
            if file.name.endswith(('.netset', '.ipset')):
                # print(file.name)
                # firehol is aggregated might be better to just do the separate lists for sake of more details
                if os.access(file.path, os.R_OK):
                    f = open(file.path, 'r')
                    # should parse information about provider of the list 
                    list_name = file.name.split('.')[0]
                    #sqlite syntax for sanitized placeholders
                    check_list = """SELECT COUNT(1)
                            FROM lists
                            WHERE name = ?"""
                    cursor.execute(check_list, (list_name,))
                    
                    exists = cursor.fetchone()[0]
                    # if the provider doesn't have an entry in the providers table, add, else, skip next few steps
                    # extract provider information
                    if not exists: 
                        # generate a UUID 
                        id = str(uuid.uuid4())
                        maintainer = ''
                        maintainer_url = ''
                        category = ''
                        for line in f:
                            # Maintainer + URL 
                            if "Maintainer" in line and not "URL" in line: 
                                maintainer = line.split(": ")[1].strip()
                            if "Maintainer URL" in line:
                                maintainer_url = line.split(": ")[1].strip()
                            # category
                            if "Category" in line:
                                category = line.split(": ")[1].strip()
                            # last modified to see if it's different, might need to use different variable 
                            if "This File Date" in line:
                                file_date = line.split(": ")[1].strip()
                        insert_list = (id, list_name, maintainer, maintainer_url, category, file_date)
                        list_id = add_list(connection, insert_list)
                        print(f'added list {list_id}')
                    else:
                        # if it exists, check the timestamp 
                        get_last_modified = """SELECT last_modified
                                        FROM lists
                                        WHERE name = ?"""
                        cursor.execute(get_last_modified, (list_name,))
                        last_modified = cursor.fetchone()[0]
                        
                        get_list_id = """SELECT list_id
                                        FROM lists
                                        WHERE name = ?"""
                        cursor.execute(get_list_id, (list_name,))
                        id = cursor.fetchone()[0]
                        
                        for line in f: 
                            if "This File Date" in line:
                                if last_modified != line.split(": ")[1].strip(): 
                                    # update database
                                    update_database(connection, id, f)
                    f.close()
                else:
                    print('error reading')

def main():
    connection = sqlite3.connect('malicious_ips_db.db')

    cursor = connection.cursor()

    # create lists table if it doesn't already exist

    create_lists = """CREATE TABLE IF NOT EXISTS lists(
        list_id TEXT PRIMARY KEY,
        name TEXT, 
        maintainer TEXT, 
        maintainer_url TEXT,
        category TEXT,
        last_modified TEXT)"""

    cursor.execute(create_lists)

    # create ip table if it doesn't already exist

    # maybe change it to reference via id instead of name? 
    create_ip = """CREATE TABLE IF NOT EXISTS ips(
        ip_id TEXT PRIMARY KEY,
        ip_address TEXT, 
        ip_or_subnet INTEGER, 
        list_id TEXT, 
        FOREIGN KEY (list_id) REFERENCES lists(list_id))"""

    cursor.execute(create_ip)

    # specify directory here, ideally should probably be an environment variable, but since everything is on one machine, I use a hardcoded path
    directory = '/etc/firehol/ipsets/'
    update_providers_table(connection, directory)
    update_ips_table(connection, directory)

if __name__ == '__main__':
    main()