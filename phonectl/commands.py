
commands = {
  "tts": {
    "has_response": False
  },
  "vol": {
    "has_response": False
  },
  "zic": {
    "has_response": False
  },
  "music": {
    "has_response": False
  }
}

def has_response(cmd):
  parsed = cmd.split(":")[0]
  meta = commands.get(parsed)
  if not meta:
    return True
  resp = meta.get('has_response')
  return True if resp == None else resp
