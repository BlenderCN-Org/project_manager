import sys

main_hda_path = sys.argv[-4]
shading_hda_path = sys.argv[-3]
obj_path = sys.argv[-2].replace("\\", "/")
asset_name = sys.argv[-1]

main_hda = "H:/01-NAD/_pipeline/_utilities/_NEF/main_hda.hdanc"

definition = hou.hda.definitionsInFile(main_hda)
definition[0].copyToHDAFile(main_hda_path, asset_name, asset_name)

hou.hda.installFile(main_hda_path)
asset_node = hou.node("/obj").createNode(asset_name, asset_name)

asset_node.allowEditingOfContents()

# Set parameters
file_highres_node = hou.node("/obj/" + asset_name + "/layout/high-res_obj_from_modeling")
file_lowres_node = hou.node("/obj/" + asset_name + "/layout/low-res_obj_from_modeling")
rop_geo_high = hou.node("/obj/" + asset_name + "/layout/save_low_res_geometry")
rop_geo_low = hou.node("/obj/" + asset_name + "/layout/save_high_res_geometry")
file_highres_node.parm("file").set(obj_path)
file_lowres_node.parm("file").set(obj_path.replace("_out.obj", "-lowres_out.obj"))
rop_geo_high.parm("sopoutput").set(obj_path.replace("mod", "lay"))
rop_geo_low.parm("sopoutput").set(obj_path.replace("_out.obj", "-lowres_out.obj").replace("mod", "lay"))

# MATERIAL NODE
# Shopnet / Copnet
shopnet_node = hou.node("/obj/" + asset_name).createNode("shopnet")
shopnet_node.setName("shopnet")
shopnet_node.setColor(hou.Color((0.4, 1, 0.4)))
shopnet_node.moveToGoodPosition()

stickynote_node = hou.node("/obj/" + asset_name).createStickyNote("texture_paths")
stickynote_node.setText("No texture available.")


# Create Subnet and HDA for Material Node
material_node = hou.node("/obj/" + asset_name).collapseIntoSubnet([shopnet_node])
material_node = material_node.createDigitalAsset(asset_name + "-shd", shading_hda_path, asset_name + "-shd")
material_node.setName("shader_building")
material_node.moveToGoodPosition()

asset_node.type().definition().updateFromNode(asset_node)
































#
#
# # SOURCE NODE
# source_node = hou.node("/obj").createNode("geo")
# source_node.setName("layout")
# source_node.node("file1").destroy()
#
# # Create inside nodes
# file_highres_node = source_node.createNode("file")
# file_lowres_node = source_node.createNode("file")
# switch_high_low_node = source_node.createNode("switch")
# material_node = source_node.createNode("material")
# transform_node = source_node.createNode("xform")
# out_layout_node = source_node.createNode("null")
# rop_geo_high = source_node.createNode("rop_geometry")
# rop_geo_low = source_node.createNode("rop_geometry")
# switch_node = source_node.createNode("switch")
# pack_node = source_node.createNode("pack")
# out_node = source_node.createNode("null")
#
# alembic_node = source_node.createNode("alembic")
# attribCopy_node = source_node.createNode("attribcopy")
#
# # Rename inside nodes
# file_highres_node.setName("high-res_obj_from_modeling")
# file_lowres_node.setName("low-res_obj_from_modeling")
# switch_high_low_node.setName("switch_between_high-res_and_low-res")
# material_node.setName("shader")
# transform_node.setName("layout_transform")
# out_layout_node.setName("OUT_LAYOUT")
# rop_geo_high.setName("save_high_res_geometry")
# rop_geo_low.setName("save_low_res_geometry")
# switch_node.setName("switch_between_static_and_anim")
# pack_node.setName("pack")
# out_node.setName("OUT_ASSET")
#
# alembic_node.setName("alembic_from_animation")
# attribCopy_node.setName("copy_shader_to_animation")
#
# # Make connections
# switch_high_low_node.setInput(0, file_highres_node)
# switch_high_low_node.setInput(1, file_lowres_node)
# material_node.setInput(0, switch_high_low_node)
# transform_node.setInput(0, material_node)
# out_layout_node.setInput(0, transform_node)
# rop_geo_high.setInput(0, out_layout_node)
# rop_geo_low.setInput(0, out_layout_node)
# attribCopy_node.setInput(0, alembic_node)
# attribCopy_node.setInput(1, out_layout_node)
# switch_node.setInput(0, attribCopy_node)
# switch_node.setInput(1, out_layout_node)
# pack_node.setInput(0, switch_node)
# out_node.setInput(0, pack_node)
#
#
# # Set parameters
# file_highres_node.parm("file").set(obj_path)
# file_lowres_node.parm("file").set(obj_path.replace("_out.obj", "-lowres_out.obj"))
# rop_geo_high.parm("sopoutput").set(obj_path.replace("mod", "lay"))
# rop_geo_low.parm("sopoutput").set(obj_path.replace("_out.obj", "-lowres_out.obj").replace("mod", "lay"))
# switch_node.parm("input").set(1)
#
# file_highres_node.setColor(hou.Color((1, 1, 0.4)))
# file_lowres_node.setColor(hou.Color((1, 1, 0.4)))
# alembic_node.setColor(hou.Color((1, 1, 0.4)))
# switch_high_low_node.setColor(hou.Color((0.4, 1, 0.4)))
# transform_node.setColor(hou.Color((0.4, 1, 0.4)))
# switch_node.setColor(hou.Color((0.4, 1, 0.4)))
# material_node.setColor(hou.Color((0.4, 1, 0.4)))
# attribCopy_node.setColor(hou.Color((0.867, 0, 0)))
# rop_geo_high.setColor(hou.Color((0.867, 0, 0)))
# rop_geo_low.setColor(hou.Color((0.867, 0, 0)))
# pack_node.setColor(hou.Color((0.867, 0, 0)))
# out_node.setColor(hou.Color((0, 0, 0)))
# out_layout_node.setColor(hou.Color((0, 0, 0)))
#
# attribCopy_node.parm("srcgrouptype").set(2)
# attribCopy_node.parm("destgrouptype").set(2)
# attribCopy_node.parm("attrib").set(2)
# attribCopy_node.parm("attribname").set("shop_materialpath")
#
# out_node.setDisplayFlag(True)
# out_node.setRenderFlag(True)
#
# # Layout nodes
# source_node.layoutChildren()
#
# # CENTER OF THE WORLD NODE
# center_node = hou.node("/obj").createNode("geo")
# center_node.setName("center")
# center_node.node("file1").destroy()
# center_node.moveToGoodPosition()
# objectMerge_node = center_node.createNode("object_merge")
# objectMerge_node.setName("object_merge")
# objectMerge_node.setColor(hou.Color((0.867, 0, 0)))
# objectMerge_node.parm("objpath1").set("../../layout/shader")
#
# center_node.setDisplayFlag(False)
# center_node.layoutChildren()
#
# # MATERIAL NODE
# # Shopnet / Copnet
# shopnet_node = hou.node("/obj").createNode("shopnet")
# copnet_node = hou.node("/obj").createNode("cop2net")
# shopnet_node.setName("shopnet")
# copnet_node.setName("copnet")
#
# shopnet_node.setColor(hou.Color((0.4, 1, 0.4)))
# copnet_node.setColor(hou.Color((0.4, 1, 0.4)))
#
# shopnet_node.moveToGoodPosition()
# copnet_node.moveToGoodPosition()
#
#
# # Create Subnet and HDA for Material Node
# material_node = hou.node("/obj").collapseIntoSubnet([shopnet_node, copnet_node])
# material_node = material_node.createDigitalAsset(asset_name + "-shd", shading_hda_path, asset_name + "-shd")
# material_node.setName("shader_building")
# material_node.moveToGoodPosition()
#
# # Create Subnet and HDA for main node
# main_digital_asset = hou.node("/obj").collapseIntoSubnet([source_node, center_node, material_node])
# main_digital_asset.setName(asset_name)
# main_digital_asset.setColor(hou.Color((0, 0.6, 1)))
# main_digital_asset.createDigitalAsset(asset_name, main_hda_path, asset_name)

