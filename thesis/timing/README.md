# Timing

This package holds the code that was used to gather the timing data for the thesis about lpm. The `*.dat` files hold the raw data that was produced when running `main.py` with n=30, which in turn executes the other `m_*.py` files in this package. Each `m_*.py` uses pythons `cProfile` to run the function to time along with some setUp and cleanUp.

## Usage
### Time functions
`python -m thesis.timing.main 30` or any number of repetitions instead of 30.
You can also time only one function by running the corresponding `m_*.py`.

Please note that we included the `.dat` files that the data shown in the thesis is based on in this folder. If you want to time them yourself, the location of the resulting `.dat` files depends on where you execute the timing script from. You might want to delete the `.dat` files that were included in this repository first to avoid confusion.

### Visualize data
Running `main.py` generates some `.dat` files. To visualize them, we recommend using [`snakeviz`](https://pypi.org/project/snakeviz/). After installing it, you can run the visualization by executing `snakeviz <file>.dat`, where `<file>` is the name of the `.dat` file to visualize.

### Interpret data
The visualization holds execution times for the whole program, but lpm's function we are interested in is only a subset of the whole program. To get a visualization that only shows lpm's timed function and methods it called, click the bar that says `m_build.py:45(_main)` (`m_build` and `45` will differ based on the `.dat` file you're viewing)

In the table below the visualization, the times measured for each function are shown. `cumtime` shows the cumulative time spent in that function (including functions it called). To get the average time that function took to execute, divide `cumtime` by the number of repetitions `n` you passed to `thesis.timing.main`.