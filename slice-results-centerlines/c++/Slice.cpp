
#include <iostream>
#include <string>

#include "Slice.h"

Slice::Slice(const int index, const std::string dataName, double pos[3])
{
  m_CenterlineIndex = index;
  m_DataName = dataName;
  std::copy(pos, pos+3, m_CenterlinePosition);
}

