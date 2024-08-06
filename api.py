from fastapi import HTTPException
from server import server
from schemas import IPInformationSchema, ProviderInformationSchema
import ipaddress
import sqlite3

def get_subnets():
    connection = sqlite3.connect('malicious_ips_db.db')
    cursor = connection.cursor()
    
    ret_subnets = """SELECT * FROM ips
                WHERE ip_or_subnet = 1"""
    cursor.execute(ret_subnets)
    subnets = cursor.fetchall()
    
    connection.close()
    return subnets

def check_ips(ip: str):
    connection = sqlite3.connect('malicious_ips_db.db')
    cursor = connection.cursor()
    
    subnets = get_subnets()
    for subnet in subnets: 
        subnet_cleaned = subnet[1].strip()
        try:
            subnet_network = ipaddress.ip_network(subnet_cleaned, strict=False)
            if ipaddress.ip_address(ip) in subnet_network:
                return subnet
        except ValueError as e:
            print(f"Error processing subnet {subnet_cleaned}: {e}")
    
    find_ip = """SELECT * FROM ips
                WHERE ip_address = ?"""

    cursor.execute(find_ip, (ip,))
    result = cursor.fetchone()
    connection.close()
    return result
    
def check_lists(id: str):
    connection = sqlite3.connect('malicious_ips_db.db')
    cursor = connection.cursor()
    
    find_provider = """SELECT * FROM lists
                    WHERE list_id = ?"""
    cursor.execute(find_provider, (id,))
    
    return cursor.fetchone()

@server.get('/blacklist/{ip}', response_model=IPInformationSchema)
def get_ip(ip: str):
    # Check if ip matches any ip or subnet in the database
    ip_obj = check_ips(str(ip))
    
    if ip_obj: 
        return {
            'id': ip_obj[0],
            'ip_address': ip_obj[1],
            'ip_or_subnet': ip_obj[2],
            'list_id': ip_obj[3]
        }
    
    raise HTTPException(
        status_code = 404, detail=f'IP {ip} not found'
    )

@server.get('/providers/{list_id}', response_model=ProviderInformationSchema)
def get_provider(list_id: str):
    provider_obj = check_lists(str(list_id))
    
    if provider_obj:
        return {
            'id': provider_obj[0],
            'name': provider_obj[1],
            'maintainer': provider_obj[2],
            'maintainer_url': provider_obj[3],
            'category': provider_obj[4]
        }
        
    raise HTTPException(
        status_code = 404, detail=f'Provider {list_id} not found'
    )