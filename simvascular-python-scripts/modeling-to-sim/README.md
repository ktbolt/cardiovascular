
This script is an example of how to prepare a model for simulation. It uses two models as examples
    1) cylinder.vtp
    2) demo.vtp

Running the **model-to-sim.py** script 

  1) Reads in closed surface from a .vtp file representing solid model. 

     a) Computes the solid model boundary faces 

     b) Writes the new solid model to the **model** directory.


  2) Generates a finite element mesh from the model

     a) Reads in the solid model created in 1)

     b) Generates the finite element mesh

     c) Extracts mesh faces and the complete surface mesh

     d) Writes meshes to the **mesh** directory


  3) Generates the mesh and .svpre files needed to run a simulation using svsolver. 

     The directory structure used by svsolver is already created. All files are
     written to the **MODEL_NAME-simulation** directory, where MODEL_NAME = cylinder or demo.

     a) Copy volume and surface meshes MODEL_NAME-simulation/mesh-complete

     b) Copy mesh wall to MODEL_NAME-simulation/mesh-complete

     c) Copy mesh faces to MODEL_NAME-simulation/mesh-complete/mesh-surfaces

     d) Generate .svpre file 


  4) Run a simulation 

     A solver.inp file is already created.

     a) cd **MODEL_NAME-simulation** directory

     b) svpre MODEL_NAME.svpre

     c) mpiexec -np 4 svsolver solver.inp


