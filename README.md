# FreeCAD Frame Creator:

## Installation:

```bash
cd ~/.FreeCAD
mkdir Macro
wget https://github.com/fivethreeo/FreeCAD-Steel_Frame/archive/master.zip
unzip master.zip
mv FreeCAD-Steel_Frame-master/* .
rm -rf FreeCAD-Steel_Frame-master
```

## Operating Instruccions:

To choose the steel Gauge, type any gauge you want, i.e.  10, 14 or 22 etc.. If you want
a custom thickness, then set the gauge to 0 and proceed to change the thickness 
to your custom value.

Windows are defined by a tuple: 
(x position,z position,  window x size, window z size)
the x position and z position should point to the lower left corner
of the window. For now, these tuples have to be specified in mm

For a reason I still don't understand, after modifying the windows property, 
you will need to manually recompute the active document for them to show
its the button that looks like a curved circular arrow.

If a you set a z position =0 then the program interprets it as a door.

FEM Switch, when set to True, the steel studs and tracks have the exact same width and
the object returned is one solid which is good for meshing and finite element analysis
otherwise the steel studs fit "inside" of the tracks and the object returned, is a 
compound of solids, this makes better sense for drawings and architecture work.


Enjoy.


