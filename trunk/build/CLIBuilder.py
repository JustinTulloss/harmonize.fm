import os.path
import string
import SCons.Builder
import SCons.Node.FS
import SCons.Util

# needed for adding methods to environment
from SCons.Script.SConscript import SConsEnvironment

def CLIRefs(env, paths, refs, **kw):
  listRefs = []
  normpaths = [env.Dir(p).abspath for p in paths]

  normpaths += env['CLIREFPATHS']

  for ref in refs:
    if not ref.endswith(env['SHLIBSUFFIX']):
      ref += env['SHLIBSUFFIX']
    pathref = detectRef(ref, normpaths, env)
    if pathref:
      listRefs.append(pathref)
    else:
      listRefs.append(ref)

  return listRefs

# look for existance of file (ref) at one of the paths
def detectRef(ref, paths, env):
  for path in paths:
    if path.endswith(ref):
      return path
    pathref = os.path.join(path, ref)
    if os.path.isfile(pathref):
      return pathref

  return ''

# the file name is included in path reference because that file won't be there
# in the first pass scons makes.  Only after the build begins, will it be there
def AddToRefPaths(env, files, **kw):
  ref = env.FindIxes(files, 'SHLIBPREFIX', 'SHLIBSUFFIX').tpath
  env['CLIREFPATHS'] = [ref] + env['CLIREFPATHS']
  return 0

def cscFlags(target, source, env, for_signature):
  listCmd = []
  if (env.has_key('WINEXE')):
    if (env['WINEXE'] == 1):
      listCmd.append('-t:winexe')
  return listCmd

def cscSources(target, source, env, for_signature):
  listCmd = []

  for s in source:
    if (str(s).endswith('.cs')):  # do this first since most will be source files
      listCmd.append(s)
    elif (str(s).endswith('.resources')):
      listCmd.append('-resource:%s' % s.get_string(for_signature))
    elif (str(s).endswith('.snk')):
      listCmd.append('-keyfile:%s' % s.get_string(for_signature))
    else:
      # just treat this as a generic unidentified source file
      listCmd.append(s)

  return listCmd

def cscRefs(target, source, env, for_signature):
  listCmd = []
  for ref in env['ASSEMBLYREFS']:
    listCmd.append('-reference:%s' % ref)
  return listCmd

MsCliBuilder = SCons.Builder.Builder(action = '$CSCCOM',
                                   source_factory = SCons.Node.FS.default_fs.Entry,
                                   suffix = '.exe')

# this check is needed because .NET assemblies like to have '.' in the name.
# scons interprets that as an extension and doesn't append the suffix as a result
def lib_emitter(target, source, env):
  newtargets = []
  for tnode in target:
    t = tnode.name
    if not t.endswith(env['SHLIBSUFFIX']):
      t += env['SHLIBSUFFIX']
    newtargets.append(t)
  return (newtargets, source)

MsCliLibBuilder = SCons.Builder.Builder(action = '$CSCLIBCOM',
                                   source_factory = SCons.Node.FS.default_fs.Entry,
                                   emitter=lib_emitter,
                                   suffix = '.dll')

res_action = SCons.Action.Action('$CLIRCCOM', '$CLIRCCOMSTR')

# prepend NAMESPACE if provided
def res_emitter(target, source, env):
  if (env.has_key('NAMESPACE')):
    newtargets = []
    for t in target:
      newtargets.append('%s.%s' % (env['NAMESPACE'], t.name))
    return (newtargets, source)
  else:
    return (targets, source)

res_builder = SCons.Builder.Builder(action=res_action,
                                    emitter=res_emitter,
                                    src_suffix='.resx',
                                    suffix='.resources',
                                    src_builder=[],
                                    source_scanner=SCons.Tool.SourceFileScanner)

SCons.Tool.SourceFileScanner.add_scanner('.resx', SCons.Defaults.CScan)

def generate(env):
  envpaths = env['ENV']['PATH']
  env['CLIREFPATHS']  = string.split(envpaths, os.pathsep)

  env['BUILDERS']['CLIProgram'] = MsCliBuilder
  env['BUILDERS']['CLILibrary'] = MsCliLibBuilder

  env['CSC']          = 'csc'
  env['_CSCLIBS']     = "${_stripixes('-r:', CILLIBS, '', '-r', '', __env__)}"
  env['_CSCLIBPATH']  = "${_stripixes('-lib:', CILLIBPATH, '', '-r', '', __env__)}"
  env['CSCFLAGS']     = SCons.Util.CLVar('-noconfig')
  env['_CSCFLAGS']    = cscFlags
  env['_CSC_SOURCES'] = cscSources
  env['_CSC_REFS']    = cscRefs
  env['CSCCOM']       = SCons.Action.Action('$CSC $CSCFLAGS $_CSCFLAGS -out:${TARGET.abspath} $_CSC_REFS $_CSC_SOURCES', '$CSCCOMSTR')
  env['CSCLIBCOM']    = SCons.Action.Action(['$CSC -t:library $CSCFLAGS $_CSCFLAGS $_CSCLIBPATH $_CSCLIBS -out:${TARGET.abspath} $_CSC_REFS $_CSC_SOURCES'], '$CSCLIBCOMSTR')
  env['CLIRC']        = 'resgen'
  env['CLIRCFLAGS']   = ''
  env['CLIRCCOM']     = '$CLIRC $CLIRCFLAGS $SOURCES $TARGETS'
  env['BUILDERS']['CLIRES'] = res_builder

  SConsEnvironment.CLIRefs = CLIRefs
  SConsEnvironment.AddToRefPaths = AddToRefPaths

def exists(env):
  return env.Detect('csc')
