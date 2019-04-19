
#include "WriteJson.h"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <ostream>
#include <sstream>
#include <string>
#include <vector>

class WriteRcrJson : public WriteJson
{
  public:
      ~WriteRcrJson(){};
      std::string fileName;

      void Init(const std::string fileName);
      void StartOutletData();
      void EndOutletData();
      void AddOutletData(const int NumData, const std::string FaceName, const float Rp, const float C, const float Rd, 
                         const std::vector<float>& time, const std::vector<float>& pressure, bool last = false);

      class WriteRcrJsonElements
      {
        public:
          std::string description = "description";
          std::string format = "format";
          std::string MaxNumTimePoints = "MaxNumTimePoints";
          std::string OutletData = "OutletData";
          std::string NumData = "NumData";
          std::string FaceName = "FaceName";
          std::string Rp = "Rp";
          std::string C = "C";
          std::string Rd = "Rd";
          std::string time = "time";
          std::string pressure = "pressure";
          std::string type = "type";
      };

  private:
      WriteJsonElements wj;
      //WriteJson wjs;
      WriteRcrJsonElements relem;

      void AddDescription();
};

