# calibration

Implement coordinate alignment algorithm used in paper `Wang, Yan, et al. "Sensing vehicle dynamics for determining driver phone use." Proceeding of the 11th annual international conference on Mobile systems, applications, and services. ACM, 2013.`

- [x] Derive **k**
  - i.e. get the unit vector of gravity acceleration
- [ ] Derive **j**
  - [x] Remove the gravity component obtained from last step
  - [ ] Use gyroscope to find the parts that the vehicle is driving straight 
  - [ ] Among the parts got from previous step, pick up the ones that the vehicle decelerates
- [ ] Obtain **i**
  - i.e. **i** = **j** X **k**
  
