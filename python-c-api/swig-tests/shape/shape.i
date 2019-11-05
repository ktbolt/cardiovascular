
%module shape 

%{
#include "shape.h"
#include "circle.h"
#include "square.h"
%}

/* Needed for returning vector<double> from function.
*/
%include "std_vector.i"
namespace std {
    %template(DoubleVector)  vector<double>;
}

%include "shape.h"
%include "circle.h"
%include "square.h"

