import math
import bpy
import bmesh
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty



def get_segments(self):
    return self['segments'] if 'segments' in self.keys() else 32  # default value


def set_segments(self, value):
    
    # Decrement amount of segments while return_value doesn't is a multiple of 4
    while value%4 != 0:
        value -= 1
    
    self['segments'] = value


class SymmetricCircle(Operator):
    """My Object Moving Script"""            # Use this as a tooltip for menu items and buttons. - FIXME:

    bl_idname = "mesh.symmetric_circle_add"  # Unique identifier for buttons and menu items to reference
    bl_label = "Symmetric Circle"            # Display name in the interface
    bl_options = {'REGISTER', 'UNDO'}        # Enable undo for the operator

    radius: FloatProperty(attr='bf_Radius', name='Radius', min=0.0001, soft_min=0, soft_max=100, default=0.1,
                          description='Radius of the circle', unit='LENGTH')

    segments: IntProperty(name="Segments", min=8, soft_max=100, default=32, step=4, get=get_segments, set=set_segments)


    def execute(self, context):

        # self.report({'INFO'}, 'Example report')

        # NOTE: Находясь в режиме редактирования, Blender обрабатывает копию сетки, которая затем сохраняется как данные объекта (context.object.data)
        #       после выхода из режима редактирования. Это может стать причиной того, что не отображаются сделанные изменения в исходной сетке:
        #       https://stackoverflow.com/questions/20349361/selected-vertex-did-not-highlight-in-blender-3d
        #           * bmesh.from_mesh(mesh)       - Загрузка в BMesh из исходной сетки
        #           * bmesh.from_edit_mesh(mesh)  - Загрузка в BMesh из текущей сетки (копия исходной сетки, находящейся сейчас в режиме редактирования)
        # NOTE: Не забыть, что код можно запускать в тестовом редакторе Blender'a, чтобы его не перезапускать каждый раз!!
        #       Однако, код в редакторе Blender работает иначе. Логика создания bmesh.ops.create_circle полностью отличается - иногда вершины индексируются не по порядку!
        
        # FIXME: При запуске Blender в консоли, выпадает ошибка - ModuleNotFoundError: No module named 'add_mesh_SymmetricPrimitives'


        bm = bmesh.new()

        if context.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')                          # Deselect all objects
            blender_mesh = bpy.data.meshes.new('SymmetricCircle')                 # Creating a new empty data (object mesh)
            blender_obj = bpy.data.objects.new('SymmetricCircle', blender_mesh)   # Creating a new object and join there the object mesh
            context.collection.objects.link(blender_obj)                          # Put the object into current collection of current scene
            context.view_layer.objects.active = blender_obj                       # Set as the active object in the scene
            blender_obj.select_set(True)                                          # Set as selected object
        elif context.mode == 'EDIT_MESH':
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(type='VERT')
            blender_mesh = context.active_object.data
            bm = bmesh.from_edit_mesh(blender_mesh)
        else:
            return {'FINISHED'}            # Lets Blender know the operator finished successfully.
         
        
        ###################################################################
        # bmesh.ops.create_circle(bm, cap_ends=False, radius=self.radius, segments=self.segments)['verts']  # return only list of BMVert

        # see: https://stackoverflow.com/questions/42879081/how-to-generate-a-set-of-co-ordinates-for-a-circle-in-python-using-the-circle-fo/42879185
        circle_verts = []
        x,y,z = 0, 0, 0  # Center of circle
        step_size = 2 * math.pi / self.segments  # The length of the circle (2*pi) is dividing by setted amount of segments

        t = 0
        while t < 2 * math.pi:
            circle_verts.append(bm.verts.new((self.radius * math.sin(t) + x, self.radius * math.cos(t) + y, z)))
            t += step_size
        
        bm.verts.ensure_lookup_table()  # You need add it when your add/remove elements in your mesh
        bm.verts.index_update()
        
        circle_verts[0].select = True  # Creating circle edges and selecting vertices and edges
        
        for i in range(1, len(circle_verts)):
            bm.edges.new([circle_verts[i], circle_verts[i-1]])
            circle_verts[i].select = True
        
        bm.edges.new([circle_verts[0], circle_verts[-1]])  # Creating closed edge between first and last vertices
        bm.edges.ensure_lookup_table()  # You need add it when your add/remove elements in your mesh
        bm.select_flush_mode()  # will ensure the associated edges and faces will be selected also.
        
        ####################################################################
        
        
        if context.mode == 'OBJECT':
            bm.to_mesh(blender_mesh)  # from bmesh to object mesh (context.object.data)
        elif context.mode == 'EDIT_MESH':
            bmesh.update_edit_mesh(blender_mesh, False) # from bmesh to edit mesh (current edited mesh, copy of source mesh)
        
        bm.free
        
        return {'FINISHED'}  # Lets Blender know the operator finished successfully.

    # For custom UI
    # def draw(self, context):
    #     col = self.layout.column()
    #     col.label(text="Custom Interface!")

    #     row = col.row()
    #     row.prop(self, "radius")
    #     row.prop(self, "segments")

    #     col.prop(self, "segments")


classes = (
    SymmetricCircle,
)


def menu_func(self, context):
    for cls in classes:
        self.layout.operator(cls.bl_idname, text="Symmetric Circle", icon='MESH_CIRCLE')
        self.layout.separator()


def register():
    bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func)

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    








''' Для теста в текстовом редакторе Блендера:

import bpy
import bmesh


#bpy.ops.object.mode_set(mode='EDIT')
#bpy.ops.object.mode_set(mode='OBJECT')


if bpy.context.mode == 'OBJECT':
    bpy.ops.object.select_all(action='DESELECT')                # Deselect all objects
    bl_mesh = bpy.data.meshes.new('SymmetricCircle')            # Creating a new object mesh
    bl_obj = bpy.data.objects.new('SymmetricCircle', bl_mesh)   # Creating a new object and join there object mesh
    bpy.context.collection.objects.link(bl_obj)                 # Put the object into current collection of the scene
    bpy.context.view_layer.objects.active = bl_obj              # Set as the active object in the scene
    bl_obj.select_set(True)                                     # Set as selected object
elif bpy.context.mode == 'EDIT_MESH':
    bl_obj = bpy.context.active_object
    bl_mesh = bl_obj.data
else:
    pass


# Make a new BMesh
bm = bmesh.new()

# Add a circle xxx, should return all geometry created, not just verts.
segments=32
bmesh.ops.create_circle(bm, cap_ends=False, radius=0.5, segments=segments)

# Оставляем вершины только у четверти круга. TODO: доработать. Сейчас работает кратно 4 вершинам
for v in bm.verts[1:int(segments/4*3)]:
    bm.verts.remove(v)

# https://docs.blender.org/api/2.93/bmesh.ops.html#bmesh.ops.mirror
# geom = This is input geometry of list of BMVert, BMEdge, BMFace
#bmesh.ops.mirror(bm, geom=bm.verts[:] + bm.edges[:], merge_dist=0.00001, axis='X')
#bmesh.ops.mirror(bm, geom=bm.verts[:] + bm.edges[:], merge_dist=0.00001, axis='Y')
#bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)

#bmesh.ops.symmetrize(bm, input=bm.edges[:], direction='-X')
#bmesh.ops.symmetrize(bm, input=bm.edges[:], direction='-Y')
#bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)
#bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


bm.verts.ensure_lookup_table()
bm.verts[0].select_set(True)

#bm.verts.ensure_lookup_table()
#for v in bm.verts:
#    print(v.co, v.normal)


bpy.ops.object.mode_set(mode='OBJECT')
# Convert (load) object mesh to BMesh. Circle mesh + current mesh
bm.from_mesh(bl_mesh)
# Convert (moving) mesh from BMesh to object mesh
bm.to_mesh(bl_mesh)
bm.free()
#bl_mesh.update()
#bl_mesh.vertices[0].select = True
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_mode(type='VERT')
bpy.ops.mesh.select_linked()




# And finally select it and make it active
#if bpy.context.mode == 'OBJECT':
#    bl_obj.select_set(True)
#    bpy.context.view_layer.objects.active = bl_obj



'''
