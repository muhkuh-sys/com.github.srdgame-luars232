local t = ...
local strDistId, strDistVersion, strCpuArch = t:get_platform()
local tResult

if strDistId=='@JONCHKI_PLATFORM_DIST_ID@' and strCpuArch=='@JONCHKI_PLATFORM_CPU_ARCH@' then
  t:install('lua_plugins/rs232/core.dll', '${install_lua_cpath}/rs232/')
  t:install('lua/rs232.lua', '${install_lua_path}/')
  tResult = true
end

return tResult
