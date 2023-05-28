import json
import csv
import operator

operators = {
    '-': operator.sub,
    '+': operator.add,
    '=': operator.eq,
    '|=': operator.ior,
    '!=': operator.ne,
    '<': operator.lt,
    '>': operator.gt,
    '<=': operator.le,
    '>=': operator.ge,
    '!<': operator.ge,
    '!>': operator.le,
    'AND': operator.and_,
    'OR': operator.or_
}
def main():
    students = read_CSV()
    statement : str = input("Enter a statement: ")
    match = match_sql_statement(statement, students)
def match_sql_statement(sql_statement, students):

    if "SELECT" in sql_statement and "FROM" in sql_statement:
        subDict = select_operation(sql_statement, students)
        write_JSON(subDict)   
    elif "INSERT" in sql_statement and "INTO" in sql_statement and "VALUES" in sql_statement:
        students = insert_operation(sql_statement, students)
        write_JSON(students)
    elif "DELETE" in sql_statement and "FROM" in sql_statement:
        students = delete_operation(sql_statement, students)
        write_JSON(students)
    else:
        raise Exception("Invalid SQL statement")
def insert_operation(sql_statement, students):
    start_index = sql_statement.find("VALUES") + 7
    end_index = sql_statement.find(")")
    values = sql_statement[start_index:end_index].strip().split(",")
    validateValues(values)
    id = int(values[0])
    students[id] = {
        'name': values[1].strip().strip("'"),
        'lastname': values[2].strip().strip("'"),
        'email': values[3].strip().strip("'"),
        'grade': int(values[4])
    }
    return students
def validateValues(values):
    if len(values) != 5:
        raise Exception("Invalid number of values")
    if not values[0].isdigit():
        raise Exception("Invalid id")
    if not values[1].replace('‘','\'').replace('’','\'').strip("'").isalpha():
        raise Exception("Invalid name")
    if not values[2].replace('‘','\'').replace('’','\'').strip("'").isalpha():
        raise Exception("Invalid lastname")
    if not values[3].count('@') == 1 or not values[3].count('.') >= 1:
        raise Exception("Invalid email")
    if not values[4].isdigit():
        raise Exception("Invalid grade")
def delete_operation(sql_statement, students):
    condition = sql_statement[sql_statement.find("WHERE")+5:].strip().split(" ")
    if len(condition) == 7:
        first_id_list = [int(i) for i in take_subDict(students, condition[:3], condition[0].lower()).keys()]
        second_id_list = [int(i) for i in take_subDict(students, condition[4:], condition[4].lower()).keys()]
        id_list = list(set(first_id_list) & set(second_id_list))
    elif len(condition) == 3:
        id_list = [int(i) for i in take_subDict(students, condition, condition[0].lower()).keys()]
    
    for id in id_list:
        del students[id]

    return students
def write_JSON(subDict):
    with open('result.json', 'w') as fp:
        json.dump(subDict, fp, indent=4)    
def select_operation(sql_statement, students):
    columns = extract_columns(sql_statement)
    condition = extract_condition(sql_statement).split(" ")
    if len(condition) == 7:
        first_subDict = take_subDict(students, condition[:3], condition[0].lower(),columns)
        second_subDict = take_subDict(students, condition[4:], condition[4].lower(),columns)
        subDict = {k: v for k, v in first_subDict.items() if k in second_subDict}
    elif len(condition) == 3:
        subDict = take_subDict(students, condition, condition[0].lower(),columns)    
        
    order =  sql_statement[sql_statement.find("BY")+3:].strip() == "DSC"
    subDict = sorted(subDict.items(), key=lambda x: int(x[0]), reverse=order)
    return subDict
def take_subDict(students, condition, parameter,columns):
    subDict = {}
    for student in students:
        a = students[student][parameter]
        typeA = type(a)
        b = typeA(condition[2])
        operation = operators[condition[1]]
        if typeA == str:
            a = a.lower()
            b = b.lower().replace('‘','\'').replace('’','\'').strip("'")
        if operation(a, b):
            if columns[0] == "*":
                subDict[student] = students[student]
            else:
                subDict[student] = {}
                for column in columns:
                    subDict[student][column] = students[student][column]
    return subDict        
def extract_condition(sql_statement):
    start_index = sql_statement.find("WHERE") + 5
    end_index = sql_statement.find("ORDER")
    condition = sql_statement[start_index:end_index].strip()

    return condition
def extract_columns(sql_statement):
    start_index = sql_statement.find("SELECT") + 6
    end_index = sql_statement.find("FROM")
    columns = sql_statement[start_index:end_index].strip()
    columns = columns.split(",")
    return columns    
def read_CSV():
    data = {}
    with open("students.csv", 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for row in csv_reader:
            key = int(row['id'])
            values = {
                'name': row['name'],
                'lastname': row['lastname'],
                'email': row['email'],
                'grade': int(row['grade'])
            }
            data[key] = values
    return dict(sorted(data.items(), key=lambda x: int(x[0])))
if __name__ == "__main__":
    main()
