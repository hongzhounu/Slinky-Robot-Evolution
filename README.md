# **Convergent Evolution of Slinky Robots**

## **Introduction**

### **Slinky Bots**
- **Segment Properties:**  
  - **Width:** Defined for each segment.  
  - **Height:** Base height per segment.  
  - **Number of Segments:** Determines overall structure.  
- **Height Function:**  
  - Given a segment number \( x \), how tall is it?  
  - \( f(x) + \) base height  

![Slinky Bot Visualization](https://github.com/user-attachments/assets/72eabdbb-ce45-4a6c-8549-63dd224f95c0)  

### **Observation**  
- Independent experiments using slinky bots consistently result in a **ramp-up shape**, suggesting **convergent evolution** in their development.  

### **Research Question**  
- Does increasing the number of genes affect the rate of convergence?  
- This can be explored by using **higher-order polynomial height functions**:  
  - **Quadratic function**: \( ax^2 + bx + c \) → **3 genes**  
  - **Cubic function**: \( ax^3 + bx^2 + cx + d \) → **4 genes**  
  - **Quartic function**: \( ax^4 + bx^3 + cx^2 + dx + e \) → **5 genes**  

---

## **Methodology**

### **The Simulation**  
For each **lineage** (quadratic, cubic, quartic):  
- **15 generations**  
- **10 individuals per generation**  
- **Aging effect**: Actuation force in springs **decreases** over time  

---

## **Results**  
- By **generation 5**, all three slinky bot lineages have **converged** to the ramp-up slinky configuration.  

![Results - Generation 5](https://github.com/user-attachments/assets/88ff1afb-4d60-4924-babb-a2c53baf6019)  
![Evolutionary Trend](https://github.com/user-attachments/assets/b7bff6ef-cb64-48db-ae0d-cb0678930067)  

---

## **Limitations**  
- **Number of trials:** Limited dataset size.  
- **Computation time:** More trials and generations could improve robustness.  
- **Fitness space constraints:** The limited functional range of slinky bots may lead to rapid convergence. Expanding robot capabilities could yield more diverse evolutionary outcomes.

---

## **Implementation**

The simulation is executed using `sim.py`, which automates the evolutionary process by evaluating multiple individuals per generation and selecting the fittest candidates.

### **Generating Randomized Gene Samples**
Each individual is initialized with five gene values \( A, B, C, D, E \), sampled from a normal distribution centered at 0. The `generate_samples` function introduces small perturbations to simulate genetic variation:

```python
import numpy as np

def generate_samples(x, n):
    scale = 0.000005
    return np.random.normal(loc=x, scale=scale, size=n)
```

### **Setting Simulation Hyperparameters**
Hyperparameters for the simulations are set manually. In particular, the GENERATION and population_size variables. The slinky bot constants involving segment parameters are also set here.
```python
GENERATION = # Set Generation number
population_size = # Set Population size
center_A, center_B, center_C, center_D, center_E = 0,0,0,0,0 # Default to 0
A = generate_samples(center_A, population_size)
B = generate_samples(center_B, population_size)
C = generate_samples(center_C, population_size)
D = generate_samples(center_D, population_size)
E = generate_samples(center_E, population_size)

segHeight, segWidth, numSeg = 0.08, 0.04, 8
```

### **Running the Simulation**
Simulations are ran in parallel, and results are parsed from the output of child processes executing the `rigid_body.py` script on the generated gene samples.

```python
process = [None] * population_size
outputs = [None] * population_size
errors = [None] * population_size

# Start processes
print("Initializing Processes")
for i in range(population_size):
    print(f"     process {i+1} running...")
    cmd = [sys.executable, 
           "rigid_body.py", 
           "train",
           str(segHeight),
           str(segWidth),
           str(numSeg),
           str(A[i]),
           str(B[i]),
           str(C[i]),
           str(D[i]),
           str(E[i])]
    process[i] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

for i in range(population_size):
    outputs[i], errors[i] = process[i].communicate()

print("")

print(f"Process     output")
for i in range(population_size):
    print(f"{i}         {outputs[i].split("\n")[-2]}")

if DEBUG:
    for i in range(population_size):
        print({errors[i]})

def parse(output):
    result = 100
    try:
        result = float(output.split("\n")[-2])
    except:
        print('Individual has invalid parameters')
    return result
```

### **Saving the Results**
Results per generation are saved in csv format sorted from best performing to worst performing.
```python
import os

to_dir = ""  # Directory for storing results
os.makedirs(to_dir, exist_ok=True)
file_path = f"{to_dir}/gen_{GENERATION}.csv"

ranks = np.arange(1, len(losses_sorted) + 1)
data = np.column_stack((ranks, losses_sorted, A_sorted, B_sorted, C_sorted, D_sorted, E_sorted))

np.savetxt(file_path, data, delimiter=",", fmt="%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f", 
           header="rank,loss,A,B,C,D,E", comments="")
```

Examples results:
```mathematica
rank,loss,A,B,C,D,E
1,0.00345,0.00123,0.00087,0.00214,0.00198,0.00076
2,0.00412,0.00145,0.00099,0.00234,0.00210,0.00082
...
```
---
### **Parsing Arguments from Parent Process**  
The `rigid_body.py` script receives arguments from `sim.py`, which initializes multiple simulations in parallel. These arguments define key parameters for the rigid-body simulation:

```python
SH = float(sys.argv[2])  # Segment Height
SW = float(sys.argv[3])  # Segment Width
NS = int(sys.argv[4])    # Number of Segments
A = float(sys.argv[5])   # Gene A
B = float(sys.argv[6])   # Gene B
C = float(sys.argv[7])   # Gene C
D = float(sys.argv[8])   # Gene D
E = float(sys.argv[9])   # Gene E
```
---
### **The Slinky Bot**
The Slinky Topography class is the blue print for a slinky bot. Parameters are set at initialization. The `slinkyRobot()` function returns objects and springs compatible with the difftaichi rigid body simulation format.
```python
class SlinkyTopography:
    def __init__(self, segheight, segwidth, numsegs, heightfunc=ConstFunction(A)):
        self.objects=[]
        self.springs=[]
        self.segheight=segheight
        self.segwidth=segwidth
        self.heightFunc=heightfunc
        self.numsegs=numsegs
    
    def add_object(self, x, halfsize, rotation=0):
        self.objects.append([x, halfsize, rotation])
        return len(self.objects) - 1

    # actuation 0.0 will be translated into default actuation
    def add_spring(self, a, b, offset_a, offset_b, length, stiffness, actuation=0.0):
        self.springs.append([a, b, offset_a, offset_b, length, stiffness, actuation])
    
    def slinkyRobot(self):
        numsegs = self.numsegs
        heightfunc = self.heightFunc
        segwidth = self.segwidth
        segheight = self.segheight
    
        # Hinge spring parameters
        stiffness = 50  # Stiffness of the hinge
        flexy = 0.5
        
        floorY = 0.1
        wallX = 0.1
        baseY = (heightfunc.run(0) + segheight) / 2 + floorY
        baseX = segwidth / 2 + wallX
        
        body = self.add_object([baseX, baseY], [0.01, (heightfunc.run(0) + segheight) / 2])
        prev = body
            
        for i in range(1, numsegs + 1):
            prevHeight = segheight + heightfunc.run(i-1)
            currHeight = segheight + heightfunc.run(i)
            connX = (i - 0.5) * segwidth + wallX
            spineX = i * segwidth + wallX
            
            rot = math.atan2(segwidth, prevHeight)
            connLength = math.sqrt(segwidth ** 2 + prevHeight ** 2)
            conn = self.add_object([connX, prevHeight/2 + floorY], [0.01, connLength/2], rotation=rot)

            spine = self.add_object([spineX, currHeight/2 + floorY], [0.01, currHeight/2])
            
            self.add_spring(prev, conn, [0, prevHeight/2 - 0.01], [0, connLength/2 - 0.01], -1, stiffness)
            
            self.add_spring(conn, spine, [0, -1 * connLength/2 + 0.01], [0, -1 * currHeight/2 + 0.01], -1, stiffness)
            
            self.add_spring(prev, spine, [0, -1 * prevHeight/2 + 0.01], [0, -1 * currHeight/2 + 0.01], 
                length=segwidth,
                stiffness=flexy)
            
            springLength = math.sqrt(segwidth ** 2 + (currHeight - prevHeight) ** 2)
            self.add_spring(prev, spine, [0, prevHeight/2 - 0.01], [0, currHeight/2 - 0.01], 
                length=springLength,
                stiffness=flexy)
            
            prev = spine
        
        return self.objects, self.springs, body
```

### **Height Functions for Slinky Shape Generation**  
The simulation uses parametric height functions to define the shape and movement of the slinky robot. These functions map an input value \( x \) to a height value, allowing for different structural variations.

#### **Constant Function**
```python
class ConstFunction:
    def __init__(self, a=0):
        self.a = 0
    
    def run(self, x):
        return self.a
```

#### **Quadratic Function**
```python
class QuadraticFunction:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
        
    def run(self, x):
        return self.a * (x ** 2) + self.b * x + self.c
```

#### **Cubic Function**
```python
class CubicFunction:
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        
    def run(self, x):
        return self.a * (x ** 3) + self.b * (x ** 2) + self.c * x + self.d
```

#### **Quartic Function**
```python
class QuarticFunction:
    def __init__(self, a, b, c, d, e):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        
    def run(self, x):
        return self.a * (x ** 4) + self.b * (x ** 3) + self.c * (x ** 2) + self.d * x + self.e
```
