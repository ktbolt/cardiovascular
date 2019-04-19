
#include "WriteJson.h"


//-----------
// AddIndent
//-----------
void WriteJson::AddIndent(const int n)
{
  m_IndentSize += n;
  m_Indent = std::string(m_IndentSize, ' ' );
}

//-------------
// OpenBracket
//-------------
void WriteJson::OpenBracket()
{
   m_OutFile << m_Indent << wj.leftBracket << std::endl;
   AddIndent(3);
}

//--------------
// CloseBracket
//--------------
void WriteJson::CloseBracket(const std::string delim)
{
   AddIndent(-3);
   m_OutFile << m_Indent << wj.rightBracket << delim << std::endl;
}

//-----------
// OpenBrace
//-----------
void WriteJson::OpenBrace()
{
   m_OutFile << m_Indent << wj.leftBrace << std::endl;
   AddIndent(3);
}

//------------
// CloseBrace
//------------
void WriteJson::CloseBrace(const std::string delim)
{
   AddIndent(-3);
   m_OutFile << m_Indent << wj.rightBrace << delim << std::endl;
}

//-------
// Quote
//-------
std::string WriteJson::Quote(const std::string name)
{
    if (name.size() == 0) {
        return "";
    }

    return wj.quote + name + wj.quote;
}

//---------
// AddPair
//---------
//
void WriteJson::AddPair(const std::string name, const std::string value, const std::string sep, const bool addQuotes)
{
  std::string writeName, writeValue;

  if (addQuotes) {
      writeValue = Quote(value);
  } else {
      writeValue = value;
  }

  m_OutFile << m_Indent << Quote(name) << wj.sp << wj.colon << wj.sp << writeValue << sep << std::endl;
}

void WriteJson::AddPair(const std::string name, const float value, const std::string sep)
{
  AddPair(name, std::to_string(value), sep, false);
}

void WriteJson::AddPair(const std::string name, const int value, const std::string sep)
{
  AddPair(name, std::to_string(value), sep, addQuotes, false);
}

void WriteJson::AddPair(const std::string name, const std::vector<float>& values, const std::string sep)
{
  std::stringstream ss;
  ss << wj.leftBracket;
  auto begin = values.begin();
  while (true) { 
      ss << *begin++;
      if (begin == values.end()) {
          break;
      }
      ss << wj.comma;
  }
  ss << wj.rightBracket;

  AddPair(name, ss.str(), sep, false);
}




