[app]
package.name = guardseg
package.domain = org.supervisore
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
android.permissions = INTERNET
android.api = 33
android.sdk_path = 
android.ndk_path = 
requirements = python3,kivy==2.1.0,kivymd==1.2.0,pillow,sqlite3
title = Supervisor de Vigilantes
android.archs = arm64-v8a, armeabi-v7a

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#
osx.python_version = 3
osx.kivy_version = 2.1.0

#
# Android specific
#
fullscreen = 0
android.minapi = 21
android.sdk = 31
android.ndk = 21e
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (bool) If True, then skip trying to update the Android sdk
#android.skip_update = False

# (bool) If True, then automatically accept SDK license
#android.accept_sdk_license = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
#android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Java .jar files to add to the libs
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) Android AAR archives to add
#android.add_aars =

# (list) Gradle dependencies to add
#android.gradle_dependencies =

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

#
# Python for android (p4a) specific
#
#p4a.url =
#p4a.fork = kivy
#p4a.branch = master
#p4a.source_dir =
#p4a.local_recipes =
#p4a.hook =
#p4a.bootstrap = sdl2
#p4a.port =
#p4a.setup_py = false

#
# iOS specific
#
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 1
#build_dir = ./.buildozer
#bin_dir = ./bin
