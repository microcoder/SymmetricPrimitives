import math
import bpy
import bmesh
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, BoolProperty


# This is table contains constant values of truncation for a circle by each 1mm in diameter for each amount subdivision when used modifier Subdivision Surface.
# keys - amount sudivision, values - value of truncation on 1mm of diameter for this subdivision
circle_trunc_values = {
    4: 0.006404966, 8: 0.006404966, 12: 0.006404966, 16: 0.006404966, 20: 0.006404966, 24: 0.006404966, 28: 0.006404966,
    32: 0.006404966, 36: 0.006404966, 40: 0.006404966, 44: 0.006404966, 48: 0.006404966, 52: 0.006404966, 56: 0.006404966, 
    60: 0.006404966, 64: 0.006404966, 68: 0.006404966, 72: 0.006404966, 76: 0.006404966, 80: 0.006404966, 84: 0.006404966, 
    88: 0.006404966, 92: 0.006404966, 96: 0.006404966, 100: 0.006404966, 104: 0.006404966, 108: 0.006404966, 112: 0.006404966,
    116: 0.006404966, 120: 0.006404966, 124: 0.006404966, 128: 0.006404966, 132: 0.006404966, 136: 0.006404966, 140: 0.006404966, 
    144: 0.006404966, 148: 0.006404966, 152: 0.006404966, 156: 0.006404966, 160: 0.006404966, 164: 0.006404966, 168: 0.006404966, 
    172: 0.006404966, 176: 0.006404966, 180: 0.006404966, 184: 0.006404966, 188: 0.006404966, 192: 0.006404966, 196: 0.006404966, 
    200: 0.006404966, 204: 0.006404966, 208: 0.006404966, 212: 0.006404966, 216: 0.006404966, 220: 0.006404966, 224: 0.006404966, 
    228: 0.006404966, 232: 0.006404966, 236: 0.006404966, 240: 0.006404966, 244: 0.006404966, 248: 0.006404966, 252: 0.006404966, 
    256: 0.006404966, 260: 0.006404966, 264: 0.006404966, 268: 0.006404966, 272: 0.006404966, 276: 0.006404966, 280: 0.006404966, 
    284: 0.006404966, 288: 0.006404966, 292: 0.006404966, 296: 0.006404966, 300: 0.006404966, 304: 0.006404966, 308: 0.006404966, 
    312: 0.006404966, 316: 0.006404966, 320: 0.006404966, 324: 0.006404966, 328: 0.006404966, 332: 0.006404966, 336: 0.006404966, 
    340: 0.006404966, 344: 0.006404966, 348: 0.006404966, 352: 0.006404966, 356: 0.006404966, 360: 0.006404966, 364: 0.006404966, 
    368: 0.006404966, 372: 0.006404966, 376: 0.006404966, 380: 0.006404966, 384: 0.006404966, 388: 0.006404966, 392: 0.006404966, 
    396: 0.006404966, 400: 0.006404966, 404: 0.006404966, 408: 0.006404966, 412: 0.006404966, 416: 0.006404966, 420: 0.006404966, 
    424: 0.006404966, 428: 0.006404966, 432: 0.006404966, 436: 0.006404966, 440: 0.006404966, 444: 0.006404966, 448: 0.006404966, 
    452: 0.006404966, 456: 0.006404966, 460: 0.006404966, 464: 0.006404966, 468: 0.006404966, 472: 0.006404966, 476: 0.006404966, 
    480: 0.006404966, 484: 0.006404966, 488: 0.006404966, 492: 0.006404966, 496: 0.006404966, 500: 0.006404966, 504: 0.006404966, 
    508: 0.006404966, 512: 0.006404966, 516: 0.006404966, 520: 0.006404966, 524: 0.006404966, 528: 0.006404966, 532: 0.006404966, 
    536: 0.006404966, 540: 0.006404966, 544: 0.006404966, 548: 0.006404966, 552: 0.006404966, 556: 0.006404966, 560: 0.006404966, 
    564: 0.006404966, 568: 0.006404966, 572: 0.006404966, 576: 0.006404966, 580: 0.006404966, 584: 0.006404966, 588: 0.006404966, 
    592: 0.006404966, 596: 0.006404966, 600: 0.006404966, 604: 0.006404966, 608: 0.006404966, 612: 0.006404966, 616: 0.006404966, 
    620: 0.006404966, 624: 0.006404966, 628: 0.006404966, 632: 0.006404966, 636: 0.006404966, 640: 0.006404966, 644: 0.006404966, 
    648: 0.006404966, 652: 0.006404966, 656: 0.006404966, 660: 0.006404966, 664: 0.006404966, 668: 0.006404966, 672: 0.006404966, 
    676: 0.006404966, 680: 0.006404966, 684: 0.006404966, 688: 0.006404966, 692: 0.006404966, 696: 0.006404966, 700: 0.006404966, 
    704: 0.006404966, 708: 0.006404966, 712: 0.006404966, 716: 0.006404966, 720: 0.006404966, 724: 0.006404966, 728: 0.006404966, 
    732: 0.006404966, 736: 0.006404966, 740: 0.006404966, 744: 0.006404966, 748: 0.006404966, 752: 0.006404966, 756: 0.006404966, 
    760: 0.006404966, 764: 0.006404966, 768: 0.006404966, 772: 0.006404966, 776: 0.006404966, 780: 0.006404966, 784: 0.006404966, 
    788: 0.006404966, 792: 0.006404966, 796: 0.006404966, 800: 0.006404966, 804: 0.006404966, 808: 0.006404966, 812: 0.006404966, 
    816: 0.006404966, 820: 0.006404966, 824: 0.006404966, 828: 0.006404966, 832: 0.006404966, 836: 0.006404966, 840: 0.006404966, 
    844: 0.006404966, 848: 0.006404966, 852: 0.006404966, 856: 0.006404966, 860: 0.006404966, 864: 0.006404966, 868: 0.006404966, 
    872: 0.006404966, 876: 0.006404966, 880: 0.006404966, 884: 0.006404966, 888: 0.006404966, 892: 0.006404966, 896: 0.006404966, 
    900: 0.006404966, 904: 0.006404966, 908: 0.006404966, 912: 0.006404966, 916: 0.006404966, 920: 0.006404966, 924: 0.006404966, 
    928: 0.006404966, 932: 0.006404966, 936: 0.006404966, 940: 0.006404966, 944: 0.006404966, 948: 0.006404966, 952: 0.006404966, 
    956: 0.006404966, 960: 0.006404966, 964: 0.006404966, 968: 0.006404966, 972: 0.006404966, 976: 0.006404966, 980: 0.006404966, 
    984: 0.006404966, 988: 0.006404966, 992: 0.006404966, 996: 0.006404966, 1000: 0.006404966
}


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
    return self.get('segments', 32)
    # return self['segments'] if 'segments' in self.keys() else 32


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
                          min=4, soft_max=1000, step=4, default=32,
                          get=get_segments, set=set_segments
    )
    auto_segments: BoolProperty(name='Auto segments',
                                description=f'Automatic calculation of the optimal number of segments for the specified radius truncation tolerance ' \
                                            'when used modifier Subdiv relative to original radius. This option has restricted maximum to {circle_trunc_values[-1]} segments',
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
        
        x,y,z = (0, 0, 0,)  # Center of circle
        step_size = 2 * math.pi / self.segments

        # Creating vertices:
        t = 0
        while t < 2 * math.pi:
            # circle_verts.append()
            bm.verts.new((self.radius * math.sin(t) + x, self.radius * math.cos(t) + y, z))
            t += step_size

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0000001)
        
        bm.verts.ensure_lookup_table()  # You need add it when your add/remove elements in your mesh
        bm.verts.index_update()
        
        # Creating edges and selecting vertices and edges:
        bm.verts[0].select = True

        for i in range(1, len(bm.verts)):
            bm.edges.new([bm.verts[i], bm.verts[i-1]])
            bm.verts[i].select = True
        
        bm.edges.new([bm.verts[0], bm.verts[-1]])  # Creating closed edge between first and last vertices
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
