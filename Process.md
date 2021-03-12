# Steps

- Add repo
	- ```ck add repo ck-compiler-gym```

- Add CompilerGym package for automatic installation (copying from similar entry)
	- ```ck cp soft:lib.python.pandas```
	- ```ck cp package:lib-python-pandas```
	- edit specific metadata in soft and package .cm/meta.json files

- Add program entry
	- ```ck add ck-compiler-gym:module:cg-program```
	- ```ck cp program:template-hello-world-c ck-compiler-gym:cg-program:```

- Add actions to cg-program module

