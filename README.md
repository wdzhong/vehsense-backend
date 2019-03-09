# calibration

Implement coordinate alignment algorithm used in paper `Wang, Yan, et al. "Sensing vehicle dynamics for determining driver phone use." Proceeding of the 11th annual international conference on Mobile systems, applications, and services. ACM, 2013.`

## Requirements
- `Python 3.x`
- Packages: `numpy`, `pandas`, `matplotlib`, `statsmodels`

## Road Map
- [x] Derive **k**
  - [x] Retrieve the gravity acceleration applied to 3 axes one by one through [low pass filter](https://medium.com/datadriveninvestor/how-to-build-exponential-smoothing-models-using-python-simple-exponential-smoothing-holt-and-da371189e1a1)
  - [ ] Use different number of data will yield different result. Need to figure out how to get a more reliable result.
- [x] Derive **j**
  - [x] Remove the gravity component obtained from last step
  - [x] Get all the periods of car accelerating through OBD or GPS data.
  - [x] Check the acc readings within all the selected periods, and pick up the acc reading that is mostly orthogonal to the gravity component as **j**
    - [ ] Use gyroscope to fine tune **j**, i.e. check if the vehicle is driving straight in the selected periods
- [x] Obtain **i**
  - [x] Normalize **j** and **k** to unit vectors
  - [x] **i** = **j** X **k**, where `X` is [cross product](https://en.wikipedia.org/wiki/Cross_product). If **j** and **k** are accurate, then **i** should already be normalized to be an unit vector.
  - [x] Save `[i, j, k]` to file, i.e. `calibration_para.txt`
  
## Usage
To run
```Python
python calibration.py [-d data_folder] [-obd] [-o]
```
 - `-d`, `--data_path`: the path to the data. If not provided or the provided is invalid folder, then it will try to use `./data`.
 - `-obd`, `--require_obd`: default is `False`; If used, set value to `True`. If `True`, then folers without `obd` file will throw exception.
 - `-o`, `--overwrite`: default is `False`; If used, set value to `True`. If `True`, then existing `calibration_para.txt` files will be overwritten. Otherwise, folders with `calibration_para.txt` file will be ignored.
