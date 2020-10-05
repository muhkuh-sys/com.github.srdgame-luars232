CMAKE_MINIMUM_REQUIRED(VERSION 2.8)

PROJECT("com.github.srdgame-luars232")

ENABLE_TESTING()
FIND_PACKAGE(PythonInterp 2.7 REQUIRED)

IF(${CMAKE_SYSTEM_NAME} STREQUAL "Windows")
	SET(SOURCES
	    src/rs232.c
	    src/rs232_windows.c
	    bindings/lua/luars232.c)
ELSE(${CMAKE_SYSTEM_NAME} STREQUAL "Windows")
	SET(SOURCES
	    src/rs232.c
	    src/rs232_posix.c
	    bindings/lua/luars232.c)
ENDIF(${CMAKE_SYSTEM_NAME} STREQUAL "Windows")

# Build the Lua module.
ADD_LIBRARY(TARGET_luars232 MODULE
            ${SOURCES})
TARGET_INCLUDE_DIRECTORIES(TARGET_luars232
                           PRIVATE ${LUA_INCLUDE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/include)
TARGET_COMPILE_DEFINITIONS(TARGET_luars232
                           PRIVATE RS232_STATIC)
TARGET_LINK_LIBRARIES(TARGET_luars232 ${LUA_LIBRARIES})

# Set the name of the output file to "core".
SET_TARGET_PROPERTIES(TARGET_luars232 PROPERTIES PREFIX "" OUTPUT_NAME "core")

# On mingw link all compiler libraries static.
IF((${CMAKE_SYSTEM_NAME} STREQUAL "Windows") AND (${CMAKE_COMPILER_IS_GNUCC}))
	SET_PROPERTY(TARGET TARGET_luars232 PROPERTY LINK_FLAGS "-static -static-libgcc -static-libstdc++")
ENDIF((${CMAKE_SYSTEM_NAME} STREQUAL "Windows") AND (${CMAKE_COMPILER_IS_GNUCC}))

# Install the lua module.
INSTALL(TARGETS TARGET_luars232
        EXPORT EXPORT_package
        LIBRARY DESTINATION ${INSTALL_DIR_LUA_MODULES}/rs232
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
        INCLUDES DESTINATION include)

INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/bindings/lua/rs232.lua
        DESTINATION ${INSTALL_DIR_LUA_SCRIPTS})

# Add tests for this module.
IF((${CMAKE_SYSTEM_NAME} STREQUAL "Windows") AND (${CMAKE_COMPILER_IS_GNUCC}))
	# Here are the MinGW specific tests.
	ADD_TEST(NAME luars232_MinGW_DLL_dependencies
	         COMMAND "${PYTHON_EXECUTABLE}" ${TEST_SCRIPT_FOLDER}/mingw_dll_dependencies.py -u lua5.1 -u lua5.2 -u lua5.3 -u lua5.4 $<TARGET_FILE:TARGET_luars232>)
ENDIF((${CMAKE_SYSTEM_NAME} STREQUAL "Windows") AND (${CMAKE_COMPILER_IS_GNUCC}))
