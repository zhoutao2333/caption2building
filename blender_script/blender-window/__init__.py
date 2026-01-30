# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "WinGenerator",
    "author" : "fff",
    "description" : "",
    "blender" : (2, 83, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy

class BlenderVersionError(Exception):
	pass

if bl_info['blender'] > bpy.app.version:
	raise BlenderVersionError(f"This addon requires Blender >= {bl_info['blender']}")


from . import prefs
from . import geoscene

IMPORT_OSM = True
IMPORT_XML = True
IMPORT_BUILDING = True
if IMPORT_OSM:
    from .operators import io_import_osm

if IMPORT_XML:
    from .operators import io_import_xml

if IMPORT_BUILDING:
    from .operators import io_import_building

import os, sys, tempfile
from datetime import datetime

def getAppData():
	home = os.path.expanduser('~')
	loc = os.path.join(home, '.bgis')
	if not os.path.exists(loc):
		os.mkdir(loc)
	return loc

APP_DATA = getAppData()

import logging
from logging.handlers import RotatingFileHandler
#temporary set log level, will be overriden reading addon prefs
#logsFormat = "%(levelname)s:%(name)s:%(lineno)d:%(message)s"
logsFormat = '{levelname}:{name}:{lineno}:{message}'
logsFileName = 'bgis.log'
try:
	#logsFilePath = os.path.join(os.path.dirname(__file__), logsFileName)
	logsFilePath = os.path.join(APP_DATA, logsFileName)
	#logging.basicConfig(level=logging.getLevelName('DEBUG'), format=logsFormat, style='{', filename=logsFilePath, filemode='w')
	logHandler = RotatingFileHandler(logsFilePath, mode='a', maxBytes=512000, backupCount=1)
except PermissionError:
	#logsFilePath = os.path.join(bpy.app.tempdir, logsFileName)
	logsFilePath = os.path.join(tempfile.gettempdir(), logsFileName)
	logHandler = RotatingFileHandler(logsFilePath, mode='a', maxBytes=512000, backupCount=1)
logHandler.setFormatter(logging.Formatter(logsFormat, style='{'))
logger = logging.getLogger(__name__)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)
logger.info('###### Starting new Blender session : {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

def _excepthook(exc_type, exc_value, exc_traceback):
	if 'BlenderGIS' in exc_traceback.tb_frame.f_code.co_filename:
		logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
	sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = _excepthook #warn, this is a global variable, can be overrided by another addon

####
'''
Workaround for `sys.excepthook` thread
https://stackoverflow.com/questions/1643327/sys-excepthook-and-threading
'''
import threading

init_original = threading.Thread.__init__

def init(self, *args, **kwargs):

	init_original(self, *args, **kwargs)
	run_original = self.run

	def run_with_except_hook(*args2, **kwargs2):
		try:
			run_original(*args2, **kwargs2)
		except Exception:
			sys.excepthook(*sys.exc_info())

	self.run = run_with_except_hook

threading.Thread.__init__ = init

####
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
	getattr(ssl, '_create_unverified_context', None)):
	ssl._create_default_https_context = ssl._create_unverified_context


# main panel
class Building_PT_MainPanel(bpy.types.Panel):
    bl_label = "Blender Window"

    # ui_type
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    bl_context = "objectmode"
    bl_category = "Windows Tools"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
 
        # import osm file button
        if IMPORT_OSM:
            col.operator("importgis.osm_file", text="Import OSM File")

        box = layout.box()
        col = box.column(align=True)
        if IMPORT_XML:
            col.operator("import.xml_file", text = "Import XML File")

        box = layout.box()
        col = box.column(align=True)
        if IMPORT_BUILDING:
            col.operator("import.xml_file2", text = "Import XML To Building")


classes = [
    Building_PT_MainPanel,
]


def register():
    for item in classes:
        bpy.utils.register_class(item)

    if IMPORT_OSM:
        io_import_osm.register()
    if IMPORT_XML:
        io_import_xml.register()
    if IMPORT_BUILDING:
        io_import_building.register()
    
    prefs.register()
    geoscene.register()

def unregister():
    for item in classes:
        bpy.utils.unregister_class(item)

    if IMPORT_OSM:
        io_import_osm.unregister()
    if IMPORT_XML:
        io_import_xml.unregister()
    if IMPORT_BUILDING:
        io_import_building.unregister()