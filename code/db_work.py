import pymongo, gridfs
import bson
import json



can_transition_group = [111,112,113,121,122,131,141,142,151,161,162,211,212,221,231,241,242,251,261,311,312,321,331,341,342,351,361,117,127,147,148,101,102,201,202,203,204,301,302,401,404]

client = pymongo.MongoClient("mongodb://localhost:27017")

print(client)

db = client['МиКМ2']
print(db)

students = db['Студенты']

def get_work_of_students(id):
    y  = students.find_one({"_id":id},{"год":1,"_id":0})
    return y.get('год')

def transition_student_to_next_year(id):
    years = get_work_of_students(id)
    max_y = 0
    for y in years.keys():
        if int(y)>max_y:
            max_y = int(y)
    last_year = years.get(str(max_y))        
    group = last_year.get('группа')
    if int(group) in can_transition_group:
        new_group=int(group)+100
        new_year = {"группа":str(new_group),"руководитель":""}
        years[str(max_y+1)] = new_year
        students.find_one_and_update({"_id":id},{"$set":{"год":years}})
        print(group)
          

for student in students.find({"ФИО":"Наземнов Глеб Андреевич"}):
    transition_student_to_next_year(student['_id'])