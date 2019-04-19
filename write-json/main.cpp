
#include "WriteRcrJson.h"

int main()
{
  WriteRcrJson rcrJson; 

  std::string fileName = "rcrt.json";

  rcrJson.Init(fileName);

  rcrJson.StartOutletData();

  auto NumData = 2;
  auto FaceName = "cap_RPA1";
  auto Rp = 2710.0836265;
  auto C = 0.000007529278617;
  auto Rd = 15147.2313752;
  std::vector<float> time = {0.0, 0.588};
  std::vector<float> pressure = {0.0, 0.0};
  rcrJson.AddOutletData(NumData, FaceName, Rp, C, Rd, time, pressure, false);

  FaceName = "cap_RPA1_1";
  Rp = 1708.8495911; 
  C = 0.000011940766938; 
  Rd = 14773.2161714; 
  rcrJson.AddOutletData(NumData, FaceName, Rp, C, Rd, time, pressure, true);

  rcrJson.EndOutletData();

  return 0;
}


