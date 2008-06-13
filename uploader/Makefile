all: devel

FILES=Harmonize_osx.py MainMenu.nib setup.py fb.py dir_browser.py upload.py itunes.py rate_limit.py

devel: $(FILES)
	python setup.py py2app -A

release: $(FILES)
	python setup.py py2app
	./mkdmg dist Harmonize
	mv dist.dmg Harmonize.dmg

publish: release
	scp Harmonize.dmg harmonize.fm:/var/opt/uploaders

clean:
	rm -rf build dist
	rm Harmonize.dmg
