from database.db import fetch_all as query, execute_query as run
from models import Vehicle,Service
class Auth:
    @staticmethod
    def login(u,p): return query('SELECT id,username,full_name,role FROM users WHERE username=%s AND password=%s',(u,p))
class Vehicles:
    @staticmethod
    def all(): return query('SELECT * FROM vehicles ORDER BY id DESC')
    @staticmethod
    def add(v): return run('INSERT INTO vehicles(plate_number,owner_name,brand,model,year,vehicle_type,contact_number) VALUES(%s,%s,%s,%s,%s,%s,%s)',(v.plate,v.owner,v.brand,v.model,v.year,v.kind,v.contact))
    @staticmethod
    def update(i,v): run('UPDATE vehicles SET plate_number=%s,owner_name=%s,brand=%s,model=%s,year=%s,vehicle_type=%s,contact_number=%s WHERE id=%s',(v.plate,v.owner,v.brand,v.model,v.year,v.kind,v.contact,i))
    @staticmethod
    def delete(i): run('DELETE FROM vehicles WHERE id=%s',(i,))
class Services:
    @staticmethod
    def all(): return query('SELECT m.*,v.plate_number,v.owner_name FROM maintenance_records m JOIN vehicles v ON v.id=m.vehicle_id ORDER BY m.id DESC')
    @staticmethod
    def add(s): return run('INSERT INTO maintenance_records(vehicle_id,service_date,service_type,description,mileage,cost,status,mechanic_name) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',(s.vehicle_id,s.date,s.service_type,s.description,s.mileage,s.cost,s.status,s.mechanic_name))
    @staticmethod
    def update(i,s): run('UPDATE maintenance_records SET vehicle_id=%s,service_date=%s,service_type=%s,description=%s,mileage=%s,cost=%s,status=%s,mechanic_name=%s WHERE id=%s',(s.vehicle_id,s.date,s.service_type,s.description,s.mileage,s.cost,s.status,s.mechanic_name,i))
    @staticmethod
    def delete(i): run('DELETE FROM maintenance_records WHERE id=%s',(i,))
class Dashboard:
    @staticmethod
    def stats(): return (query('SELECT COUNT(*) n FROM vehicles')[0]['n'],query('SELECT COUNT(*) n FROM maintenance_records')[0]['n'],query('SELECT COALESCE(SUM(cost),0) n FROM maintenance_records')[0]['n'])
