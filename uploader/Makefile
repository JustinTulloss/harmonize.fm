all: devel

FILES=Harmonize_osx.py MainMenu.nib setup.py fb.py dir_browser.py upload.py itunes.py rate_limit.py

test: test_win_upload.py Harmonize_osx.py osx_options.py osx_upload.py
	python setup.py py2app -A test

devel: $(FILES)
	python setup.py py2app -A

release: $(FILES)
	python setup.py py2app
	./mkdmg dist Harmonizer
	mv dist.dmg Harmonizer.dmg

publish: release
	scp Harmonizer.dmg harmonize.fm:/var/opt/uploaders

clean:
	rm -rf build dist
	rm Harmonizer.dmg
