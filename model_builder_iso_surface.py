'''
Known issue : when use hg.IsoSurfaceSphere() to create a sphere into an iso surface (created by hg.NewIsoSurface() ), need to invert the height and depth params.
Ex: 
iso_surface = hg.NewIsoSurface(width, height, depth)
hg.IsoSurfaceSphere(iso_surface, width, depth, height, ...)
'''

import harfang as hg
from math import pi, sin, cos

anim_spheres = False

def create_iso_surface_sphere_default():
    iso_sphere = {
        "iso_sphere_pos" : hg.Vec3(0, 0, 0),
        "iso_sphere_radius" : 1.0,
        "iso_sphere_value" : 1.0,
        "iso_sphere_exponent" : 1.0
    }
    return iso_sphere

def create_iso_surface_sphere(pos, radius):
    iso_sphere = {
        "iso_sphere_pos" : pos,
        "iso_sphere_radius" : radius,
        "iso_sphere_value" : 1.0,
        "iso_sphere_exponent" : 1.0
    }
    return iso_sphere

def create_iso_surface_spheres_list_circle(origin):
    sphere_list = []
    sphere_radius = 8.0
    radius = 10
    for i in range(10):
        angle = i / 10 * pi * 2
        x = radius * cos(angle)
        y = radius * sin(angle) 
        z = i * radius / 6
        sphere_list.append(create_iso_surface_sphere(hg.Vec3(x, y, z) + origin, sphere_radius))
    return sphere_list

def create_iso_surface_spheres_list_blob(origin):
    sphere_list = []
    sphere_radius = 6.0
    radius = 10
    for i in range(10):
        angle = i / 10 * pi * 2
        x = radius * cos(angle)
        y = radius / 2 
        z = radius * sin(angle) 
        sphere_list.append(create_iso_surface_sphere(hg.Vec3(x, y, z) + origin, sphere_radius))
    return sphere_list


def create_iso_surface_with_spheres_list(iso_surface_bounds, iso_level, iso_scale, iso_spheres_list, clock_sec): #iso_sphere_pos, iso_sphere_radius, iso_sphere_value, iso_sphere_exponent):
    # Create isosurface
    isos_width = iso_surface_bounds[0]
    isos_height = iso_surface_bounds[1]
    isos_depth = iso_surface_bounds[2]
    iso_surface = hg.NewIsoSurface(isos_width, isos_height, isos_depth)

    for i, iso_sphere in enumerate(iso_spheres_list):
        iso_sphere_pos = iso_sphere["iso_sphere_pos"]
        iso_sphere_radius = iso_sphere["iso_sphere_radius"]
        iso_sphere_value = iso_sphere["iso_sphere_value"]
        iso_sphere_exponent = iso_sphere["iso_sphere_exponent"]

        if anim_spheres:
            clock = cos(clock_sec + i) / 4
            pos_z = ((isos_height / 2 - iso_sphere_radius) * clock) + isos_height / 2
        else:
            pos_z = iso_sphere_pos.z

        hg.IsoSurfaceSphere(iso_surface, isos_width, isos_depth, isos_height, iso_sphere_pos.x, iso_sphere_pos.y, pos_z, iso_sphere_radius, iso_sphere_value, iso_sphere_exponent)


    # iso_surface = hg.GaussianBlurIsoSurface(iso_surface, isos_width, isos_height, isos_depth)

    # Create a model builder
    mdl_builder = hg.ModelBuilder()

    # Create vertex layout
    vtx_layout = hg.VertexLayoutPosFloatNormUInt8() 

    # Convert isosurface to model
    material_idx = 0
    is_okey = hg.IsoSurfaceToModel(mdl_builder, iso_surface, isos_width, isos_height, isos_depth, material_idx, iso_level, iso_scale.x, iso_scale.y, iso_scale.z)

    # Get the model from the isosurface sphere
    isoss_mdl = mdl_builder.MakeModel(vtx_layout)

    return isoss_mdl


# Init render and resources
hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit('Harfang - Model builder iso surface', res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

# Init pipeline
pipeline = hg.CreateForwardPipeline(1024, True)
res = hg.PipelineResources()

hg.AddAssetsFolder('resources_compiled')

# Init ImGui
imgui_prg = hg.LoadProgramFromAssets('core/shader/imgui')
imgui_img_prg = hg.LoadProgramFromAssets('core/shader/imgui_image')

hg.ImGuiInit(10, imgui_prg, imgui_img_prg)

# Setup scene
scene = hg.Scene()
hg.LoadSceneFromAssets("probe_scene/scene_iso_surface.scn", scene, res, hg.GetForwardPipelineInfo())

# Create camera
camera_rot_x = 0
camera_rot_y = 0
camera_distance = 50
camera_new_mtx = hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(camera_rot_x, camera_rot_y, 0)) * hg.TransformationMat4(hg.Vec3(0, 0, -10), hg.Vec3(0, 0, 0))
camera_node = hg.CreateCamera(scene, camera_new_mtx, 0.01, 1000)
scene.SetCurrentCamera(camera_node)

# Disable sphere node 
marker_node = scene.GetNode("sphere")
marker_node_pos = marker_node.GetTransform().GetPos()

ground_node = scene.GetNode("ground")

# light_mtx = hg.TransformationMat4(hg.Vec3(5, 35, 12.5), hg.Vec3(hg.DegreeToRadian(85), hg.DegreeToRadian(90), hg.DegreeToRadian(0)))
light_mtx = hg.TransformationMat4(hg.Vec3(12.5, 35, 12.5), hg.Vec3(hg.DegreeToRadian(90), hg.DegreeToRadian(90), hg.DegreeToRadian(0)))
inner_angle = hg.DegreeToRadian(30)
outer_angle = hg.DegreeToRadian(45)
light_color = hg.Color(1, 1, 1, 1)
light = hg.CreateSpotLight(scene, light_mtx, 0, inner_angle, outer_angle, light_color, 1, light_color, 1, 1, hg.LST_Map, 0.0001)

# Init input
keyboard = hg.Keyboard()

# Create materials
prg_ref = hg.LoadPipelineProgramRefFromAssets('core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())
isoss_material = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4(0.5, 0.5, 0.5), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 1, 0.25))

# Generate iso surface mdl
iso_surface_bounds = [50, 50, 50]

# iso_sphere_list = []
# for x in range(2):
#     iso_sphere = create_iso_surface_sphere_default()
#     iso_sphere_list.append(iso_sphere)

iso_sphere_list = create_iso_surface_spheres_list_circle(hg.Vec3(iso_surface_bounds[0] / 2, iso_surface_bounds[0] / 2, iso_surface_bounds[0] / 2))

iso_level = 0.8
iso_scale = hg.Vec3(1, 1, 1)

isoss_mdl = create_iso_surface_with_spheres_list(iso_surface_bounds, iso_level, iso_scale, iso_sphere_list, 1)

# Add the isosurface sphere model to the PipelineResources and get the corresponding model ref 
isoss_mdl_ref = res.AddModel('isosurface', isoss_mdl)

# Create a node from the model ref
isoss_node_scale = hg.Vec3(0.5, 0.5, 0.5)
isoss_node = hg.CreateObject(scene, hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(0, 0, 0), isoss_node_scale), isoss_mdl_ref, [isoss_material])

# main loop
while not keyboard.Down(hg.K_Escape) and hg.IsWindowOpen(win):
    render_was_reset, res_x, res_y = hg.RenderResetToWindow(win, res_x, res_y, hg.RF_VSync)
    dt = hg.TickClock()
    current_time = hg.time_to_sec_f(hg.GetClock())

    isos_width = iso_surface_bounds[0]
    isos_height = iso_surface_bounds[1]
    isos_depth = iso_surface_bounds[2]

    scale_factor = iso_scale * isoss_node_scale

    # Update camera pos input
    if hg.ReadKeyboard().Key(hg.K_W):
        camera_rot_x = camera_rot_x + (1 * pi / 180)
    elif hg.ReadKeyboard().Key(hg.K_S):
        camera_rot_x = camera_rot_x - (1 * pi / 180)
    elif hg.ReadKeyboard().Key(hg.K_A):
        camera_rot_y = camera_rot_y + (1 * pi / 180)
    elif hg.ReadKeyboard().Key(hg.K_D):
        camera_rot_y = camera_rot_y - (1 * pi / 180)
    # Update camera node pos
    camera_new_mtx = hg.TransformationMat4(hg.Vec3(isos_width / 2 * scale_factor.x, isos_height / 3 * scale_factor.y, isos_depth / 2 * scale_factor.z), hg.Vec3(camera_rot_x, camera_rot_y, 0)) * hg.TransformationMat4(hg.Vec3(0, 0, -camera_distance), hg.Vec3(0, 0, 0))
    camera_node.GetTransform().SetWorld(camera_new_mtx)

    ground_node.GetTransform().SetWorld(hg.TransformationMat4(hg.Vec3(isos_width / 2 * scale_factor.x, 0, isos_depth / 2 * scale_factor.z), hg.Vec3(0, 0, 0), hg.Vec3(isos_width * scale_factor.x, 1, isos_depth * scale_factor.z)))
    ground_node_scale = ground_node.GetTransform().GetScale()

    marker_node.GetTransform().SetPos(marker_node_pos)

    new_isoss_mdl = create_iso_surface_with_spheres_list(iso_surface_bounds, iso_level, iso_scale, iso_sphere_list, current_time)
    res.UpdateModel(isoss_mdl_ref, new_isoss_mdl)
    isoss_node.GetTransform().SetScale(isoss_node_scale)
    isoss_node_scale = isoss_node.GetTransform().GetScale()

    scene.Update(dt)

    vid, passid = hg.SubmitSceneToPipeline(0, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res)

    # Imgui
    hg.ImGuiBeginFrame(res_x, res_y, hg.TickClock(), hg.ReadMouse(), hg.ReadKeyboard())

    if hg.ImGuiBegin('IsoSurface setting', True, hg.ImGuiWindowFlags_AlwaysAutoResize):
        changed, camera_distance = hg.ImGuiInputInt("Camera distance", camera_distance)
        changed, isoss_node_scale = hg.ImGuiInputVec3("Model node scale", isoss_node_scale)
        change, marker_node_pos = hg.ImGuiInputVec3("Marker node pos", marker_node_pos)
        hg.ImGuiText("ground size : x = {0}, y = {1}, z = {2}".format(ground_node_scale.x, ground_node_scale.y, ground_node_scale.z))

        hg.ImGuiNewLine()

        changed, anim_spheres = hg.ImGuiCheckbox("Anim spheres", anim_spheres)

        hg.ImGuiNewLine()

        if hg.ImGuiCollapsingHeader("Iso surface"):
            hg.ImGuiText("iso_surface_bounds")
            changed, iso_surface_bounds[0] = hg.ImGuiInputInt("width (isos)", iso_surface_bounds[0])
            changed, iso_surface_bounds[1] = hg.ImGuiInputInt("height (isos)", iso_surface_bounds[1])
            changed, iso_surface_bounds[2] = hg.ImGuiInputInt("depth (isos)", iso_surface_bounds[2])

            changed, iso_level = hg.ImGuiInputFloat("iso_level", iso_level)

            changed, iso_scale = hg.ImGuiInputVec3("iso_scale", iso_scale)

        hg.ImGuiNewLine()

        for i, iso_sphere in enumerate(iso_sphere_list):
            str_i = str(i)
            if hg.ImGuiCollapsingHeader("Iso sphere" + str_i):
                changed, iso_sphere["iso_sphere_pos"] = hg.ImGuiInputVec3("iso_sphere_pos_" + str_i, iso_sphere["iso_sphere_pos"])
                changed, iso_sphere["iso_sphere_radius"] = hg.ImGuiInputFloat("iso_sphere_radius_" + str_i, iso_sphere["iso_sphere_radius"])
                changed, iso_sphere["iso_sphere_value"] = hg.ImGuiInputFloat("iso_sphere_value_" + str_i, iso_sphere["iso_sphere_value"])
                changed, iso_sphere["iso_sphere_exponent"] = hg.ImGuiInputFloat("iso_sphere_exponent_" + str_i, iso_sphere["iso_sphere_exponent"])
    
    hg.ImGuiEnd()

    hg.ImGuiEndFrame(vid)

    hg.Frame()
    hg.UpdateWindow(win)

hg.RenderShutdown()
hg.DestroyWindow(win)