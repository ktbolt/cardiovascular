
#include <iostream>
#include <string>

#include "Slice.h"

Slice::Slice(const int index, const int cellID, const std::string dataName, double pos[3])
{
  m_CenterlineIndex = index;
  m_CellID = cellID;
  m_DataName = dataName;
  std::copy(pos, pos+3, m_CenterlinePosition);
}

//---------------
// AddScalarData
//---------------
//
void Slice::AddScalarData(double value)
{
  //m_InterpolatedScalarData.push_back(value);
}

//---------------
// AddVectorData
//---------------
//
void Slice::AddVectorData(double values[3])
{
  //m_InterpolatedVectorData.push_back({values[0], values[1], values[2]});
}

//----------
// AddPoint
//----------
//
void Slice::AddPoint(double point[3])
{
  //m_InterpolationPoints.push_back({point[0], point[1], point[2]});
}

//-------
// Write
//-------
//
void Slice::Write(ofstream& file)
{
/*
  file << "area: " << this->area << std::endl;
  file << "centerline index: " << this->m_CenterlineIndex << std::endl;
  file << "centerline cell ID: " << this->m_CellID << std::endl;
  file << "centerline point: ";
    file << this->m_CenterlinePosition[0] << " ";
    file << this->m_CenterlinePosition[1] << "  ";
    file << this->m_CenterlinePosition[2] << std::endl;

  file << "points: " << std::endl;
  for (auto const& point : m_InterpolationPoints) {
    file << point[0] << " ";
    file << point[1] << "  ";
    file << point[2] << std::endl;
  }

  file << "data: " << std::endl;
  if (m_InterpolatedScalarData.size() != 0) { 
    for (auto const& value : m_InterpolatedScalarData) {
      file << value << std::endl;
    }
  } else if (m_InterpolatedVectorData.size() != 0) { 
    for (auto const& value : m_InterpolatedVectorData) {
      file << value[0] << " ";
      file << value[1] << "  ";
      file << value[2] << std::endl;
    }
  }
*/
}


