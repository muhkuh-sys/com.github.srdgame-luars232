#! /usr/bin/python3

from jonchki import cli_args
from jonchki import install
from jonchki import jonchkihere

import glob
import os
import subprocess


tPlatform = cli_args.parse()
print('Building for %s' % tPlatform['platform_id'])


# --------------------------------------------------------------------------
# -
# - Configuration
# -

# Get the project folder. This is the folder of this script.
strCfg_projectFolder = os.path.dirname(os.path.realpath(__file__))

# This is the complete path to the testbench folder. The installation will be
# written there.
strCfg_workingFolder = os.path.join(
    strCfg_projectFolder,
    'build',
    tPlatform['platform_id']
)

# Where is the jonchkihere tool?
strCfg_jonchkiHerePath = os.path.join(
    strCfg_projectFolder,
    'jonchki'
)
# This is the Jonchki version to use.
strCfg_jonchkiVersion = '0.0.12.1'
# Look in this folder for Jonchki archives before downloading them.
strCfg_jonchkiLocalArchives = os.path.join(
    strCfg_projectFolder,
    'jonchki',
    'local_archives'
)
# The target folder for the jonchki installation. A subfolder named
# "jonchki-VERSION" will be created there. "VERSION" will be replaced with
# the version number from strCfg_jonchkiVersion.
strCfg_jonchkiInstallationFolder = os.path.join(
    strCfg_projectFolder,
    'build'
)

# Select the verbose level for jonchki.
# Possible values are "debug", "info", "warning", "error" and "fatal".
strCfg_jonchkiVerbose = 'info'

strCfg_jonchkiLog51 = os.path.join(
    strCfg_workingFolder,
    'lua5.1',
    'jonchki.log'
)
strCfg_jonchkiLog54 = os.path.join(
    strCfg_workingFolder,
    'lua5.4',
    'jonchki.log'
)
strCfg_jonchkiSystemConfiguration = os.path.join(
    strCfg_projectFolder,
    'jonchki',
    'jonchkisys.cfg'
)
strCfg_jonchkiProjectConfiguration = os.path.join(
    strCfg_projectFolder,
    'jonchki',
    'jonchkicfg.xml'
)
strCfg_jonchkiDependencyLog51 = os.path.join(
    strCfg_projectFolder,
    'dependency-log-lua5.1.xml'
)
strCfg_jonchkiDependencyLog54 = os.path.join(
    strCfg_projectFolder,
    'dependency-log-lua5.4.xml'
)

# -
# --------------------------------------------------------------------------

astrCMAKE_COMPILER = None
astrCMAKE_PLATFORM = None
astrJONCHKI_SYSTEM = None
strMake = None
astrEnv = None

if tPlatform['host_distribution_id'] == 'ubuntu':
    if tPlatform['distribution_id'] == 'ubuntu':
        # Build on linux for linux.
        # It is currently not possible to build for another version of the OS.
        if tPlatform['distribution_version'] != tPlatform['host_distribution_version']:
            raise Exception('The target Ubuntu version must match the build host.')

        if tPlatform['cpu_architecture'] == tPlatform['host_cpu_architecture']:
            # Build for the build host.

            astrCMAKE_COMPILER = []
            astrCMAKE_PLATFORM = []
            astrJONCHKI_SYSTEM = []
            strMake = 'make'

        else:
            raise Exception('Unknown CPU architecture: "%s"' % tPlatform['cpu_architecture'])

    else:
        raise Exception('Unknown distribution: "%s"' % tPlatform['distribution_id'])

else:
    raise Exception(
        'Unknown host distribution: "%s"' %
        tPlatform['host_distribution_id']
    )

# Create the folders if they do not exist yet.
astrFolders = [
    strCfg_workingFolder,
    os.path.join(strCfg_workingFolder, 'lua5.4'),
    os.path.join(strCfg_workingFolder, 'lua5.4', 'build_requirements'),
]
for strPath in astrFolders:
    if os.path.exists(strPath) is not True:
        os.makedirs(strPath)

# Install jonchki.
strJonchki = jonchkihere.install(
    strCfg_jonchkiVersion,
    strCfg_jonchkiInstallationFolder,
    LOCAL_ARCHIVES=strCfg_jonchkiLocalArchives
)

# ---------------------------------------------------------------------------
#
# Get the build requirements for LUA5.4.
#
strCwd = os.path.join(strCfg_workingFolder, 'lua5.4', 'build_requirements')
for strMatch in glob.iglob(os.path.join(strCwd, 'lua5.4-luars232-*.xml')):
    os.remove(strMatch)

astrCmd = [
    'cmake',
    '-DCMAKE_INSTALL_PREFIX=""',
    '-DPRJ_DIR=%s' % strCfg_projectFolder,
    '-DBUILDCFG_ONLY_JONCHKI_CFG="ON"',
    '-DBUILDCFG_LUA_USE_SYSTEM="OFF"',
    '-DBUILDCFG_LUA_VERSION="5.4"'
]
astrCmd.extend(astrCMAKE_COMPILER)
astrCmd.extend(astrCMAKE_PLATFORM)
astrCmd.append(strCfg_projectFolder)
subprocess.check_call(' '.join(astrCmd), shell=True, cwd=strCwd, env=astrEnv)
subprocess.check_call(strMake, shell=True, cwd=strCwd, env=astrEnv)

astrMatch = glob.glob(os.path.join(strCwd, 'lua5.4-luars232-*.xml'))
if len(astrMatch) != 1:
    raise Exception('No match found for "lua5.4-luars232-*.xml".')

astrCmd = [
    strJonchki,
    'install-dependencies',
    '--verbose', strCfg_jonchkiVerbose,
    '--syscfg', strCfg_jonchkiSystemConfiguration,
    '--prjcfg', strCfg_jonchkiProjectConfiguration,
    '--logfile', strCfg_jonchkiLog54,
    '--dependency-log', strCfg_jonchkiDependencyLog54
]
astrCmd.extend(astrJONCHKI_SYSTEM)
astrCmd.append('--build-dependencies')
astrCmd.append(astrMatch[0])
subprocess.check_call(' '.join(astrCmd), shell=True, cwd=strCwd, env=astrEnv)


# ---------------------------------------------------------------------------
#
# Build the LUA5.4 version.
#
astrCmd = [
    'cmake',
    '-DCMAKE_INSTALL_PREFIX=""',
    '-DPRJ_DIR=%s' % strCfg_projectFolder,
    '-DBUILDCFG_LUA_USE_SYSTEM="OFF"',
    '-DBUILDCFG_LUA_VERSION="5.4"'
]
astrCmd.extend(astrCMAKE_COMPILER)
astrCmd.extend(astrCMAKE_PLATFORM)
astrCmd.append(strCfg_projectFolder)
strCwd = os.path.join(strCfg_workingFolder, 'lua5.4')
subprocess.check_call(' '.join(astrCmd), shell=True, cwd=strCwd, env=astrEnv)
subprocess.check_call('%s pack' % strMake, shell=True, cwd=strCwd, env=astrEnv)

