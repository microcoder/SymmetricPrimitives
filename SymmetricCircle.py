import math
import bpy
import bmesh
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, BoolProperty


# This is table contains constant values of truncation for a circle by each 1mm in diameter for each amount subdivision when used modifier Subdivision Surface.
# keys - amount sudivision, values - value of truncation on 1mm of diameter for this subdivision
circle_trunc_values = { 4: 0.333334,   8: 0.097631,  12: 0.0446582, 16: 0.0253736, 20: 0.0163146, 24: 0.011358,  28: 0.0083574,
                       32: 0.0064048, 36: 0.0050642, 40: 0.0041038, 44: 0.003393,  48: 0.0028518, 52: 0.0024304, 56: 0.002096,
                       60: 0.001826,  64: 0.0016052, 68: 0.001422,  72: 0.0012684, 76: 0.0011386, 80: 0.0010276, 84: 0.000932,
                       88: 0.0008492, 92: 0.000777,  96: 0.0007136, 100: 0.0006578}


def calculate_segments(self):
    for i in circle_trunc_values.items():
        if round(self.radius * 1000 * i[1], 2) <= self.max_trunc_radius * 1000:
            return i[0]
    
    return list(circle_trunc_values.keys())[-1]  # default value, limit the maximum value of calculate segments


def get_radius(self):
    return self.get('radius', 0.1)  # default value


def set_radius(self, value):
    self['radius'] = value

    if self.auto_segments:
        self['segments'] = calculate_segments(self)


def get_segments(self):
    return self.get('segments', 32)  # default value


def set_segments(self, value):
    if not self.auto_segments:
        self['segments'] = value // 4 * 4


def get_auto_segments(self):
    return self.get('auto_segments', False)


def set_auto_segments(self, value):
    self['auto_segments'] = value

    if value:
        self['segments'] = calculate_segments(self)


def get_max_trunc_radius(self):
    return self.get('max_trunc_radius', 0.00025)


def set_max_trunc_radius(self, value):
    self['max_trunc_radius'] = value

    if self.auto_segments:
        self['segments'] = calculate_segments(self)


class SymmetricCircle(Operator):
    """My Object Moving Script"""            # Use this as a tooltip for menu items and buttons. - FIXME:

    bl_idname = "mesh.symmetric_circle_add"  # Unique identifier for buttons and menu items to reference
    bl_label = "Symmetric Circle"            # Display name in the interface
    bl_options = {'REGISTER', 'UNDO'}        # Enable undo for the operator

    radius: FloatProperty(name='Radius', description='Radius a circle',
                          default=0.1, min=0.0001, soft_min=0, soft_max=100, precision=2,
                          subtype='DISTANCE', # unit='LENGTH'
                          get=get_radius, set=set_radius
    )
    segments: IntProperty(name='Segments', description='Amount segments a circle',
                          min=4, soft_max=1000, default=32, step=4,
                          get=get_segments, set=set_segments
    )
    auto_segments: BoolProperty(name='Auto segments',
                                description='Automatic calculation of the optimal number of segments for the specified radius truncation tolerance ' \
                                            'when used modifier Subdiv relative to original radius',
                                get=get_auto_segments, set=set_auto_segments
    )
    max_trunc_radius: FloatProperty(name='Maximum truncation tolerance by radius',
                                    description='Maximum truncation tolerance by radius when use the option Auto segments',
                                    default=0.00025, soft_min=0.0001, soft_max=10, step=0.001, precision=2,
                                    subtype='DISTANCE', # unit='CAMERA'
                                    get=get_max_trunc_radius, set=set_max_trunc_radius
    )
    

    def execute(self, context):

        # self.report({'WARNING'}, 'Example report')

        # NOTE: Находясь в режиме редактирования, Blender обрабатывает копию сетки, которая затем сохраняется как данные объекта (context.object.data)
        #       после выхода из режима редактирования. Это может стать причиной того, что не отображаются сделанные изменения в исходной сетке:
        #       https://stackoverflow.com/questions/20349361/selected-vertex-did-not-highlight-in-blender-3d
        #           * bmesh.from_mesh(mesh)       - Загрузка в BMesh из исходной сетки
        #           * bmesh.from_edit_mesh(mesh)  - Загрузка в BMesh из текущей сетки (копия исходной сетки, находящейся сейчас в режиме редактирования)
        # NOTE: Не забыть, что код можно запускать в тестовом редакторе Blender'a, чтобы его не перезапускать каждый раз!!
        #       Однако, код в редакторе Blender работает иначе. Логика создания bmesh.ops.create_circle полностью отличается - иногда вершины индексируются не по порядку!
        
        # FIXME: При 24 сегментах создается 25 вершин/сегментов вместо 24
        #        Например, при значении 36 сегментов в UI создается 37 вершин (одна накладывается на другую)
        # FIXME: При запуске Blender в консоли, выпадает ошибка - ModuleNotFoundError: No module named 'add_mesh_SymmetricPrimitives'
        # TODO:  Сделать self-test. Полу-реализация доступна в Blend файле версии. Реализовать через вызов оператора mesh.symmetric_circle_add()


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
            return {'CANCELLED'}            # Lets Blender know the operator finished successfully.
        
        
        ###################################################################
        # bmesh.ops.create_circle(bm, cap_ends=False, radius=self.radius, segments=self.segments)['verts']  # returning list of BMVert

        # see: https://stackoverflow.com/questions/42879081/how-to-generate-a-set-of-co-ordinates-for-a-circle-in-python-using-the-circle-fo/42879185
        circle_verts = []
        x,y,z = (0, 0, 0,)  # Center of circle
        step_size = 2 * math.pi / self.segments

        # Creating vertices:
        t = 0
        while t < 2 * math.pi:
            circle_verts.append(bm.verts.new((self.radius * math.sin(t) + x, self.radius * math.cos(t) + y, z)))
            t += step_size
        
        bm.verts.ensure_lookup_table()  # You need add it when your add/remove elements in your mesh
        bm.verts.index_update()
        
        # Creating edges and selecting vertices and edges:
        circle_verts[0].select = True

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
        
        return {'FINISHED'}  # Lets Blender know the operator finished successfully

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        # col.label(text='Custom Interface!')
        col.separator()

        row = col.row(align=True, heading='Radius')
        row.prop(self, 'radius', text='')

        row = col.row(align=True, heading='Segments')
        row.prop(self, 'segments', text='')
        row.active = True if not self.auto_segments else False

        row = col.row(align=True)
        row.prop(self, 'auto_segments')
        row_right = row.row(align=True)
        row_right.active = self.auto_segments
        row_right.prop(self, 'max_trunc_radius', text='')
        col.separator()


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
