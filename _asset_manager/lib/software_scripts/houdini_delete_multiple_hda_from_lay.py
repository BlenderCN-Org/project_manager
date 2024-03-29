import sys

hip_file = sys.argv[-2]
hdas_to_remove = sys.argv[-1]
hdas_to_remove = hdas_to_remove.split("|")

hou.hipFile.load(hip_file, suppress_save_prompt=True, ignore_load_warnings=True)
for hda in hdas_to_remove:
    hda = hda.replace("\\", "/")
    hda_name = hda.replace("\\","/").split("/")[-1].split("_")[0]
    hda_node = hou.node("/obj/" + hda_name)
    hda_node.destroy()
    hou.hda.uninstallFile(hda)
    hou.hda.uninstallFile("Embedded")


hou.hipFile.save(hip_file)
