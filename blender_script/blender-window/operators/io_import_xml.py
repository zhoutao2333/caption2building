import math
from telnetlib import X3PAD
import bpy
from bpy.props import StringProperty

import os
import os.path
import xml.etree.ElementTree as ET


import bpy
import bmesh
from mathutils import Matrix


class Blender_OT_xml_file(bpy.types.Operator):
    bl_idname = "import.xml_file"
    bl_label = "Import XML"
    bl_description = "Select and import xml xml file to building"
    bl_options = {"UNDO"}

    filepath : StringProperty(
        name = "File Path",
        description = "Filepath used for importing the file", 
        maxlen = 1024,
        subtype = "FILE_PATH"
    )

    filename_ext = ".xml"

    filter_glob : StringProperty(
        default = "*.xml",
        options = {'HIDDEN'}
    )


    my_property: bpy.props.FloatProperty(default=0.0)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if not os.path.exists(self.filepath):
                self.report({"ERROR"}, "Invalid file")
                return {"CANCELLED"}
        xml_file = open(self.filepath, encoding="utf-8")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        height = int(root.find('size').find('height').text)
        Xmin = 1e10
        Xmax = -1
        Ymin = 1e10
        Ymax = -1
        doorflag = False

        for obj in root.iter('object'):
                name = obj.find('name').text
                xmlbox = obj.find('bndbox')
                x1 = int(xmlbox.find('xmin').text)
                x2 = int(xmlbox.find('xmax').text)
                x3 = int(xmlbox.find('ymin').text)
                x4 = int(xmlbox.find('ymax').text)
                y2 = height - x3
                y1 = height - x4
                Xmin = min(Xmin,x1)
                Xmax = max(Xmax,x2)
                Ymin = min(Ymin,y1)
                Ymax = max(Ymax,y2)

                # 适用于casement side-win sliding
                scl = (((x2-x1)/20, (y2-y1)/20, 0.1),                      #中心ppanel
                        ((x2-x1)/20*0.05, (y2-y1)/20, 0.5),                      #竖框
                        ((x2-x1)/20+(x2-x1)/20*0.05, (y2-y1)/20*0.03, 0.5),      #横框
                        ((x2-x1)/20+(x2-x1)/20*0.05, (y2-y1)/20*0.03, 0.5),    #中心横框
                        ((x2-x1)/20*0.05, (y2-y1)/20*0.66, 0.5),               #0.75*竖框
                        ((x2-x1)/20+(x2-x1)/20*0.05, (y2-y1)/20*0.01, 0.5)
                )
                # 适用于fixed
                scl_1 = (((x2-x1)/20, (y2-y1)/20, 0.1),                  #中心panel
                        ((x2-x1)/20*0.02, (y2-y1)/20, 1),                    #竖框
                        ((x2-x1)/20+(x2-x1)/20*0.02, (y2-y1)/20*0.03, 1),    #横框
                        ((x2-x1)/20+(x2-x1)/20*0.02, (y2-y1)/20*0.03, 0.5),  #中心横框
                )
                # 适用于sec-win
                scl_2 = (((x2-x1)/20, (y2-y1)/20, 0.1),                  #中心panel
                        ((x2-x1)/20*0.02, (y2-y1)/20, 1),                    #竖框
                        ((x2-x1)/20+(x2-x1)/20*0.02, (y2-y1)/20*0.03, 1),    #横框
                        ((x2-x1)/20+(x2-x1)/20*0.02, (y2-y1)/20*0.03, 0.5),  #中心横框
                        ((x2-x1)/20*0.02, (y2-y1)/20*0.66, 0.5)              #0.75*竖框
                )

                # 适用于shutter
                scl_3 = (((x2-x1)/20 - 1, (y2-y1)/150, 0.1),             #中心panel
                        ((x2-x1)/20*0.02, (y2-y1)/20, 1),                    #竖框
                        ((x2-x1)/20+(x2-x1)/20*0.02, (y2-y1)/20*0.03, 1),    #横框
                        ((x2-x1)/20+(x2-x1)/20*0.02, (y2-y1)/20*0.03, 0.5),  #中心横框
                        ((x2-x1)/20*0.02, (y2-y1)/20*0.66, 0.5)              #0.75*竖框
                )

                # 适用于arch-win
                scl_4 = (((x2-x1)/20, (y2-y1)/30, 0.1),                      #中心ppanel
                        ((x2-x1)/20*0.05, (y2-y1)/30, 0.5),                      #竖框
                        ((x2-x1)/20+(x2-x1)/20*0.05, (y2-y1)/20*0.03, 0.5), 
                        ((x2-x1)/40*0.02, ((x2-x1)/40-(x2-x1)/40*0.05)-(x2-x1)/80, 0.1),                   #圆中棒
                        ((x2-x1)/20*0.02, (y2-y1)/20, 1),                   
                        ((x2-x1)/20+(x2-x1)/20*0.02, (y2-y1)/20*0.03, 1),    #横框
                        ((x2-x1)/20+(x2-x1)/20*0.02, (y2-y1)/20*0.03, 0.5),  #中心横框
                        ((x2-x1)/20*0.01, (y2-y1)/30, 0.5)              #0.75*竖框
                )


                # 适用于AC
                scl_5 = (((x2-x1)/20, (y2-y1)/20, 2),                      #中心ppanel
                        ((x2-x1)/20*0.05, (y2-y1)/20, 0.5)                     
                )


                # 适用于door
                scl_6 = (((x2-x1)/20, (y2-y1)/20, 0.1),                      #中心ppanel
                        ((x2-x1)/20*0.04, (y2-y1)/20, 0.5),                      #竖框
                        ((x2-x1)/20+(x2-x1)/20*0.05, (y2-y1)/20*0.03, 0.5),      #横框
                        ((x2-x1)/20*0.05, (y2-y1)/20*0.10, 0.5),                 #竖把手
                        ((x2-x1)/20*0.09, (y2-y1)/20*0.01, 0.5)                  #横把手
                )


                # 适用于balcony
                scl_7 = (((x2-x1)/20, (y2-y1)/20*0.03, 0.5),      #顶横杆
                        ((x2-x1)/20, (y2-y1)/20*0.01, 0.5),           #底横杆
                        ((x2-x1)/20+(x2-x1)/20*0.07, (y2-y1)/20*0.1, 10),            #底座
                        ((x2-x1)/20*0.02, (y2-y1)/20*0.66, 0.5),      #竖杆
                        ((x2-x1)/20*0.01, (y2-y1)/20*0.01, 10)        #直杆
                )


                # building
                scl_8 = (((Xmax-Xmin)/15, (Ymax-Ymin)/17, 15),                 #有门
                        ((Xmax-Xmin)/15, (Ymax-Ymin)/15, 15),                      #无门
                        ((x2-x1)/20+(x2-x1)/20*0.05, (y2-y1)/20*0.03, 0.5),      #横框
                        ((x2-x1)/20*0.05, (y2-y1)/20*0.10, 0.5),                 #竖把手
                        ((x2-x1)/20*0.09, (y2-y1)/20*0.01, 0.5)                  #横把手
                )


                dep = ((x2-x1)/10+0.05,(y2-y1)/10)

                if name == "casement":
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,(y1+y2)/20,0), scale=scl[0])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x1/10,(y1+y2)/20,0), scale=scl[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y2/10,0), scale=scl[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x2/10,(y1+y2)/20,0), scale=scl[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y1/10,0), scale=scl[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20,(y1+y2)/20,0.5), scale=scl[1])
                        # bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                        #         location=((x1+x2)/20,(y1+(y2-y1)*0.80/2)/10,0), scale=scl[3])
                                
                        for i in range(1, 4):
                                if i == 3:
                                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                                location=((x2+x1)/20,(y1+(y2-y1)*i/4)/10,1), scale=scl[3])      
                                else:
                                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                                location=((x2+x1)/20,(y1+(y2-y1)*i/4)/10,0), scale=scl[5])   
                
                if name == "side-win":
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,(y1+y2)/20,0), scale=scl[0])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x1/10,(y1+y2)/20,0), scale=scl[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y2/10,0), scale=scl[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x2/10,(y1+y2)/20,0), scale=scl[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y1/10,0), scale=scl[2])   
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,(y1+y2)/20,0), scale=scl[1]) 

                
                if name == "fixed":
                        if(x2-x1) > (y2-y1):
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl_1[0])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x1/10,(y1+y2)/20,0), scale=scl_1[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y2/10,0), scale=scl_1[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x2/10,(y1+y2)/20,0), scale=scl_1[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y1/10,0), scale=scl_1[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x1+x2)/20,(y1+(y2-y1)*0.66)/10,0), scale=scl_1[3])    
                                        
                                for i in range(1, 4):
                                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                                location=((x1+(x2-x1)*i/4)/10,(y1+y2)/20,0), scale=scl_1[1])
                        
                        else:
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl[0])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x1/10,(y1+y2)/20,0), scale=scl[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y2/10,0.1), scale=scl[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x2/10,(y1+y2)/20,0), scale=scl[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y1/10,0.1), scale=scl[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x1+x2)/20,(y1+y2)/20,0), scale=scl[2])         

                
                if name == "sliding":
                        if (x2-x1) < (y2-y1):
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl[0])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x1/10,(y1+y2)/20,0), scale=scl[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y2/10,0.1), scale=scl[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x2/10,(y1+y2)/20,0), scale=scl[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y1/10,0.1), scale=scl[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x1+x2)/20,(y1+(y2-y1)*0.66)/10,0), scale=scl[3])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x1+x2)/20,(y1+(y2-y1)*0.66/2)/10,0), scale=scl[4])  
                        else:
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl[0])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x1/10,(y1+y2)/20,0), scale=scl[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y2/10,0.1), scale=scl[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x2/10,(y1+y2)/20,0), scale=scl[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y1/10,0.1), scale=scl[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x1+x2)/20,(y1+y2)/20,0), scale=scl[1])                      

                        
                if name == "sec-win":
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,(y1+y2)/20,0), scale=scl_2[0])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x1/10,(y1+y2)/20,0), scale=scl_2[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y2/10,0), scale=scl_2[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x2/10,(y1+y2)/20,0), scale=scl_2[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y1/10,0), scale=scl_2[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20,(y1+(y2-y1)*0.66)/10,0), scale=scl_2[3])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20,(y1+(y2-y1)*0.66/2)/10,0), scale=scl_2[4])
                        bpy.ops.mesh.primitive_cylinder_add(radius=0.5,depth=dep[0],align="WORLD",
                                location=((x1+x2)/20,(y1+(y2-y1)/3)/10,0.7),rotation=(0,1.57,0))
                        bpy.ops.mesh.primitive_cylinder_add(radius=0.5,depth=dep[0],align="WORLD",
                                location=((x1+x2)/20,(y1+(y2-y1)*2/3)/10,0.7),rotation=(0,1.57,0))                
                
                        for i in range(1, 10):
                                bpy.ops.mesh.primitive_cylinder_add(radius=0.3,depth=dep[1],align="WORLD",
                                        location=((x1+(x2-x1)*i/10)/10, (y1+y2)/20, 0.7),rotation=(1.57,0,0)) 


                if name == 'sht-win':
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,(y1+y2)/20,0), scale=scl[0])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x1/10,(y1+y2)/20,0), scale=scl[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y2/10,0), scale=scl[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x2/10,(y1+y2)/20,0), scale=scl[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y1/10,0), scale=scl[2])   
                        
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,(y1+(y2-y1)*2/3)/10,0), scale=scl[3]) 

        
                if name == "shutter":
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,(y1+y2)/20,0), scale=scl_2[0])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x1/10,(y1+y2)/20,0), scale=scl_2[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y2/10,0), scale=scl_2[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x2/10,(y1+y2)/20,0), scale=scl_2[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y1/10,0), scale=scl_2[2])        
                        for i in range(1, 16):
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y2 - (y2 - y1)*i/16)/10,0), scale=scl_3[0],rotation=(-0.4,0,0))


                if name == "arch-win":
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,(y1+y2)/20-(y2-y1)/20+(y2-y1)/30,0.5), scale=scl_4[0])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x1/10,(y1+y2)/20-(y2-y1)/20+(y2-y1)/30,0.7), scale=scl_4[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y2/10-(y2-y1)/30,0.7), scale=scl_4[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x2/10,(y1+y2)/20-(y2-y1)/20+(y2-y1)/30,0.7), scale=scl_4[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x2+x1)/20,y1/10,0.7), scale=scl_4[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20,(y1+y2)/20-(y2-y1)/20+(y2-y1)/30,0.5), scale=scl_4[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x1/10+(x2-x1)/40,(y1+y2)/20-(y2-y1)/20+(y2-y1)/30,0.6), scale=scl_4[7])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x2/10-(x2-x1)/40,(y1+y2)/20-(y2-y1)/20+(y2-y1)/30,0.6), scale=scl_4[7])
                        bpy.ops.mesh.primitive_cylinder_add(radius=(x2-x1)/20 + (x2-x1)/20*0.05,depth=0.1,align="WORLD",
                                location=((x1+x2)/20, y2/10-(y2-y1)/30, 0.1),rotation=(0,0,0)) 
                        bpy.ops.mesh.primitive_cylinder_add(radius=(x2-x1)/20-(x2-x1)/20*0.05,depth=0.1,align="WORLD",
                                location=((x1+x2)/20, y2/10-(y2-y1)/30, 0.3),rotation=(0,0,0)) 
                        bpy.ops.mesh.primitive_cylinder_add(radius=(x2-x1)/40,depth=0.1,align="WORLD",
                                location=((x1+x2)/20, y2/10-(y2-y1)/30, 0.4),rotation=(0,0,0)) 
                        position = (y2-y1)/15+(x2-x1)/40+((x2-x1)/20-(x2-x1)/20*0.05-(x2-x1)/40)/2
                        position2 = (y2-y1)/15+(x2-x1)/40+((x2-x1)/20-(x2-x1)/20*0.05-(x2-x1)/40)/2-(x2-x1)/80                          
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20-(x2-x1)/40,y1/10+position2,0.5), scale=scl_4[3],rotation=(0,0,math.radians(45)))
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20,y1/10+position,0.5), scale=scl_4[3],rotation=(0,0,0))
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20+(x2-x1)/40,y1/10+position2,0.5), scale=scl_4[3],rotation=(0,0,math.radians(-45)))    
        
                        for i in range(1, 4):    
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y1/10+(y2-y1)/30*2/4*i,0.5), scale=scl[5])     


                if name == 'AC':
                        if (x2-x1) > (y2-y1):
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl_5[0])
                                bpy.ops.mesh.primitive_cylinder_add(radius=(y2-y1)/25,depth=0.1,align="WORLD",
                                        location=(x1/10+(y2-y1)/25+((y2-y1)/20-(y2-y1)/25), (y1+y2)/20, 2.1),rotation=(0,0,0)) 
                                
                        else:
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl_5[0])
                                bpy.ops.mesh.primitive_cylinder_add(radius=(x2-x1)/40,depth=0.5,align="WORLD",
                                        location=(x1/10+(x2-x1)/40+(x2-x1)/80, (y1+y2)/20+(x2-x1)/40, 2.1),rotation=(0,0,0)) 
                                bpy.ops.mesh.primitive_cylinder_add(radius=(x2-x1)/40,depth=0.5,align="WORLD",
                                        location=(x1/10+(x2-x1)/40+(x2-x1)/80,(y1+y2)/20-(x2-x1)/40, 2.1),rotation=(0,0,0)) 


                if name == 'door':
                        if (x2-x1) < (y2-y1):
                                doorflag = True
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl_6[0])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x1/10,(y1+y2)/20,0), scale=scl_6[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y2/10,0), scale=scl_6[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x2/10,(y1+y2)/20,0), scale=scl_6[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y1/10,0), scale=scl_6[2])    
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl_6[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20-(x2-x1)/100,(y1+y2)/20,0.1), scale=scl_6[3])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20-(x2-x1)/100-(x2-x1)/20*0.05,(y1+y2)/20,0), scale=scl_6[4])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20+(x2-x1)/100,(y1+y2)/20,0.1), scale=scl_6[3])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20+(x2-x1)/100+(x2-x1)/20*0.05,(y1+y2)/20,0), scale=scl_6[4])
                        else:
                                doorflag = True
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl_6[0])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x1/10,(y1+y2)/20,0), scale=scl_6[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y2/10,0), scale=scl_6[2])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=(x2/10,(y1+y2)/20,0), scale=scl_6[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,y1/10,0), scale=scl_6[2])            
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20,(y1+y2)/20,0), scale=scl_6[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x1+(x2-x1)/4)/10,(y1+y2)/20,0), scale=scl_6[1])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2-(x2-x1)/4)/10,(y1+y2)/20,0), scale=scl_6[1])               
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20-(x2-x1)/100,(y1+y2)/20,0.1), scale=scl_6[3])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20-(x2-x1)/100-(x2-x1)/20*0.05,(y1+y2)/20,0), scale=scl_6[4])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20+(x2-x1)/100,(y1+y2)/20,0.1), scale=scl_6[3])
                                bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                        location=((x2+x1)/20+(x2-x1)/100+(x2-x1)/20*0.05,(y1+y2)/20,0), scale=scl_6[4])


                if name == 'balcony':
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20,y2/10,20), scale=scl_7[0])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20,y1/10,20), scale=scl_7[1])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((x1+x2)/20,y1/10-(y2-y1)/20*0.1,10), scale=scl_7[2])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x1/10,y1/10,10), scale=scl_7[4])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x2/10,y1/10,10), scale=scl_7[4])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x1/10,y2/10,10), scale=scl_7[4])
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=(x2/10,y2/10,10), scale=scl_7[4])
        


                        for i in range(0, 11):
                                bpy.ops.mesh.primitive_cylinder_add(radius=0.3,depth=dep[1],align="WORLD",
                                        location=((x1+(x2-x1)*i/10)/10, (y1+y2)/20, 20),rotation=(1.57,0,0)) 
                        for i in range(0, 4):
                                bpy.ops.mesh.primitive_cylinder_add(radius=0.3,depth=dep[1],align="WORLD",
                                        location=(x1/10, (y1+y2)/20, (20)/4*i),rotation=(1.57,0,0)) 
                        for i in range(0, 4):
                                bpy.ops.mesh.primitive_cylinder_add(radius=0.3,depth=dep[1],align="WORLD",
                                        location=(x2/10, (y1+y2)/20, (20)/4*i),rotation=(1.57,0,0)) 


        else:
                if doorflag == True:
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((Xmin+Xmax)/20,Ymin/10+(Ymax-Ymin)/18,-15), scale=scl_8[0])

                else:
                        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                location=((Xmin+Xmax)/20,(Ymax+Ymin)/20,-15), scale=scl_8[1])
        

        

        
            

        return {"FINISHED"}


def register():
    bpy.utils.register_class(Blender_OT_xml_file)


def unregister():
    bpy.utils.unregister_class(Blender_OT_xml_file)