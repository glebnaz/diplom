import pymongo, gridfs
import bson
import json



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
    print(last_year.keys())
    #создание новго года
    #алгоритм перевода        

for student in students.find():
    transition_student_to_next_year(student['_id'])