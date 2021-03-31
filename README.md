# todo

- turns out that benchmarks are independent of file system... this means that to use runtimes, I will have to call write_bitcode() which writes the state of the current benchmark to a bitcode file at the specified path. Once I have this bitcode file, I need to compile and run it with ck (either with program api or my own function to get linkers deps and paths). The env.step(action) applies transformation to this state of the program.

- Otherwise, could use ck to completely run and compile with llvm opt.
