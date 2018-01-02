FreeCAD Frame Creator:

==================================================================
Installation:
==================================================================
in FreeCAD 0.16 go to Macro-->Macros 
Hit the Create Button
Copy and paste the code from the file Steel_Frame_Creator.py
An icon Steel_Frame.svg is included in case you want to assing 
the macro to a button as it is covered in the FreeCAD documentation.

==================================================================
Operating Instruccions:
=================================================================

To choose the steel Gage, type any gage you want, i.e.  10, 14 or 22 etc.. If you want
a custom thickness, then set the gage to 0 and proceed to change the thickness 
to your custom value.

Windows are defined by a tuple: 
(x position,z position,  window x size, window z size)
the x position and z position should point to the lower left corner
of the window. For now, these tuples have to be specified in mm

For a reason I still don't understand, after modifying the windows property, 
you will need to manually recompute the active document for them to show
its the button that looks like a curved circular arrow.


If a you set a z position =0 then the program interprets it as a door.

The rest is pretty much self explanatory.

Enjoy.


