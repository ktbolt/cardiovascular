
// This program is used to create average flow files from converted simulation results fileis (.vtp or .vtu).
//
// The program creates the following files:
//
//   all_results-pressures.txt
//   results-flows.txt
//   allll_results-averages.txt"
//   all_results-averages-from_cm-to-mmHg-L_per_min.txt";
//
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>
#include <sys/types.h>
#include <dirent.h>

#include <vtkAbstractArray.h>
#include <vtkCellData.h>
#include <vtkDataArray.h>
#include <vtkDoubleArray.h>
#include <vtkPointData.h>
#include <vtkPolyData.h>
#include <vtkSmartPointer.h>
#include <vtkUnstructuredGrid.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkXMLUnstructuredGridReader.h>

#define vtkFloatingPointType double 

#include "vtkSVIntegrateAttributes.h"
#include "vtkSVIntegrateFlowThroughSurface.h"

// Enumeration of the different options used by the program.
enum class OptionType 
{
  MeshDirectory, 
  OutputDirectory, 
  ResultsDirectory,
  SingleFile, 
  SkipWalls,
  Units
};

// Valid values for units option.
std::set<std::string> Units = {"cm", "mm"};

// Valid values for SingleFile and SkipWalls options.
std::set<std::string> YesNo = {"yes", "no"};


//----------------------------
// sys_geom_IntegrateSurface2
//----------------------------
bool sys_geom_IntegrateSurface2( vtkPolyData *pd, int tensorType, double *q, double *area )
{

  int i,j;
//  vtkPolyData *pd;
  vtkDataArray *scalars = NULL;
  vtkDataArray *vectors = NULL;
  int numPts, numPolys;
  vtkFloatingPointType *pts;
  vtkIdType *polys;
  double qflow;
  double qtotal = 0.0;
  double areatotal = 0.0;
  *q = qtotal;
  *area = areatotal;

  // pd = src->GetVtkPolyData();

  if (tensorType < 0 || tensorType > 1) {
      fprintf(stderr,"ERROR:  Invalid tensorType (%i).\n",tensorType);
      return false;
  }
  if (tensorType == 0) {
    scalars = pd->GetPointData()->GetScalars();
    if (scalars == NULL) {
        fprintf(stderr,"ERROR: No scalars!\n");
        return false;
    }
  } else {
    vectors = pd->GetPointData()->GetVectors();
    if (vectors == NULL) {
        fprintf(stderr,"ERROR: No vectors!\n");
        return false;
    }
  }

  // make sure we have normals on pd
  // pd = src->GetVtkPolyData();

  vtkUnstructuredGrid* answer;

  if (tensorType == 1) {
    vtkSVIntegrateFlowThroughSurface* integrator = vtkSVIntegrateFlowThroughSurface::New();
    integrator->SetInputDataObject(pd);
    integrator->Update();
    answer = integrator->GetOutput();
    qtotal = ((answer->GetPointData())->GetArray("Surface Flow"))->GetTuple1(0);
    areatotal = ((answer->GetCellData())->GetArray("Area"))->GetTuple1(0);
    integrator->Delete();
  } else {
    vtkSVIntegrateAttributes* integrateAtts = vtkSVIntegrateAttributes::New();
    integrateAtts->SetInputDataObject(pd);
    integrateAtts->Update();
    answer = integrateAtts->GetOutput();
    if ( !((answer->GetPointData())->HasArray( ((pd->GetPointData())->GetScalars())->GetName()))) {
      fprintf(stderr,"ERROR:  no scalar point data!\n");
      return false;
    }
    if (!((answer->GetCellData())->HasArray("Area"))) {
      fprintf(stderr,"ERROR:  no area cell data!\n");
      return false;
    }
    qtotal = ((answer->GetPointData())->GetArray( ((pd->GetPointData())->GetScalars())->GetName()))->GetTuple1(0);
    areatotal = ((answer->GetCellData())->GetArray("Area"))->GetTuple1(0);
    integrateAtts->Delete();
  }

  *q = qtotal;
  *area = areatotal;

  return true;
}

void VtpIntegrateFace(vtkSmartPointer<vtkPolyData> facevtp, std::map<std::string, double>& pmap, 
    std::map<std::string, double>& qmap, std::map<std::string, double>& amap)
{
    vtkPointData* pointData=facevtp->GetPointData();

    std::vector<std::string> pressureNames, velocityNames;

    for(int i=0;i<pointData->GetNumberOfArrays();++i)
    {
        std::string name(pointData->GetAbstractArray(i)->GetName());

        if(name.substr(0,9)=="pressure_")
            pressureNames.push_back(name);
        else if(name.substr(0,9)=="velocity_")
            velocityNames.push_back(name);
    }

    for(int i=0;i<pressureNames.size();i++)
    {
        pointData->SetActiveScalars(pressureNames[i].c_str());
        double force=0,area=0;

        sys_geom_IntegrateSurface2(facevtp,0,&force,&area);

        amap[pressureNames[i].substr(9)]=area;
        pmap[pressureNames[i].substr(9)]=force/area;
    }

    for(int i=0;i<velocityNames.size();i++)
    {
        pointData->SetActiveVectors(velocityNames[i].c_str());
        double flowrate=0,area=0;

        sys_geom_IntegrateSurface2(facevtp,1,&flowrate,&area);

        qmap[pressureNames[i].substr(9)]=flowrate;
    }

}

void VtpExtractSingleFace(std::string step, vtkSmartPointer<vtkPolyData> simvtp,vtkSmartPointer<vtkPolyData> facevtp)
{
    int faceNumPoint=facevtp->GetNumberOfPoints();
    vtkDataArray* faceNodeIDs=facevtp->GetPointData()->GetArray("GlobalNodeID");

    vtkPointData* pointData=simvtp->GetPointData();

    std::vector<std::string> pressureNames, velocityNames;

    for(int i=0;i<pointData->GetNumberOfArrays();++i)
    {
        std::string name(pointData->GetAbstractArray(i)->GetName());

        if(step=="combo")
        {
            if(name=="pressure_avg" || name=="pressure_avg_mmHg")
                continue;

            if(name.substr(0,9)=="pressure_")
                pressureNames.push_back(name);
            else if(name.substr(0,9)=="velocity_")
                velocityNames.push_back(name);
        }
        else
        {
            if(name=="pressure")
                pressureNames.push_back(name);
            else if(name=="velocity")
                velocityNames.push_back(name);
        }
    }

    std::map<int,int> mapGlobal2Local;
    vtkDataArray* simvtpGlobalIDs=pointData->GetArray("GlobalNodeID");
    for(int i=0;i<simvtp->GetNumberOfPoints();++i)
    {
        int nodeID=simvtpGlobalIDs->GetTuple1(i);
        mapGlobal2Local[nodeID]=i;
    }

    for(int i=0;i<pressureNames.size();++i)
    {
        vtkSmartPointer<vtkDoubleArray> parray=vtkSmartPointer<vtkDoubleArray>::New();
        parray->SetNumberOfComponents(1);
        parray->Allocate(100,100);

        std::string pn=pressureNames[i];
        if(step!="combo")
            pn=pn+"_"+step;

        parray->SetName(pn.c_str());

        vtkDataArray* array=pointData->GetArray(pressureNames[i].c_str());
        for(int j=0;j<faceNumPoint;++j)
        {
            int gID=faceNodeIDs->GetTuple1(j);
            int lID=mapGlobal2Local[gID];
            double p=array->GetTuple1(lID);
            parray->InsertNextTuple1(p);
        }

        facevtp->GetPointData()->AddArray(parray);
    }

    for(int i=0;i<velocityNames.size();++i)
    {
        vtkSmartPointer<vtkDoubleArray> varray=vtkSmartPointer<vtkDoubleArray>::New();
        varray->SetNumberOfComponents(3);
        varray->Allocate(100,100);

        std::string vn=velocityNames[i];
        if(step!="combo")
            vn=vn+"_"+step;

        varray->SetName(vn.c_str());

        vtkDataArray* array=pointData->GetArray(velocityNames[i].c_str());
        for(int j=0;j<faceNumPoint;++j)
        {
            int gID=faceNodeIDs->GetTuple1(j);
            int lID=mapGlobal2Local[gID];
            double* v=array->GetTuple3(lID);
            varray->InsertNextTuple3(v[0],v[1],v[2]);
        }

        facevtp->GetPointData()->AddArray(varray);
    }

}

void VtuExtractSingleFace(std::string step, vtkSmartPointer<vtkUnstructuredGrid> simug,vtkSmartPointer<vtkPolyData> facevtp)
{
    int faceNumPoint=facevtp->GetNumberOfPoints();
    vtkDataArray* faceNodeIDs=facevtp->GetPointData()->GetArray("GlobalNodeID");

    vtkPointData* pointData=simug->GetPointData();

    std::vector<std::string> pressureNames, velocityNames;

    for(int i=0;i<pointData->GetNumberOfArrays();++i)
    {
        std::string name(pointData->GetAbstractArray(i)->GetName());

        if(step=="combo")
        {
            if(name=="pressure_avg" || name=="pressure_avg_mmHg")
                continue;

            if(name.substr(0,9)=="pressure_")
                pressureNames.push_back(name);
            else if(name.substr(0,9)=="velocity_")
                velocityNames.push_back(name);
        }
        else
        {
            if(name=="pressure")
                pressureNames.push_back(name);
            else if(name=="velocity")
                velocityNames.push_back(name);
        }
    }

    std::map<int,int> mapGlobal2Local;
    vtkDataArray* simugGlobalIDs=pointData->GetArray("GlobalNodeID");
    for(int i=0;i<simug->GetNumberOfPoints();++i)
    {
        int nodeID=simugGlobalIDs->GetTuple1(i);
        mapGlobal2Local[nodeID]=i;
    }

    for(int i=0;i<pressureNames.size();++i)
    {
        vtkSmartPointer<vtkDoubleArray> parray=vtkSmartPointer<vtkDoubleArray>::New();
        parray->SetNumberOfComponents(1);
        parray->Allocate(100,100);

        std::string pn=pressureNames[i];
        if(step!="combo")
            pn=pn+"_"+step;

        parray->SetName(pn.c_str());

        vtkDataArray* array=pointData->GetArray(pressureNames[i].c_str());
        for(int j=0;j<faceNumPoint;++j)
        {
            int gID=faceNodeIDs->GetTuple1(j);
            int lID=mapGlobal2Local[gID];
            double p=array->GetTuple1(lID);
            parray->InsertNextTuple1(p);
        }

        facevtp->GetPointData()->AddArray(parray);
    }

    for(int i=0;i<velocityNames.size();++i)
    {
        vtkSmartPointer<vtkDoubleArray> varray=vtkSmartPointer<vtkDoubleArray>::New();
        varray->SetNumberOfComponents(3);
        varray->Allocate(100,100);

        std::string vn=velocityNames[i];
        if(step!="combo")
            vn=vn+"_"+step;

        varray->SetName(vn.c_str());

        vtkDataArray* array=pointData->GetArray(velocityNames[i].c_str());
        for(int j=0;j<faceNumPoint;++j)
        {
            int gID=faceNodeIDs->GetTuple1(j);
            int lID=mapGlobal2Local[gID];
            double* v=array->GetTuple3(lID);
            varray->InsertNextTuple3(v[0],v[1],v[2]);
        }

        facevtp->GetPointData()->AddArray(varray);
    }
}



bool 
CreateFlowFiles(std::string outFlowFilePath, std::string outPressureFlePath, std::string outAverageFilePath, 
     std::string outAverageUnitsFilePath, std::vector<std::string> vtxFilePaths, bool useComboFile, 
     std::string meshFaceDir, std::vector<std::string> meshFaceFileNames , std::string unit, bool skipWalls)
{
    std::map<std::string,vtkSmartPointer<vtkPolyData>> vtpMap;

    for(int i=0;i<meshFaceFileNames.size();++i)
    {
        std::string filePath=meshFaceDir+"/"+meshFaceFileNames[i];
        std::string faceName=meshFaceFileNames[i].substr(0,meshFaceFileNames[i].find_last_of('.'));

        if(skipWalls && faceName.substr(0,4)=="wall")
            continue;

        std::ifstream faceFile(filePath);
        if(!faceFile)
            continue;

        vtkSmartPointer<vtkXMLPolyDataReader> reader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
        reader->SetFileName(filePath.c_str());
        reader->Update();
        vtkSmartPointer<vtkPolyData> facevtp=reader->GetOutput();
        vtkSmartPointer<vtkDataArray> array=facevtp->GetPointData()->GetArray("GlobalNodeID");

        if(array==NULL)
            facevtp->GetPointData()->GetScalars()->SetName("GlobalNodeID");

        facevtp->GetPointData()->SetActiveScalars("GlobalNodeID");

        vtpMap[faceName]=facevtp;
    }

    std::map<std::string,vtkSmartPointer<vtkPolyData>> simVtps;
    std::map<std::string,vtkSmartPointer<vtkUnstructuredGrid>> simUgs;

    for(int i=0;i<vtxFilePaths.size();i++)
    {
        std::string vtxFilePath=vtxFilePaths[i];

        vtkSmartPointer<vtkPolyData> simvtp=NULL;
        vtkSmartPointer<vtkUnstructuredGrid> simvtu=NULL;

        if(vtxFilePath.substr(vtxFilePath.find_last_of('.'),4)==".vtp")
        {
            vtkSmartPointer<vtkXMLPolyDataReader> reader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
            reader->SetFileName(vtxFilePath.c_str());
            reader->Update();
            simvtp=reader->GetOutput();
        }
        else if(vtxFilePath.substr(vtxFilePath.find_last_of('.'),4)==".vtu")
        {
            vtkSmartPointer<vtkXMLUnstructuredGridReader> reader = vtkSmartPointer<vtkXMLUnstructuredGridReader>::New();
            reader->SetFileName(vtxFilePath.c_str());
            reader->Update();
            simvtu=reader->GetOutput();
        }

        if(useComboFile)
        {
            if(simvtp!=NULL)
                simVtps["combo"]=simvtp;

            if(simvtu!=NULL)
                simUgs["combo"]=simvtu;
        }
        else
        {
            std::string str=vtxFilePath.substr(vtxFilePath.find_last_of('_')+1);
            std::string step=str.substr(0,str.find_last_of('.'));
            if(simvtp!=NULL)
                simVtps[step]=simvtp;

            if(simvtu!=NULL)
                simUgs[step]=simvtu;
        }

    }

    if(simVtps.size()==0 && simUgs.size()==0)
        return false;

    std::map<std::string,std::map<std::string, double>> pressureMap;
    std::map<std::string,std::map<std::string, double>> flowrateMap;
    std::map<std::string,std::map<std::string, double>> areaMap;

    auto it=vtpMap.begin();
    while(it!=vtpMap.end())
    {
        for(auto step_simvtp:simVtps)
        {
            std::string step=step_simvtp.first;
            vtkSmartPointer<vtkPolyData> simvtp=step_simvtp.second;

            if(simvtp!=NULL)
                VtpExtractSingleFace(step,simvtp, it->second);
        }

        for(auto step_simug:simUgs)
        {
            std::string step=step_simug.first;
            vtkSmartPointer<vtkUnstructuredGrid> simug=step_simug.second;

            if(simug!=NULL)
                VtuExtractSingleFace(step,simug, it->second);
        }

        std::map<std::string, double> pmap;
        std::map<std::string, double> qmap;
        std::map<std::string, double> amap;

        VtpIntegrateFace(it->second,pmap,qmap,amap);

        pressureMap[it->first]=pmap;
        flowrateMap[it->first]=qmap;
        areaMap[it->first]=amap;

        it++;
    }

    ofstream pressurefs(outPressureFlePath.c_str());
    ofstream flowfs(outFlowFilePath.c_str());
    ofstream averagefs(outAverageFilePath.c_str());
    ofstream averageunitsfs(outAverageUnitsFilePath.c_str());

    pressurefs<<std::fixed<<"step\t";
    flowfs<<std::fixed<<"step\t";

    for(auto name_vtp:vtpMap)
    {
        pressurefs<<name_vtp.first<<"\t";
        flowfs<<name_vtp.first<<"\t";
    }

    pressurefs<<"\n";
    flowfs<<"\n";

    std::vector<std::string> steps;
    auto pmap=pressureMap.begin()->second;
    for(auto step:pmap)
        steps.push_back(step.first);

    for(int i=0;i<steps.size();++i)
    {
        pressurefs<<steps[i]<<"\t";
        for(auto name_pdata:pressureMap)
            pressurefs<<name_pdata.second[steps[i]]<<"\t";

        pressurefs<<"\n";
    }
    pressurefs.close();

    steps.clear();
    auto qmap=flowrateMap.begin()->second;
    for(auto step:qmap)
        steps.push_back(step.first);

    for(int i=0;i<steps.size();++i)
    {
        flowfs<<steps[i]<<"\t";
        for(auto name_fdata:flowrateMap)
            flowfs<<name_fdata.second[steps[i]]<<"\t";

        flowfs<<"\n";
    }
    flowfs.close();

    averagefs<<std::fixed<<"Face\t"<<"Pavg\t"<<"Qavg\t"<<"Pmin\t"<<"Pmin_Time\t"<<"Pmax\t"<<"Pmax_Time\t"<<"Qmin\t"<<"Qmin_Time\t"<<"Qmax\t"<<"Qmax_Time\n";
    averageunitsfs<<std::fixed<<"Face\t"<<"Pavg\t"<<"Qavg\t"<<"Pmin\t"<<"Pmin_Time\t"<<"Pmax\t"<<"Pmax_Time\t"<<"Qmin\t"<<"Qmin_Time\t"<<"Qmax\t"<<"Qmax_Time\n";
    for(auto name_vtp:vtpMap)
    {
        std::string faceName=name_vtp.first;
        pmap=pressureMap[faceName];
        qmap=flowrateMap[faceName];

        std::string step0=pmap.begin()->first;
        double pmin=pmap[step0];
        double pmax=pmap[step0];
        std::string pminStep=step0;
        std::string pmaxStep=step0;
        double pavg=0;

        step0=qmap.begin()->first;
        double qmin=qmap[step0];
        double qmax=qmap[step0];
        std::string qminStep=step0;
        std::string qmaxStep=step0;
        double qavg=0;

        for(auto step_data:pmap)
        {
            std::string step=step_data.first;
            double p=pmap[step];
            double q=qmap[step];

            if(p<pmin)
            {
                pmin=p;
                pminStep=step;
            }
            if(p>pmax)
            {
                pmax=p;
                pmaxStep=step;
            }
            if(q<qmin)
            {
                qmin=q;
                qminStep=step;
            }
            if(q>qmax)
            {
                qmax=q;
                qmaxStep=step;
            }
            pavg+=p;
            qavg+=q;
        }

        pavg/=pmap.size();
        qavg/=pmap.size();

        averagefs<<faceName<<"\t"<<pavg<<"\t"<<qavg<<"\t"
                <<pmin<<"\t"<<pminStep<<"\t"<<pmax<<"\t"<<pmaxStep<<"\t"
               <<qmin<<"\t"<<qminStep<<"\t"<<qmax<<"\t"<<qmaxStep<<"\n";

        double pscaling=1;
        double qscaling=1;

        if(unit=="mm")
        {
            pscaling=760.0/101325.0;
            qscaling=60.0/1000.0/1000.0;
        }
        else if(unit=="cm")
        {
            pscaling=76.0/101325.0;
            qscaling=60.0/1000.0;
        }
        else if(unit=="m")
        {
            pscaling=760.0/101325.0;
            qscaling=60.0*1000.0;
        }
        averageunitsfs<<faceName<<"\t"<<pavg*pscaling<<"\t"<<qavg*qscaling<<"\t"
                     <<pmin*pscaling<<"\t"<<pminStep<<"\t"<<pmax*pscaling<<"\t"<<pmaxStep<<"\t"
                    <<qmin*qscaling<<"\t"<<qminStep<<"\t"<<qmax*qscaling<<"\t"<<qmaxStep<<"\n";

    }

    averagefs.close();
    averageunitsfs.close();

    return true;
}

 
void bread_directory(const std::string& name, std::vector<std::string>& v)
{
    DIR* dirp = opendir(name.c_str());
    struct dirent * dp;
    while ((dp = readdir(dirp)) != NULL) {
        v.push_back(dp->d_name);
    }
    closedir(dirp);
}

void read_directory(const std::string& path, const std::string& name, const std::string& extension, bool addPath, 
    std::vector<std::string>& names)
{
   DIR* dirFile = opendir( path.c_str() );
   if (dirFile) {
      struct dirent* hFile;
      errno = 0;
      while (( hFile = readdir( dirFile )) != NULL ) {
         if ( !strcmp( hFile->d_name, "."  )) continue;
         if ( !strcmp( hFile->d_name, ".." )) continue;

         if (strstr(hFile->d_name, extension.c_str()) && (strstr(hFile->d_name, name.c_str()))) { 
            if (addPath) {
                names.push_back(path+hFile->d_name);
            } else {
                names.push_back(hFile->d_name);
           }
         }
      } 
      closedir( dirFile );
   }
}

//------------------
// ProcessArguments
//------------------
std::map<OptionType, std::string> ProcessArguments(int argc, char *argv[])
{
    typedef std::tuple <std::string, OptionType> OptionTuple;
    std::map<OptionType, std::string> args; 

    std::map<std::string, OptionTuple> options = {
        {"--mesh-directory", 
           std::make_tuple("The directory where the mesh surface files (.vtp) are located.", OptionType::MeshDirectory)},
        {"--output-directory", 
           std::make_tuple("The directory to write the average flow files to.", OptionType::OutputDirectory)},
        {"--results-directory", 
           std::make_tuple("The directory of the converted simulation results.", OptionType::ResultsDirectory)},
        {"--single-file", 
           std::make_tuple("Simulation results have been converted to a single .vtu file. (yes/no) ", OptionType::SingleFile)},
        {"--skip-walls", 
           std::make_tuple("Skip calculating averages for walls. (yes/no) ", OptionType::SkipWalls)},
        {"--units", 
           std::make_tuple("Units (cm, mm) ", OptionType::Units)},
    };

    bool error = false;
    bool parseOption = true;
    OptionType option;

    for (int i = 1; i < argc; ++i) {
        auto arg = argv[i]; 
        if (parseOption) {
            auto it = options.find(arg);
            if (it != options.end()) {
                option = std::get<1>(it->second);
            } else {
                std::cout << "**** ERROR: Unknown option '" << arg << "'" << std::endl;
                error = true;
                break;
            }
            parseOption = false;
        } else {
            args[option] = arg;
            parseOption = true;
        }
    }
  
    // Check for valid arguments.
    //
    if (!error && (args.size() != options.size())) {
        std::cout << "**** ERROR: Not enough arguments given" << std::endl;
        error = true;
    }

    if (!error && YesNo.count(args[OptionType::SkipWalls]) == 0) {
        std::cout << "**** ERROR: Unknown value for skip walls option: " << args[OptionType::SkipWalls] << std::endl;
        error = true;
    }

    if (!error && YesNo.count(args[OptionType::SingleFile]) == 0) {
        std::cout << "**** ERROR: Unknown value for single file option: " << args[OptionType::SingleFile] << std::endl;
        error = true;
    }

    if (!error && Units.count(args[OptionType::Units]) == 0) {
        std::cout << "**** ERROR: Unknown value for units option: " << args[OptionType::Units] << std::endl;
        error = true;
    }

    if (error) { 
        std::cout << "Usage: create-flow-files [OPTIONS]" << std::endl;
        std::cout << "OPTIONS:" << std::endl;
        for( const auto& option: options) {
            std::cout << option.first << " : " << std::get<0>(option.second) << std::endl;
        }
        exit(1);
    }


    return args;
}

//------
// main
//------
int main ( int argc, char *argv[] )
{

  // Process arguments.
  auto args = ProcessArguments(argc, argv);

  // Set output file names.
  std::string outputDir = args[OptionType::OutputDirectory];
  std::string outPressureFilePath = outputDir + "/all_results-pressures.txt";
  std::string outFlowFilePath = outputDir + "/all_results-flows.txt";
  std::string outAverageFilePath = outputDir + "/all_results-averages.txt";
  std::string outAverageUnitsFilePath = outputDir + "/all_results-averages-from_cm-to-mmHg-L_per_min.txt";
  std::cout << "Output directory: " << outputDir << std::endl;

  // Set other parameters.
  auto skipWalls = (args[OptionType::SkipWalls] == "yes"); 
  auto singleFile = (args[OptionType::SingleFile] == "yes"); 
  auto units = args[OptionType::Units];

  // Hide VTK deprecated warnings.
  vtkObject::GlobalWarningDisplayOff();

  // Read exported .vtp or .vtu results files.
  bool addPath = true;
  auto resultsDir = args[OptionType::ResultsDirectory] + "/";
  std::vector<std::string> resultsFileList;
  read_directory(resultsDir, "all_results", ".vtp", addPath, resultsFileList); 
  if (resultsFileList.size()==0) {   
      resultsFileList.clear();
      read_directory(resultsDir, "all_results", ".vtu", addPath, resultsFileList); 
  }
  std::cout << "Number of converted results files: " << resultsFileList.size() << std::endl;

  // Read surface mesh .vtp files.
  auto meshFaceDir = args[OptionType::MeshDirectory] + "/";
  std::vector<std::string> meshFaceFileNames;
  addPath = false;
  read_directory(meshFaceDir, "", ".vtp", addPath, meshFaceFileNames); 
  std::cout << "Number of face files: " << meshFaceFileNames.size() << std::endl;
  if (meshFaceFileNames.size() == 0) {
      return 1;
  }

  // Create the flow files.
  CreateFlowFiles(outFlowFilePath, outPressureFilePath, outAverageFilePath, outAverageUnitsFilePath, 
      resultsFileList, singleFile, meshFaceDir, meshFaceFileNames, units, skipWalls);

}

