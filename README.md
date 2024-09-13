# OMERO.openlink  <img src="/images/icon.png?raw=true" width="70" height="70">   

An OMERO.web plugin that creates openly accessible links (URLS for raw files) to your data in OMERO and a batch file to download the data with 'curl'.


## Main application:
* Make internal data for a publication available to reviewers in advance via a URL
* Bundle data of different groups/projects/datasets together
* Fast download of large data
* Enable external collaborators to easily access selected data via URL


## Example: 
**Provide data used in a publication**

Winkelmann, H., Richter, C. P., Eising, J., Piehler, J., & Kurre, R. (2024). Correlative single-molecule and structured illumination microscopy of fast dynamics at the plasma membrane. Nat. Commun., 15(5813), 1–19. [doi: 10.1038/s41467-024-49876-9](https://doi.org/10.1038/s41467-024-49876-9)

[OpenLink of publication data](https://omero-data.cellnanos.uos.de/pub_Winkelmann_et_al_2024_NatCommun/)
## Functionality:

<img src="/images/OpenLink.png?raw=true" height="450" > 

#### OMERO.openlink is composed of two components:

***Create_OpenLink.py*** (generation)
A server side script that generates soft links to your data and creates a **curl** file for batch download of this data.
You can share only your own data or the data of a non-private group if you are the owner of this group (the owner of the data will be informed by mail).


<img src="/images/scriptGUI.png?raw=true" height="450" >  


NOTE:
If you prefer another download manager, you can change the generated commands in the Python script.

***omero-openlink*** (visualization)
An OMERO.web plugin that lists the links to generated areas of softlinks via the nginx server. Provides the corresponding **curl** command to start the download in a shell. With the plugin the areas can also be deleted via OMERO.web.


<img src="/images/plugin.png?raw=true" width="100%" >  


## Requirements:
- OMERO.web 5.6.0 or newer
- nginx server configurations




## License

OMERO.openlink is released under the AGPL.
Any additional material in this repository (images, presentations, etc.) is available for use with attribution under the Creative Commons Attribution 4.0 International (CC BY 4.0) license.








