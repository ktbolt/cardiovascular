
#include "Mesh.h"

//---------
// HasData
//---------
// Check if the mesh has the data for the given name.
//
bool Mesh::HasData(const std::string& name)
{
    return m_PointDataNames.count(name) != 0;
}

