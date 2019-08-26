
#include <iostream>
#include <string>
#include <vector>

#include "Graphics.h"
#include "Mesh.h"
#include "Slice.h"

#include <vtkCellLocator.h>
#include <vtkCutter.h>
#include <vtkPolyData.h>
#include <vtkSmartPointer.h>

#include "Centerlines.h"

#ifndef SURFACE_MESH_H 
#define SURFACE_MESH_H 

class SurfaceMesh : public Mesh {

  public:
    SurfaceMesh();
    void AddGeometry(Graphics& graphics);
    void FindData();
    vtkSmartPointer<vtkDoubleArray> GetDataArray(std::string name);
    vtkSmartPointer<vtkDataSet> GetMesh();
    vtkSmartPointer<vtkPolyData> GetPolyData();
    bool IsSurface();
    void ReadMesh(const std::string fileName);
    void SlicePlane(int index, int cellID, std::string dataName, double pos[3], double normal[3]);
    void UndoSlice();
    void WriteSlices();
    void CalculateCenterlinesRadii(Centerlines& centerlines);

  private:
    std::string m_MeshFileName;
    vtkSmartPointer<vtkPolyData> m_Polydata;
    vtkIdType m_NumPoints;
    vtkIdType m_NumPolys;
    vtkSmartPointer<vtkCellLocator> m_CellLocator;
    void Interpolate(std::string dataName, vtkPolyData* lines, Slice* slice);
    void SliceArea(vtkPolyData* lines, Slice* slice);
    vtkSmartPointer<vtkPolyData> GetSliceLines(vtkSmartPointer<vtkCutter> cutter, double pos[3]);
    std::vector<Slice*> m_Slices;

};

#endif

