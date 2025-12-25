import bpy
#                                                                                                                               #Переменные
base_race = "chaos"                                                                                                             # расса с которой копируем территорию
base_name = "gurmuns_pass"                                                                                                       # название территории для копирования
source_obj_name = base_name + "_" + base_race
suffixes = ["enemy1","enemy2", "enemy3", "enemy4", "enemy5", "enemy6", "enemy7", "enemy8", "templar", "tyranids"]               # имена новых расс
armature_name = "Armature"                                                                                                      # название арматуры
image_race_list = ["enemy1", "enemy2", "enemy3", "enemy4", "enemy5", "enemy6", "enemy7", "enemy8", "templar_race", "tyranids_race"]   # название для текстур территорий под новые рассы
texture_share_path = "/art/ui/3d_models/texture_share/"                                                                         # стандартный путь до текстур в файлах игры
image_path = 'C:/Users/NeedMoreCoffee/Desktop/texture_share/texture_share Ready1/kaurava_iv/'                                   # путь до текстур заменяйте \ на /
map_suffixes = ["", "_spc", "_emi"]                                                                                             # Суффиксы карт(не менять!)
images = []

def get_base_name_planet():
    parts_mapping = {
        "kaurava_i_border": "kaurava_i_border",
        "kaurava_ii_border": "kaurava_ii_border",
        "kaurava_iii_border": "kaurava_iii_border",
        "kaurava_iv_border": "kaurava_iv_border"
    }
    
    for mat in bpy.data.materials:
        for key, value in parts_mapping.items():
            if key in mat.name:
                return value
    return None

base_name_planet = get_base_name_planet()  # если у вас свои названия для планеты или планет замените на: base_name_planet = "ваше название планеты"
source_obj = bpy.data.objects.get(source_obj_name)

# Функция для создания материала
def create_material(mat_name):
    if mat_name in bpy.data.materials:
        return bpy.data.materials[mat_name]
    mat = bpy.data.materials.new(name=mat_name)
    return mat

def create_duplicate_and_groups(source_obj, *broken):
    """
    Создает дубликат объекта и обновляет группы вершин.
    
    :param source_obj: исходный объект для дублирования
    :param new_name: имя нового объекта
    """
    if broken:
        # Создаем дубликат объекта
        new_obj = source_obj.copy()
        new_obj.data = source_obj.data.copy()
        bpy.context.collection.objects.link(new_obj)
        new_name = f"{base_name}_{suffix}"
        new_obj.name = new_name
        new_obj.data.name = new_name


        # Обновляем группы вершин
        for vg in new_obj.vertex_groups:
            if "chaos" in vg.name:
                vg.name = new_name
        
        return new_obj
    else:
        new_obj_broken = source_obj.copy()
        new_obj_broken.data = source_obj.data.copy()
        bpy.context.collection.objects.link(new_obj_broken)
        new_broken_name = f"{base_name}_{suffix}_broken"
        new_obj_broken.name = new_broken_name
        new_obj_broken.data.name = new_broken_name

        for vg in new_obj_broken.vertex_groups:
            if "chaos" in vg.name:
                vg.name = new_broken_name
            
        return new_obj_broken
    

for suffix in image_race_list:
    for map_suffix in map_suffixes:
        full_path = f"{image_path}{base_name_planet}_{suffix}{map_suffix}.dds"
        print(full_path)
        img = bpy.data.images.load(full_path)
        images.append(img)
        full_path_broken = f"{image_path}{base_name_planet}_{suffix}_broken{map_suffix}.dds"
        print(full_path_broken)
        img_broken = bpy.data.images.load(full_path_broken)
        images.append(img_broken)

for suffix, race in zip(suffixes, image_race_list):
    # Создаем дубликат
    new_obj = create_duplicate_and_groups(source_obj)
    
    new_obj_broken = create_duplicate_and_groups(source_obj, True)
    # копирование кости
    new_bone_name = f"{base_name}_{suffix}"
    # Получить объект арматуры
    armature_obj = bpy.data.objects[armature_name]
    # Сделать активным и выбрать
    bpy.context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)

    # Переключиться в режим редактирования
    bpy.ops.object.mode_set(mode='EDIT')

    # Получить редактируемую арматуру
    armature = bpy.context.object

    # Получить исходную кость
    source_bone = armature.data.edit_bones.get(source_obj_name)

    # Создать новую кость и скопировать параметры
    new_bone = armature.data.edit_bones.new(new_bone_name)
    new_bone.head = source_bone.head
    new_bone.tail = source_bone.tail
    new_bone.roll = source_bone.roll
    new_bone.use_connect = source_bone.use_connect
    new_bone.parent = source_bone.parent

    # Вернуться в Object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Копируем анимацию
    original_action = source_obj.animation_data.action
    new_action = original_action.copy()
    new_action.name = f"vis_{suffix}"
    new_obj.animation_data_create()
    new_obj.animation_data.action_slot = None
    new_obj.dow_force_invisible = True
    
    # Создаем материалы
    
    # Название для карты
    mat_name = f"{base_name_planet}_{race}"
    create_material(mat_name)
    # Название материала
    material_name = mat_name
    material = bpy.data.materials.get(material_name)
    # Назначение материала объекту
    new_obj.data.materials.clear()
    new_obj.data.materials.append(material)
    # Включаем использование узлов
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Очищаем существующие узлы
    nodes.clear()

    # Создаем основные узлы
    obj_info = nodes.new(type='ShaderNodeObjectInfo')
    obj_info.location = (0, 0)

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (0, -200)

    uv_map1 = nodes.new(type='ShaderNodeMapping')
    uv_map1.location = (200, 0)
    uv_map1.inputs[1].default_value[0] = -0.5
    uv_map1.inputs[1].default_value[1] = -0.5
    uv_map1.inputs[1].default_value[2] = -0.5
    links.new(tex_coord.outputs['UV'], uv_map1.inputs[0])

    uv_map2 = nodes.new(type='ShaderNodeMapping')
    uv_map2.location = (400, 0)
    uv_map2.name = "Mapping"
    uv_map2.label = "UV offset"
    links.new(uv_map1.outputs[0], uv_map2.inputs[0])

    uv_map3 = nodes.new(type='ShaderNodeMapping')
    uv_map3.location = (600, 0)
    uv_map3.inputs[1].default_value[0] = 0.5
    uv_map3.inputs[1].default_value[1] = 0.5
    uv_map3.inputs[1].default_value[2] = 0.5
    links.new(uv_map2.outputs[0], uv_map3.inputs[0])

    diff_name = f"{base_name_planet}_{race}.dds"
    image = bpy.data.images.get(diff_name)
    image.dow_export_path = f"{texture_share_path}{base_name_planet}_{race}"

    diff = nodes.new(type='ShaderNodeTexImage')
    diff.image = image
    diff.label = "diffuse"
    diff.dow_image_label = 'diffuse'
    diff.location = (800, 200)
    links.new(uv_map3.outputs[0], diff.inputs[0])

    specularity_name = f"{base_name_planet}_{race}_spc.dds"
    image = bpy.data.images.get(specularity_name)
    image.dow_export_path = f"{texture_share_path}{base_name_planet}_{race}_spc"

    specularity = nodes.new(type='ShaderNodeTexImage')
    specularity.image = image
    specularity.label = "specularity"
    specularity.dow_image_label = 'specularity'
    specularity.location = (800, -100)
    links.new(uv_map3.outputs[0], specularity.inputs[0])

    self_emi_name = f"{base_name_planet}_{race}_emi.dds"
    image = bpy.data.images.get(self_emi_name)
    image.dow_export_path = f"{texture_share_path}{base_name_planet}_{race}_emi"

    self_emi = nodes.new(type='ShaderNodeTexImage')
    self_emi.image = image
    self_emi.label = 'self_illumination'
    self_emi.dow_image_label = 'self_illumination'
    self_emi.location = (800, -400)
    links.new(uv_map3.outputs[0], self_emi.inputs[0])

    bpy.data.materials[mat_name]['full_path'] = f"{base_name_planet}_{race}"

    apply_spec = nodes.new(type='ShaderNodeMix')
    apply_spec.label = 'Apply_spec'
    apply_spec.name = "data_type"
    apply_spec.data_type = 'RGBA'
    apply_spec.blend_type = 'ADD'
    apply_spec.location = (1100, 200)
    links.new(diff.outputs[0], apply_spec.inputs[6])
    links.new(specularity.outputs[0], apply_spec.inputs[7])

    math_node = nodes.new(type='ShaderNodeMath')
    math_node.operation = 'MULTIPLY'
    math_node.location = (1100, -100)
    links.new(diff.outputs[1], math_node.inputs[0])
    links.new(obj_info.outputs[3], math_node.inputs[1])

    gamma_node = nodes.new(type='ShaderNodeGamma')
    gamma_node.location = (1100, -300)
    gamma_node.inputs['Gamma'].default_value = 0.454
    links.new(specularity.outputs[0], gamma_node.inputs[0])

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (1300, 200)
    bsdf.inputs[2].default_value = 0.133
    links.new(apply_spec.outputs[2], bsdf.inputs[0])
    links.new(gamma_node.outputs[0], bsdf.inputs[1])
    links.new(math_node.outputs[0], bsdf.inputs[4])
    links.new(self_emi.outputs[0], bsdf.inputs[27])
    links.new(self_emi.outputs[0], bsdf.inputs[28])

    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (1600, 200)
    links.new(bsdf.outputs[0], material_output.inputs[0])

# ////////////////////////////////////////////////////Broken/////////////////////////////////////////////////////////////////////

    

    new_bone_name = f"{base_name}_{suffix}_broken"
    armature_obj = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.context.object
    source_bone = armature.data.edit_bones.get(source_obj_name)
    new_bone = armature.data.edit_bones.new(new_bone_name)
    new_bone.head = source_bone.head
    new_bone.tail = source_bone.tail
    new_bone.roll = source_bone.roll
    new_bone.use_connect = source_bone.use_connect
    new_bone.parent = source_bone.parent
    bpy.ops.object.mode_set(mode='OBJECT')

    original_action = source_obj.animation_data.action
    new_action_broken = original_action.copy()
    new_action_broken.name = f"vis_{suffix}_broken"
    new_obj_broken.animation_data_create()
    new_obj_broken.animation_data.action_slot = None
    new_obj_broken.dow_force_invisible = True

    mat_broken_name = f"{base_name_planet}_{race}_broken"
    create_material(mat_broken_name)
    material_name = mat_broken_name
    material = bpy.data.materials.get(material_name)
    new_obj_broken.data.materials.clear()
    new_obj_broken.data.materials.append(material)
    # Включаем использование узлов
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Очищаем существующие узлы
    nodes.clear()

    # Создаем основные узлы
    obj_info = nodes.new(type='ShaderNodeObjectInfo')
    obj_info.location = (0, 0)

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (0, -200)

    uv_map1 = nodes.new(type='ShaderNodeMapping')
    uv_map1.location = (200, 0)
    uv_map1.inputs[1].default_value[0] = -0.5
    uv_map1.inputs[1].default_value[1] = -0.5
    uv_map1.inputs[1].default_value[2] = -0.5
    links.new(tex_coord.outputs['UV'], uv_map1.inputs[0])

    uv_map2 = nodes.new(type='ShaderNodeMapping')
    uv_map2.location = (400, 0)
    uv_map2.name = "Mapping"
    uv_map2.label = "UV offset"
    links.new(uv_map1.outputs[0], uv_map2.inputs[0])

    uv_map3 = nodes.new(type='ShaderNodeMapping')
    uv_map3.location = (600, 0)
    uv_map3.inputs[1].default_value[0] = 0.5
    uv_map3.inputs[1].default_value[1] = 0.5
    uv_map3.inputs[1].default_value[2] = 0.5
    links.new(uv_map2.outputs[0], uv_map3.inputs[0])

    diff_name = f"{base_name_planet}_{race}_broken.dds"
    image = bpy.data.images.get(diff_name)
    image.dow_export_path = f"{texture_share_path}{base_name_planet}_{race}_broken"

    diff = nodes.new(type='ShaderNodeTexImage')
    diff.image = image
    diff.label = "diffuse"
    diff.dow_image_label = 'diffuse'
    diff.location = (800, 200)
    links.new(uv_map3.outputs[0], diff.inputs[0])

    specularity_name = f"{base_name_planet}_{race}_broken_spc.dds"
    image = bpy.data.images.get(specularity_name)
    image.dow_export_path = f"{texture_share_path}{base_name_planet}_{race}_broken_spc"

    specularity = nodes.new(type='ShaderNodeTexImage')
    specularity.image = image
    specularity.label = "specularity"
    specularity.dow_image_label = 'specularity'
    specularity.location = (800, -100)
    links.new(uv_map3.outputs[0], specularity.inputs[0])

    self_emi_name = f"{base_name_planet}_{race}_broken_emi.dds"
    image = bpy.data.images.get(self_emi_name)
    image.dow_export_path = f"{texture_share_path}{base_name_planet}_{race}_broken_emi"

    self_emi = nodes.new(type='ShaderNodeTexImage')
    self_emi.image = image
    self_emi.label = 'self_illumination'
    self_emi.dow_image_label = 'self_illumination'
    self_emi.location = (800, -400)
    links.new(uv_map3.outputs[0], self_emi.inputs[0])

    bpy.data.materials[mat_broken_name]['full_path'] = f"{base_name_planet}_{race}_broken"
    bpy.data.materials[mat_broken_name]['protected'] = True

    apply_spec = nodes.new(type='ShaderNodeMix')
    apply_spec.label = 'Apply_spec'
    apply_spec.name = "data_type"
    apply_spec.data_type = 'RGBA'
    apply_spec.blend_type = 'ADD'
    apply_spec.location = (1100, 200)
    links.new(diff.outputs[0], apply_spec.inputs[6])
    links.new(specularity.outputs[0], apply_spec.inputs[7])

    math_node = nodes.new(type='ShaderNodeMath')
    math_node.operation = 'MULTIPLY'
    math_node.location = (1100, -100)
    links.new(diff.outputs[1], math_node.inputs[0])
    links.new(obj_info.outputs[3], math_node.inputs[1])

    gamma_node = nodes.new(type='ShaderNodeGamma')
    gamma_node.location = (1100, -300)
    gamma_node.inputs['Gamma'].default_value = 0.454
    links.new(specularity.outputs[0], gamma_node.inputs[0])

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (1300, 200)
    bsdf.inputs[2].default_value = 0.133
    links.new(apply_spec.outputs[2], bsdf.inputs[0])
    links.new(gamma_node.outputs[0], bsdf.inputs[1])
    links.new(math_node.outputs[0], bsdf.inputs[4])
    links.new(self_emi.outputs[0], bsdf.inputs[27])
    links.new(self_emi.outputs[0], bsdf.inputs[28])

    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (1600, 200)
    links.new(bsdf.outputs[0], material_output.inputs[0])
            
            
    '''actions = bpy.data.actions
    action_list  = []
    for i in range(len(actions)):
        if actions[i].name!= f"vis_{suffix}" and actions[i].name!= f"vis_{suffix}_broken":
                    action_list.append([{"name":actions[i].name},{"name":actions[i].name},{"selected":True}])
        elif actions[i].name == f"vis_{suffix}" or actions[i].name == f"vis_{suffix}_broken":
                    action_list.append([{"name":actions[i].name},{"name":actions[i].name},{"selected":False}])
                
    for i in range(len(action_list)):
        print(action_list[i])
    
    new_obj = bpy.data.objects.get("cape_of_despair_enemy1")
    bpy.context.view_layer.objects.active = new_obj        
    bpy.ops.object.dow_batch_configure_force_invisible(
    'INVOKE_DEFAULT',
    mesh_name=f"vis_{suffix}",
    selected_index=0,
    actions = action_list
    )'''