#!/usr/bin/env python
# coding=utf-8

import os

class Asset(object):
    def __init__(self, main, id=0, project_name="", sequence_name="", shot_number="", asset_name="", asset_path="", asset_extension="", asset_type="", asset_version="", asset_tags=[], asset_dependency="", last_access="", creator=""):
        self.main = main
        self.id = id
        self.project = project_name
        try:
            self.project_shortname = self.main.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        except:
            self.project_shortname = ""
        try:
            self.project_path = self.main.cursor.execute('''SELECT project_path FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        except:
            self.project_path = ""
        self.sequence = sequence_name
        self.shot = shot_number
        self.name = asset_name
        self.type = asset_type
        self.extension = asset_extension
        self.version = asset_version
        if not asset_tags == None and len(asset_tags) > 0:
            self.tags = asset_tags.split(",")
        else:
            self.tags = []
        self.dependency = asset_dependency
        self.last_access = last_access
        self.creator = creator
        self.nbr_of_comments = self.main.cursor.execute('''SELECT Count(*) FROM comments WHERE comment_id=? AND comment_type=?''', (self.id, self.type,)).fetchone()[0]
        self.path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname, self.sequence,
                                                                    self.shot, self.type, self.name, self.version, self.extension)
        self.full_path = self.project_path + self.path

    def print_asset(self):
        print "| -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} |".format(self.id, self.project, self.sequence, self.shot, self.name, self.path, self.type, self.version, self.tags, self.dependency, self.last_access, self.creator)

    def update_asset_path(self):
        new_path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname, self.sequence, self.shot, self.type, self.name, self.version, self.extension)
        if int(self.version) > 1:  # If version is higher than 1, go back to level 1 and increment until there is no existing file with version
            self.change_version_if_asset_already_exists(str(1).zfill(2))
            new_path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname, self.sequence, self.shot, self.type, self.name, self.version, self.extension)
            while os.path.isfile(self.project_path + new_path): # Increment version until there is no file already existing with same version
                self.change_version_if_asset_already_exists(str(int(self.version) + 1).zfill(2))
                new_path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname, self.sequence, self.shot, self.type, self.name, self.version, self.extension)

        elif int(self.version) == 1: # If asset is at version 1, increment its version until there is no file already existing with same version
            while os.path.isfile(self.project_path + new_path):
                self.change_version_if_asset_already_exists(str(int(self.version) + 1).zfill(2))
                new_path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname, self.sequence, self.shot, self.type, self.name, self.version, self.extension)

        os.rename(self.full_path, self.project_path + new_path)
        if self.type == "ref":
            os.rename(self.full_path.replace(".jpg", "_thumb.jpg"), self.project_path + new_path.replace(".jpg", "_thumb.jpg"))
        self.main.cursor.execute('''UPDATE assets SET asset_path=? WHERE asset_id=?''', (new_path, self.id,))
        self.main.db.commit()
        self.full_path = self.project_path + new_path
        self.path = new_path

    def add_asset_to_db(self):
        while os.path.isfile(self.project_path + self.path):
            if self.version != "out":
                self.change_version_if_asset_already_exists(str(int(self.version) + 1).zfill(2))
                self.path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname, self.sequence, self.shot, self.type, self.name, self.version, self.extension)
        self.full_path = self.project_path + self.path
        self.main.cursor.execute('''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_extension, asset_type, asset_version, asset_tags, asset_dependency, last_access, creator) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (self.project, self.sequence, self.shot, self.name, self.path, self.extension, self.type, self.version, ",".join(self.tags), self.dependency, self.last_access, self.creator,))
        self.id = self.main.cursor.lastrowid
        self.main.db.commit()

    def remove_asset_from_db(self):
        self.main.cursor.execute('''DELETE FROM assets WHERE asset_id=?''', (self.id,))
        self.main.db.commit()

    def change_version_if_asset_already_exists(self, new_version):
        self.main.cursor.execute('''UPDATE assets SET asset_version=? WHERE asset_id=?''', (new_version, self.id,))
        self.main.db.commit()
        self.version = new_version

    def change_name(self, new_name):
        if self.name == new_name: return
        self.main.cursor.execute('''UPDATE assets SET asset_name=? WHERE asset_id=?''', (new_name, self.id,))
        self.main.db.commit()
        self.name = new_name
        self.update_asset_path()

    def change_sequence(self, new_sequence):
        if self.sequence == new_sequence: return
        self.main.cursor.execute('''UPDATE assets SET sequence_name=? WHERE asset_id=?''', (new_sequence, self.id,))
        self.main.db.commit()
        self.sequence = new_sequence
        self.update_asset_path()

    def change_shot(self, new_shot):
        if self.shot == new_shot: return
        self.main.cursor.execute('''UPDATE assets SET shot_number=? WHERE asset_id=?''', (new_shot, self.id,))
        self.main.db.commit()
        self.shot = new_shot
        self.update_asset_path()

    def change_version(self, new_version):
        if self.version == new_version: return
        self.main.cursor.execute('''UPDATE assets SET asset_version=? WHERE asset_id=?''', (new_version, self.id,))
        self.main.db.commit()
        self.version = new_version
        self.update_asset_path()

    def change_dependency(self, new_dependency):
        self.main.cursor.execute('''UPDATE assets SET asset_dependency=? WHERE asset_id=?''', (new_dependency, self.id,))
        self.main.db.commit()
        self.dependency = new_dependency

    def add_comment(self, author, comment, time, type):
        self.main.cursor.execute('''INSERT INTO comments(comment_id, comment_author, comment_text, comment_time, comment_type) VALUES(?,?,?,?,?)''', (self.id, author, comment, time, type))
        self.main.db.commit()
        self.nbr_of_comments = self.main.cursor.execute('''SELECT Count(*) FROM comments WHERE comment_id=? AND comment_type=?''', (self.id, self.type,)).fetchone()[0]

    def remove_comment(self, author, comment, time):
        self.main.cursor.execute('''DELETE FROM comments WHERE comment_author=? AND comment_text=? AND comment_time=?''', (author, comment, time))
        self.main.db.commit()
        self.nbr_of_comments = self.main.cursor.execute('''SELECT Count(*) FROM comments WHERE comment_id=? AND comment_type=?''', (self.id, self.type,)).fetchone()[0]

    def edit_comment(self, new_comment, comment_author, old_comment, comment_time):
        self.main.cursor.execute('''UPDATE comments SET comment_text=? WHERE comment_author=? AND comment_text=? AND comment_time=?''', (new_comment, comment_author, old_comment, comment_time,))
        self.main.db.commit()

    def add_tags(self, tags):
        self.tags.extend(tags)
        self.tags = list(set(self.tags))
        self.main.cursor.execute('''UPDATE assets SET asset_tags=? WHERE asset_id=?''', (",".join(self.tags), self.id,))
        self.main.db.commit()

    def remove_tags(self, tags):
        self.tags = list(set(self.tags) - set(tags))
        self.main.cursor.execute('''UPDATE assets SET asset_tags=? WHERE asset_id=?''', (",".join(self.tags), self.id,))
        self.main.db.commit()

    def get_infos_from_id(self):
        asset = self.main.cursor.execute('''SELECT * FROM assets WHERE asset_id=?''', (self.id,)).fetchone()
        project_name = asset[1]
        sequence_name = asset[2]
        shot_number = asset[3]
        asset_name = asset[4]
        asset_extension = asset[6]
        asset_type = asset[7]
        asset_version = asset[8]
        asset_tags = asset[9]
        asset_dependency = asset[10]
        last_access = asset[11]
        creator = asset[12]

        self.project = project_name
        self.project_shortname = self.main.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        self.project_path = self.main.cursor.execute('''SELECT project_path FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        self.sequence = sequence_name
        self.shot = shot_number
        self.name = asset_name
        self.type = asset_type
        self.extension = asset_extension
        self.version = asset_version
        if asset_tags != None:
            self.tags = asset_tags.split(",")
        else:
            self.tags = []
        self.dependency = asset_dependency
        self.last_access = last_access
        self.creator = creator
        self.path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname,
                                                                        self.sequence,
                                                                        self.shot, self.type, self.name, self.version,
                                                                        self.extension)
        self.full_path = self.project_path + self.path


