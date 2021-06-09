import math
import bpy
import bmesh
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, BoolProperty


# This is table contains constant values of truncation for a circle by each 1mm in diameter for each amount subdivision when used modifier Subdivision Surface.
# keys - amount sudivision, values - value of truncation on 1mm of diameter for this subdivision
circle_trunc_values = {
    4: 0.333333313, 8: 0.097631067, 12: 0.044658184, 16: 0.025373548, 20: 0.016314536, 24: 0.010971054, 28: 0.008357316, 32: 0.006404966, 
    36: 0.004987121, 40: 0.004103929, 44: 0.003358349, 48: 0.002827346, 52: 0.002430379, 56: 0.002095923, 60: 0.001816005, 64: 0.001597404, 
    68: 0.001415908, 72: 0.001263544, 76: 0.001138449, 80: 0.001027584, 84: 0.000932068, 88: 0.000849292, 92: 0.000777096, 96: 0.000713691, 
    100: 0.000656471, 104: 0.000607073, 108: 0.000564009, 112: 0.000523627, 116: 0.000488907, 120: 0.00045687, 124: 0.000427291, 128: 0.000401065, 
    132: 0.000377595, 136: 0.000355691, 140: 0.000335649, 144: 0.000316948, 148: 0.000300333, 152: 0.000284463, 156: 0.000270158, 160: 0.000257045, 
    164: 0.000244603, 168: 0.000232905, 172: 0.000222251, 176: 0.000212342, 180: 0.000202954, 184: 0.000194237, 188: 0.000186041, 192: 0.000178516, 
    196: 0.00017114, 200: 0.00016436, 204: 0.000158027, 208: 0.000152066, 212: 0.000146329, 216: 0.000140965, 220: 0.000135899, 224: 0.000131056, 
    228: 0.000126511, 232: 0.00012219, 236: 0.000118166, 240: 0.000114217, 244: 0.000110567, 248: 0.000106916, 252: 0.000103563, 256: 0.000100359, 
    260: 9.7305e-05, 264: 9.4399e-05, 268: 9.1568e-05, 272: 8.8885e-05, 276: 8.6427e-05, 280: 8.3894e-05, 284: 8.1509e-05, 288: 7.9274e-05, 
    292: 7.7188e-05, 296: 7.5102e-05, 300: 7.309e-05, 304: 7.1153e-05, 308: 6.9365e-05, 312: 6.7577e-05, 316: 6.5863e-05, 320: 6.4224e-05, 
    324: 6.2659e-05, 328: 6.1169e-05, 332: 5.9679e-05, 336: 5.8264e-05, 340: 5.6922e-05, 344: 5.5581e-05, 348: 5.4389e-05, 352: 5.3048e-05, 
    356: 5.1931e-05, 360: 5.0813e-05, 364: 4.9621e-05, 368: 4.8578e-05, 372: 4.7535e-05, 376: 4.6492e-05, 380: 4.5598e-05, 384: 4.4629e-05, 
    388: 4.366e-05, 392: 4.2766e-05, 396: 4.1947e-05, 400: 4.1127e-05, 404: 4.0308e-05, 408: 3.9488e-05, 412: 3.8743e-05, 416: 3.7998e-05, 
    420: 3.7253e-05, 424: 3.6582e-05, 428: 3.5912e-05, 432: 3.5316e-05, 436: 3.4571e-05, 440: 3.3975e-05, 444: 3.3379e-05, 448: 3.2783e-05, 
    452: 3.2187e-05, 456: 3.159e-05, 460: 3.1143e-05, 464: 3.0547e-05, 468: 3.0026e-05, 472: 2.9504e-05, 476: 2.9057e-05, 480: 2.861e-05, 
    484: 2.8089e-05, 488: 2.7567e-05, 492: 2.712e-05, 496: 2.6748e-05, 500: 2.6375e-05, 504: 2.5854e-05, 508: 2.5481e-05, 512: 2.5108e-05, 
    516: 2.4661e-05, 520: 2.4289e-05, 524: 2.3916e-05, 528: 2.3544e-05, 532: 2.3246e-05, 536: 2.2948e-05, 540: 2.2575e-05, 544: 2.2277e-05, 
    548: 2.1905e-05, 552: 2.1607e-05, 556: 2.1309e-05, 560: 2.0936e-05, 564: 2.0638e-05, 568: 2.0415e-05, 572: 2.0117e-05, 576: 1.9819e-05, 
    580: 1.9521e-05, 584: 1.9297e-05, 588: 1.9073e-05, 592: 1.8775e-05, 596: 1.8477e-05, 600: 1.8328e-05, 604: 1.803e-05, 608: 1.7807e-05, 
    612: 1.7583e-05, 616: 1.736e-05, 620: 1.7136e-05, 624: 1.6838e-05, 628: 1.6689e-05, 632: 1.6466e-05, 636: 1.6317e-05, 640: 1.6019e-05, 
    644: 1.587e-05, 648: 1.5721e-05, 652: 1.5497e-05, 656: 1.5274e-05, 660: 1.505e-05, 664: 1.4976e-05, 668: 1.4752e-05, 672: 1.4529e-05, 
    676: 1.438e-05, 680: 1.4231e-05, 684: 1.4007e-05, 688: 1.3858e-05, 692: 1.3709e-05, 696: 1.3635e-05, 700: 1.3411e-05, 704: 1.3262e-05, 
    708: 1.3113e-05, 712: 1.2964e-05, 716: 1.2815e-05, 720: 1.2666e-05, 724: 1.2517e-05, 728: 1.2368e-05, 732: 1.2219e-05, 736: 1.2144e-05, 
    740: 1.1995e-05, 744: 1.1846e-05, 748: 1.1772e-05, 752: 1.1623e-05, 756: 1.1474e-05, 760: 1.1399e-05, 764: 1.1325e-05, 768: 1.1176e-05, 
    772: 1.1027e-05, 776: 1.0878e-05, 780: 1.0803e-05, 784: 1.0729e-05, 788: 1.058e-05, 792: 1.0505e-05, 796: 1.0431e-05, 800: 1.0282e-05, 
    804: 1.0133e-05, 808: 1.0058e-05, 812: 9.984e-06, 816: 9.835e-06, 820: 9.835e-06, 824: 9.686e-06, 828: 9.537e-06, 832: 9.462e-06, 836: 9.388e-06, 
    840: 9.313e-06, 844: 9.239e-06, 848: 9.09e-06, 852: 9.015e-06, 856: 8.941e-06, 860: 8.941e-06, 864: 8.792e-06, 868: 8.717e-06, 872: 8.643e-06, 
    876: 8.568e-06, 880: 8.494e-06, 884: 8.419e-06, 888: 8.345e-06, 892: 8.27e-06, 896: 8.196e-06, 900: 8.121e-06, 904: 8.047e-06, 908: 7.972e-06, 
    912: 7.898e-06, 916: 7.898e-06, 920: 7.823e-06, 924: 7.749e-06, 928: 7.6e-06, 932: 7.6e-06, 936: 7.451e-06, 940: 7.451e-06, 944: 7.376e-06, 
    948: 7.302e-06, 952: 7.302e-06, 956: 7.153e-06, 960: 7.153e-06, 964: 7.078e-06, 968: 7.004e-06, 972: 7.004e-06, 976: 6.855e-06, 980: 6.855e-06, 
    984: 6.855e-06, 988: 6.706e-06, 992: 6.706e-06, 996: 6.631e-06, 1000: 6.631e-06
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

    if self.auto_segmentation:
        self['segments'] = calculate_segments(self)


def get_segments(self):
    return self.get('segments', 32)
    # return self['segments'] if 'segments' in self.keys() else 32


def set_segments(self, value):
    if not self.auto_segmentation:
        self['segments'] = value // 4 * 4


def get_auto_segmentation(self):
    return self.get('auto_segmentation', False)


def set_auto_segmentation(self, value):
    self['auto_segmentation'] = value

    if value:
        self['segments'] = calculate_segments(self)


def get_max_trunc_radius(self):
    return self.get('max_trunc_radius', 0.00025)


def set_max_trunc_radius(self, value):
    self['max_trunc_radius'] = value

    if self.auto_segmentation:
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
    auto_segmentation: BoolProperty(name='Auto segmentation',
                                    description='Automatic calculation of the optimal number of segments for the specified radius truncation tolerance ' \
                                                'when used modifier Subdiv relative to original radius. This option has restricted maximum to 1000 segments',
                                    get=get_auto_segmentation, set=set_auto_segmentation
    )
    max_trunc_radius: FloatProperty(name='Maximum truncation tolerance by radius',
                                    description='Maximum truncation tolerance by radius when use the option Auto segmentation',
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

        bmesh.ops.remove_doubles(bm, verts=circle_verts, dist=0.0000001)
        circle_verts = [v for v in circle_verts if v.is_valid]  # cleaning the list from <BMVert dead at ..>        
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
        
        # bm.clear()
        # bm.free()
        
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
        row.active = True if not self.auto_segmentation else False

        row = col.row(align=True)
        row.prop(self, 'auto_segmentation')
        row_right = row.row(align=True)
        row_right.active = self.auto_segmentation
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
