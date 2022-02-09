from flask import request 

NAME_INDEX = 0
TABLE_NAME_INDEX = 1
ELEMENT_INDEX = 2
COLUMN_INDEX = 3
REQUEST_ELEMENTS_INDEX = 4
QUERY_INDEX = 5

# Name, table n ame, element names, columns, request element names 
CATEGORIES = [('tube', 'tubes',
                ['tube_name', 'tube_length', 'tube_inner_diameter', 'tube_outer_diameter', 'tube_weight', 'tube_quantity'], 
                ['name', 'length', 'inner_diameter', 'outer_diameter', 'weight', 'quantity'], 
                ['tube_name', 'tube_length', 'tube_quantity'],
                """CREATE TABLE `tubes` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `name` varchar(256) DEFAULT NULL,
                    `length` varchar(256) DEFAULT NULL,
                    `inner_diameter` float DEFAULT NULL,
                    `outer_diameter` float DEFAULT NULL,
                    `weight` float DEFAULT NULL,
                    `quantity` int DEFAULT '0',
                    PRIMARY KEY (`id`))"""), 
            ('material', 'materials',
                ['material_type', 'material_length', 'material_width', 'material_thickness', 'material_weight', 'material_quantity'], 
                ['type', 'length', 'width', 'thickness', 'weight', 'quantity'],
                ['material_type', 'material_length', 'material_width', 'material_thickness'],
                """CREATE TABLE `materials` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `type` varchar(256) DEFAULT NULL,
                    `length` float DEFAULT NULL,
                    `width` float DEFAULT NULL,
                    `thickness` float DEFAULT NULL,
                    `weight` float DEFAULT NULL,
                    PRIMARY KEY (`id`))"""), 
            ('motor', 'motors',
                ['motor_class', 'motor_average_thrust', 'motor_delay', 'motor_weight', 'motor_quantity'], 
                ['class', 'average_thrust', 'delay', 'weight', 'quantity'],
                ['motor_name', 'motor_quantity'],
                """CREATE TABLE `motors` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `class` char(1) DEFAULT NULL,
                    `average_thrust` int DEFAULT NULL,
                    `delay` int DEFAULT NULL,
                    `weight` float DEFAULT NULL,
                    `quantity` int DEFAULT '0',
                    PRIMARY KEY (`id`))"""), 
            ('recovery', 'recovery',
                ['recovery_name', 'recovery_type', 'recovery_size', 'recovery_weight', 'recovery_quantity'],
                ['name', 'type', 'size', 'weight', 'quantity'],
                ['recovery_name', 'recovery_quantity'],
                """CREATE TABLE `recovery` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `name` varchar(256) DEFAULT NULL,
                    `type` varchar(256) DEFAULT NULL,
                    `size` varchar(256) DEFAULT NULL,
                    `weight` float DEFAULT NULL,
                    `quantity` int DEFAULT '0',
                    PRIMARY KEY (`id`))"""),
            ('motorblock', 'motorblocks',
                ['motorblock_size', 'motorblock_length', 'motorblock_weight', 'motorblock_quantity'],
                ['size', 'length', 'weight', 'quantity'],
                ['motorblock_name', 'motorblock_quantity'], 
                """CREATE TABLE `motorblocks` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `size` varchar(256) DEFAULT NULL,
                    `length` varchar(256) DEFAULT NULL,
                    `weight` float DEFAULT NULL,
                    `quantity` int DEFAULT '0',
                    PRIMARY KEY (`id`))"""),
            ('centering_ring', 'centering_rings',
                ['centering_ring_inner_diameter', 'centering_ring_outer_diameter', 'centering_ring_thickness', 'centering_ring_weight', 'centering_ring_quantity'],
                ['inner_diameter', 'outer_diameter', 'thickness', 'weight', 'quantity'],
                ['centering_ring_name', 'centering_ring_quantity'], 
                """CREATE TABLE `centering_rings` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `inner_diameter` float DEFAULT NULL,
                    `outer_diameter` float DEFAULT NULL,
                    `thickness` float DEFAULT NULL,
                    `weight` float DEFAULT NULL,
                    `quantity` int DEFAULT '0',
                    PRIMARY KEY (`id`))""")]

UPLOAD_CATEGORY = ['3D_print', 'laser_cut', 'ork']

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
    elif name == "motorblock":
        return request.form.get("motorblock_name")
    elif name == "centering_ring":
        return request.form.get("centering_ring_name")