"""Original GPL-3.0-only native CMake source-assembly emission.

Inputs must already be qualified privately. This emits configuration text only;
it does not translate, build, run, install, derive module bases or certify ABI.
No game bodies, addresses, cached guest objects or vendored dependencies appear.
"""
import re
from prototype_generic import _absolute_literal, msvc_library_outputs
from prototype_sdk import require

MODULES=('mcport','r020','r100','event','r101')
OBSERVERS={'damage','refill','warp_create','warp_destroy'}
SYSTEM_LIBS='dbghelp winmm glu32 opengl32 gdi32 kernel32 user32 winspool shell32 ole32 oleaut32 uuid comdlg32 advapi32'


def cmake_project(*,runtime_source,raylib_source,adapter_directory,boot_directory,
                  host_directory,observer_directory,observer_records,module_directories,
                  generic_build,bindings_file,vu_directory=None):
    """Emit the selected prototype graph; no claim that inputs exist or are fresh.

    Retains module order, override-object ownership before generic archives, /O1
    selected source flags, byte-size /Od exceptions, angle PCH spelling and the
    separately explicit VU /O2 target. No fallback library/source search occurs.
    Bootstrap is compiled without VU callbacks; it must refuse AOT at runtime.
    Caller still validates source identities, actual configure, build and native.
    """
    paths={k:_absolute_literal(v) for k,v in dict(runtime=runtime_source,raylib=raylib_source,
        adapter=adapter_directory,boot=boot_directory,host=host_directory,
        observers=observer_directory,bindings=bindings_file).items()}
    require(type(module_directories) is dict and set(module_directories)==set(MODULES),
            'Exactly five named qualified module directories required')
    modules={n:_absolute_literal(module_directories[n]) for n in MODULES}
    require(type(observer_records) is list and len(observer_records)==4 and
            {r['id'] for r in observer_records}==OBSERVERS,'Exactly four named observer records required')
    rows={r['id']:r for r in observer_records};raw_names=set();out_names=set()
    for row in rows.values():
        require(type(row['raw_basename']) is str and
                re.fullmatch(r'[A-Za-z0-9_.-]{1,180}\.cpp',row['raw_basename']) and
                row['output']=='prototype_observe_'+row['id']+'.cpp', 'Unsafe observer source name')
        raw_names.add(row['raw_basename']);out_names.add(row['output'])
    require(len(raw_names)==len(out_names)==4,'Duplicate private source selection')
    libraries=msvc_library_outputs(generic_build)
    quoted=lambda s:'"'+s+'"'
    u=paths['runtime'];host=paths['host'];boot=paths['boot'];obs=paths['observers']
    includes=[boot,u+'/runtime/ps2xRuntime/include',u+'/runtime/ps2xRuntime/src/lib/Kernel',
        u+'/runtime/ps2xRuntime/src/lib',u+'/runtime/ps2xRuntime/src/lib/vu',
        u+'/runtime/ps2xIOP/include',u+'/runtime/ps2xIOP/src',u+'/runtime/ps2xIOP/src/emulator/devices',
        u+'/src',paths['raylib'],host,host+'/overrides',paths['adapter']]
    includes += [modules[n] for n in MODULES]
    lines=['# Original GPL source-assembly configuration; populated output is PRIVATE.',
        'cmake_minimum_required(VERSION 3.23)','project(PrototypeSourceAssembly LANGUAGES CXX)',
        'if(NOT MSVC)',' message(FATAL_ERROR "This selected profile requires MSVC")','endif()',
        'set(CMAKE_CXX_STANDARD 20)','set(CMAKE_CXX_STANDARD_REQUIRED ON)',
        'set(CMAKE_EXPORT_COMPILE_COMMANDS ON)','set(CMAKE_NINJA_FORCE_RESPONSE_FILE ON)',
        'set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "/O1 /Ob2 /DNDEBUG")',
        'set(CMAKE_MSVC_RUNTIME_LIBRARY MultiThreadedDLL)',
        'file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/qualified-sdk")',
        'configure_file('+quoted(paths['bindings'])+' "${CMAKE_CURRENT_BINARY_DIR}/qualified-sdk/bindings_private.inc" COPYONLY)',
        'include_directories('+''.join('\n '+quoted(p) for p in includes)+
            '\n "${CMAKE_CURRENT_BINARY_DIR}/qualified-sdk"\n)',
        'add_compile_definitions(NOMINMAX NDEBUG)','add_compile_options(/O1 /MD /EHsc /bigobj)',
        'file(GLOB BOOT CONFIGURE_DEPENDS '+quoted(boot+'/*.cpp')+')']
    order=('damage','refill','warp_create','warp_destroy')
    for name in order:lines+=['list(REMOVE_ITEM BOOT '+quoted(boot+'/'+rows[name]['raw_basename'])+')']
    observed=' '.join(quoted(obs+'/'+rows[n]['output']) for n in order)
    lines+=['add_library(prototype_guest OBJECT ${BOOT} '+observed+')',
        'target_precompile_headers(prototype_guest PRIVATE <ps2_runtime_macros.h> <ps2_runtime.h> <ps2_recompiled_functions.h> <ps2_recompiled_stubs.h>)',
        'foreach(SOURCE IN LISTS BOOT)',' file(SIZE "${SOURCE}" SIZE)',' if(SIZE GREATER 250000)',
        '  set_source_files_properties("${SOURCE}" PROPERTIES COMPILE_OPTIONS /Od SKIP_PRECOMPILE_HEADERS ON)',
        ' endif()','endforeach()',
        'set_source_files_properties('+observed+' PROPERTIES SKIP_PRECOMPILE_HEADERS ON)',
        'set_source_files_properties('+quoted(obs+'/'+rows['refill']['output'])+' PROPERTIES COMPILE_OPTIONS /Od)']
    for name in MODULES:
        lines+=['file(GLOB MOD_'+name+' CONFIGURE_DEPENDS '+quoted(modules[name]+'/*.cpp')+')',
            'add_library(prototype_'+name+' STATIC ${MOD_'+name+'})',
            'foreach(SOURCE IN LISTS MOD_'+name+')',' file(SIZE "${SOURCE}" SIZE)',
            ' if(SIZE GREATER 250000)','  set_source_files_properties("${SOURCE}" PROPERTIES COMPILE_OPTIONS /Od)',
            ' endif()','endforeach()']
    common=[host+'/overrides/iop_sio2.cpp',host+'/overrides/ps2_controls_screen.cpp',
            u+'/src/godhand/sha256.cpp',paths['adapter']+'/locked_input_file.cpp']
    lines+=['add_library(prototype_host OBJECT '+' '.join(quoted(p) for p in common)+')']
    guestlibs=' '.join('prototype_'+n for n in MODULES)
    generic=' '.join(quoted(libraries[n]) for n in ('ps2_runtime','rlImGui','imgui','ps2_iop','raylib'))
    def executable(target,extra=''):
        return ['add_executable('+target+' '+quoted(host+'/main.cpp')+
                ' $<TARGET_OBJECTS:prototype_guest> $<TARGET_OBJECTS:prototype_host>)',
            'target_link_options('+target+' PRIVATE /LTCG /STACK:16777216 /MAP)',
            'target_link_libraries('+target+' PRIVATE '+extra+guestlibs+' '+generic+' '+SYSTEM_LIBS+')']
    lines+=executable('prototype-bootstrap')
    lines+=['target_compile_definitions(prototype-bootstrap PRIVATE PROTOTYPE_INTERPRETER_BOOTSTRAP=1)']
    if vu_directory is not None:
        vu=_absolute_literal(vu_directory)
        lines+=['file(GLOB VU CONFIGURE_DEPENDS '+quoted(vu+'/generated/*.cpp')+')',
            'add_library(prototype_vu1 STATIC ${VU} '+quoted(vu+'/vu1_wrapper.cpp')+')',
            'target_compile_options(prototype_vu1 PRIVATE /O2)']
        lines+=executable('prototype-native','prototype_vu1 ')
    return ('\n'.join(lines)+'\n').encode('utf-8')
