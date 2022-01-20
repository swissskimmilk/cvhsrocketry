from flask import request 

NAME_INDEX = 0
TABLE_NAME_INDEX = 1
ELEMENT_INDEX = 2
COLUMN_INDEX = 3
REQUEST_ELEMENTS_INDEX = 4

CATEGORIES = [('tube', 'tubes',
                ['tube_name', 'tube_length', 'tube_inner_diameter', 'tube_outer_diameter', 'tube_weight', 'tube_quantity'], 
                ['name', 'length', 'inner_diameter', 'outer_diameter', 'weight', 'quantity'], 
                ['tube_name', 'tube_length', 'tube_quantity']), 
            ('material', 'materials',
                ['material_type', 'material_length', 'material_width', 'material_thickness', 'material_weight', 'material_quantity'], 
                ['type', 'length', 'width', 'thickness', 'weight', 'quantity'],
                ['material_type', 'material_length', 'material_width', 'material_thickness']), 
            ('motor', 'motors',
                ['motor_class', 'motor_average_thrust', 'motor_delay', 'motor_weight', 'motor_quantity'], 
                ['class', 'average_thrust', 'delay', 'weight', 'quantity'],
                ['motor_name', 'motor_quantity']), 
            ('recovery', 'recovery',
                ['recovery_name', 'recovery_type', 'recovery_size', 'recovery_weight', 'recovery_quantity'],
                ['name', 'type', 'size', 'weight', 'quantity'],
                ['recovery_name', 'recovery_quantity'])]

def processRequest(name):
    if name == "tube":
        return str(request.form.get("tube_length")) + " mm " + str(request.form.get("tube_name"))
    elif name == "material":
        return (str(request.form.get("material_length")) + " x " +
                str(request.form.get("material_width")) + " x " +
                str(request.form.get("material_thickness")) + " " +
                str(request.form.get("material_type")))
    elif name == "motor":
        return request.form.get("motor_name")
    elif name == "recovery":
        return request.form.get("recovery_name")