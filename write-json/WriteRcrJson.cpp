
#include "WriteRcrJson.h"

//----------------
// AddDescription
//----------------
//
void WriteRcrJson::AddDescription()
{
   AddPair(relem.description, wj.empty, wj.empty); 
     OpenBrace(); 
     AddPair(relem.type, "RCR boundary condition file");
     AddPair(relem.format, wj.empty, wj.empty); 
       OpenBrace(); 
       AddPair(relem.MaxNumTimePoints, "maximum number of time points for the curves defined at each outlet"); 
       AddPair(relem.OutletData, wj.empty, wj.empty); 
         OpenBrace(); 
         AddPair(relem.NumData, "number of time points for the outlet");
         AddPair(relem.FaceName, "outlet face name");
         AddPair(relem.Rp, "proximal resistance");
         AddPair(relem.C, "compliance");
         AddPair(relem.Rd, "distal vessel resistance");
         AddPair(relem.time, "time series time values");
         AddPair(relem.pressure, "time series reference pressure, evolution in time of the reference pressure at the distal end of the RCR block", wj.empty);
         CloseBrace(); // OutletData
       CloseBrace(); // format
     CloseBrace(wj.comma); // description 
}

//------
// Init
//------
void WriteRcrJson::Init(const std::string fileName)
{
   m_OutFile.open(fileName);

   OpenBrace();

   AddDescription();
}

//-----------------
// StartOutletData
//-----------------
//
void WriteRcrJson::StartOutletData()
{
   AddPair(relem.MaxNumTimePoints, 2);
   AddPair(relem.OutletData, wj.empty, wj.empty); 
   OpenBracket();
}

//---------------
// EndOutletData
//---------------
//
void WriteRcrJson::EndOutletData()
{
   CloseBracket();
   CloseBrace();
}

//---------------
// AddOutletData
//---------------
//
void WriteRcrJson::AddOutletData(const int NumData, const std::string FaceName, const float Rp, const float C, const float Rd, 
                            const std::vector<float>& time, const std::vector<float>& pressure, bool last)
{
  OpenBrace();

  AddPair(relem.NumData, NumData); 
  AddPair(relem.FaceName, FaceName); 
  AddPair(relem.Rp, Rp); 
  AddPair(relem.C, C); 
  AddPair(relem.Rd, Rd); 
  AddPair(relem.time, time); 
  AddPair(relem.pressure, pressure, wj.empty); 

  if (last) {
      CloseBrace();
  } else {
      CloseBrace(wj.comma);
  }

}

