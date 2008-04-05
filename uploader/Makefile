all: devel

FILES=Rubicon_osx.py MainMenu.nib setup.py fb.py dir_browser.py upload.py itunes.py

devel: $(FILES)
	python setup.py py2app -A

release: $(FILES)
	python setup.py py2app
	./mkdmg dist Rubicon
	mv dist.dmg Rubicon.dmg

clean:
	rm -rf build dist
	rm Rubicon.dmg
