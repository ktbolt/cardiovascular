
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <ostream>
#include <sstream>
#include <string>
#include <vector>

//-----------
// WriteJson
//-----------
//
class WriteJson
{
  public:
      class WriteJsonElements
      {
        public:
          std::string leftBrace = "{";
          std::string rightBrace = "}";
          std::string leftBracket = "[";
          std::string rightBracket = "]";
          std::string colon = ":";
          std::string comma = ",";
          std::string quote = "\"";
          std::string sp = " ";
          std::string empty = "";
      };

      ~WriteJson(){};

      std::ofstream m_OutFile;
      std::string m_Indent = "";
      int m_IndentSize = 1;
      WriteJsonElements wj;

      void AddPair(const std::string name, const std::string value, const std::string sep=",", const bool addQuotes=true);
      void AddPair(const std::string name, const int value, const std::string sep = ",");
      void AddPair(const std::string name, const float value, const std::string sep = ",");
      void AddPair(const std::string name, const std::vector<float>&, const std::string sep = ",");
      std::string Quote(const std::string name);
      void OpenBrace();
      void CloseBrace(const std::string delim = "");
      void OpenBracket();
      void CloseBracket(const std::string delim = "");
      void AddIndent(const int n);
};

