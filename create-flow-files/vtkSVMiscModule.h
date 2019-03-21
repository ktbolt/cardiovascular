
#ifndef VTKSVMISC_EXPORT_H
#define VTKSVMISC_EXPORT_H

#ifdef _SIMVASCULAR_VTKSVMISC_STATIC_DEFINE
#  define VTKSVMISC_EXPORT
#  define VTKSVMISC_NO_EXPORT
#else
#  ifndef VTKSVMISC_EXPORT
#    ifdef _simvascular_vtksvmisc_EXPORTS
        /* We are building this library */
#      define VTKSVMISC_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKSVMISC_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKSVMISC_NO_EXPORT
#    define VTKSVMISC_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKSVMISC_DEPRECATED
#  define VTKSVMISC_DEPRECATED __attribute__ ((__deprecated__))
#endif

#ifndef VTKSVMISC_DEPRECATED_EXPORT
#  define VTKSVMISC_DEPRECATED_EXPORT VTKSVMISC_EXPORT VTKSVMISC_DEPRECATED
#endif

#ifndef VTKSVMISC_DEPRECATED_NO_EXPORT
#  define VTKSVMISC_DEPRECATED_NO_EXPORT VTKSVMISC_NO_EXPORT VTKSVMISC_DEPRECATED
#endif

#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef VTKSVMISC_NO_DEPRECATED
#    define VTKSVMISC_NO_DEPRECATED
#  endif
#endif

#endif /* VTKSVMISC_EXPORT_H */
