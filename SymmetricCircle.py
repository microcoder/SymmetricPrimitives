# Это пример выноса кода одной логической функции аддона в отдельный файл

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
    """My Object Moving Script"""            # Use this as a tooltip for menu items and buttons.

    bl_idname = "mesh.symmetric_circle_add"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Symmetric Circle"            # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}        # Enable undo for the operator.

    radius: FloatProperty(attr='bf_Radius',
                          name='Radius',
                          min=0.0001, soft_min=0, max=50, default=0.1,
                          description='Radius of the circle',
                          unit='LENGTH')

    segments: IntProperty(name="Segments", min=4, soft_max=100, default=32, step=4, get=get_segments, set=set_segments)
    # segments: IntProperty(name="Segments", min=4, soft_max=100, default=32, step=4)


    def execute(self, context):

        # self.report({'INFO'}, 'F: %.2f  B: %s  S: %r' % (0.0001, True, 'Test string'))

        if context.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')                # Deselect all objects
            bl_mesh = bpy.data.meshes.new('SymmetricCircle')            # Creating a new object mesh
            bl_obj = bpy.data.objects.new('SymmetricCircle', bl_mesh)   # Creating a new object and join there object mesh
            context.collection.objects.link(bl_obj)                     # Put the object into current collection of the scene
            context.view_layer.objects.active = bl_obj                  # Set as the active object in the scene
            bl_obj.select_set(True)                                     # Set as selected object
        elif context.mode == 'EDIT_MESH':
            bl_obj = bpy.context.active_object
            bl_mesh = bl_obj.data
            bpy.ops.mesh.select_all(action='DESELECT')
        else:
            return {'FINISHED'}            # Lets Blender know the operator finished successfully.


        # Make a new BMesh
        bm = bmesh.new()
        # Add a circle xxx, should return all geometry created, not just verts.
        bmesh.ops.create_circle(bm, cap_ends=False, radius=self.radius, segments=self.segments)

        # Оставляем вершины только у четверти круга.
        # TODO: доработать. Сейчас работает кратно 4 вершинам
        for v in bm.verts[1:int(self.segments/4*3)]:
            bm.verts.remove(v)

        # geom = This is input geometry of list of BMVert, BMEdge, BMFace. https://docs.blender.org/api/2.93/bmesh.ops.html#bmesh.ops.mirror
        bmesh.ops.mirror(bm, geom=bm.verts[:] + bm.edges[:], merge_dist=0.00001, axis='X')
        bmesh.ops.mirror(bm, geom=bm.verts[:] + bm.edges[:], merge_dist=0.00001, axis='Y')

        # Alternate variant
        # bmesh.ops.symmetrize(bm, input=bm.edges[:], direction='-X')
        # bmesh.ops.symmetrize(bm, input=bm.edges[:], direction='-Y')
        # Additionally need merge vertices
        # bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)

        # Select first vertex of the circle
        bm.verts.ensure_lookup_table()
        bm.verts[0].select_set(True)

        # Switch to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')
        # Append current BMesh and object mesh from load (Circle mesh + object mesh)
        bm.from_mesh(bl_mesh)
        # Unload BMesh to object mesh
        bm.to_mesh(bl_mesh)
        bm.free()

        # Switch to Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')

        bl_mesh.vertices[0].select = True
        # bl_mesh.update()
        bpy.ops.mesh.select_linked()


        # TODO: Нужно сделать еще recalculate Normals. Изучить функции ниже:
        # bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        # bmesh.utils.edge_rotate(edge, ccw=False)

        # And finally select it and make it active.
        # TODO: Нужно снимать выделения с других объектов
        # bl_obj.select_set(True)
        # context.view_layer.objects.active = bl_obj

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.

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
