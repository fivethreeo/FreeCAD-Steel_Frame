# FreeCAD Frame Creator

## Installation

```bash
cd ~/.FreeCAD
mkdir Macro
cd Macro
wget https://github.com/fivethreeo/FreeCAD-Steel_Frame/archive/master.zip
unzip master.zip
mv FreeCAD-Steel_Frame-master/* .
rm -rf FreeCAD-Steel_Frame-master
```

## Operating Instructions

In FreeCAD 0.19+ go to the `Macro > Macros` dropdown menu.  You will see the macro in the list.  

**Note**: An icon Steel_Frame.svg is included in case you want to assign
the macro to a button as it is covered in the FreeCAD documentation.

To choose the steel Gauge, type any gauge you want, i.e.  10, 14 or 22 etc..  
If you want a custom thickness, then set the gauge to 0 and proceed to change the thickness 
to your custom value.

Windows are defined by a tuple: 
(x position, z position, window x size, window z size)
the x position and z position should point to the lower left corner
of the window. For now, these tuples have to be specified in mm


If a you set a z position =0 then the program interprets it as a door.

FEM Switch, when set to True, the steel studs and tracks have the exact same width and
the object returned is one solid which is good for meshing and finite element analysis
otherwise the steel studs fit "inside" of the tracks and the object returned, is a 
compound of solids, this makes better sense for drawings and architecture work.

## Known Issues

For a reason I still don't understand, after modifying the windows property, 
you will need to manually recompute the active document for them to show.  
It's the button that looks like a curved circular arrow.

## Feedback

Please open a ticket in the github issue queue. There is also a [dedicated FreeCAD forum thread]()
for more in-depth discussion.  


Enjoy.