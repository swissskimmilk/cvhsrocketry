NAME_INDEX = 0
ELEMENT_INDEX = 1
COLUMN_INDEX = 2
REQUEST_ELEMENTS_INDEX = 3

CATEGORIES = [{'tube', 
            ['tube_name', 'tube_length', 'tube_inner_diameter', 'tube_outer_diameter', 'tube_weight', 'tube_quantity'], 
            ['name', 'length', 'inner_diameter', 'outer_diameter', 'weight', 'quantity'], 
            ['tube_name', 'tube_length', 'tube_quantity']}, 
        {'material', 
            ['material_type', 'material_length', 'material_width', 'material_thickness', 'material_weight', 'material_quantity'], 
            ['type', 'length', 'width', 'thickness', 'weight', 'quantity'],
            ['material_type', 'material_length', 'material_width', 'material_thickness']}, 
        {'motor', 
            ['motor_class', 'motor_average_thrust', 'motor_delay', 'motor_weight', 'motor_quantity'], 
            ['class', 'average_thrust', 'delay', 'weight', 'quantity'],
            ['motor_name', 'motor_quantity']}, 
        {'recovery',
            ['recovery_name', 'recovery_type', 'recovery_size', 'recovery_weight', 'recovery_quantity'],
            ['name', 'type', 'size', 'weight', 'quantity'],
            ['recovery_name', 'recovery_quantity']}]
