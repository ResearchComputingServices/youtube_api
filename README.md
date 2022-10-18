# YouTubeAPI WebApp Prototype

This project attempts to turn the YouTubeAPI python script (main branch) into a user friendly webapp
using Voila, Binder, and ipywidgets.

I am following the tutorial found here:

https://blog.finxter.com/how-to-create-an-interactive-web-application-using-jupyter-notebook/

and associated video:

https://www.youtube.com/watch?v=t8P6estGusQ


# Helpful commands

Encountered an error when trying to load modules in jupyter, this command fixed it

conda install google-auth google-auth-oauthlib

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The package zulu was required but I could not install it using conda so I found this work around:

1. Run conda create -n venv_name and conda activate venv_name, where venv_name is the name of your virtual environment.

2. Run conda install pip. This will install pip to your venv directory.

3. Find your anaconda directory, and find the actual venv folder. It should be somewhere like /anaconda/envs/venv_name/.

4. Install new packages by doing /anaconda/envs/venv_name/bin/pip install package_name.

