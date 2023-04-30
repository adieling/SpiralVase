import bpy
import bmesh
from math import cos, sin, radians

class SpiralVasePanel(bpy.types.Panel):
    bl_label = "Spiral Vase"
    bl_idname = "OBJECT_PT_spiral_vase"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Spiral Vase'

    def draw(self, context):
        layout = self.layout

        # Add options to control the behavior of the script
        col = layout.column()
        col.label(text="Geometry options:")
        col.prop(context.scene, "num_slices")
        col.prop(context.scene, "slice_height")
        col.prop(context.scene, "num_samples")
        col.prop(context.scene, "base_radius")
        col.prop(context.scene, "slice_scale")
        col.prop(context.scene, "slice_rotate")
        col.prop(context.scene, "minor_radius")
        col.prop(context.scene, "minor_freq")
        col.prop(context.scene, "slice_wave")

        # Add a button to run the script
        layout.operator("spiralvase.run_script", text="Generate Spiral Vase")


class SpiralVaseRunScript(bpy.types.Operator):
    bl_idname = "spiralvase.run_script"
    bl_label = "Generate Spiral Vase"

    def execute(self, context):
        # Get the values of the options
        num_slices = context.scene.num_slices
        slice_height = context.scene.slice_height
        num_samples = context.scene.num_samples
        base_radius = context.scene.base_radius
        slice_scale = context.scene.slice_scale
        slice_rotate = context.scene.slice_rotate
        minor_radius = context.scene.minor_radius
        minor_freq = context.scene.minor_freq
        slice_wave = context.scene.slice_wave
    
        sincircle(num_slices, slice_height,
                  slice_scale[0], slice_scale[1], slice_scale[2],
                  slice_rotate[0], slice_rotate[1], slice_rotate[2],
                  base_radius, minor_radius,
                  num_samples, minor_freq,
                  slice_wave[0], slice_wave[1], slice_wave[2]
        )

        return {'FINISHED'}
    
def run_spiral_vase_operator(self, context):
    # Get the operator by its ID
    op = bpy.ops.spiralvase.run_script
    # Invoke the operator to generate the spiral vase
    op()    

def register():
    bpy.utils.register_class(SpiralVasePanel)
    bpy.utils.register_class(SpiralVaseRunScript)

    # Create properties for the options
    bpy.types.Scene.num_slices = bpy.props.IntProperty(name="Slices", default=200, description="Number of slices (or layers) generated in the model.", update=run_spiral_vase_operator)
    bpy.types.Scene.slice_height = bpy.props.FloatProperty(name="Slice Height", default=0.2, step=0.1, description="Height of each slice.", update=run_spiral_vase_operator)
    bpy.types.Scene.num_samples = bpy.props.IntProperty(name="Samples", default=200, description="Number of samples taken on the edge of each slice.", update=run_spiral_vase_operator)
    bpy.types.Scene.base_radius = bpy.props.FloatProperty(name="Base Radius", default=14.0, step=0.1, description="Base radius of each slice before scaling is applied.", update=run_spiral_vase_operator)
    bpy.types.Scene.slice_scale = bpy.props.FloatVectorProperty(name="Slice Scale", size=3, default=(0, 100, 0.3), description="Controls the scaling of each slice, when set to [0 0 1] no scaling is performed. The slice scaling is calculated by a sine wave running vertically, where the first and second arguments are used to linearly interpolate (for each slice) a value in the domain of the sine function (in degrees). The final argument defines the amplitude of the sine wave.", update=run_spiral_vase_operator)
    bpy.types.Scene.slice_rotate = bpy.props.FloatVectorProperty(name="Slice Rotate", size=3, default=(0, 180, 30), description="Controls the rotation of each slice, when set to [0 0 1] no rotation is performed. The slice rotation is calculated by a sine wave running vertically, where the first and second arguments are used to linearly interpolate (for each slice) a value in the domain of the sine function (in degrees). The final argument defines the amplitude of the sine wave.", update=run_spiral_vase_operator)
    bpy.types.Scene.minor_radius = bpy.props.FloatProperty(name="Minor Radius", default=1.0, step=0.1, description="Each slice starts as a circle, and then has its edge transformed into a sine wave. This value sets the amplitude of the sine wave. To have each slice remain as a circle, set this value to 0.", update=run_spiral_vase_operator)
    bpy.types.Scene.minor_freq = bpy.props.IntProperty(name="Minor Freq", default=12, description="Each slice starts as a circle, and then has its edge transformed into a sine wave. This value sets the number of resulting sine waves. Only complete waves are supported, thus this value must be an integer.", update=run_spiral_vase_operator)
    bpy.types.Scene.slice_wave = bpy.props.FloatVectorProperty(name="Slice Wave", size=3, default=(0, 1480, 199), description="Controls the magnitude of the sine wave applied on each slice by running a second vertical sine wave, that is multiplied against the wave on the edge of each slice. This can be used to create a bumpy texture on the vase or chamfer the base/top. The first two parameters define the start and stop of the sine wave. E.g. values of [0, 180, slices] would result in a round top and bottom with the ridges graduated in and out. The final parameter is a cut-off (in layers), so that it's possible to chamfer the base of the base into a circle, i.e. the default value of [0,90,20] will start the base with a round circle (as the first value is sin(0)=0) and over the subsequent 20 layers graduate to the maximum ridges as sin(90)=1.", update=run_spiral_vase_operator)


def unregister():
    # Remove the options from the scene properties
    del bpy.types.Scene.num_slices
    del bpy.types.Scene.slice_height
    del bpy.types.Scene.num_samples
    del bpy.types.Scene.base_radius
    del bpy.types.Scene.slice_scale
    del bpy.types.Scene.slice_rotate
    del bpy.types.Scene.minor_radius
    del bpy.types.Scene.minor_freq
    del bpy.types.Scene.slice_wave

    bpy.utils.unregister_class(SpiralVasePanel)
    bpy.utils.unregister_class(SpiralVaseRunScript)
    
    
    
def sincircle(layers, layer_height,
              layer_start_angle, layer_end_angle, layer_amplitude, 
              layer_r_start_angle, layer_r_end_angle, layer_r, 
              major_r, minor_r,
              major_steps, minor_rate,
              minor_r_start, minor_r_end, minor_r_cutout):
    

    def drange(start, stop, step):
        "range that supports floats"
        r = start
        while r < stop:
            yield r
            r += step

    scene = bpy.context.scene

    bpy.ops.object.mode_set(mode='OBJECT')

    # delete objects, clean up ....
    print("preparing environment")
    #for i in bpy.data.objects :
    #    i.select_set(True)
    #    bpy.ops.object.delete()
    objects_to_delete = []
    for obj in bpy.data.objects:
        objects_to_delete.append(obj)

    for obj in objects_to_delete:
        bpy.data.objects.remove(obj, do_unlink=True)


    # add camera
    bpy.ops.object.camera_add()
    scene.camera = bpy.context.active_object

    # setup camera
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 768
    scene.camera.data.lens_unit = 'FOV'
    scene.camera.data.angle = radians(10)
    scene.camera.data.clip_end = 4000
    scene.camera.rotation_euler[0] = radians(80)
    scene.camera.rotation_euler[1] = 0
    scene.camera.rotation_euler[2] = 0

    # add light
    bpy.ops.object.light_add(type='SUN')
    light = bpy.context.active_object
    light.data.color = (0.228546, 0.271841, 1) # light blue
    light.rotation_euler[0] = scene.camera.rotation_euler[0]
    light.rotation_euler[1] = scene.camera.rotation_euler[1]
    light.rotation_euler[2] = scene.camera.rotation_euler[2]

    print("building object")
    mesh = bpy.data.meshes.new("mesh")  # add a new mesh
    # add a new object using the mesh
    obj = bpy.data.objects.new("SpiralVase", mesh)

    #scene.objects.append(obj)  # put the object into the scene (link)
    #scene.objects.active = obj  # set as the active object in the scene
    #obj.select = True  # select object
    scene.collection.objects.link(obj)  # put the object into the scene (link)
    bpy.context.view_layer.objects.active = obj  # set as the active object in the scene
    obj.select_set(True)  # select object


    mesh = bpy.context.object.data
    bm = bmesh.new()

    # util function
    def interpolate(start,end,points,point) :
        "linear interpolate to find point of points between start and end"
        if point >= points :
            return end
        if point <= 0 :
            return start
        return ((end - start) / points) * point + start

    print("calculating vertices")

    old_layer_vs = None
    for l in range(0,layers) :
        vs = []
        v1 = None
        for i in drange(0,360,360/major_steps) :
            r = (minor_r *
                 sin(radians(i * minor_rate)) *
                 sin(radians(interpolate(minor_r_start,
                                         minor_r_end,
                                         minor_r_cutout,
                                         l))))
            R = r + (major_r *
                     (sin(radians(interpolate(layer_start_angle,
                                              layer_end_angle,
                                              layers,
                                              l))) * layer_amplitude + 1))

            i += (layer_r *
                  sin(radians(interpolate(layer_r_start_angle,
                                          layer_r_end_angle,
                                          layers,
                                          l))))

            base_v = (sin(radians(i)) * R, cos(radians(i)) * R, l*layer_height)
            v2 = bm.verts.new(base_v)
            vs.append(v2)

            # connect vertex to previous layer
            if l > 0 :
                bm.edges.new((old_layer_vs[len(vs)-1],v2))

            # connect vertex on same layer
            if v1 != None :
                bm.edges.new((v1,v2))

                # draw face
                if l > 0 :
                    bm.faces.new((old_layer_vs[len(vs)-2],
                                  old_layer_vs[len(vs)-1],
                                  v2,
                                  v1))
            else :
                v0 = v2
            v1 = v2

        # close the loop on the layer
        bm.edges.new((v0,v2))

        # draw last face on layer
        if l > 0 :
            bm.faces.new((old_layer_vs[0],old_layer_vs[len(vs)-1],v2,v0))

        # save the layer samples that were actually calculated (could vary
        # because of rounding issues from major_steps)
        if l == 0 :
            layer_samples = len(bm.verts)
            print("samples per layer " + str(layer_samples))

        # save easy access to the just calculated vertices for next layer
        old_layer_vs = vs

    # bottom face
    bm.faces.new(bm.verts[:layer_samples])

    if layers > 0 :
        # top face
        bm.faces.new(bm.verts[-layer_samples:])

    print("finalise")
    # make the bmesh the object's mesh
    bm.to_mesh(mesh)
    bm.free()  # always do this when finished

    # adjust view to whole object
    for area in bpy.context.screen.areas :
        if area.type == 'VIEW_3D' :
            ctx = bpy.context.copy()
            ctx['area'] = area
            ctx['region'] = area.regions[-1]
            if area.spaces.active.region_3d.is_perspective :
                bpy.ops.view3d.view_persportho(ctx)
            bpy.ops.view3d.view_selected(ctx)
            bpy.ops.view3d.camera_to_view_selected(ctx)

    # set light position to camera position
    light.location[0] = scene.camera.location[0]
    light.location[1] = scene.camera.location[1]
    light.location[2] = scene.camera.location[2]

if __name__ == "__main__":
    register()