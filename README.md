Pour l'installation du module Bluetooth PyBluez :
Doc officielle : https://github.com/pybluez/pybluez/blob/master/docs/install.rst

	* Sur Linux : 
		sudo pip install pybluez

	* Sur Windows : 
		Installer SDK Windows 10 ! (cf doc officielle)
		Manière recommandée : 
			Installer python3
			python -m pip install --upgrade pip
			pip -v install pybluez

		Manière alternative : 
			git clone https://github.com/pybluez/pybluez
			cd pybluez
			python setup.py install
